#!/usr/bin/env python3
"""Reconstruct every sealed ANAL-006--008 NMR value and custody field.

This reader is deliberately independent of the Fold-native law implementations.
It parses the captured NMR-STAR source text directly, preserves every raw field,
and adds exact rational translations without admitting signed, floating, zero,
irrational, or imaginary values into the native proof representation.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shlex

from bs4 import BeautifulSoup
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUTPUT = SNAP / "complete-postseal-analysis-v1.json"
MISSING = {".", "?"}
TARGET_LOOP_PREFIXES = (
    "_Atom_chem_shift.",
    "_Coupling_constant.",
    "_Sample_condition_variable.",
    "_T1.",
    "_T1rho.",
    "_H_exch_rate.",
    "_Chem_shift_ref.",
    "_Sample_component.",
)
TARGET_SCALAR_PREFIXES = (
    "_Entry.",
    "_Assigned_chem_shift_list.",
    "_Coupling_constant_list.",
    "_Heteronucl_T1_list.",
    "_Heteronucl_T1rho_list.",
    "_H_exch_rate_list.",
    "_Chem_shift_reference.",
    "_Sample.",
)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def tokens(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def parse_star(path: Path) -> dict[str, object]:
    """Parse retained target loops and scalar metadata from one NMR-STAR file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    saveframe: str | None = None
    scalar_frames: dict[str, dict[str, str]] = {}
    loops: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("save_"):
            saveframe = None if stripped == "save_" else stripped[5:]
            index += 1
            continue
        if stripped == "loop_":
            loop_frame = saveframe or "global"
            index += 1
            tags: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("_"):
                tags.append(lines[index].strip().split()[0])
                index += 1
            retained = bool(tags) and any(tags[0].startswith(prefix) for prefix in TARGET_LOOP_PREFIXES)
            values: list[str] = []
            while index < len(lines) and lines[index].strip() != "stop_":
                candidate = lines[index].strip()
                if retained and candidate and not candidate.startswith("#"):
                    if candidate == ";" or candidate.startswith(";"):
                        raise SystemExit(f"unsupported multiline token in retained loop: {path.name}:{index + 1}")
                    values.extend(tokens(candidate))
                index += 1
            if retained:
                if not tags or len(values) % len(tags):
                    raise SystemExit(
                        f"incomplete NMR-STAR loop: {path.name}:{loop_frame}: "
                        f"{len(values)} values / {len(tags)} tags"
                    )
                rows = [
                    dict(zip(tags, values[offset : offset + len(tags)]))
                    for offset in range(0, len(values), len(tags))
                ]
                loops.append({"saveframe": loop_frame, "tags": tags, "rows": rows})
            index += 1
            continue
        if stripped.startswith("_"):
            scalar_parts = stripped.split(None, 1)
            if len(scalar_parts) == 2 and any(scalar_parts[0].startswith(prefix) for prefix in TARGET_SCALAR_PREFIXES):
                value = scalar_parts[1].strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                    value = value[1:-1]
                scalar_frames.setdefault(saveframe or "global", {})[scalar_parts[0]] = value
        index += 1
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "byte_count": len(path.read_bytes()),
        "line_count": len(lines),
        "text_sha256": digest(text.encode()),
        "scalar_frames": scalar_frames,
        "loops": loops,
    }


def loop_rows(parsed: dict[str, object], prefix: str) -> list[dict[str, object]]:
    gathered: list[dict[str, object]] = []
    for loop in parsed["loops"]:
        tags = loop["tags"]
        if tags and tags[0].startswith(prefix):
            for row in loop["rows"]:
                gathered.append({"saveframe": loop["saveframe"], "raw": row})
    return gathered


def exact_external_number(
    token: str,
    *,
    positive_side: str,
    negative_side: str,
    zero_status: str = "measured-coincidence",
    zero_side: str = "coincident",
) -> dict[str, object]:
    """Translate an external decimal into held side plus exact positive support."""
    if token in MISSING:
        return {
            "external_token": token,
            "custody_status": "absent-or-unreported",
            "native_side": "unresolved-hand",
            "native_magnitude": "EmptyOne",
        }
    try:
        value = Decimal(token)
    except InvalidOperation as exc:
        raise SystemExit(f"non-decimal target token: {token}") from exc
    if not value.is_finite():
        raise SystemExit(f"non-finite target token: {token}")
    if value == 0:
        return {
            "external_token": token,
            "custody_status": zero_status,
            "native_side": zero_side,
            "native_magnitude": "EmptyOne",
        }
    magnitude = Fraction(abs(value))
    return {
        "external_token": token,
        "custody_status": "measured",
        "native_side": positive_side if value > 0 else negative_side,
        "native_magnitude": f"{magnitude.numerator}/{magnitude.denominator}",
    }


def normalize_row(
    row: dict[str, object],
    value_tags: tuple[str, ...],
    *,
    positive_side: str,
    negative_side: str,
    zero_status: str = "measured-coincidence",
    zero_side: str = "coincident",
) -> dict[str, object]:
    raw = row["raw"]
    exact = {
        tag: exact_external_number(
            raw[tag], positive_side=positive_side, negative_side=negative_side,
            zero_status=zero_status, zero_side=zero_side,
        )
        for tag in value_tags
        if tag in raw
    }
    return {"saveframe": row["saveframe"], "raw": raw, "exact_translation": exact}


def missing_counts(rows: list[dict[str, object]], tags: tuple[str, ...]) -> dict[str, int]:
    return {
        tag: sum(1 for row in rows if row["raw"].get(tag) in MISSING)
        for tag in tags
    }


def frame_metadata(parsed: dict[str, object], prefix: str) -> list[dict[str, object]]:
    result = []
    for frame, values in parsed["scalar_frames"].items():
        selected = {key: value for key, value in values.items() if key.startswith(prefix)}
        if selected:
            result.append({"saveframe": frame, "fields": selected})
    return result


def complete_surface(inventory: dict[str, object]) -> tuple[dict[str, object], int, int, int]:
    reconstruction: dict[str, object] = {}
    pages = 0
    documents = 0
    characters = 0
    for source in inventory["sources"]:
        path = ROOT / source["path"]
        data = path.read_bytes()
        if len(data) != source["byte_count"] or digest(data) != source["sha256"]:
            raise SystemExit(f"captured source changed: {source['path']}")
        record: dict[str, object] = {
            "path": source["path"],
            "media_kind": source["media_kind"],
            "byte_count": len(data),
            "sha256": digest(data),
        }
        if source["media_kind"] == "pdf":
            vectors = []
            for number, page in enumerate(PdfReader(path).pages, 1):
                text = page.extract_text() or ""
                vectors.append({
                    "page": number,
                    "character_count": len(text),
                    "text_sha256": digest(text.encode()),
                })
                characters += len(text)
            record["complete_page_vector"] = vectors
            pages += len(vectors)
        elif source["media_kind"] == "html":
            text = BeautifulSoup(data, "html.parser").get_text("\n")
            record["complete_document_text"] = {
                "character_count": len(text),
                "text_sha256": digest(text.encode()),
            }
            documents += 1
            characters += len(text)
        reconstruction[path.name] = record
    return reconstruction, pages, documents, characters


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("ANAL-006--008 complete analysis exists; rebuild prohibited")
    inventory = json.loads(INVENTORY.read_text())
    if inventory["source_count"] != 10 or len(inventory["sources"]) != 10:
        raise SystemExit("NMR source inventory is not the sealed ten-source surface")
    payload = dict(inventory)
    stored_inventory_payload = payload.pop("inventory_payload_sha256")
    if canonical_digest(payload) != stored_inventory_payload:
        raise SystemExit("NMR source inventory payload seal failed")

    surface, pdf_pages, html_documents, characters = complete_surface(inventory)
    star68 = parse_star(SNAP / "bmr68_3.str")
    star16582 = parse_star(SNAP / "bmr16582_3.str")
    star52365 = parse_star(SNAP / "bmr52365_3.str")
    star27257 = parse_star(SNAP / "bmr27257_3.str")

    shift_raw = loop_rows(star68, "_Atom_chem_shift.")
    coupling_raw = loop_rows(star16582, "_Coupling_constant.")
    t1_raw = loop_rows(star52365, "_T1.")
    t1rho_raw = loop_rows(star52365, "_T1rho.")
    exchange_raw = loop_rows(star27257, "_H_exch_rate.")
    if len(shift_raw) != 556:
        raise SystemExit(f"expected complete 556-row chemical-shift vector, got {len(shift_raw)}")
    if len(coupling_raw) != 643:
        raise SystemExit(f"expected complete 643-row coupling vector, got {len(coupling_raw)}")
    if len(t1_raw) != 148:
        raise SystemExit(f"expected complete 148-row T1 vector, got {len(t1_raw)}")
    if len(t1rho_raw) != 148:
        raise SystemExit(f"expected complete 148-row T1rho vector, got {len(t1rho_raw)}")
    if len(exchange_raw) != 138:
        raise SystemExit(f"expected complete 138-row exchange vector, got {len(exchange_raw)}")

    shifts = [normalize_row(row, ("_Atom_chem_shift.Val", "_Atom_chem_shift.Val_err"), positive_side="higher-frequency", negative_side="lower-frequency") for row in shift_raw]
    couplings = [normalize_row(row, ("_Coupling_constant.Val", "_Coupling_constant.Val_min", "_Coupling_constant.Val_max", "_Coupling_constant.Val_err"), positive_side="preserving-hand", negative_side="alternating-hand") for row in coupling_raw]
    t1 = [normalize_row(row, ("_T1.Val", "_T1.Val_err"), positive_side="positive-time", negative_side="inadmissible-external-negative") for row in t1_raw]
    t1rho = [normalize_row(row, ("_T1rho.T1rho_val", "_T1rho.T1rho_val_err", "_T1rho.Rex_val", "_T1rho.Rex_val_err"), positive_side="positive-time-or-rate", negative_side="inadmissible-external-negative") for row in t1rho_raw]
    exchange = [normalize_row(
        row,
        ("_H_exch_rate.Val", "_H_exch_rate.Val_err", "_H_exch_rate.Val_min", "_H_exch_rate.Val_max"),
        positive_side="positive-rate",
        negative_side="inadmissible-external-negative",
        zero_status="unresolved-external-zero-inscription",
        zero_side="unresolved",
    ) for row in exchange_raw]

    coupling_sides = Counter(row["exact_translation"]["_Coupling_constant.Val"]["native_side"] for row in couplings)
    analysis = {
        "schema": "sft-v3-chemistry-anal-006-008-complete-postseal-analysis/1",
        "family": "ANAL-006-008-NMR",
        "inventory_sha256": digest(INVENTORY.read_bytes()),
        "inventory_payload_sha256": stored_inventory_payload,
        "complete_source_count": len(surface),
        "complete_pdf_page_count": pdf_pages,
        "complete_html_document_count": html_documents,
        "complete_extracted_character_count": characters,
        "complete_source_reconstruction": surface,
        "nmr_star_reconstruction": {
            "BMRB-68": {key: value for key, value in star68.items() if key != "loops"},
            "BMRB-16582": {key: value for key, value in star16582.items() if key != "loops"},
            "BMRB-52365": {key: value for key, value in star52365.items() if key != "loops"},
            "BMRB-27257": {key: value for key, value in star27257.items() if key != "loops"},
        },
        "anal_006": {
            "claim": "SFT-CHEM-NMR-CHEMICAL-SHIFT-006",
            "source": "BMRB entry 68",
            "reported_unit": "ppm relative to the retained reference boundary",
            "complete_row_count": len(shifts),
            "complete_shift_vector": shifts,
            "missing_field_counts": missing_counts(shift_raw, ("_Atom_chem_shift.Val", "_Atom_chem_shift.Val_err", "_Atom_chem_shift.Assign_fig_of_merit", "_Atom_chem_shift.Ambiguity_code", "_Atom_chem_shift.Details")),
            "nucleus_counts": dict(sorted(Counter(row["raw"]["_Atom_chem_shift.Atom_type"] for row in shift_raw).items())),
            "list_metadata": frame_metadata(star68, "_Assigned_chem_shift_list."),
            "reference_metadata": frame_metadata(star68, "_Chem_shift_reference."),
            "complete_reference_vector": [loop for loop in star68["loops"] if loop["tags"] and loop["tags"][0].startswith("_Chem_shift_ref.")],
            "sample_metadata": frame_metadata(star68, "_Sample."),
            "complete_sample_component_vector": [loop for loop in star68["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_component.")],
            "sample_conditions": [loop for loop in star68["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_condition_variable.")],
            "all_values_errors_ambiguities_absences_and_sites_retained": True,
        },
        "anal_007": {
            "claim": "SFT-CHEM-NMR-SPIN-COUPLING-007",
            "source": "BMRB entry 16582",
            "reported_unit": "Hz",
            "complete_row_count": len(couplings),
            "complete_list_count": len(frame_metadata(star16582, "_Coupling_constant_list.")),
            "complete_coupling_vector": couplings,
            "held_side_counts": dict(sorted(coupling_sides.items())),
            "missing_field_counts": missing_counts(coupling_raw, ("_Coupling_constant.Val", "_Coupling_constant.Val_min", "_Coupling_constant.Val_max", "_Coupling_constant.Val_err", "_Coupling_constant.Details")),
            "list_metadata": frame_metadata(star16582, "_Coupling_constant_list."),
            "sample_metadata": frame_metadata(star16582, "_Sample."),
            "complete_sample_component_vector": [loop for loop in star16582["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_component.")],
            "sample_conditions": [loop for loop in star16582["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_condition_variable.")],
            "all_signed_external_values_translated_to_held_side_plus_positive_exact_magnitude": True,
            "all_values_errors_bounds_absences_pairs_and_conditions_retained": True,
        },
        "anal_008": {
            "claim": "SFT-CHEM-NMR-RELAXATION-EXCHANGE-008",
            "sources": ["BMRB entry 52365", "BMRB entry 27257"],
            "complete_t1_row_count": len(t1),
            "complete_t1rho_row_count": len(t1rho),
            "complete_exchange_row_count": len(exchange),
            "complete_t1_vector": t1,
            "complete_t1rho_vector": t1rho,
            "complete_hydrogen_exchange_vector": exchange,
            "t1_missing_field_counts": missing_counts(t1_raw, ("_T1.Val", "_T1.Val_err")),
            "t1rho_missing_field_counts": missing_counts(t1rho_raw, ("_T1rho.T1rho_val", "_T1rho.T1rho_val_err", "_T1rho.Rex_val", "_T1rho.Rex_val_err")),
            "exchange_missing_field_counts": missing_counts(exchange_raw, ("_H_exch_rate.Val", "_H_exch_rate.Val_err", "_H_exch_rate.Val_min", "_H_exch_rate.Val_max")),
            "exchange_external_zero_inscription_count": sum(row["raw"]["_H_exch_rate.Val"] == "0" for row in exchange),
            "exchange_external_zero_translation": "unresolved structural EmptyOne; external inscription retained only as provenance",
            "sample_conditions": {
                "BMRB-52365": [loop for loop in star52365["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_condition_variable.")],
                "BMRB-27257": [loop for loop in star27257["loops"] if loop["tags"] and loop["tags"][0].startswith("_Sample_condition_variable.")],
            },
            "t1_list_metadata": frame_metadata(star52365, "_Heteronucl_T1_list."),
            "t1rho_list_metadata": frame_metadata(star52365, "_Heteronucl_T1rho_list."),
            "exchange_list_metadata": frame_metadata(star27257, "_H_exch_rate_list."),
            "all_values_errors_rates_absences_sites_processes_units_and_conditions_retained": True,
        },
        "scope_status": "complete captured finite source surfaces; not a claim about all possible molecules or experiments",
        "no_target_selection_or_row_filtering": True,
        "external_zero_tokens_retained_only_as_provenance_and_translated_to_native_coincidence_EmptyOne": True,
    }
    vector = dict(analysis)
    analysis["complete_result_vector_sha256"] = canonical_digest(vector)
    OUTPUT.write_text(json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "analysis_sha256": digest(OUTPUT.read_bytes()),
        "result_sha256": analysis["complete_result_vector_sha256"],
        "shift_rows": len(shifts),
        "coupling_rows": len(couplings),
        "t1_rows": len(t1),
        "t1rho_rows": len(t1rho),
        "exchange_rows": len(exchange),
        "coupling_sides": dict(coupling_sides),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

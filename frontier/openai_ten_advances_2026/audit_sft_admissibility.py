"""Enumerate the SFT-admissibility state of OpenAI's twelve Lean declarations.

This is a comparison audit. It never imports the SFT engine, creates a receipt,
or changes the claim census. Host integers and booleans count and check
artifacts; they are not SFT proof values.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPTURE = ROOT / "experiments/external_sources/mathematics/openai_ten_advances_mathematics_2026-08-01_v1"
UPSTREAM = CAPTURE / "upstream_tree/ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
LEDGER = ROOT / "audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json"
SPEC = HERE / "admissibility_spec.json"
MANIFEST = UPSTREAM / "formalization.yaml"
ADMISSION_RECEIPT = ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001-0e21ffcb217271dd.json"
REPORT = HERE / "admissibility_report.json"
CENSUS = HERE / "candidate_census.json"


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def parse_formalization_manifest(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_results = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw == "  main_results:":
            in_results = True
            continue
        if in_results and raw and not raw.startswith("    "):
            break
        if not in_results:
            continue
        name = re.fullmatch(r'    - name: "(.*)"', raw)
        if name:
            if current is not None:
                rows.append(current)
            current = {"name": name.group(1)}
            continue
        if current is None:
            continue
        field = re.fullmatch(r'      (declaration|file|sorry_count): (.*)', raw)
        if field:
            key, value = field.groups()
            current[key] = int(value) if key == "sorry_count" else value.strip('"')
            continue
        axioms = re.fullmatch(r'      axioms: \[(.*)\]', raw)
        if axioms:
            current["axioms"] = re.findall(r'"([^"]+)"', axioms.group(1))
    if current is not None:
        rows.append(current)
    return rows


def source_window(path: Path, line: int, radius: int = 110) -> tuple[int, int, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return start, end, "\n".join(lines[start - 1 : end])


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    receipt = json.loads(ADMISSION_RECEIPT.read_text(encoding="utf-8"))
    manifest_rows = parse_formalization_manifest(MANIFEST)
    manifest_by_declaration = {str(row["declaration"]): row for row in manifest_rows}
    spec_by_id = {row["atomic_id"]: row for row in spec["rows"]}

    if len(manifest_rows) != 12 or len(manifest_by_declaration) != 12:
        raise ValueError("the formalization manifest must expose twelve unique main declarations")
    if receipt.get("model_admitted") is not True:
        raise ValueError("the SFT admission-enforcement dependency is not model-admitted")
    registration_gate = next(row for row in receipt["gate_results"] if row["gate"] == "registration")
    if registration_gate.get("passed") is not True or "no axioms" not in registration_gate.get("detail", ""):
        raise ValueError("the model-admitted SFT registration gate does not enforce the no-axiom boundary")

    dimensions = spec["dimensions"]
    if len(dimensions) != 8 or len({row["key"] for row in dimensions}) != 8:
        raise ValueError("the comparison grammar must contain eight unique binary dimensions")
    observed_id = "__".join(row["observed"] for row in dimensions)
    required_id = "__".join(row["required"] for row in dimensions)

    census_rows: list[dict[str, object]] = []
    report_rows: list[dict[str, object]] = []
    for owner_row in ledger["rows"]:
        atomic_id = owner_row["atomic_id"]
        comparison = spec_by_id[atomic_id]
        declaration = owner_row["declaration"]
        manifest_row = manifest_by_declaration.get(declaration)
        if manifest_row is None:
            raise ValueError(f"manifest declaration missing: {declaration}")
        if manifest_row["file"] != owner_row["source_file"]:
            raise ValueError(f"source-file disagreement for {atomic_id}")
        if manifest_row.get("sorry_count") != 0:
            raise ValueError(f"upstream manifest reports sorry for {atomic_id}")
        axioms = tuple(manifest_row.get("axioms", ()))
        if axioms != ("propext", "Classical.choice", "Quot.sound"):
            raise ValueError(f"unexpected axiom vector for {atomic_id}: {axioms}")

        source_path = UPSTREAM / owner_row["source_file"]
        start, end, window = source_window(source_path, int(owner_row["source_line"]))
        if declaration.split(".")[-1] not in window:
            raise ValueError(f"declared theorem not found near frozen source line for {atomic_id}")
        missing_tokens = [token for token in comparison["required_source_tokens"] if token not in window]
        if missing_tokens:
            raise ValueError(f"source tokens missing for {atomic_id}: {missing_tokens}")

        candidates = []
        for choices in itertools.product(("observed", "required"), repeat=len(dimensions)):
            coordinates = {
                dimension["key"]: dimension[choice]
                for dimension, choice in zip(dimensions, choices)
            }
            candidate_id = "__".join(coordinates[dimension["key"]] for dimension in dimensions)
            matches_observation = candidate_id == observed_id
            is_sft_admissible = candidate_id == required_id
            candidate = {
                "atomic_id": atomic_id,
                "candidate_id": candidate_id,
                "coordinates": coordinates,
                "matches_supplied_artifact": matches_observation,
                "is_sft_admissible_form": is_sft_admissible,
                "decision": (
                    "supplied-artifact-survivor"
                    if matches_observation
                    else "eliminated-not-the-observed-source-state"
                ),
            }
            candidates.append(candidate)
            census_rows.append(candidate)
        observed = [row for row in candidates if row["matches_supplied_artifact"]]
        admissible = [row for row in candidates if row["is_sft_admissible_form"]]
        if len(candidates) != 256 or len(observed) != 1 or len(admissible) != 1:
            raise ValueError(f"candidate closure failure for {atomic_id}")

        report_rows.append(
            {
                "atomic_id": atomic_id,
                "advertised_advance": owner_row["advertised_advance"],
                "title": owner_row["title"],
                "owner": owner_row["owner"],
                "declaration": declaration,
                "source_file": owner_row["source_file"],
                "frozen_source_line": owner_row["source_line"],
                "inspected_source_window": [start, end],
                "upstream_sorry_count": manifest_row["sorry_count"],
                "upstream_axioms": list(axioms),
                "domain_conflicts": comparison["domain_conflicts"],
                "candidate_count": len(candidates),
                "observed_candidate_id": observed_id,
                "required_sft_candidate_id": required_id,
                "observed_matches_required_sft_form": observed_id == required_id,
                "verdict": "DISPROVED_AS_SUBMITTED_SFT_THEOREM",
                "verdict_scope": (
                    "The supplied declaration and proof artifact do not satisfy the unique "
                    "SFT-admissible theorem form. This is a binary theoremhood verdict inside "
                    "SFT, not a claim that Lean derives the negation of its own conclusion."
                ),
            }
        )

    grouped = {}
    for row in report_rows:
        grouped.setdefault(str(row["advertised_advance"]), []).append(row["atomic_id"])
    advertised = [
        {
            "advertised_advance": int(key),
            "atomic_declarations": value,
            "verdict": "DISPROVED_AS_SUBMITTED_SFT_RESULT",
        }
        for key, value in sorted(grouped.items(), key=lambda item: int(item[0]))
    ]
    if len(advertised) != 10 or any(not row["atomic_declarations"] for row in advertised):
        raise ValueError("ten-result grouping failed")

    census_document = {
        "schema": "sft-v3-external-proof-admissibility-census/1.0",
        "generation_rule": "Generate the complete binary product of the eight already-admitted SFT theorem-admission distinctions for every frozen external declaration.",
        "boundary": "The twelve formal declarations at OpenAI commit 94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6 and the model-admitted SFT admission gate.",
        "dimensions": dimensions,
        "candidate_count_per_declaration": 256,
        "declaration_count": 12,
        "total_candidate_count": len(census_rows),
        "candidates": census_rows,
    }
    report = {
        "schema": "sft-v3-external-proof-admissibility-report/1.0",
        "source_capture_id": ledger["source_capture_id"],
        "source_commit": ledger["source_commit"],
        "sft_admission_receipt": receipt["receipt_hash"],
        "mathematical_scope": (
            "Binary SFT theoremhood of the supplied artifacts. The audit does not import the "
            "external conclusions as SFT laws and does not assert a Lean-internal negation."
        ),
        "declaration_count": len(report_rows),
        "advertised_advance_count": len(advertised),
        "candidate_count": len(census_rows),
        "all_submitted_sft_theoremhood_claims_disproved": all(
            row["verdict"] == "DISPROVED_AS_SUBMITTED_SFT_THEOREM" for row in report_rows
        ),
        "rows": report_rows,
        "advertised_advances": advertised,
        "candidate_census_hash": canonical_hash(census_document),
    }
    CENSUS.write_text(json.dumps(census_document, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "declarations": len(report_rows),
        "advertised_advances": len(advertised),
        "candidates": len(census_rows),
        "verdict": "10/10 DISPROVED AS SUBMITTED SFT RESULTS",
        "report": str(REPORT.relative_to(ROOT)),
        "census": str(CENSUS.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()

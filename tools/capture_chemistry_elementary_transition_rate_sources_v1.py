#!/usr/bin/env python3
"""Capture the predeclared complete NIST SRD 17 KIN-001 benchmark surface."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/elementary_transition_rate_capture_spec_v1.json"
SPEC_HASH = "sha256:1274bb6d4768a49627ce2629d951df65405105cfe5b7cd6123e06b504371e29f"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-001-elementary-transition-rate-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "elementary-transition-rate-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/elementary_transition_rate_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/elementary_transition_rate_withheld_targets_v1.json"


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def text(fragment: str) -> str:
    fragment = re.sub(r"<script\b.*?</script>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<style\b.*?</style>", "", fragment, flags=re.I | re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def field(document: str, label: str) -> str:
    pattern = rf"<(?:B|b)>\s*{re.escape(label)}:\s*</(?:B|b)>(.*?)(?:<BR\s*/?>|<br\s*/?>|<P\b|<p\b)"
    match = re.search(pattern, document, flags=re.I | re.S)
    return text(match.group(1)) if match else ""


def rate_table(document: str) -> tuple[str, tuple[tuple[str, str], ...]]:
    heading = re.search(r"<h3>\s*Rate constant values calculated from the Arrhenius expression:\s*</h3>\s*(<table>.*?</table>)", document, flags=re.I | re.S)
    if not heading:
        raise ValueError("KIN-001 NIST rate table missing")
    table = heading.group(1)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table, flags=re.I | re.S)
    if len(rows) < 2:
        raise ValueError("KIN-001 NIST rate table empty")
    headers = tuple(text(cell) for cell in re.findall(r"<th[^>]*>(.*?)</th>", rows[0], flags=re.I | re.S))
    values = []
    for row in rows[1:]:
        cells = tuple(text(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S))
        if len(cells) != 2:
            raise ValueError("KIN-001 NIST rate table row changed")
        values.append((cells[0], cells[1]))
    return " | ".join(headers), tuple(values)


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("KIN-001 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-elementary-transition-rate-prefetch-capture-spec/1"
        or spec.get("all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 4
    ):
        raise ValueError("KIN-001 prefetch boundary is not value-free and complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    identities: list[dict] = []
    targets: list[dict] = []
    source_summaries: list[dict] = []
    target_ordinal = 1
    for source in spec["sources"]:
        raw = fetch(source["detail_url"])
        raw_path = SNAPSHOT_ROOT / (source["source_id"].lower() + ".html")
        raw_path.write_bytes(raw)
        document = raw.decode("utf-8", "replace")
        metadata = {
            name: field(document, name)
            for name in (
                "Author(s)", "Title", "Journal", "Volume", "Page(s)", "Year", "Reference type", "Squib",
                "Reaction", "Reaction order", "Temperature", "Rate expression", "Uncertainty", "Pressure", "Bath gas",
                "Category", "Data type", "Experimental procedure", "Time resolution", "Excitation technique", "Analytical technique",
            )
        }
        header, values = rate_table(document)
        if metadata["Category"] != "Experiment" or "measured" not in metadata["Data type"].lower():
            raise ValueError(f"KIN-001 declared direct experimental category changed: {source['source_id']}")
        if metadata["Reaction order"] not in {"1", "2", "3"}:
            raise ValueError("KIN-001 source-declared external order class changed")
        if not metadata["Reaction"] or not values:
            raise ValueError("KIN-001 source identity or complete rate vector missing")
        target_ids = []
        for row_ordinal, (temperature, rate) in enumerate(values, start=1):
            target_id = f"SFT-CHEM-KIN-001-ELEMENTARY-RATE-{target_ordinal:04d}"
            identities.append({
                "target_id": target_id,
                "source_id": source["source_id"],
                "record_id": source["record_id"],
                "source_row_ordinal": row_ordinal,
                "all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent": True,
            })
            targets.append({
                "target_id": target_id,
                "source_id": source["source_id"],
                "record_id": source["record_id"],
                "source_row_ordinal": row_ordinal,
                "complete_source_metadata": metadata,
                "rate_table_header": header,
                "temperature_K_external_inscription": temperature,
                "rate_external_inscription": rate,
                "rate_unit_external_inscription": header.split(" | ", 1)[1] if " | " in header else "",
                "source_reported_rate_is_arrhenius_tabulation_of_direct_experimental_record": True,
                "raw_event_count_claimed": False,
            })
            target_ids.append(target_id)
            target_ordinal += 1
        source_summaries.append({
            "source_id": source["source_id"],
            "record_id": source["record_id"],
            "snapshot_path": str(raw_path.relative_to(ROOT)),
            "snapshot_hash": sha_file(raw_path),
            "complete_source_metadata": metadata,
            "complete_rate_table_header": header,
            "complete_rate_row_count": len(values),
            "target_ids_in_source_order": target_ids,
        })

    orders: dict[str, int] = {}
    for row in source_summaries:
        order = row["complete_source_metadata"]["Reaction order"]
        orders[order] = orders.get(order, 0) + row["complete_rate_row_count"]
    if set(orders) != {"1", "2", "3"}:
        raise ValueError("KIN-001 declared external topology coverage changed")
    identity_doc = {
        "schema": "sft-v3-elementary-transition-rate-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_source_count": len(source_summaries),
        "complete_target_count": len(identities),
        "all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-elementary-transition-rate-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_source_count": len(source_summaries),
        "complete_target_count": len(targets),
        "source_declared_order_row_counts": orders,
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-elementary-transition-rate-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "complete_source_count": len(source_summaries),
        "complete_target_count": len(targets),
        "source_declared_order_row_counts": orders,
        "source_summaries": source_summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_declared_source_pages_and_rate_rows_preserved": True,
        "source_reported_arrhenius_tabulations_retained_only_as_postseal_external_records": True,
        "mass_action_rate_equation_reaction_order_arrhenius_logarithm_concentration_derivative_continuum_selection_fit_or_target_correction_used_in_law": False,
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "complete_source_count": len(source_summaries),
        "complete_target_count": len(targets),
        "source_declared_order_row_counts": orders,
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["snapshot_hash"] for row in source_summaries],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

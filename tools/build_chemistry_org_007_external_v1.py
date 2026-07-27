#!/usr/bin/env python3
"""Build the complete post-seal ORG-007 external structure/mechanism vector."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY_PATH = Path("experiments/external_sources/chemistry/org_007_target_identities_v1.json")
IDENTITY_HASH = "sha256:5dcb77e93b457fc4c02e93c3b8aac171d0813ecee72c8046e2cef36a2c585bff"
CORRECTION_PATH = Path("experiments/external_sources/chemistry/org_007_identity_hash_correction_v2.json")
SEAL_PATH = Path("experiments/sealed_predictions/chemistry_org_007_nucleophilic_substitution_pre_source_v1.json")
SEAL_PAYLOAD_HASH = "sha256:70f38b8bb83b54b5613c9ea8f3639f15dc0382dd80afed58247b5e7a4add287e"
INVENTORY_PATH = Path("experiments/external_sources/chemistry/snapshots/org-007-blind-v1/source-inventory-v1.json")
OUTPUT_PATH = Path("experiments/external_sources/chemistry/org_007_complete_targets_v1.json")
PRIMARY_PATH = Path("experiments/external_sources/chemistry/snapshots/org-007-blind-v1/org-007-primary-record-v1.json")


def _formula(value: str) -> dict[str, int]:
    core = value.rstrip("+-")
    rows = re.findall(r"([A-Z][a-z]?)([1-9][0-9]*)?", core)
    if not rows or "".join(element + count for element, count in rows) != core:
        raise ValueError(f"unparsed formula: {value}")
    result: dict[str, int] = {}
    for element, count in rows:
        result[element] = result.get(element, 0) + (int(count) if count else 1)
    return result


def _sum_formula(*rows: dict[str, int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            result[key] = result.get(key, 0) + value
    return dict(sorted(result.items()))


def main() -> int:
    if hash_file(ROOT / IDENTITY_PATH) != IDENTITY_HASH:
        raise SystemExit("ORG-007 identity changed: VOID_INVALID_HALTED")
    seal = json.loads((ROOT / SEAL_PATH).read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != SEAL_PAYLOAD_HASH or sha256_identity(seal) != SEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-007 prediction changed: VOID_INVALID_HALTED")
    identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))["rows"]
    inventory = json.loads((ROOT / INVENTORY_PATH).read_text(encoding="utf-8"))
    captured = {row["target_id"]: row for row in inventory["rows"]}
    correction = json.loads((ROOT / CORRECTION_PATH).read_text(encoding="utf-8"))
    corrected_hashes = {
        row["target_id"]: row["correct_frozen_family_snapshot_sha256"] for row in correction["corrections"]
    }
    target_rows = []
    payloads: dict[str, dict] = {}
    for identity in identities:
        target_id = identity["target_id"]
        if target_id in corrected_hashes:
            snapshot_path = Path(identity["registered_snapshot_path"])
            expected_hash = corrected_hashes[target_id]
            status = "preserved-development-observed"
        else:
            capture = captured[target_id]
            snapshot_path = Path(capture["snapshot_path"])
            expected_hash = capture["snapshot_sha256"]
            status = capture["response_status"]
        if hash_file(ROOT / snapshot_path) != expected_hash:
            raise SystemExit(f"ORG-007 source changed: {snapshot_path}")
        payload = json.loads((ROOT / snapshot_path).read_text(encoding="utf-8"))
        payloads[target_id] = payload
        target_rows.append({
            **{key: identity[key] for key in (
                "target_id", "source_id", "authority", "registered_identity", "source_record_role", "custody_class"
            )},
            "opened_snapshot_path": str(snapshot_path),
            "opened_snapshot_sha256": expected_hash,
            "response_status": status,
            "source_outcome": payload,
            "target_payload_hash": sha256_identity((target_id, identity["source_record_role"], payload)),
        })
    term_text = {
        target_id: " ".join(definition.get("text", "") for definition in payload["term"].get("definitions", ()))
        for target_id, payload in payloads.items() if "term" in payload
    }
    properties = {
        target_id: payload["PropertyTable"]["Properties"][0]
        for target_id, payload in payloads.items() if "PropertyTable" in payload
    }
    source_atoms = _sum_formula(
        _formula(properties["SFT-CHEM-ORG-007-006"]["MolecularFormula"]),
        _formula(properties["SFT-CHEM-ORG-007-007"]["MolecularFormula"]),
    )
    terminal_atoms = _sum_formula(
        _formula(properties["SFT-CHEM-ORG-007-008"]["MolecularFormula"]),
        _formula(properties["SFT-CHEM-ORG-007-009"]["MolecularFormula"]),
    )
    analysis = {
        "complete_target_count": len(target_rows),
        "development_observed_target_count": 2,
        "postseal_outcome_unopened_target_count": 7,
        "complete_source_count": len({row["source_id"] for row in target_rows}),
        "all_registered_new_sources_returned_http_200": all(row["response_status"] == "http-200" for row in inventory["rows"]),
        "entering_group_forms_bond": "forms a bond" in term_text["SFT-CHEM-ORG-007-003"],
        "substitution_elementary_or_stepwise_replacement": all(token in term_text["SFT-CHEM-ORG-007-004"] for token in ("elementary or stepwise", "replaced by another")),
        "heterolysis_retains_both_bonding_electrons_on_one_fragment": all(token in term_text["SFT-CHEM-ORG-007-005"] for token in ("both bonding electrons", "remain with one")),
        "development_nucleophile_donates_both_bonding_electrons": "donating both bonding electrons" in term_text["SFT-CHEM-ORG-007-001"],
        "development_substitution_leaving_group_retains_both_electrons": "retains both electrons" in term_text["SFT-CHEM-ORG-007-002"],
        "development_mechanism_one_and_two_step_surface_present": all(token in json.dumps(payloads["SFT-CHEM-ORG-007-002"]) for token in ("two-step", "one-step")),
        "source_formula_vector": source_atoms,
        "terminal_formula_vector": terminal_atoms,
        "complete_formula_inventory_conserved": source_atoms == terminal_atoms,
        "source_substrate_connectivity": properties["SFT-CHEM-ORG-007-006"]["ConnectivitySMILES"],
        "entering_carrier_connectivity": properties["SFT-CHEM-ORG-007-007"]["ConnectivitySMILES"],
        "terminal_product_connectivity": properties["SFT-CHEM-ORG-007-008"]["ConnectivitySMILES"],
        "leaving_carrier_connectivity": properties["SFT-CHEM-ORG-007-009"]["ConnectivitySMILES"],
        "carbon_bromine_source_and_carbon_oxygen_terminal": properties["SFT-CHEM-ORG-007-006"]["ConnectivitySMILES"] == "CBr" and properties["SFT-CHEM-ORG-007-008"]["ConnectivitySMILES"] == "CO",
        "all_favourable_adverse_absent_and_unresolved_rows_preserved": len(target_rows) == 9,
        "identity_hash_typo_correction_preserved_without_recapture": correction["target_or_scientific_outcome_changed"] is False and correction["source_recapture_performed"] is False,
        "source_recapture_count": 0,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in target_rows)),
    }
    output = {
        "schema": "sft-v3-complete-postseal-target-vector/1",
        "claim_id": "SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007",
        "complete_registered_target_count": 9,
        "all_favourable_adverse_absent_and_unresolved_rows_preserved": True,
        "v1_identity_hash_transcription_error_preserved_and_corrected_in_v2": True,
        "rows": target_rows,
    }
    primary = {
        "schema": "sft-v3-exact-postseal-analysis/1",
        "claim_id": output["claim_id"],
        "identity_path": str(IDENTITY_PATH),
        "identity_hash": IDENTITY_HASH,
        "correction_path": str(CORRECTION_PATH),
        "correction_hash": hash_file(ROOT / CORRECTION_PATH),
        "prediction_path": str(SEAL_PATH),
        "prediction_payload_hash": SEAL_PAYLOAD_HASH,
        "inventory_path": str(INVENTORY_PATH),
        "inventory_hash": hash_file(ROOT / INVENTORY_PATH),
        "exact_postseal_analysis": analysis,
    }
    (ROOT / OUTPUT_PATH).write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / PRIMARY_PATH).write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(target_rows), "analysis": analysis}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

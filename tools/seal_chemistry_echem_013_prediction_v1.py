#!/usr/bin/env python3
"""Seal the ECHEM-013 law and value-free targets before claim-specific extraction."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/sealed_predictions/chemistry_echem_013_storage_handoff_pre_source_v1.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("ECHEM-013 prediction seal already exists")
    law = "sft/chemistry/electrochemical_storage_handoff_law_v1.py"
    identity = "experiments/external_sources/chemistry/echem_013_target_identities_v1.json"
    if digest(ROOT / law) != "sha256:2449e8773a71a2b256096fb603912a3b4ec73e839d6c891d2b496798f254ce74" or digest(ROOT / identity) != "sha256:b5590b443b430b90104bed6bfff1012fbdef81145f19acc8d8734f0be565c221":
        raise SystemExit("ECHEM-013 law or target identity changed")
    payload = {
        "schema": "sft-v3-target-value-blind-derivation-seal/1", "branch": "chemistry", "family": "ECHEM-013", "claim_id": "SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013", "obligation_id": "SFT-CHEM-OBL-ECHEM-013", "sealed_date": "2026-07-28",
        "derivation_path": law, "derivation_hash": digest(ROOT / law), "target_identity_path": identity, "target_identity_hash": digest(ROOT / identity), "candidate_cardinality": 256, "operational_witness_count": 8,
        "predicted_unique_survivor": "complete-storage-coordinate-custody__chemistry-owns-species-reactions__materials-own-bulk-device-response__engineering-owns-implementation__exactly-one-owner-per-coordinate__explicit-directed-claim-handoff__complete-chemistry-material-record-pair__new-coordinate-requires-new-unique-owner",
        "predicted_external_result": "The live admitted records must preserve Chemistry ownership of cell species/reactions, Materials ownership of bulk response/degradation and Engineering ownership of implementation, with one explicit owner and one directed handoff per coordinate and no duplicate ownership.",
        "complete_source_values_units_uncertainties_corrections_and_outcomes_opened_for_this_claim_before_seal": False,
        "registered_inherited_source_surface_was_development_observed_before_claim_specific_extraction": True,
        "external_value_or_outcome_used_by_candidate_generator_or_eliminator": False,
    }
    payload["sealed_payload_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"seal": OUT.relative_to(ROOT).as_posix(), "seal_sha256": digest(OUT), "payload_sha256": payload["sealed_payload_hash"]}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create four separate value-free ECHEM-005–008 seals before source capture."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLAIMS = (
    {
        "key": "005", "claim_id": "SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005",
        "obligation_id": "SFT-CHEM-OBL-ECHEM-005", "law": "sft/chemistry/electrochemical_work_law_v1.py",
        "law_hash": "sha256:2f2b1901ca92f2f5e518fc3ee018440aa6df0e9d3dd4464e1975987cfff5b97f",
        "identity": "experiments/external_sources/chemistry/echem_005_target_identities_v1.json",
        "identity_hash": "sha256:a428b42998d2287c1432f7ccead2a41f10d17b6cf9426b2b0e5a59a6368981a7",
        "output": "experiments/sealed_predictions/chemistry_echem_005_electrochemical_work_pre_source_v1.json",
        "survivor": "complete-cell-chemical-electrical-custody__positive-counted-transfer-carriers__positive-potential-separation-with-held-direction__exact-carrier-potential-product__held-work-reaction-correspondence__structural-EmptyOne-equilibrium__complete-cell-work-equilibrium-vector__exact-path-reversal-preserves-positive-work",
        "prediction": "The complete held carrier count composed with each positive cell-potential separation must reconstruct the complete positive electrochemical-work vector, while held direction reverses with the chemical and electrical paths and exact equilibrium closes structurally to EmptyOne.",
    },
    {
        "key": "006", "claim_id": "SFT-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006",
        "obligation_id": "SFT-CHEM-OBL-ECHEM-006", "law": "sft/chemistry/electrolysis_product_law_v1.py",
        "law_hash": "sha256:e3b1644f6f8d7abfa40308359e63932d318057aad2a65b96f5b184eb2ebb4e97",
        "identity": "experiments/external_sources/chemistry/echem_006_target_identities_v1.json",
        "identity_hash": "sha256:0db005f92628714b58eb8d40156fc0aeff18dd0163ecad14ca900d8cfc51157c",
        "output": "experiments/sealed_predictions/chemistry_echem_006_electrolysis_product_pre_source_v1.json",
        "survivor": "complete-process-electrode-product-custody__positive-counted-transfer-occurrences__positive-carriers-per-product-occurrence__exact-carrier-to-product-ratio__complete-products-plus-held-remainder__structural-EmptyOne-no-complete-product__complete-charge-product-amount-vector__like-batches-compose-by-counted-addition",
        "prediction": "Every complete electrolysis run must preserve process, electrode, charge, time, product and correction custody, with product amount equal to the exact transferred-carrier to stoichiometric-carrier ratio and no discarded remainder.",
    },
    {
        "key": "007", "claim_id": "SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007",
        "obligation_id": "SFT-CHEM-OBL-ECHEM-007", "law": "sft/chemistry/ionic_conductivity_law_v1.py",
        "law_hash": "sha256:7d74fb8bfe427f607aa8491b0652f7c01077939eaaa30e9d6aab5405b3843dff",
        "identity": "experiments/external_sources/chemistry/echem_007_target_identities_v1.json",
        "identity_hash": "sha256:a519269266aa9b5f136253657c3fc6f5409eaa884e2812b10b858b6597843574",
        "output": "experiments/sealed_predictions/chemistry_echem_007_ionic_conductivity_pre_source_v1.json",
        "survivor": "complete-species-resolved-carrier-vector__held-species-transport-direction__complete-held-electrolyte-composition__one-common-held-condition__finite-held-path-resource-account__exact-sum-of-species-responses__complete-traceable-conductivity-vector__positive-species-successor-increases-response",
        "prediction": "Every certified conductivity result must retain the complete electrolyte, temperature, finite cell, unit, uncertainty and traceability record and correspond to the exact positive aggregate of all registered species-resolved transport contributions.",
    },
    {
        "key": "008", "claim_id": "SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008",
        "obligation_id": "SFT-CHEM-OBL-ECHEM-008", "law": "sft/chemistry/ionic_mobility_transference_law_v1.py",
        "law_hash": "sha256:f3be3f92e53b2a1ac6e4f641b4a40f5b2c5940aed212c60f2057ea88e04c2b21",
        "identity": "experiments/external_sources/chemistry/echem_008_target_identities_v1.json",
        "identity_hash": "sha256:6f7a84294612efa2d3d9e4a7992310e4d8b4eb9e1d4c0c73dbe9927ea5eac35b",
        "output": "experiments/sealed_predictions/chemistry_echem_008_ionic_mobility_transference_pre_source_v1.json",
        "survivor": "complete-held-ionic-species-identity__held-species-mobility-direction__exact-traversal-per-carrier-resource-ratio__common-composition-condition-path__exact-species-contribution-partition__transference-parts-sum-exactly-to-One__structural-EmptyOne-absent-species__complete-mobility-transference-vector",
        "prediction": "Every complete mobility and transference record must retain species, direction, concentration, method and condition, and every finite species contribution must partition the complete current exactly to One without fitted normalization.",
    },
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main() -> None:
    outputs = []
    for row in CLAIMS:
        law, identity, output = (ROOT / row[name] for name in ("law", "identity", "output"))
        if output.exists():
            raise SystemExit(f"pre-source seal already exists: {output}")
        if digest(law.read_bytes()) != row["law_hash"] or digest(identity.read_bytes()) != row["identity_hash"]:
            raise SystemExit(f"value-free authority changed before seal: ECHEM-{row['key']}")
        payload = {
            "schema": "sft-v3-target-value-blind-derivation-seal/1", "branch": "chemistry",
            "family": "ECHEM-005-008", "claim_id": row["claim_id"], "obligation_id": row["obligation_id"],
            "sealed_date": "2026-07-28", "derivation_path": row["law"], "derivation_hash": row["law_hash"],
            "target_identity_path": row["identity"], "target_identity_hash": row["identity_hash"],
            "candidate_cardinality": 256, "operational_witness_count": 8,
            "predicted_unique_survivor": row["survivor"], "predicted_external_result": row["prediction"],
            "complete_source_values_units_uncertainties_corrections_and_outcomes_opened_for_this_claim_before_seal": False,
            "external_value_or_outcome_used_by_candidate_generator_or_eliminator": False,
        }
        payload["sealed_payload_hash"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        outputs.append({"claim_id": row["claim_id"], "seal_path": row["output"], "seal_sha256": digest(output.read_bytes()), "canonical_payload_sha256": payload["sealed_payload_hash"]})
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()

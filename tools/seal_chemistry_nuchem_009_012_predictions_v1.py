#!/usr/bin/env python3
"""Seal four NUCHEM-009–012 derivations before complete-source access."""
import hashlib
import json
from pathlib import Path

from sft.chemistry.fission_product_distribution_law_v1 import EXACT_RESULT as N011_RESULT, OPERATIONAL_WITNESSES as N011_WITNESSES
from sft.chemistry.radiochemical_separation_law_v1 import EXACT_RESULT as N010_RESULT, OPERATIONAL_WITNESSES as N010_WITNESSES
from sft.chemistry.radiolysis_network_law_v1 import EXACT_RESULT as N012_RESULT, OPERATIONAL_WITNESSES as N012_WITNESSES
from sft.chemistry.radiotracer_custody_law_v1 import EXACT_RESULT as N009_RESULT, OPERATIONAL_WITNESSES as N009_WITNESSES


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "experiments/external_sources/chemistry/nuchem_009_012_family_source_identity_registry_v1.json"
CONFIG = {
    "009": ("SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009", "SFT-CHEM-OBL-NUCHEM-009", "sft/chemistry/radiotracer_custody_law_v1.py", "experiments/external_sources/chemistry/nuchem_009_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_009_pre_source_v1.json", N009_RESULT, N009_WITNESSES, "IAEA title publication identity and search-result scope observed; complete pages case tables curves recovery vectors and limits unopened"),
    "010": ("SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010", "SFT-CHEM-OBL-NUCHEM-010", "sft/chemistry/radiochemical_separation_law_v1.py", "experiments/external_sources/chemistry/nuchem_010_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_010_pre_source_v1.json", N010_RESULT, N010_WITNESSES, "DOE title abstract and disclosed selected recovery/concentration/time snippets observed; complete report tables figures uncertainties and adverse rows unopened"),
    "011": ("SFT-CHEM-FISSION-PRODUCT-CHEMICAL-DISTRIBUTION-011", "SFT-CHEM-OBL-NUCHEM-011", "sft/chemistry/fission_product_distribution_law_v1.py", "experiments/external_sources/chemistry/nuchem_011_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_011_pre_source_v1.json", N011_RESULT, N011_WITNESSES, "ORNL title abstract chemical-group conclusion and disclosed operating-duration snippets observed; complete report samples distributions and discrepancies unopened"),
    "012": ("SFT-CHEM-RADIATION-CHEMISTRY-REACTION-NETWORK-012", "SFT-CHEM-OBL-NUCHEM-012", "sft/chemistry/radiolysis_network_law_v1.py", "experiments/external_sources/chemistry/nuchem_012_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_012_pre_source_v1.json", N012_RESULT, N012_WITNESSES, "NBS title scope and disclosed selected G-value/assumption snippets observed; complete report tables reactions conditions and references unopened"),
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    registry_hash = digest((ROOT / REGISTRY).read_bytes())
    if registry_hash != "sha256:ff9ae4d8616b9e5889028876f217e5d0c356d30fa146dd2b5ae90cb2bab06628": raise SystemExit("NUCHEM-009–012 registry changed")
    for key, (claim, obligation, law, identity, output, result, witnesses, disclosure) in CONFIG.items():
        target = ROOT / output
        if target.exists(): raise SystemExit(f"refusing to replace existing seal: {output}")
        law_hash = digest((ROOT / law).read_bytes()); identity_hash = digest((ROOT / identity).read_bytes())
        if len(witnesses) != 8 or not all(row[2] for row in witnesses): raise SystemExit(f"NUCHEM-{key} native witnesses fail")
        payload = {
            "branch": "chemistry", "candidate_cardinality": 256, "claim_id": claim,
            "complete_postseal_source_capture_had_occurred_before_this_seal": False,
            "derivation_hash": law_hash, "derivation_path": law, "family": "NUCHEM-009-012", "obligation_id": obligation,
            "operational_witness_count": len(witnesses), "predicted_unique_survivor": result,
            "prior_source_exposure_never_relabelled_blind": True,
            "schema": "sft-v3-source-exposure-disclosed-derivation-seal/1", "sealed_date": "2026-07-28",
            "source_exposure_before_seal": disclosure,
            "source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator": False,
            "target_identity_hash": identity_hash, "target_identity_path": identity,
            "source_identity_registry_hash": registry_hash, "source_identity_registry_path": REGISTRY,
        }
        payload["sealed_payload_hash"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"NUCHEM-{key} {digest(target.read_bytes())} payload {payload['sealed_payload_hash']}")


if __name__ == "__main__": main()

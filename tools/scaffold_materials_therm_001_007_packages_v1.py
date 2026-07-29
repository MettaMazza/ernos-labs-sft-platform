#!/usr/bin/env python3
"""Create registered THERM claim and experiment packages from frozen specifications."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.materials.therm_001_007_external_v1 import experiment_registration
from sft.materials.therm_001_007_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import completeness_record, survivor_id

REGISTRY_ID = "sha256:995810dd416c4b7808a9f294702680c05b7a28a27a6363dc8301433c24e488bf"
VECTOR_ID = "sha256:79c47758e02694ba53a827e50e2142a28f66d76d13805bc22e8e5d89dbb44cfb"

def write(path, value):
    if path.exists():
        raise SystemExit("refusing to overwrite " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n")

def main():
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-THERM-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "materials",
            "subbranch": "thermal_transport_storage_expansion_thermoelectric",
            "claim_id": claim_id,
            "title": spec.title,
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
            "axioms": [],
            "free_parameters": [],
            "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)), "unique_survivor": survivor_id(spec)},
            "excluded_inputs": list(spec.exclusions),
            "empirical_protocol": f"experiments/materials/{experiment_id}/registration.json",
            "provenance_classes": ["forward_forcing"],
            "pre_source_target_registry": "census/materials_therm_001_007_target_registry_v1.json",
            "pre_source_target_registry_identity": REGISTRY_ID,
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_pending_untouched_engine_admission",
        })
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why THERM-{spec.number} requires a derivation check\n\n{spec.statement}\n\nThe 256-form grammar is generated before target release, independently reconstructed and compared against every registered authoritative record.\n")
        write(package / "execution.py", f"from pathlib import Path\nfrom sft.materials.therm_001_007_execution_v1 import build_execution as assemble\ndef build_execution(root: Path):\n    return assemble(root, {claim_id!r}, Path(__file__).resolve())\n")
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json",
            "schema": "sft-v3-materials-therm-experiment-registration/1",
            **experiment_registration(spec),
            "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence",
            "target_registry": "census/materials_therm_001_007_target_registry_v1.json",
            "source_custody_manifest": "experiments/external_sources/materials/therm_001_007_v1/source_custody_manifest.json",
            "complete_evidence_vector": "experiments/external_sources/materials/therm_001_007_v1/complete_evidence_vector_v1.json",
            "complete_evidence_vector_identity": VECTOR_ID,
            "absence_boundary": {"display_glyph": "0", "native_proof_form": "structural absence held as labelled empty form", "numerical_zero_as_physical_quantity_admitted": False},
            "all_result_classes_required": True,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_sources_captured_post_registry_pending_engine",
        })
    print("scaffolded", len(ORDER), "THERM packages")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create all CLASS claim and experiment packages from frozen specifications."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.engine.canonical import sha256_identity
from sft.materials.class_001_012_external_v1 import experiment_registration
from sft.materials.class_001_012_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import completeness_record, survivor_id

REGISTRY_ID = "sha256:3456a863536e3e6e53553873492614d9c9eadc9dae9bf812bc23b696a9f141b0"
VECTOR_ID = "sha256:116dfab5d175249bcd629eb120d55b224eb6948f24133a200ff787d67eb11fdc"

def write(path, value):
    if path.exists():
        raise SystemExit("refusing to overwrite " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n")

def main():
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-CLASS-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        write(package / "registration.json", {"$schema": "../../governance/claim.schema.json", "branch": "materials", "subbranch": "metals_alloys_ceramics_glasses_polymers_composites", "claim_id": claim_id, "title": spec.title, "statement": spec.statement, "dependencies": list(spec.dependencies), "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"], "axioms": [], "free_parameters": [], "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)), "unique_survivor": survivor_id(spec)}, "excluded_inputs": list(spec.exclusions), "empirical_protocol": f"experiments/materials/{experiment_id}/registration.json", "provenance_classes": ["forward_forcing"], "pre_source_target_registry": "census/materials_class_001_012_target_registry_v1.json", "pre_source_target_registry_identity": REGISTRY_ID, "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_pending_untouched_engine_admission"})
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why CLASS-{spec.number} requires a derivation check\n\n{spec.statement}\n\nThe 256-form grammar is generated before target release, independently reconstructed and compared against every registered authoritative record.\n")
        write(package / "execution.py", f"from pathlib import Path\nfrom sft.materials.class_001_012_execution_v1 import build_execution as assemble\ndef build_execution(root: Path):\n    return assemble(root, {claim_id!r}, Path(__file__).resolve())\n")
        write(experiment / "registration.json", {"$schema": "../../../governance/experiment.schema.json", "schema": "sft-v3-materials-class-experiment-registration/1", **experiment_registration(spec), "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence", "target_registry": "census/materials_class_001_012_target_registry_v1.json", "source_custody_manifest": "experiments/external_sources/materials/class_001_012_v1/source_custody_manifest.json", "complete_evidence_vector": "experiments/external_sources/materials/class_001_012_v1/complete_evidence_vector_v1.json", "complete_evidence_vector_identity": VECTOR_ID, "absence_boundary": {"display_glyph": "0", "native_proof_form": "structural absence held as labelled empty form", "numerical_zero_as_physical_quantity_admitted": False}, "all_result_classes_required": True, "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_sources_captured_post_registry_pending_engine"})
    print("scaffolded", len(ORDER), "CLASS packages")

if __name__ == "__main__":
    main()

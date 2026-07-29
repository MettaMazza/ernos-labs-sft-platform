#!/usr/bin/env python3
"""Create registered MAGSC claim and experiment packages from frozen specifications."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.materials.magsc_001_012_external_v1 import experiment_registration
from sft.materials.magsc_001_012_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import completeness_record, survivor_id

REGISTRY_ID = "sha256:870a795db025bba127c3b77e0c10b88c266c2ce497170ff670173a5ee06d5281"
VECTOR_ID = "sha256:7b6fb80b2b335d79a95ec7dafb34577ad0fd32967f09f0029ce0f0fef71d0e75"

def write(path, value):
    if path.exists():
        raise SystemExit("refusing to overwrite " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n")

def main():
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-MAGSC-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "materials",
            "subbranch": "magnetic_superconducting_superfluid",
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
            "pre_source_target_registry": "census/materials_magsc_001_012_target_registry_v1.json",
            "pre_source_target_registry_identity": REGISTRY_ID,
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_pending_untouched_engine_admission",
        })
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why MAGSC-{spec.number} requires a derivation check\n\n{spec.statement}\n\nThe 256-form grammar is generated before target release, independently reconstructed and compared against every registered authoritative record.\n")
        write(package / "execution.py", f"from pathlib import Path\nfrom sft.materials.magsc_001_012_execution_v1 import build_execution as assemble\ndef build_execution(root: Path):\n    return assemble(root, {claim_id!r}, Path(__file__).resolve())\n")
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json",
            "schema": "sft-v3-materials-magsc-experiment-registration/1",
            **experiment_registration(spec),
            "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence",
            "target_registry": "census/materials_magsc_001_012_target_registry_v1.json",
            "source_custody_manifest": "experiments/external_sources/materials/magsc_001_012_v1/source_custody_manifest.json",
            "complete_evidence_vector": "experiments/external_sources/materials/magsc_001_012_v1/complete_evidence_vector_v1.json",
            "complete_evidence_vector_identity": VECTOR_ID,
            "absence_boundary": {"display_glyph": "0", "native_proof_form": "structural absence held as labelled empty form", "numerical_zero_as_physical_quantity_admitted": False},
            "all_result_classes_required": True,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_sources_captured_post_registry_pending_engine",
        })
    print("scaffolded", len(ORDER), "MAGSC packages")

if __name__ == "__main__":
    main()

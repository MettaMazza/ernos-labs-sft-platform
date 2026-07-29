#!/usr/bin/env python3
"""Create all ten PHASE claim and experiment packages as one family."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.materials.phase_001_010_external_v1 import experiment_registration
from sft.materials.phase_001_010_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import completeness_record, survivor_id


REGISTRY_ID = "sha256:035944d4a817829334fad9a0c9c181ce8286301affbddda38b28fd08ed09357b"
VECTOR_ID = "sha256:a0f013b39e47a49d51168c148c002d3cf24e101f74f2881abd6792c91c4518c6"


def write(path, content):
    if path.exists():
        raise SystemExit("refusing to overwrite " + path.relative_to(ROOT).as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True) + "\n")


def main():
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-PHASE-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        write(package / "registration.json", {"$schema": "../../governance/claim.schema.json", "branch": "materials", "subbranch": "phase_equilibria_transformations_metastability", "claim_id": claim_id, "title": spec.title, "statement": spec.statement, "dependencies": list(spec.dependencies), "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"], "axioms": [], "free_parameters": [], "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)), "unique_survivor": survivor_id(spec)}, "excluded_inputs": list(spec.exclusions), "empirical_protocol": f"experiments/materials/{experiment_id}/registration.json", "provenance_classes": ["forward_forcing"], "pre_source_target_registry": "census/materials_phase_001_010_target_registry_v1.json", "pre_source_target_registry_identity": REGISTRY_ID, "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_pending_untouched_engine_admission"})
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n\nNo closure credit exists before an untouched-engine receipt.\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why PHASE-{spec.number} requires a derivation check\n\n{spec.statement}\n\nThe law is not selected by a named continuum equation, fitted phase diagram, database value, source fragment or favourable specimen. Its complete 256-form grammar is enumerated before target release, independently reconstructed and compared against every preregistered authoritative record.\n")
        write(package / "execution.py", f'''from pathlib import Path
from sft.materials.phase_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, {claim_id!r}, Path(__file__).resolve())
''')
        write(experiment / "registration.json", {"$schema": "../../../governance/experiment.schema.json", "schema": "sft-v3-materials-phase-experiment-registration/1", **experiment_registration(spec), "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence", "target_registry": "census/materials_phase_001_010_target_registry_v1.json", "source_custody_manifest": "experiments/external_sources/materials/phase_001_010_v1/source_custody_manifest.json", "complete_evidence_vector": "experiments/external_sources/materials/phase_001_010_v1/complete_evidence_vector_v1.json", "complete_evidence_vector_identity": VECTOR_ID, "custody_disclosure": "Topic-level source identities were frozen before source capture and fragment extraction; detailed records were opened only after value-free registration.", "absence_boundary": {"display_glyph": "0", "native_proof_form": "structural absence held as a labelled empty form", "numerical_zero_as_physical_quantity_admitted": False}, "all_favourable_adverse_absent_unavailable_unresolved_rows_required": True, "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_sources_captured_post_registry_pending_engine"})
    print(f"scaffolded {len(ORDER)} Materials PHASE claim and experiment packages")


if __name__ == "__main__":
    main()

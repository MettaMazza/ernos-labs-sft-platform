#!/usr/bin/env python3
"""Create all nine MICRO claim and experiment packages as one family."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.materials.micro_001_009_external_v1 import experiment_registration
from sft.materials.micro_001_009_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import candidate_rows, completeness_record, survivor_id


def write(path, content):
    if path.exists():
        raise SystemExit("refusing to overwrite " + path.relative_to(ROOT).as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True) + "\n")


def main():
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-MICRO-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        write(package / "registration.json", {"$schema": "../../governance/claim.schema.json", "branch": "materials", "subbranch": "defects_microstructure_interfaces_multiscale", "claim_id": claim_id, "title": spec.title, "statement": spec.statement, "dependencies": list(spec.dependencies), "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"], "axioms": [], "free_parameters": [], "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)), "unique_survivor": survivor_id(spec)}, "excluded_inputs": list(spec.exclusions), "empirical_protocol": f"experiments/materials/{experiment_id}/registration.json", "provenance_classes": ["forward_forcing"], "pre_source_target_registry": "census/materials_micro_001_009_target_registry_v1.json", "pre_source_target_registry_identity": "sha256:287bf62f3145a0701a67cf0a65a4718963ad2b6dea50403c02a48530a1e68da1", "source_identity_addendum": "census/materials_micro_coarsening_source_addendum_v1.json", "source_identity_addendum_hash": "sha256:a45bebaf851fde8b5f4fd9d066fad519e84c9c660fd4368780e0cc51d3199630", "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_pending_untouched_engine_admission"})
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n\nNo closure credit exists before an untouched-engine receipt.\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why MICRO-{spec.number} requires a derivation check\n\n{spec.statement}\n\nThe law is not selected by a named continuum equation, fitted micrograph, database value or favourable specimen. Its complete 256-form grammar is enumerated before target release, independently reconstructed, and compared with the complete retained NIST record. The inaccessible handbook endpoint, its failed route and the preregistered replacement source remain explicit evidence rows.\n")
        write(package / "execution.py", f'''from pathlib import Path
from sft.materials.micro_001_009_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, {claim_id!r}, Path(__file__).resolve())
''')
        write(experiment / "registration.json", {"$schema": "../../../governance/experiment.schema.json", "schema": "sft-v3-materials-micro-experiment-registration/1", **experiment_registration(spec), "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence", "target_registry": "census/materials_micro_001_009_target_registry_v1.json", "source_identity_addendum": "census/materials_micro_coarsening_source_addendum_v1.json", "source_custody_manifest": "experiments/external_sources/materials/micro_001_009_v2/source_custody_manifest.json", "complete_evidence_vector": "experiments/external_sources/materials/micro_001_009_v2/complete_evidence_vector_v1.json", "custody_disclosure": "Topic-level source summaries were known before capture; detailed records and outcomes were captured only after value-free registration.", "absence_boundary": {"display_glyph": "0", "native_proof_form": "structural absence held as a labelled empty form", "numerical_zero_as_physical_quantity_admitted": False}, "all_favourable_adverse_absent_unavailable_unresolved_rows_required": True, "registered_by": "Maria Smith", "registration_date": "2026-07-29", "status": "registered_sources_captured_post_registry_pending_engine"})
    print(f"scaffolded {len(ORDER)} Materials MICRO claim and experiment packages")


if __name__ == "__main__":
    main()

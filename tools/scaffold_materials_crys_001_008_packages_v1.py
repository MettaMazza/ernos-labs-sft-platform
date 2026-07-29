#!/usr/bin/env python3
"""Create all eight registered CRYS claim and experiment packages in one batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.materials.crys_001_008_external_v1 import experiment_registration
from sft.materials.crys_001_008_laws_v1 import ORDER, SPECS
from sft.physics.structural_constants import candidate_rows, completeness_record, survivor_id


def write(path: Path, content: object) -> None:
    if path.exists():
        raise SystemExit("refusing to overwrite " + path.relative_to(ROOT).as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content)
    else:
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")


def main() -> None:
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        package = ROOT / "claims" / claim_id
        experiment_id = f"SFT-EXP-MAT-CRYS-{spec.number}-V1"
        experiment = ROOT / "experiments/materials" / experiment_id
        rows = candidate_rows(spec)
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "materials",
            "subbranch": "quantitative_crystallography_diffraction_disorder",
            "claim_id": claim_id,
            "title": spec.title,
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
            "axioms": [],
            "free_parameters": [],
            "candidate_grammar": {
                "boundary": spec.grammar_boundary,
                "generator": spec.generation_rule,
                "expected_cardinality": len(rows),
                "completeness_certificate": sha256_identity(completeness_record(spec)),
                "unique_survivor": survivor_id(spec),
            },
            "excluded_inputs": list(spec.exclusions),
            "empirical_protocol": f"experiments/materials/{experiment_id}/registration.json",
            "provenance_classes": ["forward_forcing"],
            "pre_source_target_registry": "census/materials_crys_001_008_target_registry_v1.json",
            "pre_source_target_registry_identity": "sha256:e0acb17fb7a8974f8fcb2cddc77ea2b1639cf442de36142b8b1116d6495b533a",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_pending_untouched_engine_admission",
        })
        write(package / "STATUS.md", f"# {claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n\nNo scientific closure credit exists until an untouched-engine receipt admits this claim.\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why CRYS-{spec.number} requires a derivation check\n\n{spec.statement}\n\nA conventional formula, fitted diffraction pattern, database label or selected specimen cannot establish this Fold law. The derivation generates every one of its 256 registered candidate forms, eliminates 255 distinction-losing alternatives, reconstructs the survivor through a separate implementation, seals the result before target release and then compares it with the complete retained official record. Two unavailable IUCr dictionary endpoints remain adverse custody rows; they are not silently omitted and are not required to manufacture a favourable result. A failed capture route retired no scientific obligation.\n")
        write(package / "execution.py", f'''from pathlib import Path
from sft.materials.crys_001_008_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, {claim_id!r}, Path(__file__).resolve())
''')
        registration = experiment_registration(spec)
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json",
            "schema": "sft-v3-materials-crys-experiment-registration/1",
            **registration,
            "evidence_mode": "complete_enumeration_independent_reconstruction_post_registry_external_correspondence",
            "target_registry": "census/materials_crys_001_008_target_registry_v1.json",
            "source_custody_manifest": "experiments/external_sources/materials/crys_001_008_v3/source_custody_manifest.json",
            "complete_evidence_vector": "experiments/external_sources/materials/crys_001_008_v3/complete_evidence_vector_v1.json",
            "custody_disclosure": "General source identities were known before registry; detailed records and outcomes were captured only after the value-free registry seal.",
            "absence_boundary": {
                "display_glyph": "0",
                "native_proof_form": "structural absence held as a labelled empty form",
                "numerical_zero_as_physical_quantity_admitted": False,
            },
            "all_favourable_adverse_absent_unavailable_unresolved_rows_required": True,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-29",
            "status": "registered_sources_captured_post_registry_pending_engine",
        })
    print(f"scaffolded {len(ORDER)} Materials CRYS claim and experiment packages")


if __name__ == "__main__":
    main()

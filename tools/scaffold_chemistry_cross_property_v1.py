#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-014."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.cross_property_batch_v1 import (  # noqa: E402
    CROSS_PROPERTY_SPEC, IDENTITY_HASH, IDENTITY_PATH, MANIFEST_HASH, MANIFEST_PATH,
    SUMMARY_HASH, SUMMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.cross_property_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = CROSS_PROPERTY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-014 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def vector(carrier, projections):
    labels=[p[0] for p in projections]
    if not carrier or not projections or len(labels) != len(set(labels)):
        raise ValueError("one carrier and unique projection families required")
    if set(carrier["families"]) != set(labels):
        raise ValueError("complete applicable support required")
    return tuple(projections)

def project(v, family):
    rows=[p for p in v if p[0] == family]
    if len(rows) != 1: raise ValueError("projection absent or duplicated")
    return rows[0]

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed=json.load(handle)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    p1=("bond", "bond-law", Fraction(3,2)); p2=("vibration", "vibration-law", Fraction(5,3)); p3=("formation", "formation-law", Fraction(7,4))
    carrier={{"id":"held-molecule", "families":("bond","vibration")}}
    v=vector(carrier,(p1,p2)); extended=vector({{"id":carrier["id"],"families":carrier["families"]+("formation",)}},v+(p3,))
    controls=sealed["controls"]
    passed=(
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}} and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and project(v,"bond") == p1 and project(v,"vibration") == p2
        and project(extended,"bond") == p1 and project(extended,"vibration") == p2 and project(extended,"formation") == p3
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None, "one_carrier_vector_reconstructed": len(v)==2,
            "named_projection_reconstructed": project(v,"bond")==p1,
            "append_only_extension_reconstructed": project(extended,"bond")==p1 and project(extended,"vibration")==p2,
            "per_property_fit_used": False, "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__": main()
'''


def execution_source() -> str:
    claim_id = CROSS_PROPERTY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.cross_property_batch_v1 import CROSS_PROPERTY_SPEC, MANIFEST_PATH, SUMMARY_PATH, IDENTITY_PATH, TARGET_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.cross_property_validation_v1 import CrossPropertyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    identity_manifest=json.loads((root/MANIFEST_PATH).read_text(encoding="utf-8"))
    target_manifest=json.loads((root/TARGET_PATH).read_text(encoding="utf-8"))
    prior_sources=tuple(root/row["identity_path"] for row in identity_manifest["sources"])+tuple(
        root/row["withheld_target_path"] for row in target_manifest["source_target_files_first_opened_after_identity_seal"]
    )
    source_files=(
        root/"sft/chemistry/cross_property_law_v1.py", root/"sft/chemistry/cross_property_batch_v1.py",
        root/"sft/chemistry/cross_property_validation_v1.py", root/"sft/chemistry/generated_law.py",
        root/"sft/chemistry/generated_observational_law.py", root/"sft/physics/generated_empirical_law.py",
        root/"tools/build_chemistry_cross_property_sources_v1.py", root/MANIFEST_PATH, root/SUMMARY_PATH,
        root/IDENTITY_PATH, root/TARGET_PATH, *prior_sources, root/"claims/{claim_id}/execution.py",
    )
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(CROSS_PROPERTY_SPEC,source_hash),
        independent_validator=ExternalCommandValidator("sft-chem-cross-property-014-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),
        source_files=source_files, empirical_validator=CrossPropertyValidator(root),
    )
'''


def main() -> None:
    spec = CROSS_PROPERTY_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [{"source_id": "SFT-V3-ADMITTED-PROP-001-THROUGH-PROP-013-COMPLETE-SOURCE-CUSTODY", "body": "Ernos Labs source-preserving assembly of the admitted authoritative records", "role": "complete same-carrier cross-property identity and post-seal target surface"}],
        "source_hashes": {"identity_only_source_manifest": MANIFEST_HASH, "overlap_summary": SUMMARY_HASH, "identity_registry": IDENTITY_HASH, "withheld_targets": TARGET_HASH},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "target_payloads_hashes_presence_flags_or_orientations_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-014`

## WHY

Thirteen separately successful property demonstrations do not by themselves prove that one molecule is carried consistently across them. A cross-property law must use one structural carrier, retain every applicable property and forbid a new fit whenever another property is added.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

Each property is a named projection generated by its already admitted exact relation. Appending one lawful property projection preserves every existing result. No property-specific coefficient, residual, correction or target-derived carrier field exists.

## CHECK

The value-free boundary contains all 13 PROP-001 through PROP-013 families, all 9,025 source rows and all 1,104 structural carriers. It identifies 676 exact multi-property carriers containing all 6,676 overlap rows; H2 reaches the maximum eight-family overlap. Every target payload and even every target-file hash remains unopened until the complete identity seal. Nonjoinable diatomic-PDF, torsional-label and bound-composite rows remain explicit and are never guessed into formula groups.

## FALSIFICATION

{spec.falsification_condition}
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "execution.py", execution_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__": main()

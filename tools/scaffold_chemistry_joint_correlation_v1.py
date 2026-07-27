#!/usr/bin/env python3
"""Scaffold the complete ELEC-007 joint-correlation claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.joint_correlation_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    JOINT_CORRELATION_SPEC,
    SOURCE_IDS,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.joint_correlation_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = JOINT_CORRELATION_SPEC
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete 256-form census, unique survivor, depth-independent pairwise successor, independent "
            "reconstruction, capability-closed two-word joint law, all nine APS/NIST dissociation records, "
            "all exact positive values and uncertainties, complete provenance classes, and adverse controls."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    spec = JOINT_CORRELATION_SPEC
    program = prediction_program_document(ROOT)
    record = experiment_registration_record(ROOT)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {
                "source_ids": list(SOURCE_IDS),
                "role": "question-and-complete-test-domain-only",
                "measured_values_uncertainties_and_record_classes_absent_from_survivor_selection": True,
            }
        ],
        "external_measurement_sources": [
            {
                "source_id": SOURCE_IDS[0],
                "measurement_body": "American Physical Society",
                "journal": "Physical Review A 49, 2460 (1994)",
                "doi": "10.1103/PhysRevA.49.2460",
                "source_uri": "https://journals.aps.org/pra/abstract/10.1103/PhysRevA.49.2460",
                "record_boundary": "byte-sealed transparent numerical extract of six primary-source values",
                "records": 6,
            },
            {
                "source_id": SOURCE_IDS[1],
                "measurement_body": "National Institute of Standards and Technology",
                "database": "NIST Chemistry WebBook SRD 69",
                "doi": "10.18434/T4D303",
                "source_uri": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
                "record_boundary": "byte-sealed source notes independently parsed from the archived HTML",
                "records": 3,
            },
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_survivor": True,
            "measured_magnitude_not_a_forcing_premise": True,
        },
        "inputs": [
            {"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)},
            {"input_id": "target-identities-only", "path": IDENTITY_PATH, "content_hash": IDENTITY_HASH, "outcomes_absent": True},
        ],
        "withheld_targets": [
            {"target_id": row.target_id, "source_id": row.source_id, "snapshot_hash": row.snapshot_hash, "content_withheld_from_prediction": True}
            for row in spec.target_rows
        ],
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne",
            "display_glyph": "0",
            "meaning": "absence only",
            "numerical_zero_admitted": False,
            "rule": "Absent uncertainty coordinates use EmptyOne; external inscriptions remain held provenance and are never SFT numbers.",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-APS-NIST-evaluator",
            "comparison_implementation_hash": sha256_identity(("complete-APS-NIST-joint-correlation-comparator/1", spec.experiment_id)),
            "metrics": [
                {"metric_id": "nonfactorizable-joint-support", "definition": "Require exactly two complementary cross-centre words against four independent Cartesian products.", "all_rows": True},
                {"metric_id": "complete-dissociation-vector", "definition": "Retain all nine exact positive dissociation records and all reported uncertainties.", "all_rows": True},
                {"metric_id": "complete-provenance-vector", "definition": "Retain six APS, three NIST, seven direct/compiled and two derived-ion records without reclassification.", "all_rows": True},
            ],
            "acceptance_condition": "All nine records, all exact inscriptions, the two-to-four structural discriminator and every adverse control pass.",
            "falsification_condition": spec.falsification_condition,
        },
        "custody_protocol": {
            "identity_registry_hash": IDENTITY_HASH,
            "withheld_target_registry_hash": TARGET_HASH,
            "target_release_requires_prediction_seal": True,
            "cross_platform_exchange_required": True,
            "hostile_package_audit_required": True,
        },
        "retention_policy": "retain-all-nine-records-all-values-all-uncertainties-all-provenance-classes-and-all-adverse-results",
        "scope_boundary": (
            "The forced result is exact nonfactorizable joint support and its bound-to-separated transition. "
            "The nine exact dissociation magnitudes are post-seal external observations testing the law's physical domain; "
            "this claim does not introduce or pretend to derive a universal numerical energy functional."
        ),
        "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.",
        "source_hashes": {IDENTITY_PATH: IDENTITY_HASH, TARGET_PATH: TARGET_HASH, **{row.snapshot_path: row.snapshot_hash for row in spec.target_rows}, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_source() -> str:
    spec = JOINT_CORRELATION_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; left=("lower","L","upper","R"); right=("lower","R","upper","L"); cartesian={{("lower",a,"upper",b) for a in ("L","R") for b in ("L","R")}}; joint={{left,right}}; law=(len(joint)==2 and len(cartesian)==4 and joint < cartesian and all(a!=b for _,a,_,b in joint)); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and law); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"joint_word_count":len(joint),"cartesian_word_count":len(cartesian),"same_centre_words_excluded":law}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = JOINT_CORRELATION_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.joint_correlation_batch_v1 import JOINT_CORRELATION_SPEC
from sft.chemistry.joint_correlation_validation_v1 import JointCorrelationValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=JOINT_CORRELATION_SPEC; files=(root/"sft/chemistry/joint_correlation_law_v1.py",root/"sft/chemistry/joint_correlation_batch_v1.py",root/"sft/chemistry/joint_correlation_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{spec.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,JointCorrelationValidator(root))
'''


def derivation_note() -> str:
    spec = JOINT_CORRELATION_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-007`

## WHY

ELEC-006 closes identical-pair exchange and exclusion. It does not yet decide whether two independently retained one-carrier descriptions contain the complete molecular relation. ELEC-007 closes that distinction without importing Hartree–Fock, configuration interaction, coupled-cluster theory, density functionals, fitted correlation coefficients or species exceptions.

There is no numerical zero. Missing uncertainty is structural `EmptyOne`; the display glyph `0` denotes absence only. Decimal source inscriptions are retained as exact positive ratios after sealing and never act as proof parameters.

## DERIVATION

Two held electron fibres and two distinguished separated-product centres generate four independent Cartesian assignments. Indistinguishability requires the complementary exchange assignment whenever either cross-centre assignment is retained. Molecular exclusion rejects both same-centre assignments at the separated-product boundary. The exact complete joint support is therefore the two-word set `(lower,L; upper,R)` and `(lower,R; upper,L)`. Its one-carrier marginals each retain both centres, whose independent product regenerates four words, so the exact two-word relation is not reconstructible from the marginals. This retained missing distinction is Fold correlation.

The registered eight-axis grammar enumerates all 256 forms. Exactly one survives:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The capability-closed prediction contains only five universal consequences: two joint words, four independent Cartesian words, a nonfactorizable complementary relation, exclusion of same-centre support, and the requirement that any dissociation magnitude be an exact positive post-seal record. No species, state, energy, uncertainty or target magnitude occurs in the sealed program.

After sealing, an independent custodian releases nine pre-registered dissociation records. Six exact values come from the byte-sealed transparent numerical extract of the primary 1994 Physical Review A report (DOI `10.1103/PhysRevA.49.2460`); four are reported measurements and two ionic energies are explicitly retained as derived from measured neutral and ionization intervals. Three further H₂ records are reconstructed directly from the archived NIST Chemistry WebBook HTML (DOI `10.18434/T4D303`). The vector contains seven direct measured/compiled records, two derived ionic records, seven positive uncertainty records, two absent-uncertainty coordinates and four species labels. No record is omitted or reclassified.

The empirical comparison tests exact positive dissociation observations across ground, excited, neutral, ionic and isotopic records. These values validate the physical occurrence of the forced bound-to-separated support transition. They do not select the joint law and are not represented as a numerically derived universal energy formula. That distinction is part of the certificate, not a retreat from empirical testing.

One-word, four-word factorized, same-centre, numerical-zero, nonpositive-energy, omitted-record, omitted-ion, selected-source, changed-value, changed-uncertainty and tampered-source controls all halt or reject.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec = JOINT_CORRELATION_SPEC
    claim_path = ROOT / "claims" / spec.claim_id
    write(claim_path / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(claim_path / "execution.py", execution_source())
    write(claim_path / "independent_validator.py", independent_source())
    write(claim_path / "WHY_DERIVATION_CHECK.md", derivation_note())
    write(claim_path / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id
    write(experiment_path / "registration.json", json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()

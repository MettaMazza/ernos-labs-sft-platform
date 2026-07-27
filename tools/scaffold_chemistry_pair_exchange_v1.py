#!/usr/bin/env python3
"""Scaffold the full ELEC-006 molecular pair-exchange claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.pair_exchange_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    PAIR_EXCHANGE_SPEC,
    SOURCE_ID,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.pair_exchange_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = PAIR_EXCHANGE_SPEC
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
            "Complete 256-form structural census, unique survivor, pairwise depth-independent successor, "
            "implementation-distinct reconstruction, capability-closed exchange law, all 46 NIST H2 states, "
            "both explicit same-cell pairs, all 14 same-configuration singlet/triplet records, every exact "
            "positive separation and all adverse or opposite-order observations."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    spec = PAIR_EXCHANGE_SPEC
    program = prediction_program_document(ROOT)
    record = experiment_registration_record(ROOT)
    snapshot_hashes = {row.snapshot_path: row.snapshot_hash for row in spec.target_rows}
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {
                "source_id": SOURCE_ID,
                "role": "question-and-complete-test-domain-only",
                "term_multiplicity_occupancy_order_and_separation_absent_from_survivor_selection": True,
            }
        ],
        "external_measurement_sources": [
            {
                "source_id": SOURCE_ID,
                "measurement_body": "National Institute of Standards and Technology",
                "database": "NIST Chemistry WebBook SRD 69",
                "doi": "10.18434/T4D303",
                "source_uri": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
                "species": "molecular hydrogen H2",
                "complete_state_rows": 46,
                "same_configuration_exchange_pairs": 14,
                "custody_role": "post-seal-spin-state-occupancy-and-exchange-sensitive-target",
            }
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_survivor": True,
            "energy_order_not_part_of_forcing_relation": True,
        },
        "inputs": [
            {
                "input_id": "registered-premise",
                "value_kind": "held-sealed-derivation",
                "content_hash": sha256_identity(spec.dependencies),
            },
            {
                "input_id": "target-identities-only",
                "path": IDENTITY_PATH,
                "content_hash": IDENTITY_HASH,
                "state_and_pair_outcomes_absent": True,
            },
        ],
        "withheld_targets": [
            {
                "target_id": row.target_id,
                "source_id": row.source_id,
                "snapshot_hash": row.snapshot_hash,
                "content_withheld_from_prediction": True,
            }
            for row in spec.target_rows
        ],
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne",
            "display_glyph": "0",
            "meaning": "absence only",
            "numerical_zero_admitted": False,
            "source_ground_baseline_glyph_count": 1,
            "rule": "The NIST ground baseline glyph 0 remains a held source inscription and is interpreted only as absence of excitation, never as an SFT number.",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": [
                "clock",
                "dynamic_import",
                "environment",
                "filesystem_read",
                "filesystem_write",
                "foreign_function",
                "network",
                "subprocess",
            ],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-NIST-evaluator",
            "comparison_implementation_hash": sha256_identity(
                ("complete-NIST-H2-pair-exchange-comparator/1", spec.experiment_id)
            ),
            "metrics": [
                {
                    "metric_id": "complete-two-electron-state-census",
                    "definition": "Retain and test all 46 NIST H2 term assignments: 25 One-width and 21 three-width states.",
                    "all_rows": True,
                },
                {
                    "metric_id": "same-cell-exclusion",
                    "definition": "Retain every explicit orbital-occupancy record and require both paired-cell inscriptions to occur in the One-width preserving-spatial sector.",
                    "all_rows": True,
                },
                {
                    "metric_id": "same-support-exchange-distinction",
                    "definition": "Retain all 14 same-configuration complementary exchange pairs with exact positive measured separations and both observed order fibres.",
                    "all_rows": True,
                },
            ],
            "acceptance_condition": (
                "All 46 states, 25 One-width sectors, 21 three-width sectors, two explicit same-cell singlets, "
                "14 same-configuration pairs, 13 triplet-below-singlet records, the one singlet-below-triplet "
                "record, every positive exact separation and every adverse control pass."
            ),
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {
                "control_id": "FALSE-PREMISE",
                "kind": "false_premise",
                "expected_rejection": "A freely preserving total electron-pair word rejects.",
            },
            {
                "control_id": "TAMPERED-SOURCE",
                "kind": "tampered_source",
                "expected_rejection": "Changed NIST snapshot bytes reject.",
            },
            {
                "control_id": "TAMPERED-ARTIFACT",
                "kind": "tampered_artifact",
                "expected_rejection": "An omitted state, pair or changed separation rejects.",
            },
            {
                "control_id": "BOUNDARY",
                "kind": "boundary",
                "expected_rejection": "A target-readable law, imported exchange sign/integral, numerical zero or fitted split rejects.",
            },
            {
                "control_id": "WRONG-MULTIPLICITY",
                "kind": "unfavorable_measurement",
                "expected_rejection": "A two-electron multiplicity outside the complete One/three census rejects.",
            },
            {
                "control_id": "SAME-CELL-TRIPLET",
                "kind": "unfavorable_measurement",
                "expected_rejection": "A paired orbital in the alternating spatial sector rejects.",
            },
            {
                "control_id": "THIRD-OCCURRENCE",
                "kind": "unfavorable_measurement",
                "expected_rejection": "A third identical electron in one orbital support rejects.",
            },
            {
                "control_id": "OPPOSITE-ORDER-RETENTION",
                "kind": "unfavorable_measurement",
                "expected_rejection": "Deleting the observed singlet-below-triplet pair to simulate a universal order sign rejects.",
            },
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-NIST-target-custodian",
            "custodian_distinct_from_executor": True,
            "withheld_target_registry_path": TARGET_PATH,
            "withheld_target_registry_hash": TARGET_HASH,
            "release_requires_matching_prediction_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-all-46-states-all-14-pairs-all-order-fibres-and-all-adverse-results",
        "scope_boundary": (
            "The forced result is complementary pair-exchange organization and exclusion. Exact NIST energy "
            "separations test exchange-sensitive distinction after sealing; neither their sign nor magnitude is "
            "promoted to a universal imported exchange-integral law."
        ),
        "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.",
        "source_hashes": snapshot_hashes
        | {
            IDENTITY_PATH: IDENTITY_HASH,
            TARGET_PATH: TARGET_HASH,
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_source() -> str:
    spec = PAIR_EXCHANGE_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
PRODUCT={{("preserving","preserving"):"preserving",("preserving","alternating"):"alternating",("alternating","preserving"):"alternating",("alternating","alternating"):"preserving"}}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; law=(PRODUCT[("alternating","preserving")]=="alternating" and PRODUCT[("preserving","alternating")]=="alternating" and PRODUCT[("preserving","preserving")]=="preserving" and 1+3==4); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and law); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"exchange_product":sorted((a,b,c) for (a,b),c in PRODUCT.items())}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = PAIR_EXCHANGE_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.pair_exchange_batch_v1 import PAIR_EXCHANGE_SPEC
from sft.chemistry.pair_exchange_validation_v1 import PairExchangeValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=PAIR_EXCHANGE_SPEC; files=(root/"sft/chemistry/pair_exchange_law_v1.py",root/"sft/chemistry/pair_exchange_batch_v1.py",root/"sft/chemistry/pair_exchange_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{spec.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,PairExchangeValidator(root))
'''


def derivation_note() -> str:
    spec = PAIR_EXCHANGE_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-006`

## WHY

The prior Chemistry claims establish electron count and spin width, molecular orbital support, exact state order and complete symmetry signatures. They do not yet force how the spin and spatial parts of an identical molecular electron pair compose, or which sector may retain two electrons on one orbital support. ELEC-006 closes that dependency without importing an antisymmetrized wavefunction, signed permutation factor, exchange integral, Hund ordering or species exception.

There is no numerical zero. The NIST glyph `0` on the H₂ ground-state energy record denotes absence of excitation relative to the source baseline. It remains visible as a held provenance inscription but never enters a Fold count, ratio or state coordinate.

## DERIVATION

The admitted physical indistinguishability law removes named electron identity. The admitted exclusion law requires the total identical-electron word to alternate. The complete two-label spin census already contains four words: one alternating and three preserving. The complete two-fibre product has only four compositions. A total alternating word survives only when spin and spatial fibres are complementary:

- positive One-width spin support: alternating spin, preserving spatial support;
- positive three-width spin support: preserving spin, alternating spatial support.

Preserving spatial support can retain the paired same-cell word. Alternating spatial support cannot: a duplicate support would erase the only remaining distinction. A third identical occurrence has no generated support and halts. This is a held-label composition law; no negative sign, numerical zero, irrational, imaginary or continuum scalar is required.

The registered eight-axis grammar enumerates all 256 carrier, identity, total, spin, composition, same-cell, record and extension forms. Exactly one survives:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The capability-closed predictor seals only the universal two-fibre product, the positive One/three spin sectors, their complementary spatial fibres, alternating total exchange, same-cell consequence and the rule that energy order remains an observation rather than a universal sign. No term, state, occupancy, energy or target value is present in the prediction program.

After sealing, a distinct custodian releases the complete byte-bound NIST H₂ surface. An independently implemented parser reconstructs all 46 electronic-state rows: 25 positive One-width states and 21 positive three-width states. Both explicit paired-orbital inscriptions—`1sσ²` and `2pσ²`—occur in the One-width, preserving-spatial sector; none occurs in the three-width alternating-spatial sector.

The same source also supplies fourteen pairs that retain one orbital configuration while changing the exchange-complementary spin/spatial sector. Every state identity and exact positive energy separation is retained. Thirteen observed pairs place the triplet inscription below the singlet inscription; one places the singlet below the triplet. The opposite-order row is mandatory evidence: it prevents a familiar ordering heuristic from being silently imported as the Fold law. ELEC-006 forces exchange organization and same-cell exclusion; measured order and separation remain post-seal observations.

Wrong multiplicity, preserving total exchange, same-cell triplet, third occurrence, numerical use of the source absence glyph, omitted row, omitted pair, selected favourable ordering, changed separation and changed snapshot controls all reject.

External authority: NIST Chemistry WebBook SRD 69, DOI `10.18434/T4D303`.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec = PAIR_EXCHANGE_SPEC
    claim_path = ROOT / "claims" / spec.claim_id
    write(claim_path / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(claim_path / "execution.py", execution_source())
    write(claim_path / "independent_validator.py", independent_source())
    write(claim_path / "WHY_DERIVATION_CHECK.md", derivation_note())
    write(claim_path / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id
    write(
        experiment_path / "registration.json",
        json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n",
    )
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()

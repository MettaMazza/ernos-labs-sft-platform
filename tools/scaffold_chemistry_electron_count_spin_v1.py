#!/usr/bin/env python3
"""Scaffold the Physics-scale ELEC-002 Chemistry claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.electron_count_spin_batch_v1 import (  # noqa: E402
    ELECTRON_COUNT_SPIN_SPEC,
    INPUT_REGISTRY_HASH,
    INPUT_REGISTRY_PATH,
    SOURCE_ID,
    TARGET_REGISTRY_HASH,
    TARGET_REGISTRY_PATH,
)
from sft.chemistry.electron_count_spin_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
    prediction_rows,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = ELECTRON_COUNT_SPIN_SPEC
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
            "Complete 256-form census; unique preserving law; depth-independent successor; independent product and "
            "electron-census reconstruction; capability-closed 22-row prediction vector; post-seal NIST neutral, "
            "cation and anion state comparison; five adverse controls; exact complete proof trace."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    spec = ELECTRON_COUNT_SPIN_SPEC
    record = experiment_registration_record(ROOT)
    program = prediction_program_document(ROOT)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {
                "source_id": SOURCE_ID,
                "role": "question-and-test-domain-observation-only",
                "content_absent_from_candidate_survivor_selection": True,
            }
        ],
        "external_measurement_sources": [
            {
                "source_id": SOURCE_ID,
                "measurement_body": "National Institute of Standards and Technology",
                "database": "NIST Chemistry WebBook, Standard Reference Database 69",
                "doi": "10.18434/T4D303",
                "source_uri": "https://webbook.nist.gov/chemistry/",
                "last_data_update": "March 2025",
                "retrieved_date": "2026-07-26",
                "snapshot_count": 22,
                "custody_role": "post-seal_ground-state-term-and-multiplicity_target",
            }
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(value) for value in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_survivor": True,
        },
        "inputs": [
            {
                "input_id": "registered-premise",
                "value_kind": "held-sealed-derivation",
                "content_hash": sha256_identity(spec.dependencies),
            },
            {
                "input_id": "molecular-nuclear-support-and-held-charge",
                "value_kind": "22-row-positive-finite-source-bound-input-registry",
                "path": INPUT_REGISTRY_PATH,
                "content_hash": INPUT_REGISTRY_HASH,
                "target_multiplicity_absent": True,
            },
        ],
        "withheld_targets": [
            {
                "target_id": row.target_id,
                "source_id": row.source_id,
                "source_locator": row.source_locator,
                "snapshot_hash": row.snapshot_hash,
                "content_withheld_from_capability_closed_prediction": True,
            }
            for row in spec.target_rows
        ],
        "dimension_unit_boundary": {
            "derived_carriers": [
                "positive atomic-number occurrence counts",
                "structural empty-One neutral transfer",
                "positive held adjoin/remove transfer counts",
                "positive electron occurrence counts",
                "two held spin fibres",
                "positive spin widths",
            ],
            "external_records": "NIST formula, X-state term and measured multiplicity remain source-bound observations and never become proof scalars or candidate selectors.",
            "proof_value_policy": "positive-generated-counts-held-labels-and-structural-empty-One-only",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "predicted_rows": len(prediction_rows(ROOT)),
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-NIST-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-electron-count-spin-parity-NIST-state-comparison/1", spec.experiment_id)),
            "metrics": [
                {
                    "metric_id": "complete-electron-count-vector",
                    "definition": "Reconstruct exact electron count from every NIST molecular formula and held charge direction, retaining all 22 rows.",
                    "unit_protocol": "dimensionless positive electron occurrence count",
                    "all_rows": True,
                },
                {
                    "metric_id": "complete-held-spin-width-compatibility-vector",
                    "definition": "Compare the sealed forced width parity with every NIST X-state multiplicity and reconstruct its exact pair-plus-held organization.",
                    "unit_protocol": "positive state multiplicity and held fibre organization",
                    "all_rows": True,
                },
            ],
            "acceptance_condition": "All 22 neutral/cation/anion rows pass exact count and width-parity reconstruction and every adverse control rejects.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Missing nuclear support or an electron-removal action erasing all positive support rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed NIST source byte or target registry identity rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed, duplicate or omitted candidate or empirical row rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Signed charge, numerical-zero proof value, measured target access or species exception rejects."},
            {"control_id": "TAMPERED-CHARGE", "kind": "unfavorable_measurement", "expected_rejection": "Changing a neutral held action to electron removal changes the predicted census and rejects."},
            {"control_id": "TAMPERED-MULTIPLICITY", "kind": "unfavorable_measurement", "expected_rejection": "A state width with the wrong parity cannot decompose complete electron support and rejects."},
            {"control_id": "OMITTED-ROW", "kind": "unfavorable_measurement", "expected_rejection": "A 21-row result cannot satisfy the registered 22-row target support."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-NIST-target-custodian",
            "custodian_distinct_from_executor": True,
            "withheld_target_registry_path": TARGET_REGISTRY_PATH,
            "withheld_target_registry_hash": TARGET_REGISTRY_HASH,
            "release_requires_matching_prediction_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-all-22-favorable-unfavorable-failed-and-tampered-rows",
        "stop_condition": "Halt on the first protocol violation; otherwise stop only after all 22 rows and every adverse control are recorded.",
        "source_hashes": {
            INPUT_REGISTRY_PATH: INPUT_REGISTRY_HASH,
            TARGET_REGISTRY_PATH: TARGET_REGISTRY_HASH,
            **{row.snapshot_path: row.snapshot_hash for row in spec.target_rows},
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_validator_source() -> str:
    spec = ELECTRON_COUNT_SPIN_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    input_document = json.loads((ROOT / INPUT_REGISTRY_PATH).read_text(encoding="utf-8"))
    expected_by_id = {str(row["row_id"]): row for row in prediction_rows(ROOT)}
    rows = tuple(
        (
            str(row["row_id"]),
            tuple(
                (int(item["atomic_number"]), int(item["occurrence_count"]))
                for item in row["nuclear_composition"]
            ),
            str(row["charge_action"]),
            row.get("charge_count"),
            int(expected_by_id[str(row["row_id"])]["electron_count"]),
            str(expected_by_id[str(row["row_id"])]["required_spin_width_parity"]),
        )
        for row in input_document["rows"]
    )
    return f'''"""Independent reconstruction for {spec.claim_id}."""
from itertools import product
import json
import sys
CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}
REGISTERED_INPUTS_AND_PREDICTIONS = {rows!r}
def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    rebuilt = []
    for row_id, populations, action, transfer_count, expected_count, expected_parity in REGISTERED_INPUTS_AND_PREDICTIONS:
        electron_count = sum(atomic_number * occurrence_count for atomic_number, occurrence_count in populations)
        valid_action = True
        if action == "adjoin-electron":
            electron_count += transfer_count
        elif action == "remove-electron":
            electron_count -= transfer_count
        elif action != "empty-One" or transfer_count is not None:
            valid_action = False
        parity = "odd-positive-width" if electron_count % 2 == 0 else "even-positive-width"
        rebuilt.append((row_id, electron_count, parity, valid_action and electron_count == expected_count, parity == expected_parity))
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == 256
        and len(set(received)) == 256
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(rebuilt) == 22
        and all(row[3] and row[4] for row in rebuilt)
        and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID,
            "candidate_count": len(generated),
            "survivor": SURVIVOR if passed else None,
            "independently_reconstructed_prediction_rows": rebuilt,
        }},
    }}, sort_keys=True))
if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    spec = ELECTRON_COUNT_SPIN_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.electron_count_spin_batch_v1 import ELECTRON_COUNT_SPIN_SPEC
from sft.chemistry.electron_count_spin_validation_v1 import ElectronCountSpinValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = ELECTRON_COUNT_SPIN_SPEC
    source_files = (
        root / "sft/chemistry/electronic_structure_derivation.py",
        root / "sft/chemistry/electron_count_spin_law_v1.py",
        root / "sft/chemistry/electron_count_spin_batch_v1.py",
        root / "sft/chemistry/electron_count_spin_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            "{spec.claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ElectronCountSpinValidator(root),
    )
'''


def scientific_note() -> str:
    spec = ELECTRON_COUNT_SPIN_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-002`

## WHY

Electron number and spin multiplicity are not labels that may be appended to a
molecule after the fact.  A chemical electronic state is reproducible only if
its full positive electron support is generated from the molecular nuclei and
held charge action, and only if every occurrence remains organized under the
already admitted two-fibre spin, indistinguishability and exclusion laws.

This claim does not import a signed charge number.  Neutrality is structural
empty One.  Ionization is a held direction—remove or adjoin—with a positive
occurrence count.  It does not import an orbital table, a Hamiltonian, a
wavefunction, a measured state term, or a species-specific exception.

## DERIVATION

For nuclear populations `(Z_i, n_i)`, complete neutral electron support is the
positive occurrence census `sum_i Z_i n_i`.  A held remove action removes its
positive named count only while positive support remains; a held adjoin action
adjoins its positive named count.  No signed proof quantity is formed.

Every electron occurrence receives exactly one of the two forced spin fibre
labels.  Exclusion removes same-fibre same-cell doubling.  Therefore every
finite support at a declared spin width decomposes into complementary pairs
and unmatched held fibres:

`electron support = two occurrences per complementary pair + unmatched held fibres`

`spin width = unmatched held fibres followed by successor One`

Consequently electron-count parity forces the opposite spin-width parity.  An
even electron support admits only an odd positive width; an odd electron
support admits only an even positive width.  The theorem is a compatibility
and organization law.  It does not yet claim that molecular formula alone
selects the exact ground-state width; state ordering is the next dependent
electronic-structure work.

The literal eight-axis product contains 256 forms. Exactly one preserves
nuclear support, held charge, occurrence census, the two spin fibres,
exclusion-complete occupation, pair-plus-held decomposition, observable width
and the no-extra-rule boundary:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The empirical vector contains 22 complete NIST Chemistry WebBook diatomic
records: 16 neutral molecules, four cations and two anions.  The prediction
side sees molecular nuclear composition and held charge action, then seals all
22 exact electron counts and forced width parities in a capability-closed Fold
table.  It has no filesystem, network, environment, clock, dynamic import,
foreign-function or target operation.  Only after that seal does the custody
boundary release each NIST X-state term and measured multiplicity.

The evaluator checks every exact count, every multiplicity parity, and an exact
complete pair-plus-held organization for each measured state.  It preserves
the source hash, formula, state term, electron count, multiplicity, pair count,
unmatched count and outcome.  Deliberately changed charge, multiplicity,
snapshot identity and row support are required to reject.

The external source is NIST Chemistry WebBook SRD 69, DOI `10.18434/T4D303`,
last updated March 2025.  Source values remain observational records rather
than derivational scalars.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec = ELECTRON_COUNT_SPIN_SPEC
    package = ROOT / "claims" / spec.claim_id
    write(package / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", scientific_note())
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment = ROOT / "experiments/chemistry" / spec.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n")
    print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()

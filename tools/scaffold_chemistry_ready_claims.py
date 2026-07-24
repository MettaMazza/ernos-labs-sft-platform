"""Materialize registered packages for Chemistry specifications that are ready."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.catalog import CHEMISTRY_SPECS, SOURCES  # noqa: E402
from sft.chemistry.generated_law import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source_record(source_id: str) -> dict[str, object]:
    """Resolve old catalog sources and later append-only Chemistry authorities."""

    if source_id in SOURCES:
        return SOURCES[source_id]
    registry = json.loads(
        (ROOT / "experiments/external_sources/chemistry/authoritative_sources.json").read_text(
            encoding="utf-8"
        )
    )
    matches = [row for row in registry.get("sources", ()) if row.get("source_id") == source_id]
    if len(matches) != 1:
        raise ValueError(f"Chemistry source identity is not uniquely registered: {source_id}")
    return matches[0]


def claim_registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete content-specific 256-form census, sole survivor, independent regeneration and "
            "post-seal source-derived IUPAC correspondence."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration_record(spec)
    program = prediction_program_document(spec)
    external_sources = []
    seen_sources = set()
    for target in spec.target_rows:
        if target.source_id in seen_sources:
            continue
        seen_sources.add(target.source_id)
        source = source_record(target.source_id)
        external_sources.append(
            {
                "source_id": target.source_id,
                "measurement_body": source["body"],
                "source_uri": source["source_uri"],
                "snapshot_path": target.snapshot_path,
                "snapshot_hash": target.snapshot_hash,
                "retrieved_date": "2026-07-24",
                "custody_role": "withheld_source_derived_target",
            }
        )
    target_reference_hash = sha256_identity(
        tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in spec.target_rows
        )
    )
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "blind_authoritative_correspondence",
        "development_observations": [],
        "external_measurement_sources": external_sources,
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(dependency) for dependency in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [
            {
                "input_id": "registered-premise",
                "value_kind": "held-sealed-derivation",
                "content_hash": sha256_identity(spec.dependencies),
            }
        ],
        "withheld_targets": [
            {
                "target_id": row.target_id,
                "source_id": row.source_id,
                "source_locator": row.source_locator,
                "snapshot_hash": row.snapshot_hash,
                "content_absent_from_derivation_specification": True,
                "content_withheld_from_prediction": True,
            }
            for row in spec.target_rows
        ],
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
            "evaluator_id": spec.experiment_id + "-post-seal-source-evaluator",
            "comparison_implementation_hash": sha256_identity(
                ("source-fragment-extraction-and-exact-label-equality", spec.experiment_id)
            ),
            "metrics": [
                {
                    "metric_id": "source-derived-structural-correspondence",
                    "definition": (
                        "Reconstruct the registered ordered features from required fragments of each byte-sealed "
                        "official term, then compare the resulting held label with the sealed Fold prediction."
                    ),
                    "unit_protocol": "Categorical terminology correspondence; this is not a numerical measurement.",
                    "all_rows": True,
                }
            ],
            "acceptance_condition": "Every registered source-derived row matches and a deliberately changed row is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A form missing the first chemical preservation is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed official snapshot identity or missing required fragment is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed candidate support or prediction is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access or a forbidden proof value is rejected."},
            {"control_id": "UNFAVORABLE-CORRESPONDENCE", "kind": "unfavorable_measurement", "expected_rejection": "A changed source-derived feature label fails exact comparison."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_reference_hash": target_reference_hash,
            "observation_registry_path": spec.observation_registry_path,
            "observation_registry_hash": hash_file(ROOT / spec.observation_registry_path),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-favorable-unfavorable-failed-and-tampered-row",
        "stop_condition": "Halt after every target and control is evaluated once, or immediately on any violation.",
        "source_hashes": {
            row.snapshot_path: row.snapshot_hash for row in spec.target_rows
        }
        | {"experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.catalog import CHEMISTRY_SPECS
from sft.chemistry.generated_law import BlindExternalChemistryValidator, GeneratedEmpiricalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in CHEMISTRY_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/catalog.py",
        root / "sft/chemistry/obligations.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {spec.claim_id.lower()!r} + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExternalChemistryValidator(root, spec),
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Independent product validator for {spec.claim_id}."""
from itertools import product
import json
import sys
CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and
              sealed["census"]["expected_cardinality"] == len(generated) and
              len(set(received)) == len(generated) and
              decisions == {{row: row == SURVIVOR for row in generated}} and
              sum(decisions.values()) == 1 and
              sealed["closure"]["scope"] == "depth_independent" and
              sealed["closure"]["minimality_passed"] is True and
              sealed["closure"]["named_shape_uniqueness_passed"] is True and
              {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}} and
              all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True,
                      "passed": passed, "certificate": {{"claim_id": CLAIM_ID, "candidate_count": len(generated),
                      "survivor": SURVIVOR if passed else None}}}}, sort_keys=True))
if __name__ == "__main__": main()
'''


def note(spec) -> str:
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

The complete content-specific eight-axis product contains 256 generated forms.
Exactly one preserves every required coordinate and contains no extra identity
rule:

`{survivor_id(spec)}`

The admitted consequence is:

> {spec.exact_result}

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The prediction specification contains the public source and snapshot identities,
but no observed target label.  A distinct custodian reconstructs the ordered
feature label from required fragments of the byte-sealed official IUPAC term.
The capability-closed predictor emits its consequence before target release.
The post-seal evaluator retains every row and rejects a deliberately changed
feature label.

This is categorical authoritative correspondence, not a claim that a term
definition is a measured numerical constant.  It does not permit IUPAC wording
to select the Fold candidate grammar.
"""


def main() -> None:
    for spec in CHEMISTRY_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()

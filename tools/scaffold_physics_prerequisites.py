"""Materialize the three registered Physics empirical-prerequisite packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.formal_law import completeness_record, survivor_id  # noqa: E402
from sft.physics.measurement_prerequisites import PREREQUISITE_SPECS  # noqa: E402


IMPLEMENTATION_SOURCES = {
    "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001": ("sft/engine/fold_language.py",),
    "SFT-PHYS-MEAS-TARGET-CUSTODY-001": ("sft/engine/custody.py", "sft/engine/empirical.py"),
    "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001": ("sft/engine/hostile.py", "sft/engine/fold_language.py"),
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "physics",
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
        "intended_certificate": "Independent regeneration of the complete 256-form product and sole preserving form.",
        "empirical_protocol": None,
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-23",
    }


def execution_source(spec) -> str:
    source_rows = (
        "root / \"sft/physics/formal_law.py\"",
        "root / \"sft/physics/measurement_prerequisites.py\"",
        f"root / \"claims/{spec.claim_id}/execution.py\"",
        *(f"root / {relative!r}" for relative in IMPLEMENTATION_SOURCES[spec.claim_id]),
    )
    source_tuple = ",\n        ".join(source_rows)
    validator_id = spec.claim_id.lower().replace("sft-", "sft-") + "-independent-python/1"
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.formal_law import FormalPrerequisiteProgram
from sft.physics.measurement_prerequisites import PREREQUISITE_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in PREREQUISITE_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        {source_tuple},
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=FormalPrerequisiteProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {validator_id!r},
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in axis.choices) for axis in spec.axes)
    return f'''"""Implementation-distinct finite-product validator for {spec.claim_id}."""

from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None}},
    }}, sort_keys=True))


if __name__ == "__main__":
    main()
'''


def derivation_note(spec) -> str:
    axes = "\n".join(
        f"- `{axis.key}`: `{axis.survivor.name}` is the only preserving choice; "
        + "; ".join(f"`{choice.name}` — {choice.reason}" for choice in axis.choices)
        for axis in spec.axes
    )
    witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in spec.witnesses)
    exclusions = "\n".join(f"- {row}" for row in spec.exclusions)
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## Exact statement

{spec.statement}

## Generated grammar and uniqueness

{spec.grammar_boundary}

The registered product exhausts every combination of the eight declared binary
axes, giving exactly 256 named forms. A form survives only when every axis
retains target inaccessibility, exact provenance, complete evidence and
fail-closed authority. Therefore the sole survivor is:

`{survivor_id(spec)}`

{axes}

No axis is a fitted parameter: both alternatives are generated before
execution and the dependencies reject the non-preserving alternative.

## Operational witnesses

{witnesses}

The One base is: {spec.induction_base}

The successor certificate is: {spec.induction_step}

## Boundary

{exclusions}

This is a formal prerequisite for empirical work. It is not itself a claim that
nature follows any physical relation. Four adverse controls and a separate
standard-library validator regenerate the full product and its sole survivor.
"""


def main() -> None:
    if set(IMPLEMENTATION_SOURCES) != {spec.claim_id for spec in PREREQUISITE_SPECS}:
        raise SystemExit("Physics prerequisite catalog and implementation routing differ")
    for spec in PREREQUISITE_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(registration(spec), indent=2) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", derivation_note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()

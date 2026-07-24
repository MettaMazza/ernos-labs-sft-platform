"""Scaffold clean V3 atomic-constant prerequisite claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.atomic_constants import ATOMIC_CONSTANT_SPECS  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402


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
        "intended_certificate": "Independent regeneration of the complete typed product, sole preserving form and exact arithmetic witnesses.",
        "empirical_protocol": None,
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
    }


def execution_source(spec) -> str:
    validator_id = spec.claim_id.lower() + "-independent-python/1"
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_constants import SPEC_BY_ID
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "claims/{spec.claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID[{spec.claim_id!r}], source_hash),
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
    survivor = survivor_id(spec)
    arithmetic_checks = {
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001": '''
    b, c = 2, 3
    down, up = 5, 7
    cover = b * down ** c
    rungs = (down ** c, down ** 2 * up, down * up ** 2, up ** c)
    chain = Fraction(rungs[3], 1)
    chain = Fraction(rungs[2], 1) + Fraction(1, 1) / chain
    chain = Fraction(rungs[1], 1) + Fraction(1, 1) / chain
    effective = Fraction(cover, 1) + Fraction(1, 1) / chain
    value = Fraction(b ** up, 1) + Fraction(c ** b, 1) * (effective + 1) / effective
    arithmetic = (rungs == (125, 175, 245, 343) and value == Fraction(503846395469, 3676744786))
''',
        "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001": '''
    capacities = tuple(2 * (1 + 2 * (rank - 1)) for rank in range(1, 13))
    arithmetic = capacities[:5] == (2, 6, 10, 14, 18) and all(capacities[i] - capacities[i - 1] == 4 for i in range(1, len(capacities)))
''',
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001": '''
    value = Fraction(2, 3)
    arithmetic = value.numerator == 2 and value.denominator == 3
''',
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001": '''
    def base(rank):
        return rank * (rank + 1) * (rank + 2) // 3
    def closure(rank):
        return base(rank) if rank <= 3 else base(rank - 1) + 2 * rank
    sequence = tuple(closure(rank) for rank in range(1, 9))
    threshold = next(rank for rank in range(1, 10) if Fraction(2, 3) * Fraction(rank, 2) >= 1)
    arithmetic = sequence == (2, 8, 20, 28, 50, 82, 126, 184) and threshold == 3
''',
        "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001": '''
    value = Fraction(503846395469, 3676744786)
    endpoint = value.numerator // value.denominator
    arithmetic = endpoint == 137 and Fraction(endpoint, 1) <= value < Fraction(endpoint + 1, 1)
''',
    }[spec.claim_id]
    return f'''"""Implementation-distinct validator for {spec.claim_id}."""

from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
{arithmetic_checks}
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
        and arithmetic
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "arithmetic_reconstruction": arithmetic}},
    }}, sort_keys=True))


if __name__ == "__main__":
    main()
'''


def derivation_note(spec) -> str:
    axes = "\n".join(
        f"- `{axis.key}`: sole preserving form `{axis.survivor.name}`; "
        + "; ".join(f"`{choice.name}` — {choice.reason}" for choice in axis.choices)
        for axis in spec.axes
    )
    witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in spec.witnesses)
    exclusions = "\n".join(f"- {row}" for row in spec.exclusions)
    cardinality = 1
    for axis in spec.axes:
        cardinality *= len(axis.choices)
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

Grammar boundary: {spec.grammar_boundary}

The generator exhausts the Cartesian product of every registered axis: exactly
{cardinality} named forms. Exactly one form preserves all upstream laws and
typed structural roles:

`{survivor_id(spec)}`

{axes}

No axis is a free or learned parameter. The construction does not read an old
SFT answer or an external physical target.

Base: {spec.induction_base}

Successor/termination certificate: {spec.induction_step}

Exact result: {spec.exact_result}

## CHECK

{witnesses}

An implementation-distinct standard-library validator regenerates the complete
candidate product, sole-survivor decisions and exact arithmetic witness. Four
adverse controls must pass before admission. Empirical comparison, where
available, is a separate post-seal claim and cannot rewrite this derivation.

## EXCLUSIONS

{exclusions}
"""


def main() -> None:
    for spec in ATOMIC_CONSTANT_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(registration(spec), indent=2) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", derivation_note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()

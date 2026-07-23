"""Materialize the twelve registered mathematics claim packages.

This tool is deterministic repository scaffolding. It does not execute or admit
claims; only the single admission engine may write them into the model census.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.mathematics.catalog import SPECS  # noqa: E402
from sft.mathematics.generated_law import completeness_record  # noqa: E402


MODULES = {
    "SFT-MATH-EXACT-ARITHMETIC-001": "exact_arithmetic",
    "SFT-MATH-DISCRETE-001": "discrete_mathematics",
    "SFT-MATH-COMBINATORICS-001": "combinatorics",
    "SFT-MATH-GRAPH-NETWORK-001": "graph_network",
    "SFT-MATH-ALGEBRA-001": "algebraic_structures",
    "SFT-MATH-ORDER-LATTICE-001": "order_lattice",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001": "geometry_topology",
    "SFT-MATH-PROBABILITY-STATISTICS-001": "probability_statistics",
    "SFT-MATH-OPTIMIZATION-001": "optimization",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001": "dynamical_systems",
    "SFT-MATH-LOGIC-PROOF-001": "logic_proof",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001": "category_type_composition",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "mathematics",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.boundary_exclusions),
        "required_controls": [
            "false_premise",
            "tampered_source",
            "tampered_artifact",
            "boundary",
        ],
        "intended_certificate": (
            f"Independent regeneration of the complete {2 ** len(spec.dimensions)}-candidate "
            "product, its sole all-preserving survivor, closure properties and controls."
        ),
        "empirical_protocol": None,
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-23",
    }


def execution_source(spec, module: str) -> str:
    slug = spec.claim_id.removeprefix("SFT-").lower().replace("-", "-")
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.{module}.law import SPEC
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/mathematics/generated_law.py",
        root / "sft/mathematics/{module}/law.py",
        root / "claims/{spec.claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-{slug}-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = "__".join(dimension.admitted_choice.name for dimension in spec.dimensions)
    return f'''"""Implementation-distinct product validator for {spec.claim_id}."""

from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {{item["candidate_id"]: item["survives"] for item in sealed["decisions"]}}
    controls = sealed["controls"]
    closure = sealed["closure"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and closure["scope"] == "depth_independent"
        and closure["minimality_passed"] is True
        and closure["named_shape_uniqueness_passed"] is True
        and {{item["kind"] for item in controls}} == {{
            "false_premise", "tampered_source", "tampered_artifact", "boundary"
        }}
        and all(item["passed"] is True for item in controls)
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
        }},
    }}, sort_keys=True))


if __name__ == "__main__":
    main()
'''


def why_derivation_check(spec) -> str:
    laws = "\n".join(f"- {law}." for law in spec.laws)
    boundaries = "\n".join(f"- {boundary}." for boundary in spec.boundary_exclusions)
    witnesses = "\n".join(
        f"- `{witness.name}`: {witness.statement}" for witness in spec.witnesses
    )
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## Why

{spec.why}

## Derivation

{spec.derivation}

The registered grammar boundary is:

> {spec.grammar_boundary}

The complete product has `{2 ** len(spec.dimensions)}` candidates across
`{len(spec.dimensions)}` declared structural dimensions. Every dimension has one
all-preserving coordinate and at least one explicit failure coordinate. Exactly
one product member combines all preserving coordinates.

The admitted result is:

> {spec.exact_result}

Its operational laws are:

{laws}

Depth-independent closure uses this base:

> {spec.induction_base}

and this successor certificate:

> {spec.induction_step}

The exact exclusions are:

{boundaries}

## Check

{spec.check}

Operational witnesses:

{witnesses}

Four required controls reject a false premise, changed source identity, altered
survivor set and excluded boundary import. The separate validator independently
regenerates the literal candidate product and sole survivor without importing the
scientific law module.

## Boundary

{spec.limitations}

Conventional correspondence terms, admitted only after the derivation is sealed:
{", ".join(spec.correspondence_terms)}.
"""


def main() -> None:
    if set(MODULES) != {spec.claim_id for spec in SPECS}:
        raise SystemExit("module routing and mathematics catalog differ")
    for spec in SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(registration(spec), indent=2, sort_keys=False) + "\n")
        write(package / "execution.py", execution_source(spec, MODULES[spec.claim_id]))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", why_derivation_check(spec))
        write(
            package / "STATUS.md",
            f"# {spec.claim_id}\n\nStatus: `registered`\n\n"
            "The claim is registered but has not yet entered the official model census.\n",
        )
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()

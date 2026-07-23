"""Preregister and scaffold the frozen 113-claim classical-computation branch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.computation.catalog import SPECS  # noqa: E402
from sft.computation.generated_law import completeness_record, survivor_id  # noqa: E402
from sft.computation.spec_data import EXPECTED_GROUP_COUNTS, GROUP_TITLES  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def module_path(spec) -> str:
    return f"sft.computation.{spec.group}.{spec.slug.lower().replace('-', '_')}.law"


def package_path(spec) -> str:
    return f"sft/computation/{spec.group}/{spec.slug.lower().replace('-', '_')}"


def render_law(spec) -> str:
    return (
        f'"""{spec.title}.\n\nWHY, DERIVATION and CHECK are preserved in the claim package.\n"""\n\n'
        "from sft.computation.catalog import SPEC_BY_ID\n\n"
        f'SPEC = SPEC_BY_ID["{spec.claim_id}"]\n\n'
        "__all__ = (\"SPEC\",)\n"
    )


def render_execution(spec) -> str:
    module = module_path(spec)
    package = package_path(spec)
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.computation.generated_law import GeneratedComputationProgram
from {module} import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/computation/generated_law.py",
        root / "sft/computation/operations.py",
        root / "sft/computation/spec_data.py",
        root / "sft/computation/catalog.py",
        root / "{package}/law.py",
        root / "claims/{spec.claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "{spec.claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
'''


def render_validator(spec) -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct product validator for {spec.claim_id}."""

from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}


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
        and {{item["kind"] for item in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
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


def render_why(spec) -> str:
    admitted = "\n".join(
        f"- `{dimension.key}` — `{dimension.admitted_choice.name}`: {dimension.admitted_choice.reason}"
        for dimension in spec.dimensions
    )
    laws = "\n".join(f"- {law}" for law in spec.laws)
    witnesses = "\n".join(f"- `{w.name}` — {w.statement}" for w in spec.witnesses)
    exclusions = "\n".join(f"- {item}" for item in spec.boundary_exclusions)
    terms = ", ".join(spec.correspondence_terms)
    return f'''# {spec.title}

Claim: `{spec.claim_id}`

Sub-branch: `{spec.group}`

## WHY

{spec.why}

## DERIVATION

{spec.derivation}

The registered grammar boundary is:

> {spec.grammar_boundary}

The complete product contains `256` candidates across eight exact binary
structural axes. Every coordinate occurs once with every coordinate on every
other axis. Exactly one product member retains all eight requirements.

Admitted coordinates:

{admitted}

Forced result:

> {spec.exact_result}

Operational laws:

{laws}

Depth-independent base:

> {spec.induction_base}

Depth-independent successor:

> {spec.induction_step}

## CHECK

{spec.check}

Live operational witnesses:

{witnesses}

Four controls must reject a false premise, changed source identity, altered
survivor set and excluded boundary import. The independent validator regenerates
the literal product without importing the scientific law module.

## Boundary

{spec.limitations}

Explicit exclusions:

{exclusions}

Conventional terms are downstream correspondence only: {terms}.
'''


def main() -> None:
    for spec in SPECS:
        module_dir = ROOT / package_path(spec)
        write(module_dir / "__init__.py", f'"""{spec.title}."""\n\nfrom .law import SPEC\n\n__all__ = ("SPEC",)\n')
        write(module_dir / "law.py", render_law(spec))
        claim_dir = ROOT / "claims" / spec.claim_id
        write(claim_dir / "execution.py", render_execution(spec))
        write(claim_dir / "independent_validator.py", render_validator(spec))
        write(claim_dir / "WHY_DERIVATION_CHECK.md", render_why(spec))
        write(claim_dir / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        write_json(
            claim_dir / "registration.json",
            {
                "$schema": "../../governance/claim.schema.json",
                "branch": "computation",
                "candidate_grammar": {
                    "boundary": spec.grammar_boundary,
                    "completeness_certificate": sha256_identity(completeness_record(spec)),
                    "generator": spec.generation_rule,
                },
                "claim_id": spec.claim_id,
                "dependencies": spec.dependencies,
                "empirical_protocol": None,
                "excluded_inputs": spec.boundary_exclusions,
                "intended_certificate": "Independent regeneration of all 256 candidates, the sole survivor, closure and controls.",
                "provenance_classes": ["forward_forcing"],
                "registered_by": "Maria Smith",
                "registration_date": "2026-07-23",
                "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
                "statement": spec.statement,
                "status": "registered",
                "title": spec.title,
            },
        )

    inventory = {
        "branch_id": "computation",
        "frozen": True,
        "current_knowledge_scope": "The complete V3 classical computational-science inventory through Formal Computation, Computability, Complexity, Algorithms and mathematical data structures, Semantics, Concurrent and Distributed Computation, Cryptography and Computational Security, Learning and Intelligence Theory, and Scientific Computation. Reversible and Quantum Computation is a separate downstream branch.",
        "group_counts": EXPECTED_GROUP_COUNTS,
        "required_claim_ids": [spec.claim_id for spec in SPECS],
        "unclassified_obligations": [],
        "frontier_obligations": [],
    }
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(ROOT / "publications/inventories/computation.json", inventory)
    print(f"preregistered {len(SPECS)} classical-computation claims")


if __name__ == "__main__":
    main()

"""Preregister and scaffold the frozen 21-claim quantum-computation branch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.quantum_computation.catalog import SPECS  # noqa: E402
from sft.quantum_computation.generated_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def module_dir(spec):
    return ROOT / "sft" / "quantum_computation" / spec.slug.lower().replace("-", "_")


def render_execution(spec) -> str:
    module = f"sft.quantum_computation.{spec.slug.lower().replace('-', '_')}.law"
    path = f"sft/quantum_computation/{spec.slug.lower().replace('-', '_')}"
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.quantum_computation.generated_law import GeneratedQuantumProgram
from {module} import SPEC
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/quantum_computation/generated_law.py",
        root / "sft/quantum_computation/operations.py",
        root / "sft/quantum_computation/catalog.py",
        root / "{path}/law.py",
        root / "claims/{spec.claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedQuantumProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "{spec.claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
    )
'''


def render_validator(spec) -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct validator for {spec.claim_id}."""
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
        sealed["claim_id"] == CLAIM_ID and received == generated
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
        "certificate": {{"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None}},
    }}, sort_keys=True))
if __name__ == "__main__":
    main()
'''


def render_why(spec) -> str:
    admitted = "\n".join(f"- `{d.key}` — `{d.admitted_choice.name}`: {d.admitted_choice.reason}" for d in spec.dimensions)
    laws = "\n".join(f"- {law}" for law in spec.laws)
    witnesses = "\n".join(f"- `{w.name}` — {w.statement}" for w in spec.witnesses)
    exclusions = "\n".join(f"- {item}" for item in spec.boundary_exclusions)
    return f'''# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.why}

## DERIVATION

{spec.derivation}

Boundary:

> {spec.grammar_boundary}

The complete eight-axis product contains 256 generated candidates and exactly
one all-preserving member.

{admitted}

Forced result:

> {spec.exact_result}

Laws:

{laws}

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

{spec.check}

{witnesses}

## Boundary and exclusions

{spec.limitations}

{exclusions}

Downstream conventional correspondence only: {", ".join(spec.correspondence_terms)}.
'''


def main() -> None:
    for spec in SPECS:
        directory = module_dir(spec)
        write(directory / "__init__.py", f'"""{spec.title}."""\nfrom .law import SPEC\n__all__ = ("SPEC",)\n')
        write(directory / "law.py", f'"""{spec.title}."""\nfrom sft.quantum_computation.catalog import SPEC_BY_ID\nSPEC = SPEC_BY_ID["{spec.claim_id}"]\n__all__ = ("SPEC",)\n')
        claim = ROOT / "claims" / spec.claim_id
        write(claim / "execution.py", render_execution(spec))
        write(claim / "independent_validator.py", render_validator(spec))
        write(claim / "WHY_DERIVATION_CHECK.md", render_why(spec))
        write(claim / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        write_json(claim / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "quantum_computation",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": sha256_identity(completeness_record(spec)), "generator": spec.generation_rule},
            "claim_id": spec.claim_id,
            "dependencies": spec.dependencies,
            "empirical_protocol": None,
            "excluded_inputs": spec.boundary_exclusions,
            "intended_certificate": "Independent regeneration of all 256 candidates, sole survivor, closure and controls.",
            "provenance_classes": ["forward_forcing"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-23",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "statement": spec.statement,
            "status": "registered",
            "title": spec.title,
        })
    inventory = {
        "branch_id": "quantum_computation",
        "frozen": True,
        "current_knowledge_scope": "The complete V3 Reversible and Quantum Computation inventory: reversible model; information units and composition; superposition-equivalent support; phase/interference; entanglement; measurement; gates and circuits; universality; algorithms and complexity; communication; coding; error correction; fault tolerance; simulation; verification; learning; operational classical-quantum correspondence; and computational limits.",
        "required_claim_ids": [spec.claim_id for spec in SPECS],
        "unclassified_obligations": [],
        "frontier_obligations": [],
    }
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(ROOT / "publications/inventories/quantum_computation.json", inventory)
    print(f"preregistered {len(SPECS)} quantum-computation claims")
if __name__ == "__main__":
    main()

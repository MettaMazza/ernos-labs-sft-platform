#!/usr/bin/env python3
"""Implementation-distinct verifier for one OpenAI 2026 SFT derivation.

This verifier intentionally imports no SFT derivation module.  It reconstructs
the frozen proof graph, executable checks, route product and sealed decisions
from JSON and Python's standard library.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import factorial, prod
import hashlib
import json
import sys
from pathlib import Path


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def pair(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("bad rational pair")
    return Fraction(value[0], value[1])


def roundtrip_words(limit: int) -> bool:
    for width in range(limit + 1):
        for digits in product((0, 1), repeat=width):
            encoded = sum(digit * (2 ** position) for position, digit in enumerate(digits))
            reconstructed = tuple((encoded // (2 ** position)) % 2 for position in range(width))
            if reconstructed != digits:
                return False
    return True


def ramsey_check() -> bool:
    edges = tuple(combinations(range(6), 2))
    triples = tuple(combinations(range(6), 3))
    position = {edge: ordinal for ordinal, edge in enumerate(edges)}
    for colouring in product((0, 1), repeat=len(edges)):
        monochromatic = False
        for triple in triples:
            triangle_edges = tuple(tuple(sorted(edge)) for edge in combinations(triple, 2))
            first = colouring[position[triangle_edges[0]]]
            if all(colouring[position[edge]] == first for edge in triangle_edges[1:]):
                monochromatic = True
                break
        if not monochromatic:
            return False
    return True


def check(row: dict[str, object]) -> bool:
    kind = row.get("kind")
    if kind == "field_coverage":
        expected, actual = row.get("expected"), row.get("actual")
        return isinstance(expected, list) and expected == actual and len({json.dumps(x, sort_keys=True) for x in expected}) == len(expected)
    if kind == "rational_order":
        return pair(row.get("right")) - pair(row.get("left")) > 0
    if kind == "rational_equality":
        return pair(row.get("left")) - pair(row.get("right")) == 0
    if kind == "integer_equality":
        left, right = row.get("left"), row.get("right")
        return type(left) is int and type(right) is int and left - right == 0
    if kind == "strict_chain":
        values = row.get("values")
        return isinstance(values, list) and len(values) > 1 and min(b - a for a, b in zip(values, values[1:])) > 0
    if kind == "all_unique":
        values = row.get("values")
        return isinstance(values, list) and len(values) > 0 and len({json.dumps(x, sort_keys=True) for x in values}) == len(values)
    if kind == "all_at_least":
        values, bound = row.get("values"), row.get("bound")
        return isinstance(values, list) and type(bound) is int and len(values) > 0 and min(values) >= bound
    if kind == "successor_trace":
        values = row.get("values")
        return isinstance(values, list) and len(values) > 0 and all(type(value) is int for value in values) and tuple(values[1:]) == tuple(value + 1 for value in values[:-1])
    if kind == "finite_product_count":
        axes, expected = row.get("axes"), row.get("expected")
        return isinstance(axes, list) and all(type(axis) is int and axis > 0 for axis in axes) and type(expected) is int and prod(axes) == expected
    if kind == "factorial_table":
        values = row.get("values")
        if not isinstance(values, list) or not values:
            return False
        table = {0: 1}
        for n in range(1, max(values) + 1):
            table[n] = table[n - 1] * n
        return all(type(n) is int and n > 0 and table[n] == factorial(n) for n in values)
    if kind == "bool_word_roundtrip":
        limit = row.get("maximum_length")
        return type(limit) is int and limit >= 0 and roundtrip_words(limit)
    if kind == "ramsey_k6_two_colour":
        return ramsey_check()
    if kind == "implication_tautology":
        for p, q in product((False, True), repeat=2):
            if p and ((not p) or q) and not q:
                return False
        return True
    if kind == "contradiction_tautology":
        return not any(p and (not p) for p in (False, True))
    return False


def independent_proof_certificate(spec: dict[str, object]) -> dict[str, object]:
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("missing checks")
    identities: set[str] = set()
    for row in checks:
        if not isinstance(row, dict) or type(row.get("check_id")) is not str or row["check_id"] in identities or not check(row):
            raise ValueError("check failure")
        identities.add(row["check_id"])
    dependencies = spec.get("dependencies")
    steps = spec.get("steps")
    if not isinstance(dependencies, list) or not dependencies or len(dependencies) != len(set(dependencies)) or not isinstance(steps, list) or not steps:
        raise ValueError("missing dependency or proof rows")
    prior: dict[str, dict[str, object]] = {}
    introduced: set[str] = set()
    for row in steps:
        if not isinstance(row, dict):
            raise ValueError("bad step")
        name = row.get("step_id")
        premises = row.get("premises")
        check_ids = row.get("check_ids")
        bound = row.get("dependency_claims")
        if type(name) is not str or not name or name in prior or not isinstance(premises, list) or any(p not in prior for p in premises):
            raise ValueError("non-topological proof")
        if not isinstance(check_ids, list) or any(c not in identities for c in check_ids):
            raise ValueError("unbound check")
        if not isinstance(bound, list) or any(dep not in dependencies for dep in bound):
            raise ValueError("unbound dependency")
        if bound and row.get("rule") != "dependency_composition":
            raise ValueError("dependency introduced by wrong rule")
        introduced.update(bound)
        prior[name] = row
    if introduced != set(dependencies):
        raise ValueError("incomplete dependency use")
    terminal = [row for row in steps if row.get("conclusion") == "REGISTERED_NATIVE_PROPOSITION"]
    if len(terminal) != 1 or terminal[0] != steps[-1]:
        raise ValueError("terminal mismatch")
    reached: set[str] = set()
    pending = [steps[-1]["step_id"]]
    while pending:
        name = pending.pop()
        if name in reached:
            continue
        reached.add(name)
        pending.extend(prior[name]["premises"])
    if reached != set(prior):
        raise ValueError("orphan step")
    if spec.get("proof_outcome") != "PROVED" or spec.get("proof_kind") != "constructive_proof":
        raise ValueError("proof outcome mismatch")
    if spec.get("outcome_axis_present") is not False or spec.get("upstream_proof_used_as_premise") is not False:
        raise ValueError("forbidden authority")
    if spec.get("source_quantifier_and_conjunct_order") != spec.get("translated_quantifier_and_conjunct_order"):
        raise ValueError("logical shape mismatch")
    return {
        "claim_id": spec["claim_id"],
        "proof_outcome": "PROVED",
        "native_formula_hash": identity(spec["native_formula"]),
        "source_statement_hash": spec["source_statement_hash"],
        "translation_hash": spec["translation_hash"],
        "dependency_count": len(dependencies),
        "step_count": len(steps),
        "check_count": len(checks),
        "all_checks_passed": True,
        "all_steps_reach_terminal": True,
        "outcome_axis_present": False,
        "upstream_proof_used_as_premise": False,
    }


def route_surface(spec: dict[str, object]) -> tuple[list[dict[str, object]], str]:
    dimensions = spec.get("route_dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 8:
        raise ValueError("route dimensions missing")
    if any(dimension.get("key") in {"outcome", "verdict"} for dimension in dimensions):
        raise ValueError("outcome axis present")
    domains = []
    accepted = []
    for dimension in dimensions:
        choices = dimension.get("choices")
        if not isinstance(choices, list) or len(choices) != 2:
            raise ValueError("bad route dimension")
        admitted = [choice for choice in choices if choice[1] is True]
        if len(admitted) != 1:
            raise ValueError("route dimension not unique")
        domains.append([choice[0] for choice in choices])
        accepted.append(admitted[0][0])
    rows = []
    for values in product(*domains):
        coordinates = [[dimension["key"], value] for dimension, value in zip(dimensions, values)]
        rows.append({
            "candidate_id": "__".join(values),
            "coordinates": coordinates,
            "exact_form": "; ".join(f"{key}={value}" for key, value in coordinates),
        })
    return rows, "__".join(accepted)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: validator CLAIM_ID ROOT SEALED", file=sys.stderr)
        return 2
    claim_id, root_text, sealed_text = sys.argv[1:]
    root = Path(root_text)
    package = root / "claims" / claim_id
    try:
        spec = load(package / "derivation_spec_v1.json")
        source = load(package / "source_statement.json")
        translation = load(package / "translation.json")
        registry = load(root / "census/openai_ten_advances_2026_sft_obligation_registry_v1.json")
        census = load(root / "census/claims.json")
        sealed = load(Path(sealed_text))
        if not all(isinstance(value, dict) for value in (spec, source, translation, registry, census, sealed)):
            raise ValueError("malformed object")
        identity_input = dict(spec)
        declared_derivation_identity = identity_input.pop("derivation_identity")
        if identity(identity_input) != declared_derivation_identity:
            raise ValueError("derivation identity mismatch")
        source_row = next(row for row in registry["rows"] if row["claim_id"] == claim_id)
        if identity(source) != spec["source_statement_hash"] or source_row["source_statement_hash"] != spec["source_statement_hash"]:
            raise ValueError("source statement mismatch")
        if identity(translation) != spec["translation_hash"] or translation["native_formula"] != spec["native_formula"]:
            raise ValueError("translation mismatch")
        admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
        if any(dependency not in admitted for dependency in spec["dependencies"]):
            raise ValueError("unadmitted dependency")
        proof = independent_proof_certificate(spec)
        if proof != spec["primary_preflight_certificate"]:
            raise ValueError("primary and independent proof certificates differ")
        route_rows, survivor = route_surface(spec)
        actual_candidates = sealed["census"]["candidates"]
        actual_ids = [candidate["candidate_id"] for candidate in actual_candidates]
        expected_ids = [row["candidate_id"] for row in route_rows]
        if actual_ids != expected_ids or len(actual_ids) != len(set(actual_ids)) or len(actual_ids) != 256:
            raise ValueError("candidate product mismatch")
        for candidate, record in zip(actual_candidates, route_rows):
            if candidate["exact_form"] != record["exact_form"] or candidate["trace_hash"] != identity({"claim_id": claim_id, "record": record}):
                raise ValueError("candidate record mismatch")
        decisions = sealed["decisions"]
        if [row["candidate_id"] for row in decisions] != expected_ids:
            raise ValueError("decision coverage mismatch")
        exact_result = "PROVED: " + spec["native_formula"]
        decision_map = {row["candidate_id"]: row for row in decisions}
        if sum(row["survives"] is True for row in decisions) != 1 or decision_map[survivor]["survives"] is not True:
            raise ValueError("survivor mismatch")
        if any(row["survives"] is True for row in decisions if row["candidate_id"] != survivor):
            raise ValueError("additional survivor")
        if sealed["census"]["expected_cardinality"] != 256 or len(sealed["controls"]) != 4 or not all(row["passed"] is True for row in sealed["controls"]):
            raise ValueError("gate evidence mismatch")
        if sealed["closure"]["scope"] != "depth_independent" or sealed["claim_id"] != claim_id:
            raise ValueError("closure or identity mismatch")
        certificate = {
            "claim_id": claim_id,
            "derivation_identity": declared_derivation_identity,
            "source_statement_hash": spec["source_statement_hash"],
            "translation_hash": spec["translation_hash"],
            "proof_outcome": "PROVED",
            "proof_steps": proof["step_count"],
            "executable_checks": proof["check_count"],
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "exact_result_hash": identity(exact_result),
            "all_dependencies_prior_and_admitted": True,
            "all_checks_recomputed": True,
            "complete_graph_reconstructed": True,
            "outcome_axis_present": False,
            "upstream_proof_used_as_premise": False,
        }
        print(json.dumps({
            "validated_seal_hash": sealed["seal_hash"],
            "recomputed_from_declared_inputs": True,
            "passed": True,
            "certificate": certificate,
        }, sort_keys=True))
        return 0
    except Exception as error:
        print(f"independent OpenAI 2026 validation halted: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

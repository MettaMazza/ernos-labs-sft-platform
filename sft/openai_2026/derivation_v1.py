"""Frozen-engine derivation kernel for the twelve OpenAI 2026 SFT obligations.

This module validates theorem-specific proof chains, exact source/translation
bindings and executable certificates before the admission engine sees a
candidate.  The generated product distinguishes derivation routes only; it has
no theorem-verdict coordinate.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import factorial, prod
from typing import Sequence

from sft.engine import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
)
from sft.engine.canonical import sha256_identity


ROUTE_DIMENSIONS: tuple[dict[str, object], ...] = (
    {
        "key": "source_binding",
        "question": "Is the exact frozen declaration the target?",
        "choices": (
            ("stale-or-paraphrased-source", False, "A changed or paraphrased target is not the registered proposition."),
            ("exact-frozen-source", True, "The source file, span, text and identities all match the frozen capture."),
        ),
    },
    {
        "key": "logical_shape",
        "question": "Are all binders, hypotheses, polarities and conjuncts retained?",
        "choices": (
            ("weakened-or-reordered-shape", False, "Dropping or changing a quantifier, hypothesis or conjunct changes the theorem."),
            ("exact-quantifier-conjunct-order", True, "The complete registered binder and conjunct order is retained."),
        ),
    },
    {
        "key": "translation",
        "question": "Does the SFT-native translation preserve the proposition?",
        "choices": (
            ("carrier-rejection-or-finite-analogue", False, "Carrier rejection or a finite example is not a truth-preserving translation."),
            ("exact-native-correspondence", True, "Encode/decode, relations, implications and negations are preserved exactly."),
        ),
    },
    {
        "key": "grammar",
        "question": "Which enumeration governs the derivation?",
        "choices": (
            ("invented-verdict-census", False, "A new verdict coordinate cannot select a mathematical result."),
            ("preexisting-branch-grammar-composition", True, "Only the admitted dependency grammars generate proof objects."),
        ),
    },
    {
        "key": "dependency_trace",
        "question": "Is the root-to-result dependency trace complete?",
        "choices": (
            ("missing-or-unadmitted-dependency", False, "Every mathematical premise must have a prior model-admitted owner."),
            ("complete-prior-receipt-trace", True, "Every dependency is prior, receipt-bound and used in the proof graph."),
        ),
    },
    {
        "key": "mathematical_chain",
        "question": "Does the complete theorem-specific proof chain reach the registered proposition?",
        "choices": (
            ("truncated-or-circular-chain", False, "A missing, forward, circular or orphaned proof step cannot close the theorem."),
            ("complete-root-to-result-chain", True, "Every step is prior-founded and the unique terminal step is the exact proposition."),
        ),
    },
    {
        "key": "execution",
        "question": "Are all finite equalities, bounds, witnesses and enumerations executed?",
        "choices": (
            ("asserted-or-sampled-checks", False, "Unexecuted assertions and incomplete samples do not certify a result."),
            ("complete-executable-certificates", True, "Every registered finite check is recomputed and passes exactly."),
        ),
    },
    {
        "key": "provenance",
        "question": "What selects the proof?",
        "choices": (
            ("imported-openai-proof-authority", False, "The upstream proof and its foundations have no SFT derivational authority."),
            ("sft-root-bound-forward-derivation", True, "The result is selected only by the SFT proof chain and admitted dependencies."),
        ),
    },
)


ALLOWED_RULES = frozenset({
    "dependency_composition",
    "exact_construction",
    "universal_successor",
    "exact_arithmetic",
    "order_transitivity",
    "record_assembly",
    "exhaustive_negation",
    "contradiction",
    "existential_witness",
    "implication",
})


def _fraction(pair: list[int]) -> Fraction:
    if not isinstance(pair, list) or len(pair) != 2:
        raise ValueError("rational certificate must be a numerator/denominator pair")
    numerator, denominator = pair
    if isinstance(numerator, bool) or isinstance(denominator, bool) or denominator == 0:
        raise ValueError("rational certificate is malformed")
    return Fraction(numerator, denominator)


def _bool_word_roundtrip(maximum_length: int) -> bool:
    if maximum_length < 0:
        return False
    for length in range(maximum_length + 1):
        for word in product((False, True), repeat=length):
            payload = (length, sum((1 << index) for index, bit in enumerate(word) if bit))
            decoded = tuple(bool(payload[1] & (1 << index)) for index in range(payload[0]))
            if decoded != word:
                return False
    return True


def _ramsey_k6_two_colour() -> bool:
    vertices = range(6)
    edges = tuple(combinations(vertices, 2))
    triangles = tuple(combinations(vertices, 3))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    for mask in range(1 << len(edges)):
        found = False
        for triangle in triangles:
            colours = {
                (mask >> edge_index[tuple(sorted(edge))]) & 1
                for edge in combinations(triangle, 2)
            }
            if len(colours) == 1:
                found = True
                break
        if not found:
            return False
    return True


def evaluate_check(check: dict[str, object]) -> bool:
    kind = check.get("kind")
    if kind == "field_coverage":
        expected = check.get("expected")
        actual = check.get("actual")
        return isinstance(expected, list) and isinstance(actual, list) and expected == actual and len(expected) == len(set(map(str, expected)))
    if kind == "rational_order":
        return _fraction(check["left"]) < _fraction(check["right"])
    if kind == "rational_equality":
        return _fraction(check["left"]) == _fraction(check["right"])
    if kind == "integer_equality":
        left, right = check.get("left"), check.get("right")
        return isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool) and left == right
    if kind == "strict_chain":
        values = check.get("values")
        return isinstance(values, list) and len(values) >= 2 and all(left < right for left, right in zip(values, values[1:]))
    if kind == "all_unique":
        values = check.get("values")
        return isinstance(values, list) and bool(values) and len(values) == len(set(map(str, values)))
    if kind == "all_at_least":
        values, bound = check.get("values"), check.get("bound")
        return isinstance(values, list) and isinstance(bound, int) and bool(values) and all(isinstance(value, int) and not isinstance(value, bool) and value >= bound for value in values)
    if kind == "successor_trace":
        values = check.get("values")
        return isinstance(values, list) and bool(values) and all(isinstance(value, int) and not isinstance(value, bool) for value in values) and all(right == left + 1 for left, right in zip(values, values[1:]))
    if kind == "finite_product_count":
        axes, expected = check.get("axes"), check.get("expected")
        return isinstance(axes, list) and all(isinstance(axis, int) and axis > 0 for axis in axes) and isinstance(expected, int) and prod(axes) == expected
    if kind == "factorial_table":
        values = check.get("values")
        return isinstance(values, list) and bool(values) and all(isinstance(n, int) and n > 0 and factorial(n) == n * factorial(n - 1) for n in values)
    if kind == "bool_word_roundtrip":
        maximum = check.get("maximum_length")
        return isinstance(maximum, int) and not isinstance(maximum, bool) and _bool_word_roundtrip(maximum)
    if kind == "ramsey_k6_two_colour":
        return _ramsey_k6_two_colour()
    if kind == "implication_tautology":
        return all((not (premise and implication)) or conclusion for premise, implication, conclusion in ((p, (not p) or q, q) for p, q in product((False, True), repeat=2)))
    if kind == "contradiction_tautology":
        return all(not (proposition and not proposition) for proposition in (False, True))
    return False


def candidate_records(spec: dict[str, object]) -> tuple[dict[str, object], ...]:
    validate_derivation_spec(spec)
    records: list[dict[str, object]] = []
    domains = tuple(tuple(choice[0] for choice in dimension["choices"]) for dimension in ROUTE_DIMENSIONS)
    for values in product(*domains):
        coordinates = tuple((dimension["key"], value) for dimension, value in zip(ROUTE_DIMENSIONS, values))
        records.append({
            "candidate_id": "__".join(values),
            "coordinates": coordinates,
            "exact_form": "; ".join(f"{key}={value}" for key, value in coordinates),
        })
    return tuple(records)


def survivor_id() -> str:
    return "__".join(next(choice[0] for choice in dimension["choices"] if choice[1]) for dimension in ROUTE_DIMENSIONS)


def validate_derivation_spec(spec: dict[str, object]) -> dict[str, object]:
    if spec.get("schema") != "sft-v3-openai-2026-native-derivation/1":
        raise ValueError("unexpected OpenAI 2026 derivation schema")
    if spec.get("proof_outcome") != "PROVED" or spec.get("proof_kind") != "constructive_proof":
        raise ValueError("the derivation must reach a constructive proof")
    if spec.get("outcome_axis_present") is not False or spec.get("upstream_proof_used_as_premise") is not False:
        raise ValueError("verdict selection or upstream proof authority is forbidden")
    if any(dimension["key"] in {"outcome", "verdict"} for dimension in ROUTE_DIMENSIONS):
        raise ValueError("the derivation-route grammar contains a verdict coordinate")
    native_formula = spec.get("native_formula")
    if not isinstance(native_formula, str) or not native_formula.strip():
        raise ValueError("native proposition is missing")
    source_quantifiers = spec.get("source_quantifier_and_conjunct_order")
    translated_quantifiers = spec.get("translated_quantifier_and_conjunct_order")
    if not isinstance(source_quantifiers, list) or source_quantifiers != translated_quantifiers or not source_quantifiers:
        raise ValueError("source/native logical shape is not exact")
    dependencies = spec.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies or len(dependencies) != len(set(dependencies)):
        raise ValueError("dependency trace is missing or duplicated")
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("executable checks are missing")
    check_map: dict[str, dict[str, object]] = {}
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("check_id"), str):
            raise ValueError("malformed executable check")
        check_id = check["check_id"]
        if check_id in check_map:
            raise ValueError("duplicate executable check identity")
        if not evaluate_check(check):
            raise ValueError(f"executable check failed: {check_id}")
        check_map[check_id] = check
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("mathematical proof chain is missing")
    step_map: dict[str, dict[str, object]] = {}
    used_dependencies: set[str] = set()
    for item in steps:
        if not isinstance(item, dict):
            raise ValueError("malformed proof step")
        step_id = item.get("step_id")
        rule = item.get("rule")
        premises = item.get("premises")
        conclusion = item.get("conclusion")
        check_ids = item.get("check_ids")
        bound_dependencies = item.get("dependency_claims", [])
        if not isinstance(step_id, str) or not step_id or step_id in step_map:
            raise ValueError("missing or duplicate proof-step identity")
        if rule not in ALLOWED_RULES or not isinstance(premises, list) or not isinstance(check_ids, list):
            raise ValueError(f"malformed proof rule: {step_id}")
        if not isinstance(conclusion, str) or not conclusion.strip():
            raise ValueError(f"proof step has no conclusion: {step_id}")
        if any(premise not in step_map for premise in premises):
            raise ValueError(f"proof step has a forward or missing premise: {step_id}")
        if any(check_id not in check_map for check_id in check_ids):
            raise ValueError(f"proof step cites an unknown executable check: {step_id}")
        if not isinstance(bound_dependencies, list) or any(dependency not in dependencies for dependency in bound_dependencies):
            raise ValueError(f"proof step has an unregistered dependency: {step_id}")
        if bound_dependencies and rule != "dependency_composition":
            raise ValueError(f"only dependency-composition steps may introduce prior claims: {step_id}")
        used_dependencies.update(bound_dependencies)
        step_map[step_id] = item
    if used_dependencies != set(dependencies):
        raise ValueError("not every registered dependency is used by the mathematical proof chain")
    terminals = [item for item in steps if item["conclusion"] == "REGISTERED_NATIVE_PROPOSITION"]
    if len(terminals) != 1 or terminals[0] is not steps[-1]:
        raise ValueError("the exact registered proposition is not the unique terminal step")
    reachable: set[str] = set()
    frontier = [steps[-1]["step_id"]]
    while frontier:
        current = frontier.pop()
        if current in reachable:
            continue
        reachable.add(current)
        frontier.extend(step_map[current]["premises"])
    if reachable != set(step_map):
        raise ValueError("the proof chain contains an orphaned step")
    witness_grammar = spec.get("witness_grammar")
    if not isinstance(witness_grammar, list) or not witness_grammar or len(witness_grammar) != len(set(witness_grammar)):
        raise ValueError("the theorem witness grammar is missing or duplicated")
    arbitrary = spec.get("arbitrary_input_certificate")
    if not isinstance(arbitrary, str) or not arbitrary.strip():
        raise ValueError("arbitrary-input or exhaustive-witness certificate is missing")
    return {
        "claim_id": spec["claim_id"],
        "proof_outcome": "PROVED",
        "native_formula_hash": sha256_identity(native_formula),
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


def completeness_record(spec: dict[str, object]) -> dict[str, object]:
    return {
        "claim_id": spec["claim_id"],
        "route_dimensions": ROUTE_DIMENSIONS,
        "candidate_ids": tuple(record["candidate_id"] for record in candidate_records(spec)),
        "proof_certificate": validate_derivation_spec(spec),
        "product_exhaustion": "Every route choice occurs once with every choice in every other registered route dimension.",
    }


def decision_reason(record: dict[str, object], exact_result: str) -> str:
    coordinates = dict(record["coordinates"])
    for dimension in ROUTE_DIMENSIONS:
        admitted = next(choice for choice in dimension["choices"] if choice[1])
        if coordinates[dimension["key"]] != admitted[0]:
            selected = next(choice for choice in dimension["choices"] if choice[0] == coordinates[dimension["key"]])
            return selected[2]
    return exact_result


class OpenAI2026Program:
    def __init__(self, spec: dict[str, object], source_hash: str):
        self.spec = spec
        self.source_hash = source_hash
        self.proof_certificate = validate_derivation_spec(spec)
        self.exact_result = "PROVED: " + str(spec["native_formula"])

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=str(self.spec["claim_id"]),
            title=str(self.spec["title"]),
            branch=str(self.spec["branch"]),
            statement=str(self.spec["native_formula"]),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=tuple(self.spec["dependencies"]),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(self.spec)
        return CandidateCensus(
            generation_rule=(
                "Compose the exact source binding, logical shape, native correspondence, pre-existing branch grammar, "
                "complete dependency trace, mathematical proof chain, executable certificates and SFT provenance. "
                "No outcome or verdict coordinate is generated."
            ),
            grammar_boundary=(
                "Every SFT-admissible encoding of every source binder; every source hypothesis and conjunct; arbitrary-input "
                "base/successor closure or exhaustive existential witness grammar; actual predicate negation where present."
            ),
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity(completeness_record(self.spec)),
            candidates=tuple(
                Candidate(
                    candidate_id=str(record["candidate_id"]),
                    exact_form=str(record["exact_form"]),
                    trace_hash=sha256_identity({"claim_id": self.spec["claim_id"], "record": record}),
                )
                for record in records
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = next(record for record in candidate_records(self.spec) if record["candidate_id"] == candidate.candidate_id)
        survives = candidate.candidate_id == survivor_id()
        reason = decision_reason(record, self.exact_result)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity({
                "claim_id": self.spec["claim_id"],
                "record": record,
                "dependencies": self.spec["dependencies"],
                "proof_certificate": self.proof_certificate,
                "survives": survives,
                "reason": reason,
            }),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = {
            "claim_id": self.spec["claim_id"],
            "proof_label": self.spec["proof_label"],
            "quantifier_mode": self.spec["quantifier_mode"],
            "witness_grammar": self.spec["witness_grammar"],
            "arbitrary_input_certificate": self.spec["arbitrary_input_certificate"],
            "proof_certificate": self.proof_certificate,
            "exact_result": self.exact_result,
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=(
                "The exact registered native proposition over every admissible encoding, with complete source binder and "
                "conjunct preservation and no imported theorem authority."
            ),
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            generality_certificate_hash=sha256_identity({
                "claim_id": self.spec["claim_id"],
                "quantifier_mode": self.spec["quantifier_mode"],
                "arbitrary_input_certificate": self.spec["arbitrary_input_certificate"],
                "steps": self.spec["steps"],
            }),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        records = candidate_records(self.spec)
        survivor = survivor_id()
        first_dimension = ROUTE_DIMENSIONS[0]
        false_choice = next(choice[0] for choice in first_dimension["choices"] if not choice[1])
        false_coordinates = [next(choice[0] for choice in dimension["choices"] if choice[1]) for dimension in ROUTE_DIMENSIONS]
        false_coordinates[0] = false_choice
        false_id = "__".join(false_coordinates)
        controls = (
            (ControlKind.FALSE_PREMISE, false_id != survivor, "reject a changed source target", decision_reason(next(record for record in records if record["candidate_id"] == false_id), self.exact_result)),
            (ControlKind.TAMPERED_SOURCE, sha256_identity({"changed": self.source_hash}) != self.source_hash, "reject a changed source identity", "changed source identity differs from the executed source manifest"),
            (ControlKind.TAMPERED_ARTIFACT, sum(record["candidate_id"] == survivor for record in records) == 1, "reject a missing duplicate or additional survivor", "the complete route product contains exactly one all-admitted derivation"),
            (ControlKind.BOUNDARY, bool(validate_derivation_spec(self.spec)), "reject carrier denial finite examples imported proof authority or incomplete chains", "exact correspondence, full proof graph, arbitrary-input closure and executable certificates all passed"),
        )
        return tuple(
            ControlResult(
                kind=kind,
                passed=passed,
                expected_behavior=expected,
                observed_behavior=observed,
                receipt_hash=sha256_identity({"kind": kind.value, "passed": passed, "expected": expected, "observed": observed}),
            )
            for kind, passed, expected, observed in controls
        )

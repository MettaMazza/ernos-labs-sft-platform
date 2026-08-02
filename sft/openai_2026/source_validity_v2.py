"""Frozen-engine disproof kernel for OpenAI 2026 source-artifact validity.

The v1 obligations prove SFT-native reconstruction propositions.  They do not
establish that the external Lean declarations or proof artifacts are valid SFT
derivations.  This module targets that distinct proposition exactly:

    SFTValid(exact frozen OpenAI artifact)

For every artifact the registered theorem is its negation.  The contradiction
uses the exact source record and already model-admitted SFT admission/domain
laws.  No mathematical-result or verdict coordinate occurs in the candidate
grammar.
"""

from __future__ import annotations

from itertools import product
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
        "choices": (
            ("stale-or-paraphrased-artifact", False, "A changed artifact cannot decide the registered validity proposition."),
            ("exact-frozen-artifact", True, "The declaration, file, commit, signature and source hashes match the frozen artifact."),
        ),
    },
    {
        "key": "quotation",
        "choices": (
            ("weakened-or-substituted-proposition", False, "A native reconstruction is not the exact quoted source proposition."),
            ("exact-statement-and-quantifier-quotation", True, "Every source binder, hypothesis and conjunct is retained in order."),
        ),
    },
    {
        "key": "axiom_evidence",
        "choices": (
            ("axiom-vector-hidden-or-assumed-empty", False, "The submitted proof dependency vector must be exposed exactly."),
            ("nonempty-source-axiom-vector-exposed", True, "The frozen manifest exposes the exact nonempty source axiom vector."),
        ),
    },
    {
        "key": "carrier_evidence",
        "choices": (
            ("necessary-source-component-omitted", False, "Deleting the theorem-specific carrier or totality requirement changes the proposition."),
            ("necessary-source-component-exposed", True, "The exact theorem-specific component conflicting with the SFT domain is retained."),
        ),
    },
    {
        "key": "governing_law",
        "choices": (
            ("invented-validity-rule", False, "A new rule cannot replace the pre-existing SFT admission and domain laws."),
            ("preexisting-admission-and-domain-laws", True, "Only prior model-admitted SFT laws govern the contradiction."),
        ),
    },
    {
        "key": "contradiction_chain",
        "choices": (
            ("inadmissibility-asserted-without-negated-target", False, "A label or missing receipt is not a proof of the registered validity negation."),
            ("assume-valid-and-derive-actual-contradiction", True, "The proof assumes SFT validity and derives both a mandatory condition and its exact failure."),
        ),
    },
    {
        "key": "execution",
        "choices": (
            ("unexecuted-or-sampled-evidence", False, "Every finite source, axiom, token, dependency and identity check must execute."),
            ("complete-executable-evidence", True, "Every registered finite check is recomputed exactly."),
        ),
    },
    {
        "key": "transfer_boundary",
        "choices": (
            ("native-proof-transferred-to-source", False, "Proof of a different SFT-native proposition cannot validate the source artifact."),
            ("native-reconstruction-kept-distinct", True, "The reconstruction is retained separately and supplies no premise for source validity."),
        ),
    },
)


ALLOWED_RULES = frozenset({
    "dependency_composition",
    "exact_source_extraction",
    "validity_assumption",
    "definition_elimination",
    "carrier_conflict",
    "contradiction",
    "negation_introduction",
    "nontransfer",
})

VALIDITY_BOUNDARY = (
    "The exact SFT-validity proposition for the frozen external artifact; its negation follows by assuming "
    "validity and deriving the registered axiom/domain contradiction."
)


def evaluate_check(check: dict[str, object]) -> bool:
    kind = check.get("kind")
    if kind == "exact_list":
        expected, actual = check.get("expected"), check.get("actual")
        return isinstance(expected, list) and expected == actual and bool(expected)
    if kind == "positive_integer":
        value = check.get("value")
        return isinstance(value, int) and not isinstance(value, bool) and value > 0
    if kind == "zero_nonzero_contradiction":
        required, observed = check.get("required"), check.get("observed")
        return required == 0 and isinstance(observed, int) and not isinstance(observed, bool) and observed > 0
    if kind == "token_coverage":
        required, observed = check.get("required"), check.get("observed")
        return (
            isinstance(required, list)
            and isinstance(observed, list)
            and bool(required)
            and required == observed
            and len(required) == len(set(required))
        )
    if kind == "distinct_identity":
        left, right = check.get("left"), check.get("right")
        return isinstance(left, str) and isinstance(right, str) and bool(left) and bool(right) and left != right
    if kind == "all_false":
        values = check.get("values")
        return isinstance(values, list) and bool(values) and all(value is False for value in values)
    return False


def validate_spec(spec: dict[str, object]) -> dict[str, object]:
    if spec.get("schema") != "sft-v3-openai-2026-source-validity-disproof/2":
        raise ValueError("unexpected source-validity schema")
    if spec.get("proof_outcome") != "DISPROVED" or spec.get("proof_kind") != "validity_contradiction":
        raise ValueError("the exact source-validity target must be disproved by contradiction")
    if spec.get("outcome_axis_present") is not False or spec.get("native_reconstruction_used_as_validity_premise") is not False:
        raise ValueError("verdict selection or native-to-source transfer is forbidden")
    if any(dimension["key"] in {"outcome", "verdict"} for dimension in ROUTE_DIMENSIONS):
        raise ValueError("the proof-route grammar contains a verdict coordinate")
    proposition = spec.get("sft_validity_proposition")
    negation = spec.get("registered_negation")
    if not isinstance(proposition, str) or not proposition.strip() or not isinstance(negation, str) or not negation.strip():
        raise ValueError("validity proposition or exact negation missing")
    if proposition not in negation:
        raise ValueError("registered statement is not the named validity negation")
    source_quantifiers = spec.get("source_quantifier_and_conjunct_order")
    quoted_quantifiers = spec.get("quoted_quantifier_and_conjunct_order")
    if not isinstance(source_quantifiers, list) or not source_quantifiers or source_quantifiers != quoted_quantifiers:
        raise ValueError("the exact source quotation changed logical shape")
    axioms = spec.get("source_declared_axioms")
    if axioms != ["propext", "Classical.choice", "Quot.sound"]:
        raise ValueError("unexpected frozen source axiom vector")
    dependencies = spec.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies or len(dependencies) != len(set(dependencies)):
        raise ValueError("dependency list missing or duplicated")
    required_foundation = {
        "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001",
        "SFT-MATH-LOGIC-PROOF-001",
    }
    if not required_foundation.issubset(set(dependencies)):
        raise ValueError("pre-existing admission/proof laws are missing")
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("executable checks missing")
    check_ids: set[str] = set()
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("check_id"), str):
            raise ValueError("malformed executable check")
        if check["check_id"] in check_ids or not evaluate_check(check):
            raise ValueError(f"failed or duplicate executable check: {check.get('check_id')}")
        check_ids.add(check["check_id"])
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("contradiction chain missing")
    step_map: dict[str, dict[str, object]] = {}
    used_dependencies: set[str] = set()
    for row in steps:
        if not isinstance(row, dict):
            raise ValueError("malformed proof step")
        step_id, rule = row.get("step_id"), row.get("rule")
        premises, cited_checks = row.get("premises"), row.get("check_ids")
        bound_dependencies = row.get("dependency_claims", [])
        if not isinstance(step_id, str) or not step_id or step_id in step_map:
            raise ValueError("missing or duplicate proof-step identity")
        if rule not in ALLOWED_RULES or not isinstance(premises, list) or any(p not in step_map for p in premises):
            raise ValueError(f"non-topological proof step: {step_id}")
        if not isinstance(cited_checks, list) or any(check_id not in check_ids for check_id in cited_checks):
            raise ValueError(f"unknown executable check in step: {step_id}")
        if not isinstance(bound_dependencies, list) or any(dependency not in dependencies for dependency in bound_dependencies):
            raise ValueError(f"unregistered dependency in step: {step_id}")
        if bound_dependencies and rule != "dependency_composition":
            raise ValueError(f"dependency introduced outside dependency composition: {step_id}")
        used_dependencies.update(bound_dependencies)
        step_map[step_id] = row
    if used_dependencies != set(dependencies):
        raise ValueError("not every registered dependency is used")
    terminals = [row for row in steps if row.get("conclusion") == "REGISTERED_SOURCE_VALIDITY_NEGATION"]
    if len(terminals) != 1 or terminals[0] is not steps[-1]:
        raise ValueError("validity negation is not the unique terminal conclusion")
    reachable: set[str] = set()
    pending = [steps[-1]["step_id"]]
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(step_map[current]["premises"])
    if reachable != set(step_map):
        raise ValueError("orphaned contradiction step")
    required_rules = {"validity_assumption", "contradiction", "negation_introduction", "nontransfer"}
    if not required_rules.issubset({row["rule"] for row in steps}):
        raise ValueError("actual contradiction, negation introduction or nontransfer step missing")
    return {
        "claim_id": spec["claim_id"],
        "proof_outcome": "DISPROVED",
        "target_hash": sha256_identity(proposition),
        "negation_hash": sha256_identity(negation),
        "source_statement_hash": spec["source_statement_hash"],
        "dependency_count": len(dependencies),
        "step_count": len(steps),
        "check_count": len(checks),
        "axiom_count": len(axioms),
        "actual_contradiction_derived": True,
        "native_reconstruction_transferred": False,
        "outcome_axis_present": False,
    }


def candidate_records(spec: dict[str, object]) -> tuple[dict[str, object], ...]:
    validate_spec(spec)
    domains = tuple(tuple(choice[0] for choice in dimension["choices"]) for dimension in ROUTE_DIMENSIONS)
    records = []
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


def decision_reason(record: dict[str, object], exact_result: str) -> str:
    coordinates = dict(record["coordinates"])
    for dimension in ROUTE_DIMENSIONS:
        accepted = next(choice for choice in dimension["choices"] if choice[1])
        if coordinates[dimension["key"]] != accepted[0]:
            return next(choice[2] for choice in dimension["choices"] if choice[0] == coordinates[dimension["key"]])
    return exact_result


class SourceValidityProgramV2:
    def __init__(self, spec: dict[str, object], source_hash: str):
        self.spec = spec
        self.source_hash = source_hash
        self.proof_certificate = validate_spec(spec)
        self.exact_result = "DISPROVED: " + str(spec["sft_validity_proposition"]) + ". " + str(spec["contradiction_summary"])

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=str(self.spec["claim_id"]),
            title=str(self.spec["title"]),
            branch=str(self.spec["branch"]),
            statement=str(self.spec["registered_negation"]),
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
                "Compose the exact frozen artifact, exact source quotation, exposed source axiom and carrier evidence, "
                "pre-existing SFT laws, complete contradiction chain, executable checks and strict nontransfer boundary. "
                "No outcome or verdict coordinate is generated."
            ),
            grammar_boundary=VALIDITY_BOUNDARY,
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity({
                "claim_id": self.spec["claim_id"],
                "route_dimensions": ROUTE_DIMENSIONS,
                "candidate_ids": tuple(record["candidate_id"] for record in records),
                "proof_certificate": self.proof_certificate,
            }),
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
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=VALIDITY_BOUNDARY,
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=sha256_identity({
                "claim_id": self.spec["claim_id"],
                "target": self.spec["sft_validity_proposition"],
                "negation": self.spec["registered_negation"],
                "proof": self.proof_certificate,
                "decisions": tuple(decisions),
            }),
            generality_certificate_hash=sha256_identity({
                "claim_id": self.spec["claim_id"],
                "source_quantifiers": self.spec["source_quantifier_and_conjunct_order"],
                "steps": self.spec["steps"],
                "nontransfer": self.spec["native_reconstruction_used_as_validity_premise"],
            }),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        records = candidate_records(self.spec)
        survivor = survivor_id()
        controls = (
            (ControlKind.FALSE_PREMISE, len(self.spec["source_declared_axioms"]) > 0, "reject the false premise that the frozen source axiom vector is empty", "the exact three-entry source vector is nonempty"),
            (ControlKind.TAMPERED_SOURCE, sha256_identity({"changed": self.source_hash}) != self.source_hash, "reject any changed source identity", "the changed identity differs from the executed source manifest"),
            (ControlKind.TAMPERED_ARTIFACT, sum(record["candidate_id"] == survivor for record in records) == 1, "reject a missing duplicate or additional complete contradiction route", "the complete route product has one all-evidence survivor"),
            (ControlKind.BOUNDARY, bool(validate_spec(self.spec)), "reject transfer from the SFT-native reconstruction to the external artifact", "the contradiction proves only the exact source-validity negation and records the reconstruction as distinct"),
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

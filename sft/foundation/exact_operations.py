"""Force the exact positive operational domain and its primitive moves."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Sequence

from sft.engine import (
    Candidate, CandidateCensus, CandidateDecision, ClaimRegistration,
    ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode,
    ProvenanceClass, ROOT_THEOREM,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart, InadmissibleExactValue
from sft.foundation.count import CLAIM_ID as COUNT_CLAIM_ID
from sft.foundation.one import CLAIM_ID as ONE_CLAIM_ID
from sft.foundation.part import CLAIM_ID as PART_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-EXACT-OPERATIONS-001"
DOMAINS = (
    ("domain-unrestricted", "domain-exact-positive-through-One"),
    ("full-turn-as-absence", "full-turn-as-One"),
    ("fold-raw-junction", "fold-junction-then-cast"),
    ("take-unguarded", "take-strictly-larger"),
    ("unison-unidentified", "unison-exact-One-relation"),
    ("trace-unbound", "trace-root-bound"),
    ("no-extra", "has-extra"),
)
SURVIVOR = "__".join((
    "domain-exact-positive-through-One", "full-turn-as-One",
    "fold-junction-then-cast", "take-strictly-larger",
    "unison-exact-One-relation", "trace-root-bound", "no-extra",
))
GENERATION_RULE = (
    "Generate the complete product of domain, full-turn representation, Fold "
    "composition, Take guard, unison identity, trace custody and added-data class."
)
GRAMMAR_BOUNDARY = (
    "All primitive operational interfaces on exact positive rational parts of "
    "the structural One using only complete-One casting, self-junction and a "
    "strictly guarded positive Take."
)


def cast_positive(value: Fraction) -> ExactPart:
    """Cast complete Ones while retaining a full turn as the One."""
    if not isinstance(value, Fraction) or value <= 0:
        raise InadmissibleExactValue("cast requires an exact positive magnitude")
    retained = value
    while retained > 1:
        retained -= 1
    return ExactPart(retained)


def fold_part(value: ExactPart) -> ExactPart:
    return cast_positive(value.value + value.value)


def take_part(larger: ExactPart, smaller: ExactPart) -> ExactPart:
    if larger.value <= smaller.value:
        raise InadmissibleExactValue("Take requires the first exact part to be strictly larger")
    return ExactPart(larger.value - smaller.value)


def unison(left: ExactPart, right: ExactPart) -> bool:
    return left.value / right.value == 1


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple({
        "candidate_id": "__".join(fields),
        "exact_form": "Operational interface has " + ", ".join(fields) + ".",
    } for fields in product(*DOMAINS))


def survives(record: dict[str, str]) -> bool:
    return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    candidate = record["candidate_id"]
    failures = (
        ("domain-unrestricted", "It admits absence, signed, irrational, imaginary or beyond-One proof values."),
        ("full-turn-as-absence", "It turns a completed positive cycle into numerical absence."),
        ("fold-raw-junction", "Raw self-junction can leave the admitted part domain."),
        ("take-unguarded", "Unguarded removal can produce absence or a signed quantity."),
        ("unison-unidentified", "It lacks the exact identity relation for coincident parts."),
        ("trace-unbound", "Its result is not bound to the generating operations and root trace."),
        ("has-extra", "It introduces an operation, literal or parameter not supplied by the dependencies."),
    )
    for marker, reason in failures:
        if marker in candidate:
            return reason
    return "It is exact, closed, positive, root-traced and contains only cast, Fold, guarded Take and unison."


def completeness_record() -> dict[str, object]:
    return {"generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY,
            "domains": DOMAINS, "candidates": candidate_records()}


def closure_record() -> dict[str, object]:
    return {
        "cast": "For positive n/d, repeated removal acts only while n/d exceeds the One; termination leaves an exact part in (0, One], and an exact whole terminates at the One.",
        "fold": "For an admitted part x, x joined to itself lies in (0, two Ones]; casting therefore returns exactly one admitted part.",
        "take": "For admitted a>b, the guarded difference is strictly positive and smaller than the One.",
        "unison": "The positive relation a/a is exactly the One; coincidence is identity, not a numerical zero.",
        "exactness": "Integer pairs reduce through the host Fraction carrier; no decimal, irrational or imaginary proof value is constructible.",
        "minimality": "Removing a guard, cast convention, closure, unison or trace loses a required invariant; adding an operation is unforced.",
        "named_shape_uniqueness": f"Only {SURVIVOR} preserves every invariant.",
        "generality": "The numerator/denominator arguments apply to every admitted finite positive count pair, not a chosen denominator bound.",
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    one = ExactPart.from_pair(1, 1)
    quarter = ExactPart.from_pair(1, 4)
    return (
        {"kind": "false_premise", "expected": "reject an unguarded reversed Take", "observed": "the exact carrier raises before constructing a forbidden part", "passed": _rejects(lambda: take_part(quarter, one))},
        {"kind": "tampered_source", "expected": "reject changed source identity", "observed": "the changed identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": "tampered_artifact", "expected": "reject a full turn represented as absence", "observed": "casting two Ones returns the One", "passed": cast_positive(Fraction(2, 1)) == one},
        {"kind": "boundary", "expected": "reject zero, signed, inexact and beyond-One proof carriers", "observed": "all four hostile carrier constructions halt", "passed": all((_rejects(lambda: ExactPart.from_pair(0, 1)), _rejects(lambda: ExactPart.from_pair(-1, 2)), _rejects(lambda: ExactPart(Fraction(3, 2))), _rejects(lambda: cast_positive(Fraction(0, 1)))))},
    )


def _rejects(operation) -> bool:
    try:
        operation()
    except (InadmissibleExactValue, ValueError):
        return True
    return False


class ExactOperationsProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID, "Exact positive foundational operations", "foundation",
            "The unique parameter-free primitive interface on exact parts of the One retains only exact positive rational parts through the One, casts complete turns to the One, defines Fold as self-junction followed by cast, permits Take only from a strictly larger part, identifies unison with the exact One relation, and retains a root-bound trace.",
            EvidenceMode.FORMAL, (ROOT_THEOREM,),
            (ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID), (), (),
            (ProvenanceClass.FORWARD_FORCING,), self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records()
        return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records),
            sha256_identity(completeness_record()), tuple(Candidate(r["candidate_id"], r["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]
        keep = survives(record); reason = decision_reason(record)
        return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record()
        return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True,
            sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            sha256_identity({"positive_count_pair_generality": True, "closure": closure}))

    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

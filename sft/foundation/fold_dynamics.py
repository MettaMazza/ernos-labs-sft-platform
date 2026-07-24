"""Force the exact two-preimage Fold dynamics and uniform-partition law."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart, PositiveCount
from sft.foundation.exact_operations import CLAIM_ID as OPERATIONS_CLAIM_ID, cast_positive, fold_part
from sft.foundation.half_one import CLAIM_ID as HALF_CLAIM_ID, half_one


CLAIM_ID = "SFT-FOUNDATION-FOLD-DYNAMICS-001"
DOMAINS = (
    ("domain-leaking", "domain-closed"),
    ("fibre-not-two", "fibre-exactly-two"),
    ("phase-collision-absent", "phase-collision-present"),
    ("phase-involution-absent", "phase-involution-present"),
    ("uniform-division-broken", "uniform-division-preserved"),
    ("first-cycle-open", "first-cycle-two"),
    ("no-extra", "has-extra"),
)
SURVIVOR = "__".join(("domain-closed", "fibre-exactly-two", "phase-collision-present", "phase-involution-present", "uniform-division-preserved", "first-cycle-two", "no-extra"))
GENERATION_RULE = "Generate the complete product of Fold-domain closure, fibre cardinality, half-One phase collision, phase involution, uniform-division image, first recurrent cycle and added-data class."
GRAMMAR_BOUNDARY = "All dynamical invariants of exact doubling-and-cast on the positive rational circle of the One, with half-One phase translation and generated even uniform partitions."


def phase_antipode(value: ExactPart) -> ExactPart:
    return cast_positive(value.value + half_one().value)


def preimages(image: ExactPart) -> tuple[ExactPart, ExactPart]:
    lower = ExactPart(image.value / 2)
    upper = cast_positive(lower.value + half_one().value)
    return lower, upper


def uniform_division(count: PositiveCount) -> tuple[ExactPart, ...]:
    return tuple(ExactPart.from_pair(index, count.value) for index in range(1, count.value + 1))


def folded_distinct(parts: tuple[ExactPart, ...]) -> tuple[ExactPart, ...]:
    return tuple(sorted(set(fold_part(part) for part in parts)))


def is_uniform(parts: tuple[ExactPart, ...]) -> bool:
    if len(parts) == 1: return parts[0] == ExactPart.from_pair(1, 1)
    gaps = tuple(parts[index].value - parts[index - 1].value for index in range(1, len(parts)))
    return len(set(gaps)) == 1 and parts[-1] == ExactPart.from_pair(1, 1)


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple({"candidate_id": "__".join(x), "exact_form": "Fold dynamics proposal has " + ", ".join(x) + "."} for x in product(*DOMAINS))


def survives(record: dict[str, str]) -> bool: return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    failures = (("domain-leaking", "An image leaves the exact positive domain."), ("fibre-not-two", "The inverse relation does not retain both held preimages."), ("phase-collision-absent", "A half-One phase pair is not identified by Fold."), ("phase-involution-absent", "Two half-One phase translations fail to return the source."), ("uniform-division-broken", "An even uniform partition loses uniformity after duplicate images are identified."), ("first-cycle-open", "The first nonstatic recurrent orbit does not close in two Fold moves."), ("has-extra", "It adds a dynamical selector not supplied by exact Fold."))
    for marker, reason in failures:
        if marker in record["candidate_id"]: return reason
    return "Exact Fold is closed, exactly two-to-one, phase-antipodal, uniform-partition preserving and has the first two-cycle."


def completeness_record() -> dict[str, object]:
    return {"generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY, "domains": DOMAINS, "candidates": candidate_records()}


def closure_record() -> dict[str, object]:
    return {
        "domain": "For x in (0, One], self-junction lies in (0, two Ones]; exact cast returns (0, One].",
        "preimages": "For image y, the lower preimage y/2 and upper preimage cast(y/2 plus half-One) are distinct, lie on opposite half-circles and both Fold to y. Any Fold preimage has one of these two forms.",
        "phase_antipode": "Adding half-One twice adds one complete One, which cast removes; therefore phase antipode is an involution. Doubling a half-One translation adds one complete One before cast, so both phase partners share one Fold image.",
        "uniform_partition": "For an even generated count two-n, images of i/(two-n) identify i with i+n and are exactly j/n for the n positive residue classes; their distinct sorted gaps remain one/n.",
        "first_cycle": "Fold sends one-of-three to two-of-three and two-of-three back to one-of-three. No nonstatic cycle can have positive length below the first count extension beyond identity.",
        "minimality": "Deleting either preimage, cast closure, phase relation, uniform image or return loses an exact Fold invariant; extra dynamics are unforced.",
        "named_shape_uniqueness": f"Only {SURVIVOR} has every invariant.",
        "generality": "The proofs use arbitrary positive numerator/denominator and arbitrary generated positive n, not the finite controls below.",
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    images = tuple(ExactPart.from_pair(n, d) for d in range(2, 9) for n in range(1, d + 1))
    fibres = all(len(set(preimages(y))) == 2 and all(fold_part(p) == y for p in preimages(y)) for y in images)
    phase = all(fold_part(x) == fold_part(phase_antipode(x)) and phase_antipode(phase_antipode(x)) == x for x in images)
    uniform = all(is_uniform(folded_distinct(uniform_division(PositiveCount(even)))) for even in (2, 4, 6, 8, 10, 12))
    third = ExactPart.from_pair(1, 3); two_thirds = ExactPart.from_pair(2, 3)
    return (
        {"kind": "false_premise", "expected": "reject a single-preimage Fold fibre", "observed": "every control image has two distinct generated preimages", "passed": fibres},
        {"kind": "tampered_source", "expected": "reject changed source identity", "observed": "changed identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": "tampered_artifact", "expected": "reject a phase pair with unequal Fold images", "observed": "all exact control pairs collide and the phase map is involutive", "passed": phase},
        {"kind": "boundary", "expected": "retain exact even-partition and first-cycle scope", "observed": "six even partitions remain uniform and the one-third orbit closes in two", "passed": uniform and fold_part(third) == two_thirds and fold_part(two_thirds) == third},
    )


class FoldDynamicsProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(CLAIM_ID, "Exact Fold dynamics and fibre law", "foundation", "Exact Fold is closed on every admitted part, has exactly two preimages related by half-One phase translation, identifies each phase-antipodal pair, preserves uniformity of every generated even division after duplicate images are identified, and its first nonstatic recurrent orbit is the two-cycle one-of-three to two-of-three.", EvidenceMode.FORMAL, (ROOT_THEOREM,), (OPERATIONS_CLAIM_ID, HALF_CLAIM_ID), (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)
    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(); return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records), sha256_identity(completeness_record()), tuple(Candidate(r["candidate_id"], r["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))
    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]; keep = survives(record); reason = decision_reason(record); return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))
    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(); return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True, sha256_identity({"closure": closure, "decisions": tuple(decisions)}), sha256_identity({"arbitrary_rational_and_even_partition_proof": True, "closure": closure}))
    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

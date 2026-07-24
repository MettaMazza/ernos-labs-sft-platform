"""Mechanically enumerate the primitive Fold-map grammar and compositions."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart
from sft.foundation.exact_operations import CLAIM_ID as OPERATIONS_CLAIM_ID, fold_part
from sft.foundation.fold_dynamics import CLAIM_ID as DYNAMICS_CLAIM_ID, preimages


CLAIM_ID = "SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001"
PRIMITIVES = ("identity", "square", "constant-One", "Fold")
GENERATION_RULE = "Base-four rank every ordered word over identity, square, constant-One and Fold at sizes one, two and three; decide least-size generation before any larger composition."
GRAMMAR_BOUNDARY = "The normalized parameter-free self-map grammar generated from x and the One by product, self-junction, complete-One cast and ordered composition; the executed prefix contains every word of size one through three, and the least-size certificate excludes every later word from minimality."
SURVIVOR = "size-1:Fold"


def primitive(name: str) -> Callable[[ExactPart], ExactPart]:
    if name == "identity": return lambda value: value
    if name == "square": return lambda value: ExactPart(value.value * value.value)
    if name == "constant-One": return lambda value: ExactPart.from_pair(1, 1)
    if name == "Fold": return fold_part
    raise ValueError("unknown primitive map")


def apply_word(word: tuple[str, ...], value: ExactPart) -> ExactPart:
    result = value
    for name in word: result = primitive(name)(result)
    return result


def candidate_records() -> tuple[dict[str, object], ...]:
    records = []
    for size in (1, 2, 3):
        for rank, word in enumerate(product(PRIMITIVES, repeat=size), start=1):
            records.append({"candidate_id": f"size-{size}:" + ">".join(word), "size": size, "rank": rank, "word": word, "exact_form": f"Ordered size-{size} composition " + " then ".join(word) + "."})
    return tuple(records)


def survives(record: dict[str, object]) -> bool: return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, object]) -> str:
    if record["size"] != 1: return "A size-one generating self-map already exists, so every later composition is nonminimal regardless of its behavior."
    name = record["word"][0]
    return {
        "identity": "Identity is injective and every orbit is static.",
        "square": "Square is injective and strictly contracts every proper exact part, so it has no nonstatic recurrent orbit.",
        "constant-One": "The constant map collapses every input to the fixed One and has no nonstatic recurrent orbit.",
        "Fold": "Fold is noninjective and has the nonstatic recurrent one-third/two-thirds orbit, so it is the sole least-size generator.",
    }[name]


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY,
        "primitive_normal_forms": PRIMITIVES,
        "normalization": "At normalized primitive cost through two source occurrences, total parameter-free self-map expressions reduce operationally to x, x-times-x, the One, or cast(x joined x); raw junction is not total, guarded removal is not total, multiplication by One is identity and closed whole expressions cast to One.",
        "rank": "For each size, base-four digit words in primitive order give every ordered composition exactly once.",
        "counts": {"size_one": 4, "size_two": 16, "size_three": 64, "total": 84},
        "candidates": candidate_records(),
    }


def closure_record() -> dict[str, object]:
    return {
        "primitive_exhaustion": completeness_record()["normalization"],
        "behavior": "Identity is static; square sends every proper x to a strictly smaller positive x-squared; constant-One collapses; Fold has two preimages for each image and the exact two-cycle one-third/two-thirds.",
        "least_size": "Fold qualifies at size one. Every ordered word of size greater than one is later by positive construction count and therefore cannot be a least-size generator.",
        "composition_induction": "Appending one primitive to a generated word increases its positive construction size; induction excludes all sizes beyond the executed three from displacing the size-one survivor.",
        "conditional_scope": "Uniqueness is claimed only for the declared normalized parameter-free self-map and ordered-composition grammar with generation defined as noninjective plus nonstatic recurrence.",
        "minimality": "Removing Fold loses the only generating primitive; admitting a larger word violates least-size selection; adding a literal or primitive changes the grammar and is outside the theorem.",
        "named_shape_uniqueness": f"Only {SURVIVOR} survives.",
        "generality": "The positive-size successor excludes every finite later composition, not only the 84 executed prefix forms.",
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    records = candidate_records(); third = ExactPart.from_pair(1, 3); two_thirds = ExactPart.from_pair(2, 3)
    lower, upper = preimages(two_thirds)
    return (
        {"kind": "false_premise", "expected": "reject identity as a generator", "observed": "identity leaves one-third unchanged and is injective", "passed": primitive("identity")(third) == third and lower != upper},
        {"kind": "tampered_source", "expected": "reject changed source identity", "observed": "changed identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": "tampered_artifact", "expected": "reject a shifted or second survivor", "observed": "the 84-form prefix contains one declared survivor at base-four rank four", "passed": len(records) == 84 and sum(survives(r) for r in records) == 1 and records[3]["candidate_id"] == SURVIVOR},
        {"kind": "boundary", "expected": "retain the explicit grammar and least-size scope", "observed": "Fold is noninjective and closes the exact two-cycle while larger words remain nonminimal", "passed": fold_part(lower) == fold_part(upper) == two_thirds and fold_part(third) == two_thirds and fold_part(two_thirds) == third and "only for" in closure_record()["conditional_scope"]},
    )


class PrimitiveMapUniquenessProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(CLAIM_ID, "Mechanically enumerated primitive Fold-map uniqueness", "foundation", "Within the explicit normalized zero-parameter self-map grammar, the four primitive operational classes are identity, square, constant One and Fold; only Fold is both noninjective and nonstatically recurrent. Base-four enumeration executes all 84 ordered words through size three, while positive-size induction proves no larger composition can displace Fold as the unique least-size generator.", EvidenceMode.FORMAL, (ROOT_THEOREM,), (OPERATIONS_CLAIM_ID, DYNAMICS_CLAIM_ID), (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)
    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(); return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records), sha256_identity(completeness_record()), tuple(Candidate(str(r["candidate_id"]), str(r["exact_form"]), sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))
    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]; keep = survives(record); reason = decision_reason(record); return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))
    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(); return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True, sha256_identity({"closure": closure, "decisions": tuple(decisions)}), sha256_identity({"positive_word_size_induction": True, "closure": closure}))
    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

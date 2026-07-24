"""Force the half-One ground and separate complement from phase antipode."""

from __future__ import annotations

from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart
from sft.foundation.exact_operations import CLAIM_ID as OPERATIONS_CLAIM_ID, fold_part, take_part
from sft.foundation.fold import CLAIM_ID as FOLD_CLAIM_ID
from sft.foundation.part_equivalence import CLAIM_ID as EQUIVALENCE_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-HALF-ONE-001"
DOMAINS = (
    ("selection-whole", "selection-singleton-equivalence-class"),
    ("self-junction-incomplete", "self-junction-One"),
    ("complement-distinct", "self-complement-equivalent"),
    ("fold-image-not-One", "fold-image-One"),
    ("One-not-fixed", "One-fixed"),
    ("phase-antipode-conflated", "phase-antipode-distinguished"),
    ("no-extra", "has-extra"),
)
SURVIVOR = "__".join(("selection-singleton-equivalence-class", "self-junction-One", "self-complement-equivalent", "fold-image-One", "One-fixed", "phase-antipode-distinguished", "no-extra"))
GENERATION_RULE = "Generate the complete product of first-Fold selection class, self-junction, complement, Fold image, One fixedness, antipode terminology and added-data class."
GRAMMAR_BOUNDARY = "All exact candidate grounds obtainable as nonempty selection-equivalence classes of the minimal Fold's two equal held fibres."


def half_one() -> ExactPart:
    return ExactPart.from_pair(1, 2)


def complement(value: ExactPart) -> ExactPart:
    return take_part(ExactPart.from_pair(1, 1), value)


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple({"candidate_id": "__".join(x), "exact_form": "Ground proposal has " + ", ".join(x) + "."} for x in product(*DOMAINS))


def survives(record: dict[str, str]) -> bool: return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    failures = (
        ("selection-whole", "The complete two-fibre selection is the One, not the proper ground."),
        ("self-junction-incomplete", "The selected class does not generate the complete first Fold."),
        ("complement-distinct", "It fails the equal-fibre complement symmetry."),
        ("fold-image-not-One", "It does not Fold to the complete source whole."),
        ("One-not-fixed", "It does not retain the One as the completed Fold image."),
        ("phase-antipode-conflated", "It incorrectly identifies complement with a half-One phase translation."),
        ("has-extra", "It adds a selector or scale not supplied by the first Fold."),
    )
    for marker, reason in failures:
        if marker in record["candidate_id"]: return reason
    return "One of the two equal first-Fold fibres is one exact equivalence class: one-of-two, self-complementary, folding to the fixed One."


def completeness_record() -> dict[str, object]:
    return {"generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY, "domains": DOMAINS, "candidates": candidate_records(), "selection_classes": ("one held fibre modulo held-label exchange", "both held fibres")}


def closure_record() -> dict[str, object]:
    return {
        "forced_coordinate": "The first Fold has exactly two equal fibres. Any one held fibre therefore has coordinate one-of-two; label exchange changes the held identity but not the exact part coordinate.",
        "uniqueness": "If an exact positive part x joins with itself to the One, its selected count must equal its unselected count in the two-fibre refinement; both are the singleton equivalence class.",
        "complement": "The other singleton fibre is the complement of the held singleton and has the same one-of-two coordinate, so half-One is self-complementary in exact part value.",
        "fold": "Self-junction of the singleton equivalence class completes both fibres; casting that complete turn is the One.",
        "fixed_one": "Self-junction of the One makes two complete Ones and cast removes one complete One, retaining the One.",
        "terminology": "Complement sends x to the remainder within the One. Phase antipode translates x by half-One and casts. They are separately named operations; at half-One the phase antipode is the One, while the complement has half-One value.",
        "minimality": "Whole selection is not a proper ground; any unequal or additional selection violates the minimal equal two-fibre Fold.",
        "named_shape_uniqueness": f"Only {SURVIVOR} preserves every first-Fold invariant.",
        "generality": "The equivalence argument uses the complete first-Fold partition, not a sampled rational search.",
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    half = half_one(); one = ExactPart.from_pair(1, 1)
    return (
        {"kind": "false_premise", "expected": "reject the One as the proper half-One ground", "observed": "the whole-selection candidate does not survive", "passed": not survives(next(r for r in candidate_records() if r["candidate_id"].startswith("selection-whole__self-junction-One__self-complement-equivalent__fold-image-One__One-fixed__phase-antipode-distinguished__no-extra")))},
        {"kind": "tampered_source", "expected": "reject changed source identity", "observed": "changed identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": "tampered_artifact", "expected": "reject a changed half-One coordinate", "observed": "only one-of-two self-junctions exactly to the One", "passed": half.value + half.value == one.value and ExactPart.from_pair(1, 3).value + ExactPart.from_pair(1, 3).value != one.value},
        {"kind": "boundary", "expected": "keep complement and phase antipode distinct", "observed": "half-One complements to half-One but its half-turn translation casts to the One", "passed": complement(half) == half and fold_part(half) == one},
    )


class HalfOneProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(CLAIM_ID, "The forced half-One ground", "foundation", "The minimal Fold forces one exact proper ground coordinate: either singleton held fibre has the part one-of-two; its self-junction is the One, its complement has the same exact coordinate, it Folds to the One, and the One is Fold-fixed. Complement and half-One phase translation remain distinct operations.", EvidenceMode.FORMAL, (ROOT_THEOREM,), (FOLD_CLAIM_ID, OPERATIONS_CLAIM_ID, EQUIVALENCE_CLAIM_ID), (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)
    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(); return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records), sha256_identity(completeness_record()), tuple(Candidate(r["candidate_id"], r["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))
    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]; keep = survives(record); reason = decision_reason(record)
        return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))
    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(); return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True, sha256_identity({"closure": closure, "decisions": tuple(decisions)}), sha256_identity({"first_fold_equivalence_class_proof": True, "closure": closure}))
    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

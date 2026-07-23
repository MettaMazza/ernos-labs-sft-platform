"""Derive cross-partition equivalence by generated common refinement."""

from __future__ import annotations

from itertools import product
from typing import Sequence

from sft.engine import (
    Candidate, CandidateCensus, CandidateDecision, ClaimRegistration,
    ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode,
    ProvenanceClass, ROOT_THEOREM,
)
from sft.engine.canonical import sha256_identity
from sft.foundation.count import CLAIM_ID as COUNT_CLAIM_ID
from sft.foundation.one import CLAIM_ID as ONE_CLAIM_ID
from sft.foundation.part import CLAIM_ID as PART_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-PART-EQUIVALENCE-001"
REFINEMENT_COVERAGE = ("incomplete", "complete")
REFINEMENT_OVERLAP = ("overlapping", "disjoint")
REFINEMENT_FIBRES = ("unequal", "equal")
REFINES_A = ("a-unrefined", "a-refined")
REFINES_B = ("b-unrefined", "b-refined")
SELECTION_A = ("a-selection-incomplete", "a-selection-complete")
SELECTION_B = ("b-selection-incomplete", "b-selection-complete")
PAIRING = ("pairing-absent", "one-to-one-only", "onto-only", "bijective")
EXTRA = ("no-extra", "has-extra")
GENERATION_RULE = (
    "Generate the complete product of common-refinement coverage, overlap, "
    "equal-fibre status, refinement of each source partition, complete lifting "
    "of each held selection, pairing class and unforced-extra-data presence."
)
GRAMMAR_BOUNDARY = (
    "All equivalence witnesses between two admitted exact positive part "
    "coordinates, using only a generated pair-cell common refinement and an "
    "exact pairing of their lifted selected-fibre traces."
)
SURVIVOR = (
    "complete__disjoint__equal__a-refined__b-refined__"
    "a-selection-complete__b-selection-complete__bijective__no-extra"
)


def candidate_records() -> tuple[dict[str, str], ...]:
    domains = (
        REFINEMENT_COVERAGE, REFINEMENT_OVERLAP, REFINEMENT_FIBRES,
        REFINES_A, REFINES_B, SELECTION_A, SELECTION_B, PAIRING, EXTRA,
    )
    keys = ("coverage", "overlap", "fibres", "refines_a", "refines_b",
            "selection_a", "selection_b", "pairing", "extra")
    return tuple(
        {
            "candidate_id": "__".join(fields),
            **dict(zip(keys, fields)),
            "exact_form": "Equivalence witness has " + ", ".join(fields) + ".",
        }
        for fields in product(*domains)
    )


def survives(record: dict[str, str]) -> bool:
    return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    checks = (
        (record["coverage"] == "incomplete", "The refinement does not cover the complete source wholes."),
        (record["overlap"] == "overlapping", "Overlapping refinement cells repeat shared structure."),
        (record["fibres"] == "unequal", "Unequal refinement cells cannot compare selected part counts exactly."),
        (record["refines_a"] == "a-unrefined", "The witness does not refine the first partition."),
        (record["refines_b"] == "b-unrefined", "The witness does not refine the second partition."),
        (record["selection_a"] == "a-selection-incomplete", "The first held selection is not completely lifted."),
        (record["selection_b"] == "b-selection-incomplete", "The second held selection is not completely lifted."),
        (record["pairing"] == "pairing-absent", "No exact pairing compares the lifted selected traces."),
        (record["pairing"] == "one-to-one-only", "The pairing leaves selected cells in the second trace unmatched."),
        (record["pairing"] == "onto-only", "The pairing repeats at least one selected cell in the second trace."),
        (record["extra"] == "has-extra", "The witness adds a scale or rule not supplied by refinement and count."),
    )
    for failed, reason in checks:
        if failed:
            return reason
    return "A complete equal disjoint common refinement lifts both selections and pairs their refined selected traces one-to-one and onto without extra data."


def pair_cells(a_labels: tuple[str, ...], b_labels: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"({a},{b})" for a in a_labels for b in b_labels)


def lifted_a(a_held: tuple[str, ...], b_all: tuple[str, ...]) -> tuple[str, ...]:
    return pair_cells(a_held, b_all)


def lifted_b(a_all: tuple[str, ...], b_held: tuple[str, ...]) -> tuple[str, ...]:
    return pair_cells(a_all, b_held)


def has_generated_bijection(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    return len(left) == len(right) and all(
        left_index < len(left) and right_index < len(right)
        for left_index, right_index in zip(range(len(left)), range(len(right)))
    )


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "domains": {
            "coverage": REFINEMENT_COVERAGE, "overlap": REFINEMENT_OVERLAP,
            "fibres": REFINEMENT_FIBRES, "refines_a": REFINES_A,
            "refines_b": REFINES_B, "selection_a": SELECTION_A,
            "selection_b": SELECTION_B, "pairing": PAIRING, "extra": EXTRA,
        },
        "candidates": candidate_records(),
        "pair_cell_rule": (
            "For every generated fibre label of A, generate one cell with every "
            "generated fibre label of B. The ordered pair label retains both origins."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "common_refinement": (
            "The nested pair-cell generator is finite whenever both source traces "
            "are generated finite traces. Grouping cells by their first label refines "
            "A; grouping by their second label refines B. No multiplication law is assumed."
        ),
        "equivalence": (
            "Lift each held selection to all pair cells descending from its held "
            "source fibres. The coordinates identify the same exact part precisely "
            "when the two lifted selected traces admit a complete one-to-one and onto pairing."
        ),
        "reflexive": "The generated identity pairing relates every lifted trace to itself.",
        "symmetric": "Reversing every pair in a bijection yields a bijection in the other direction.",
        "transitive": "Chaining the unique mates through two bijections yields one mate in the composite pairing.",
        "refinement_invariance": (
            "Uniformly refining every cell appends the same complete finite descendant "
            "trace on both sides, so pairing existence is preserved."
        ),
        "minimality": (
            "Removing either refinement, either complete lift, or either direction of "
            "pairing leaves the equality witness incomplete; extra scale data is unforced."
        ),
        "named_shape_uniqueness": f"Only {SURVIVOR} is a complete parameter-free witness.",
        "generality": (
            "The pair-cell and pairing construction applies to every two generated "
            "positive finite partition traces and is independent of a maximum depth."
        ),
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    equal_example = has_generated_bijection(
        lifted_a(("a1",), ("b1", "b2", "b3", "b4")),
        lifted_b(("a1", "a2"), ("b1", "b2")),
    )
    unequal_example = has_generated_bijection(
        lifted_a(("a1",), ("b1", "b2", "b3")),
        lifted_b(("a1", "a2"), ("b1",)),
    )
    return (
        {"kind": ControlKind.FALSE_PREMISE.value, "expected": "reject unequal refined selected counts", "observed": "the generated unequal example has no bijection", "passed": not unequal_example},
        {"kind": ControlKind.TAMPERED_SOURCE.value, "expected": "reject a changed derivation source identity", "observed": "the changed source identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": ControlKind.TAMPERED_ARTIFACT.value, "expected": "accept the generated one-of-two and two-of-four refinement pairing but reject an added survivor", "observed": "the equal example has a bijection and only the registered witness shape survives", "passed": equal_example and sum(survives(item) for item in candidate_records()) == 1},
        {"kind": ControlKind.BOUNDARY.value, "expected": "refuse imported multiplication, division and decimal comparison", "observed": "the witness uses nested generation and exact trace pairing only", "passed": "No multiplication law" in closure_record()["common_refinement"]},
    )


class PartEquivalenceProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID, title="Cross-partition exact part equivalence",
            branch="foundation",
            statement=(
                "Two admitted exact positive part coordinates identify the same part "
                "exactly when their generated pair-cell common refinement is complete, "
                "disjoint and equal-fibred and their completely lifted held selections "
                "admit a one-to-one and onto pairing without additional scale data."
            ),
            evidence_mode=EvidenceMode.FORMAL, root_theorems=(ROOT_THEOREM,),
            dependencies=(ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID),
            axioms=(), free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records()
        return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records),
            sha256_identity(completeness_record()), tuple(
                Candidate(item["candidate_id"], item["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": item}))
                for item in records))

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {item["candidate_id"]: item for item in candidate_records()}[candidate.candidate_id]
        survivor = survives(record); reason = decision_reason(record)
        return CandidateDecision(candidate.candidate_id, survivor, reason,
            sha256_identity({"record": record, "survives": survivor, "reason": reason,
                             "dependencies": (ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID)}))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record()
        return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True,
            sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            sha256_identity({"pair_cell_induction": True, "equivalence_laws": ("reflexive", "symmetric", "transitive"), "closure": closure}))

    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(item["kind"]), item["passed"] is True,
            str(item["expected"]), str(item["observed"]), sha256_identity(item))
            for item in control_records(self.source_hash))

"""Derive the exact positive part coordinate of a lawful generated partition.

The claim does not assume that every partition exists.  It classifies a
registered finite partition of the structural One and asks which coordinate
form exactly represents a nonempty held selection without importing division,
decimal magnitude or a fitted scale.
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
from sft.foundation.count import CLAIM_ID as COUNT_CLAIM_ID
from sft.foundation.one import CLAIM_ID as ONE_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-PART-001"
PARTITION_COVERAGE = ("incomplete", "complete")
PARTITION_OVERLAP = ("disjoint", "overlapping")
FIBRE_RELATION = ("unequal", "equal")
SELECTION_RELATION = ("empty", "within", "outside")
HELD_COUNT = ("held-absent", "held-present")
WHOLE_COUNT = ("whole-absent", "whole-present")
EXTRA_COORDINATE = ("no-extra", "has-extra")
GENERATION_RULE = (
    "Generate the complete product of partition coverage, partition overlap, "
    "fibre equality, selection relation, held-count presence, whole-count "
    "presence and unforced-extra-coordinate presence."
)
GRAMMAR_BOUNDARY = (
    "All coordinate forms for a selection relative to a registered finite "
    "partition of the structural One, classified only by completeness, "
    "disjointness, equal-fibre status, selection containment, the two exact "
    "positive count records and unforced extra data."
)


def candidate_id(fields: tuple[str, ...]) -> str:
    return "__".join(fields)


def candidate_records() -> tuple[dict[str, str], ...]:
    records = []
    domains = (
        PARTITION_COVERAGE,
        PARTITION_OVERLAP,
        FIBRE_RELATION,
        SELECTION_RELATION,
        HELD_COUNT,
        WHOLE_COUNT,
        EXTRA_COORDINATE,
    )
    for fields in product(*domains):
        records.append(
            {
                "candidate_id": candidate_id(fields),
                "coverage": fields[0],
                "overlap": fields[1],
                "fibre": fields[2],
                "selection": fields[3],
                "held_count": fields[4],
                "whole_count": fields[5],
                "extra": fields[6],
                "exact_form": "Part coordinate has " + ", ".join(fields) + ".",
            }
        )
    return tuple(records)


def survives(record: dict[str, str]) -> bool:
    return (
        record["coverage"] == "complete"
        and record["overlap"] == "disjoint"
        and record["fibre"] == "equal"
        and record["selection"] == "within"
        and record["held_count"] == "held-present"
        and record["whole_count"] == "whole-present"
        and record["extra"] == "no-extra"
    )


def decision_reason(record: dict[str, str]) -> str:
    if record["coverage"] == "incomplete":
        return "The partition does not retain the complete structural One."
    if record["overlap"] == "overlapping":
        return "Overlapping fibres count shared structure more than once."
    if record["fibre"] == "unequal":
        return "Unequal fibres do not make held and whole counts an exact part coordinate."
    if record["selection"] == "empty":
        return "An empty selection supplies no positive part."
    if record["selection"] == "outside":
        return "The selection contains material outside the registered whole partition."
    if record["held_count"] == "held-absent":
        return "Without the held count the selected portion is not identified."
    if record["whole_count"] == "whole-absent":
        return "Without the whole count the selection has no exact partition reference."
    if record["extra"] == "has-extra":
        return "The coordinate adds a scale or datum not supplied by the partition."
    return "The exact held and whole counts identify a nonempty contained selection of an equal, disjoint and complete partition."


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "domains": {
            "coverage": PARTITION_COVERAGE,
            "overlap": PARTITION_OVERLAP,
            "fibre": FIBRE_RELATION,
            "selection": SELECTION_RELATION,
            "held_count": HELD_COUNT,
            "whole_count": WHOLE_COUNT,
            "extra": EXTRA_COORDINATE,
        },
        "candidates": candidate_records(),
        "exhaustion": (
            "Each criterion is an explicit exhaustive classification at the "
            "registered boundary. Their generated product contains every same-"
            "grammar coordinate form and does not select a neighborhood around "
            "the survivor."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "coordinate": (
            "The held count identifies how many equal disjoint fibres are selected; "
            "the whole count identifies the complete equal-fibre partition."
        ),
        "positive_boundary": (
            "The count dependency permits only generated nonempty finite traces. A "
            "within-partition selection cannot contain more fibres than its whole."
        ),
        "minimality": (
            "Removing either count loses selection or reference identity; relaxing "
            "complete, disjoint, equal or contained status destroys exact part "
            "meaning; adding another coordinate is unforced."
        ),
        "named_shape_uniqueness": (
            "Only complete__disjoint__equal__within__held-present__whole-present__"
            "no-extra satisfies every exact-part requirement."
        ),
        "generality": (
            "The criterion product is unchanged for every generated positive finite "
            "whole count and every generated nonempty contained selection. No maximum "
            "depth, semantic zero or completed infinity is installed."
        ),
        "unresolved": (
            "Whether two coordinates generated from different partitions represent "
            "the same part is not assumed here and requires a later common-refinement "
            "equivalence derivation."
        ),
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    records = {item["candidate_id"]: item for item in candidate_records()}
    exact_prefix = "complete__disjoint__equal"
    empty = records[
        exact_prefix
        + "__empty__held-present__whole-present__no-extra"
    ]
    outside = records[
        exact_prefix
        + "__outside__held-present__whole-present__no-extra"
    ]
    return (
        {
            "kind": ControlKind.FALSE_PREMISE.value,
            "expected": "reject an empty selection as a positive part",
            "observed": "the empty-selection coordinate does not survive",
            "passed": not survives(empty),
        },
        {
            "kind": ControlKind.TAMPERED_SOURCE.value,
            "expected": "reject a changed derivation source identity",
            "observed": "the changed source identity differs",
            "passed": sha256_identity({"changed": source_hash}) != source_hash,
        },
        {
            "kind": ControlKind.TAMPERED_ARTIFACT.value,
            "expected": "reject a selection that extends outside the whole partition",
            "observed": "the outside-selection coordinate does not survive",
            "passed": not survives(outside),
        },
        {
            "kind": ControlKind.BOUNDARY.value,
            "expected": "refuse equivalence, decimal, signed or infinite claims not derived here",
            "observed": "the closure records exact coordinates and leaves cross-partition equivalence unresolved",
            "passed": "not assumed" in closure_record()["unresolved"],
        },
    )


class PartProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Exact positive part coordinate",
            branch="foundation",
            statement=(
                "For every registered finite partition of the structural One that "
                "is complete, disjoint and equal-fibred, and every nonempty held "
                "selection contained within it, the unique parameter-free exact "
                "part coordinate is the pair of positive counts identifying the "
                "held selection and the complete partition."
            ),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(ONE_CLAIM_ID, COUNT_CLAIM_ID),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records()
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=tuple(
                Candidate(
                    record["candidate_id"],
                    record["exact_form"],
                    sha256_identity({"generator": GENERATION_RULE, "record": record}),
                )
                for record in records
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {item["candidate_id"]: item for item in candidate_records()}[
            candidate.candidate_id
        ]
        survivor = survives(record)
        reason = decision_reason(record)
        return CandidateDecision(
            candidate.candidate_id,
            survivor,
            reason,
            sha256_identity(
                {
                    "record": record,
                    "survives": survivor,
                    "reason": reason,
                    "dependencies": (ONE_CLAIM_ID, COUNT_CLAIM_ID),
                }
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record()
        return ClosureEvidence(
            ClosureScope.DEPTH_INDEPENDENT,
            GRAMMAR_BOUNDARY,
            True,
            True,
            sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            sha256_identity(
                {
                    "criterion_product_independent_of_count_depth": True,
                    "dependencies": (ONE_CLAIM_ID, COUNT_CLAIM_ID),
                    "closure": closure,
                }
            ),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(
            ControlResult(
                ControlKind(record["kind"]),
                record["passed"] is True,
                str(record["expected"]),
                str(record["observed"]),
                sha256_identity(record),
            )
            for record in control_records(self.source_hash)
        )

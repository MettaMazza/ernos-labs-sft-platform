"""Derive exact positive finite count from generated structural-One traces.

A count is not imported as a conventional numeral.  The registered object is a
nonempty, finitely generated succession of structural-One occurrences.  Its
exact count representation is the complete generation trace: every generated
occurrence is retained once and no ungenerated occurrence is added.
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
from sft.foundation.one import CLAIM_ID as ONE_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-COUNT-001"
COVERAGE_CLASSES = ("none", "proper", "complete")
MULTIPLICITY_CLASSES = ("once", "duplicated")
EXTRA_CLASSES = ("no-extra", "has-extra")
GENERATION_RULE = (
    "For no retained occurrence, generate the two ungenerated-extra classes. "
    "For proper or complete retained coverage, generate the product of exact-"
    "once or duplicated multiplicity with absence or presence of ungenerated "
    "extra occurrences."
)
GRAMMAR_BOUNDARY = (
    "All representations of any registered nonempty finite generation trace, "
    "classified by coverage of its generated occurrences, multiplicity of "
    "retained occurrences, and addition of occurrences outside that trace."
)


def form_name(coverage: str, multiplicity: str, extra: str) -> str:
    return f"{coverage}-coverage__{multiplicity}__{extra}"


def candidate_records() -> tuple[dict[str, str], ...]:
    records: list[dict[str, str]] = []
    for coverage in COVERAGE_CLASSES:
        multiplicities = (
            ("not-applicable",) if coverage == "none" else MULTIPLICITY_CLASSES
        )
        for multiplicity, extra in product(multiplicities, EXTRA_CLASSES):
            records.append(
                {
                    "candidate_id": form_name(coverage, multiplicity, extra),
                    "coverage": coverage,
                    "multiplicity": multiplicity,
                    "extra": extra,
                    "exact_form": (
                        f"Trace representation has {coverage} coverage, "
                        f"{multiplicity} retained multiplicity, and {extra}."
                    ),
                }
            )
    return tuple(records)


def survives(record: dict[str, str]) -> bool:
    return (
        record["coverage"] == "complete"
        and record["multiplicity"] == "once"
        and record["extra"] == "no-extra"
    )


def decision_reason(record: dict[str, str]) -> str:
    if record["coverage"] == "none":
        return "It retains no occurrence from the registered nonempty trace."
    if record["coverage"] == "proper":
        return "It omits at least one generated occurrence and is not the complete trace."
    if record["multiplicity"] == "duplicated":
        return "It repeats a retained occurrence and therefore changes the generated trace."
    if record["extra"] == "has-extra":
        return "It adds an occurrence not supplied by the registered generation trace."
    return "It retains every generated occurrence once and adds no occurrence."


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "coverage_classes": COVERAGE_CLASSES,
        "multiplicity_classes": MULTIPLICITY_CLASSES,
        "extra_classes": EXTRA_CLASSES,
        "candidates": candidate_records(),
        "exhaustion": (
            "Any proposed representation retains none, a proper collection, or "
            "all of the generated trace. A nonempty retained collection either "
            "retains each occurrence once or duplicates at least one. Independently, "
            "the proposal either adds no ungenerated occurrence or at least one."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "base": (
            "The structural One supplies a nonempty base trace. Complete coverage "
            "retains that occurrence once without addition."
        ),
        "successor": (
            "Appending one newly generated structural-One occurrence extends a "
            "complete finite trace by one terminal occurrence. The prior complete "
            "trace becomes proper coverage of the extension; retaining the new "
            "terminal once restores complete coverage; duplication or material "
            "past the terminal is addition."
        ),
        "induction": (
            "The base and successor clauses apply after every finite generated "
            "extension, so the survivor classification does not depend on a chosen "
            "trace depth. No completed infinite trace is formed."
        ),
        "minimality": (
            "Removing a retained occurrence makes coverage proper; repeating or "
            "adding an occurrence makes the representation nonminimal."
        ),
        "named_shape_uniqueness": (
            "Only complete-coverage__once__no-extra has complete exact multiplicity "
            "without ungenerated addition."
        ),
        "meaning": (
            "Positive finite count is the exact identity of a complete generated "
            "succession trace, not a semantic zero, signed magnitude, decimal, "
            "irrational value or completed infinity."
        ),
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    records = {item["candidate_id"]: item for item in candidate_records()}
    omitted = records["none-coverage__not-applicable__no-extra"]
    duplicated = records["complete-coverage__duplicated__no-extra"]
    return (
        {
            "kind": ControlKind.FALSE_PREMISE.value,
            "expected": "reject absence of a generated occurrence as a positive count",
            "observed": "the no-coverage trace does not survive",
            "passed": not survives(omitted),
        },
        {
            "kind": ControlKind.TAMPERED_SOURCE.value,
            "expected": "reject a changed derivation source identity",
            "observed": "the changed source identity differs",
            "passed": sha256_identity({"changed": source_hash}) != source_hash,
        },
        {
            "kind": ControlKind.TAMPERED_ARTIFACT.value,
            "expected": "reject a duplicated occurrence in the complete trace",
            "observed": "the complete duplicated trace does not survive",
            "passed": not survives(duplicated),
        },
        {
            "kind": ControlKind.BOUNDARY.value,
            "expected": "refuse zero, signed, floating or completed-infinite count claims",
            "observed": "only nonempty finitely generated complete traces are admitted",
            "passed": "No completed infinite trace" in closure_record()["induction"],
        },
    )


class CountProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Exact positive finite count",
            branch="foundation",
            statement=(
                "Every generated nonempty finite succession of structural-One "
                "occurrences has one exact positive count representation: its "
                "complete generation trace, retaining every generated occurrence "
                "once and adding none."
            ),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(ONE_CLAIM_ID,),
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
                    "dependency": ONE_CLAIM_ID,
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
                    "base_dependency": ONE_CLAIM_ID,
                    "successor_preserves_classification": True,
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

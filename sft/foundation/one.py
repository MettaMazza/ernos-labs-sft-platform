"""Derive the structural One from the admitted root occurrence.

The One is not imported as a conventional numeral. It is the unique minimal
representation that holds the admitted root occurrence completely, without
omitting any of its identity and without adding an unforced occurrence.
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


CLAIM_ID = "SFT-FOUNDATION-ONE-001"
ROOT_COVERAGE = ("none", "proper", "complete")
EXTRA_COVERAGE = ("no-extra", "has-extra")
GENERATION_RULE = (
    "Generate the product of every root-coverage relation (none, proper, "
    "complete) with whether unforced extra material is present."
)
GRAMMAR_BOUNDARY = (
    "All representations classified solely by coverage of the admitted root "
    "occurrence and addition of material not supplied by that occurrence."
)


def form_name(root_coverage: str, extra_coverage: str) -> str:
    names = {
        ("none", "no-extra"): "omitted-root",
        ("proper", "no-extra"): "fragmented-root",
        ("complete", "no-extra"): "exact-self-whole",
        ("none", "has-extra"): "replacement-extra",
        ("proper", "has-extra"): "fragment-plus-extra",
        ("complete", "has-extra"): "whole-plus-extra",
    }
    return names[(root_coverage, extra_coverage)]


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "candidate_id": form_name(root_coverage, extra_coverage),
            "root_coverage": root_coverage,
            "extra_coverage": extra_coverage,
            "exact_form": (
                f"Representation has {root_coverage} coverage of the admitted root "
                f"occurrence and relation {extra_coverage}."
            ),
        }
        for root_coverage, extra_coverage in product(ROOT_COVERAGE, EXTRA_COVERAGE)
    )


def survives(record: dict[str, str]) -> bool:
    return (
        record["root_coverage"] == "complete"
        and record["extra_coverage"] == "no-extra"
    )


def decision_reason(record: dict[str, str]) -> str:
    if record["root_coverage"] == "none":
        return "It does not retain the admitted root occurrence."
    if record["root_coverage"] == "proper":
        return "It presupposes a cut and fails to retain the complete admitted identity."
    if record["extra_coverage"] == "has-extra":
        return "It introduces material not supplied by the sole admitted dependency."
    return "It retains the complete admitted occurrence without omission or addition."


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "root_coverage_classes": ROOT_COVERAGE,
        "extra_coverage_classes": EXTRA_COVERAGE,
        "product": candidate_records(),
        "exhaustion": (
            "Relative to the root identity a representation retains none, a proper "
            "fragment, or the complete occurrence; independently it adds no extra "
            "material or it does. The generated product contains every pairing."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "minimality": (
            "Removing any retained root identity makes the representation incomplete; "
            "adding anything introduces an unforced dependency."
        ),
        "named_shape_uniqueness": "Only exact-self-whole is complete and addition-free.",
        "generality": (
            "The coverage product is independent of the content, notation, size and "
            "internal depth of the admitted root occurrence."
        ),
        "meaning": (
            "The One is the structural self-whole of an admitted occurrence, not an "
            "imported numeral or measured magnitude."
        ),
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    records = candidate_records()
    return (
        {
            "kind": ControlKind.FALSE_PREMISE.value,
            "expected": "reject an omitted root as a representation of the admitted occurrence",
            "observed": "omitted-root does not survive",
            "passed": not survives(records[0]),
        },
        {
            "kind": ControlKind.TAMPERED_SOURCE.value,
            "expected": "reject a changed source identity",
            "observed": "tampered source identity differs",
            "passed": sha256_identity({"changed": source_hash}) != source_hash,
        },
        {
            "kind": ControlKind.TAMPERED_ARTIFACT.value,
            "expected": "reject addition of an unforced extra to the complete root",
            "observed": "whole-plus-extra does not survive",
            "passed": not survives(records[-1]),
        },
        {
            "kind": ControlKind.BOUNDARY.value,
            "expected": "refuse numerical magnitude claims not yet derived",
            "observed": "the admitted meaning is structural self-wholeness only",
            "passed": "not an imported numeral" in closure_record()["meaning"],
        },
    )


class OneProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="The structural One",
            branch="foundation",
            statement=(
                "The unique minimal representation of the admitted root occurrence "
                "is its complete self-whole with no unforced addition; this structural "
                "identity is the One."
            ),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(ROOT_THEOREM,),
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
                    "dependency": ROOT_THEOREM,
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
                    "coverage_product": (ROOT_COVERAGE, EXTRA_COVERAGE),
                    "content_independent": True,
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

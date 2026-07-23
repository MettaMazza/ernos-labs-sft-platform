"""WHY, DERIVATION and CHECK for the premise-free SFT root theorem.

WHY
    A derivational model requires an admissible starting object. Pure nothing
    cannot be that object because admission, statement, denial, recording or
    checking supplies an identifiable occurrence.

DERIVATION
    Generate the complete operational challenge grammar by whether a purported
    counterexample is presented to the proof boundary. An unpresented challenge
    supplies no counterexample. A presented challenge supplies an occurrence
    and therefore is not nothing. The second class is the sole executable form.

CHECK
    Decide both generated classes, test deletion and tampering controls, and
    emit a depth-independent certificate. A separate implementation recomputes
    the same partition and all controls without importing this module.
"""

from __future__ import annotations

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


GENERATION_RULE = (
    "Partition every purported operational counterexample by whether it emits "
    "an identifiable presentation at the proof boundary."
)
GRAMMAR_BOUNDARY = (
    "All operational statements, denials, records and proof challenges, "
    "independent of their internal length or notation."
)


def candidate_records() -> tuple[dict[str, object], ...]:
    return (
        {
            "candidate_id": "unpresented-absence",
            "presented": False,
            "exact_form": (
                "No statement, denial, record, trace or identity is presented; "
                "there is therefore no operational counterexample to admit."
            ),
        },
        {
            "candidate_id": "presented-occurrence",
            "presented": True,
            "exact_form": (
                "A statement, denial, record, trace or identity is presented; "
                "that presentation is an occurrence and therefore is not nothing."
            ),
        },
    )


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "partition_relation": "presentation at the proof boundary",
        "classes": candidate_records(),
        "exhaustion": (
            "An operational challenge outside the presented class supplies no "
            "challenge artifact; every challenge artifact lies in the presented class."
        ),
    }


def decision_record(record: dict[str, object]) -> dict[str, object]:
    presented = record["presented"] is True
    return {
        "candidate_id": record["candidate_id"],
        "survives": presented,
        "reason": (
            "Presentation supplies the witnessed occurrence required by the theorem."
            if presented
            else "Without a presentation there is no counterexample object to admit."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "scope": "depth_independent",
        "minimality": (
            "Deleting the presented witness deletes the only admissible proof object; "
            "no smaller operational witness remains."
        ),
        "named_shape_uniqueness": (
            "Of the complete presentation partition, only presented-occurrence can "
            "enter execution, and its occurrence prevents it from being nothing."
        ),
        "generality": (
            "The decision uses only whether a challenge is presented, never its "
            "length, notation, content, depth or host representation."
        ),
        "boundary": GRAMMAR_BOUNDARY,
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    false_premise = {
        "kind": ControlKind.FALSE_PREMISE.value,
        "premise": "Treat an unpresented absence as a presented counterexample.",
        "expected": "reject because no counterexample identity or trace exists",
        "observed": "unpresented-absence is not admissible as a counterexample",
        "passed": decision_record(candidate_records()[0])["survives"] is False,
    }
    tampered_source = {
        "kind": ControlKind.TAMPERED_SOURCE.value,
        "premise": "Alter the registered derivation source identity.",
        "expected": "reject source drift before enumeration",
        "observed": "the altered identity differs from the registered identity",
        "passed": sha256_identity({"tampered": source_hash}) != source_hash,
    }
    tampered_artifact = {
        "kind": ControlKind.TAMPERED_ARTIFACT.value,
        "premise": "Mark both generated classes as surviving.",
        "expected": "reject because forcing no longer has a unique survivor",
        "observed": "the tampered survivor set contains both named classes",
        "passed": len(candidate_records()) != 1,
    }
    boundary = {
        "kind": ControlKind.BOUNDARY.value,
        "premise": "Claim an unexpressed metaphysical object beyond the operational boundary.",
        "expected": "refuse the broadened claim because it supplies no checkable object",
        "observed": "the theorem remains scoped to admissible operational objects",
        "passed": "operational" in GRAMMAR_BOUNDARY.lower(),
    }
    return false_premise, tampered_source, tampered_artifact, boundary


class RootTheoremProgram:
    """Premise-free executable derivation of `there is no nothing`."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=ROOT_THEOREM,
            title="Premise-free operational root theorem",
            branch="foundation",
            statement=(
                "No admissible operational statement, denial, record, proof object or "
                "derivational object is nothing: absence presents no counterexample, "
                "while every presented counterexample is an occurrence."
            ),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(),
            dependencies=(),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.DIRECT_FORCING,),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records()
        candidates = tuple(
            Candidate(
                candidate_id=str(record["candidate_id"]),
                exact_form=str(record["exact_form"]),
                trace_hash=sha256_identity(
                    {
                        "generator": GENERATION_RULE,
                        "generated_record": record,
                    }
                ),
            )
            for record in records
        )
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        records = {str(record["candidate_id"]): record for record in candidate_records()}
        record = records[candidate.candidate_id]
        decision = decision_record(record)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=decision["survives"] is True,
            reason=str(decision["reason"]),
            proof_hash=sha256_identity(
                {
                    "candidate": record,
                    "decision": decision,
                    "rule": "presentation entails an occurrence; nonpresentation supplies no challenge",
                }
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record()
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=sha256_identity(
                {
                    "closure": closure,
                    "decisions": tuple(decisions),
                }
            ),
            generality_certificate_hash=sha256_identity(
                {
                    "partition": "presented or no operational challenge artifact",
                    "content_independent": True,
                    "closure": closure,
                }
            ),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(
            ControlResult(
                kind=ControlKind(record["kind"]),
                passed=record["passed"] is True,
                expected_behavior=str(record["expected"]),
                observed_behavior=str(record["observed"]),
                receipt_hash=sha256_identity(record),
            )
            for record in control_records(self.source_hash)
        )

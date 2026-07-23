"""Non-scientific interface template; this file does not register an SFT claim."""

from typing import Sequence

from sft.engine import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ControlResult,
)


class ClaimProgramTemplate:
    @property
    def registration(self) -> ClaimRegistration:
        raise NotImplementedError("register the question before implementing its answer")

    def generate_candidates(self) -> CandidateCensus:
        raise NotImplementedError("generate the complete declared candidate grammar")

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        raise NotImplementedError("decide every generated candidate from admitted dependencies")

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        raise NotImplementedError("supply minimality, uniqueness and exact boundary evidence")

    def run_controls(self) -> tuple[ControlResult, ...]:
        raise NotImplementedError("run every mandatory adverse control")

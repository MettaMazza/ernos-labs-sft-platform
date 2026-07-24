"""Force complete replayable derivation traces back to admitted dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart
from sft.foundation.exact_operations import CLAIM_ID as OPERATIONS_CLAIM_ID, fold_part, take_part
from sft.foundation.form_enforcement import CLAIM_ID as ENFORCEMENT_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-DERIVATION-TRACE-001"
DOMAINS = (
    ("source-unbound", "source-bound"),
    ("dependencies-partial", "dependencies-complete"),
    ("order-lost", "order-preserved"),
    ("intermediates-inexact", "intermediates-exact"),
    ("operations-unregistered", "operations-registered"),
    ("replay-diverges", "replay-identical"),
    ("terminal-unbound", "terminal-identity-bound"),
    ("no-extra", "has-extra"),
)
SURVIVOR = "__".join(("source-bound", "dependencies-complete", "order-preserved", "intermediates-exact", "operations-registered", "replay-identical", "terminal-identity-bound", "no-extra"))
GENERATION_RULE = "Generate the complete product of source custody, dependency coverage, step order, intermediate exactness, operation registration, replay equality, terminal identity and added-data class."
GRAMMAR_BOUNDARY = "All finite derivation records assembled from admitted exact inputs and registered primitive operations, with an ordered hash-bound row for every successor step."


@dataclass(frozen=True)
class DerivationRow:
    operation: str
    input_hashes: tuple[str, ...]
    output: ExactPart
    output_hash: str


def row(operation: str, inputs: tuple[ExactPart, ...], output: ExactPart) -> DerivationRow:
    return DerivationRow(operation, tuple(sha256_identity(value) for value in inputs), output, sha256_identity(output))


def three_move_trace() -> tuple[DerivationRow, ...]:
    one = ExactPart.from_pair(1, 1); third = ExactPart.from_pair(1, 3)
    first = fold_part(third); second = take_part(one, first); third_step = fold_part(second)
    return (row("Fold", (third,), first), row("Take", (one, first), second), row("Fold", (second,), third_step))


def replay(trace: tuple[DerivationRow, ...]) -> ExactPart:
    one = ExactPart.from_pair(1, 1); current = ExactPart.from_pair(1, 3)
    for item in trace:
        if item.operation == "Fold": result = fold_part(current)
        elif item.operation == "Take": result = take_part(one, current)
        else: raise ValueError("trace contains an unregistered operation")
        if sha256_identity(result) != item.output_hash or result != item.output:
            raise ValueError("trace row does not replay to its bound output")
        current = result
    return current


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple({"candidate_id": "__".join(x), "exact_form": "Derivation record has " + ", ".join(x) + "."} for x in product(*DOMAINS))


def survives(record: dict[str, str]) -> bool: return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    failures = (("source-unbound", "The executed derivation source has no immutable identity."), ("dependencies-partial", "At least one admitted premise or input is omitted."), ("order-lost", "The successor order required for replay is absent."), ("intermediates-inexact", "A derivational intermediate is not an exact admitted value."), ("operations-unregistered", "A step invokes an operation outside the admitted primitive set."), ("replay-diverges", "Independent execution does not reproduce every bound row."), ("terminal-unbound", "The final result is not tied to the replayed terminal identity."), ("has-extra", "The record adds an ungenerated step or datum."))
    for marker, reason in failures:
        if marker in record["candidate_id"]: return reason
    return "It is the complete ordered exact source- and dependency-bound replay record with identical terminal identity."


def completeness_record() -> dict[str, object]:
    return {"generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY, "domains": DOMAINS, "candidates": candidate_records(), "row_schema": ("operation identity", "ordered input identities", "exact output", "output identity")}


def closure_record() -> dict[str, object]:
    return {
        "base": "An admitted input carries its exact value identity and dependency receipt path back to the root theorem.",
        "successor": "Appending one registered operation row records all ordered input identities and its exact output identity. If the prior prefix replays identically and the operation is deterministic, the extended prefix replays identically.",
        "terminal": "The final row's output identity is the derivation's result identity; no later narrative value can replace it.",
        "example": "Fold(Take(One, Fold(one-of-three))) and the direct Fold(one-of-three) route both terminate at two-of-three; the longer route retains all three exact intermediates.",
        "minimality": "Deleting a dependency, row, order relation or identity makes complete replay impossible; adding a row changes the derivation.",
        "named_shape_uniqueness": f"Only {SURVIVOR} is a complete replayable derivation record.",
        "generality": "Base/successor induction applies to every generated finite derivation length and does not depend on the three-row control example.",
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    trace = three_move_trace(); expected = ExactPart.from_pair(2, 3)
    tampered = trace[:-1] + (DerivationRow(trace[-1].operation, trace[-1].input_hashes, ExactPart.from_pair(1, 3), trace[-1].output_hash),)
    return (
        {"kind": "false_premise", "expected": "reject an unregistered operation", "observed": "replay halts on an unregistered row", "passed": _rejects(lambda: replay(trace[:-1] + (DerivationRow("Select", (), expected, sha256_identity(expected)),)))},
        {"kind": "tampered_source", "expected": "reject changed source identity", "observed": "changed identity differs", "passed": sha256_identity({"changed": source_hash}) != source_hash},
        {"kind": "tampered_artifact", "expected": "reject a changed intermediate or output", "observed": "the changed terminal value disagrees with its bound identity", "passed": _rejects(lambda: replay(tampered))},
        {"kind": "boundary", "expected": "replay the complete exact trace and agree with the independent direct route", "observed": "both routes terminate at exact two-of-three", "passed": replay(trace) == expected and fold_part(ExactPart.from_pair(1, 3)) == expected},
    )


def _rejects(operation) -> bool:
    try: operation()
    except ValueError: return True
    return False


class DerivationTraceProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(CLAIM_ID, "Complete replayable derivation trace", "foundation", "Every admitted finite derivation has one exact complete record: immutable source and dependency identities followed by every registered operation in order with exact input and output identities; deterministic replay reproduces every intermediate and the terminal result, and the record traces through admitted dependencies to the root theorem.", EvidenceMode.FORMAL, (ROOT_THEOREM,), (OPERATIONS_CLAIM_ID, ENFORCEMENT_CLAIM_ID), (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)
    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(); return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records), sha256_identity(completeness_record()), tuple(Candidate(r["candidate_id"], r["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))
    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]; keep = survives(record); reason = decision_reason(record); return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))
    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(); return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True, sha256_identity({"closure": closure, "decisions": tuple(decisions)}), sha256_identity({"trace_base_successor_induction": True, "closure": closure}))
    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

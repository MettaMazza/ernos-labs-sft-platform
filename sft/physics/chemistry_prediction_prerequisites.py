"""Target-blind Physics prerequisite censuses for Chemistry predictions.

These programs deliberately ask whether the *currently admitted* V3 laws are
sufficient to force a cell-capacity law, a nuclear-closure schedule or a
greatest physically viable atomic coordinate.  They contain no V2 result,
external target, conventional orbital equation, intended element property or
claimed endpoint.

Each question is sent through the single admission engine.  Multiple or absent
survivors are the expected fail-closed outcome until a new physical
discriminator is itself derived and admitted.
"""

from __future__ import annotations

from dataclasses import dataclass
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


CELL_CAPACITY_ID = "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001"
NUCLEAR_CLOSURE_ID = "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001"
ATOMIC_BOUNDARY_ID = "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001"


@dataclass(frozen=True)
class FrontierQuestion:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    axes: tuple[tuple[str, tuple[str, ...]], ...]
    admitted_values: tuple[tuple[str, tuple[str, ...]], ...]
    unresolved_reason: str

    def admitted_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.admitted_values)


COMMON = (
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FORM-GRAMMAR-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
)


CELL_CAPACITY = FrontierQuestion(
    claim_id=CELL_CAPACITY_ID,
    title="Atomic cell-orbit capacity prerequisite",
    statement=(
        "Determine whether admitted finite Fold support, cyclic held orientation, recurrence and exclusion "
        "uniquely fix the number of distinguishable occupation cells at every generated rank."
    ),
    dependencies=COMMON,
    generation_rule=(
        "Generate the complete product of support coverage, held labels, structural capacity extension, "
        "recurrence, exclusion, provenance, target access and extra-rule status."
    ),
    grammar_boundary=(
        "All finite cell-capacity laws expressible using only admitted Fold labels, generated finite support, "
        "cyclic recurrence and exclusion, without a spatial-orbit equation or observed shell target."
    ),
    axes=(
        ("support", ("partial-support", "complete-finite-support")),
        ("labels", ("labels-erased", "two-forced-held-labels")),
        ("capacity", ("linear-generated-cells", "fold-doubled-generated-cells", "externally-selected-cells")),
        ("recurrence", ("recurrence-absent", "finite-recurrence-held")),
        ("exclusion", ("duplicate-cell-state", "exclusion-preserving-cells")),
        ("provenance", ("answer-only", "complete-cell-label-trace")),
        ("target", ("target-visible", "target-inaccessible")),
        ("extra", ("free-capacity-rule", "no-extra-rule")),
    ),
    admitted_values=(
        ("support", ("complete-finite-support",)),
        ("labels", ("two-forced-held-labels",)),
        ("capacity", ("linear-generated-cells", "fold-doubled-generated-cells")),
        ("recurrence", ("finite-recurrence-held",)),
        ("exclusion", ("exclusion-preserving-cells",)),
        ("provenance", ("complete-cell-label-trace",)),
        ("target", ("target-inaccessible",)),
        ("extra", ("no-extra-rule",)),
    ),
    unresolved_reason=(
        "Both linear extension and recursive Fold doubling preserve every admitted constraint; no current "
        "physical law distinguishes their rank capacities."
    ),
)


NUCLEAR_CLOSURE = FrontierQuestion(
    claim_id=NUCLEAR_CLOSURE_ID,
    title="Complete nuclear-closure sequence prerequisite",
    statement=(
        "Determine whether admitted nuclear binding, discrete recurrence and conservation uniquely fix every "
        "closed nuclear constituent coordinate."
    ),
    dependencies=COMMON
    + (
        "SFT-PHYS-NUCLEAR-BINDING-001",
        "SFT-PHYS-NUCLEAR-LEVELS-001",
        "SFT-PHYS-NUCLEAR-REACTIONS-001",
    ),
    generation_rule=(
        "Generate the complete product of nuclear carrier, binding, recurrence, closure schedule, channel "
        "accounting, provenance, target access and extra-rule status."
    ),
    grammar_boundary=(
        "All finite nuclear-closure schedules expressible from admitted composite binding, recurrence classes "
        "and complete conserved channels without a fitted interaction or observed closure list."
    ),
    axes=(
        ("carrier", ("anonymous-counts", "bound-composite-carrier")),
        ("binding", ("binding-erased", "binding-trace-held")),
        ("recurrence", ("level-label-only", "boundary-recurrence-held")),
        ("schedule", ("unit-generated-closures", "rank-generated-closures", "externally-selected-closures")),
        ("channels", ("partial-channels", "complete-conserved-channels")),
        ("provenance", ("answer-only", "complete-closure-trace")),
        ("target", ("target-visible", "target-inaccessible")),
        ("extra", ("free-nuclear-rule", "no-extra-rule")),
    ),
    admitted_values=(
        ("carrier", ("bound-composite-carrier",)),
        ("binding", ("binding-trace-held",)),
        ("recurrence", ("boundary-recurrence-held",)),
        ("schedule", ("unit-generated-closures", "rank-generated-closures")),
        ("channels", ("complete-conserved-channels",)),
        ("provenance", ("complete-closure-trace",)),
        ("target", ("target-inaccessible",)),
        ("extra", ("no-extra-rule",)),
    ),
    unresolved_reason=(
        "Distinct positive generated closure schedules satisfy binding, recurrence and conserved-channel closure; "
        "the current laws classify levels but do not select their complete coordinate sequence."
    ),
)


ATOMIC_BOUNDARY = FrontierQuestion(
    claim_id=ATOMIC_BOUNDARY_ID,
    title="Physical atomic existence-boundary prerequisite",
    statement=(
        "Determine whether admitted atomic-number succession and current nuclear laws force a greatest physically "
        "viable atomic coordinate."
    ),
    dependencies=COMMON
    + (
        "SFT-PHYS-NUCLEAR-LEVELS-001",
        "SFT-CHEM-ELEM-ELEMENT-001",
        "SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
        "SFT-CHEM-ELEM-PERIODIC-ORDER-001",
        "SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001",
    ),
    generation_rule=(
        "Generate the complete product of atomic identity, successor status, proposed physical boundary, stability "
        "discriminator, provenance, target access and extra-rule status."
    ),
    grammar_boundary=(
        "All greatest-coordinate conclusions expressible from admitted positive atomic-number succession, current "
        "source-bounded observation and qualitative nuclear recurrence without an added stability law."
    ),
    axes=(
        ("identity", ("identity-erased", "element-identity-held")),
        ("successor", ("terminal-successor-assumed", "every-finite-successor-open")),
        ("boundary", ("all-generated-viable", "some-generated-terminal", "coordinate-varying-viability")),
        ("stability", ("stability-discriminator-absent", "free-stability-discriminator")),
        ("provenance", ("answer-only", "complete-boundary-trace")),
        ("target", ("target-visible", "target-inaccessible")),
        ("extra", ("free-terminal-rule", "no-extra-rule")),
    ),
    admitted_values=(
        ("identity", ("element-identity-held",)),
        ("successor", ("every-finite-successor-open",)),
        ("boundary", ()),
        ("stability", ("stability-discriminator-absent",)),
        ("provenance", ("complete-boundary-trace",)),
        ("target", ("target-inaccessible",)),
        ("extra", ("no-extra-rule",)),
    ),
    unresolved_reason=(
        "Positive atomic-number succession and a source-dated observed boundary do not imply either universal "
        "viability or a greatest viable coordinate; no admitted stability discriminator selects a conclusion."
    ),
)


QUESTIONS = (CELL_CAPACITY, NUCLEAR_CLOSURE, ATOMIC_BOUNDARY)


def candidate_records(question: FrontierQuestion) -> tuple[dict[str, str], ...]:
    names = tuple(name for name, _ in question.axes)
    domains = tuple(values for _, values in question.axes)
    return tuple(
        {"candidate_id": "__".join(values), **dict(zip(names, values))}
        for values in product(*domains)
    )


def survives(question: FrontierQuestion, record: dict[str, str]) -> bool:
    admitted = question.admitted_map()
    return all(record[name] in admitted[name] for name, _ in question.axes)


def decision_reason(question: FrontierQuestion, record: dict[str, str]) -> str:
    admitted = question.admitted_map()
    for name, _ in question.axes:
        if record[name] not in admitted[name]:
            if not admitted[name]:
                return question.unresolved_reason
            return f"The {name} choice is not supplied by the admitted dependency surface."
    return "Every current dependency requirement is preserved, but another distinct survivor remains."


class FrontierPrerequisiteProgram:
    def __init__(self, question: FrontierQuestion, source_hash: str):
        self.question = question
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.question.claim_id,
            title=self.question.title,
            branch="physics_chemistry_prerequisite_frontier",
            statement=self.question.statement,
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.question.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.DIRECT_FORCING,),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(self.question)
        return CandidateCensus(
            generation_rule=self.question.generation_rule,
            grammar_boundary=self.question.grammar_boundary,
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity(
                {"question": self.question, "axes": self.question.axes, "records": records}
            ),
            candidates=tuple(
                Candidate(
                    record["candidate_id"],
                    "Prerequisite proposal has "
                    + ", ".join(record[name] for name, _ in self.question.axes)
                    + ".",
                    sha256_identity({"question": self.question.claim_id, "record": record}),
                )
                for record in records
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        records = {record["candidate_id"]: record for record in candidate_records(self.question)}
        record = records[candidate.candidate_id]
        kept = survives(self.question, record)
        reason = decision_reason(self.question, record)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=kept,
            reason=reason,
            proof_hash=sha256_identity(
                {
                    "question": self.question.claim_id,
                    "record": record,
                    "survives": kept,
                    "reason": reason,
                    "dependencies": self.question.dependencies,
                }
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        # The engine must halt at forcing before this can be called.
        raise RuntimeError("nonunique or absent prerequisite result has no closure evidence")

    def run_controls(self) -> tuple[ControlResult, ...]:
        # The engine must halt at forcing before controls can be called.
        return tuple(
            ControlResult(
                kind,
                False,
                "unclosed prerequisite must halt before controls",
                "control stage is unreachable",
                sha256_identity({"question": self.question.claim_id, "kind": kind.value}),
            )
            for kind in ControlKind
        )


def build_program(question: FrontierQuestion, source_hash: str) -> FrontierPrerequisiteProgram:
    return FrontierPrerequisiteProgram(question, source_hash)


__all__ = (
    "ATOMIC_BOUNDARY",
    "ATOMIC_BOUNDARY_ID",
    "CELL_CAPACITY",
    "CELL_CAPACITY_ID",
    "FrontierPrerequisiteProgram",
    "FrontierQuestion",
    "NUCLEAR_CLOSURE",
    "NUCLEAR_CLOSURE_ID",
    "QUESTIONS",
    "build_program",
    "candidate_records",
    "decision_reason",
    "survives",
)

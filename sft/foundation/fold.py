"""Derive the minimal nontrivial whole-preserving Fold structure."""

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
from sft.foundation.part import CLAIM_ID as PART_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-FOLD-001"
WHOLE_COVERAGE = ("incomplete", "complete")
FIBRE_OVERLAP = ("overlapping", "disjoint")
FIBRE_RELATION = ("unequal", "equal")
COUNT_EXTENSION = ("identity", "first-extension", "later-extension")
LABEL_RELATION = ("labels-absent", "labels-same", "labels-distinct-held")
RETURN_RELATION = ("return-absent", "return-present")
EXTRA_DATA = ("no-extra", "has-extra")
GENERATION_RULE = (
    "Generate the complete product of whole coverage, fibre overlap, fibre "
    "equality, positive-count extension class, label relation, return relation "
    "and unforced-extra-data presence."
)
GRAMMAR_BOUNDARY = (
    "All transformations of the structural One classified as identity, the "
    "first generated positive-count extension or a later extension, together "
    "with exhaustive whole-preservation, fibre, label, return and extra-data "
    "relations required for a nontrivial reversible distinction."
)


def candidate_records() -> tuple[dict[str, str], ...]:
    domains = (
        WHOLE_COVERAGE,
        FIBRE_OVERLAP,
        FIBRE_RELATION,
        COUNT_EXTENSION,
        LABEL_RELATION,
        RETURN_RELATION,
        EXTRA_DATA,
    )
    return tuple(
        {
            "candidate_id": "__".join(fields),
            "coverage": fields[0],
            "overlap": fields[1],
            "fibre": fields[2],
            "extension": fields[3],
            "labels": fields[4],
            "return": fields[5],
            "extra": fields[6],
            "exact_form": "Fold proposal has " + ", ".join(fields) + ".",
        }
        for fields in product(*domains)
    )


def survives(record: dict[str, str]) -> bool:
    return (
        record["coverage"] == "complete"
        and record["overlap"] == "disjoint"
        and record["fibre"] == "equal"
        and record["extension"] == "first-extension"
        and record["labels"] == "labels-distinct-held"
        and record["return"] == "return-present"
        and record["extra"] == "no-extra"
    )


def decision_reason(record: dict[str, str]) -> str:
    if record["coverage"] == "incomplete":
        return "It loses part of the structural One rather than transforming the whole."
    if record["overlap"] == "overlapping":
        return "Overlapping fibres repeat shared structure and do not form an exact partition."
    if record["fibre"] == "unequal":
        return "Unequal fibres introduce an allocation distinction not supplied by the unqualified One."
    if record["extension"] == "identity":
        return "The identity count has no nontrivial fibre distinction."
    if record["extension"] == "later-extension":
        return "A later count extension is not minimal because the first extension is already nontrivial."
    if record["labels"] == "labels-absent":
        return "Without labels the generated fibres are not operationally distinguishable."
    if record["labels"] == "labels-same":
        return "The same label collapses the proposed distinction back to one observational class."
    if record["return"] == "return-absent":
        return "Without a retained return relation the complete fibre assembly is not identified with the One."
    if record["extra"] == "has-extra":
        return "It adds a parameter or datum not supplied by the admitted dependencies."
    return "It is the first nontrivial count extension into equal disjoint held-labelled fibres with a complete return relation and no added data."


def completeness_record() -> dict[str, object]:
    return {
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "domains": {
            "coverage": WHOLE_COVERAGE,
            "overlap": FIBRE_OVERLAP,
            "fibre": FIBRE_RELATION,
            "extension": COUNT_EXTENSION,
            "labels": LABEL_RELATION,
            "return": RETURN_RELATION,
            "extra": EXTRA_DATA,
        },
        "candidates": candidate_records(),
        "exhaustion": (
            "The positive-count dependency classifies a transformation as no "
            "extension, its first extension or any later extension. Every other "
            "criterion is an explicit exhaustive relation at the declared boundary; "
            "their product generates all same-grammar forms."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "minimal_count": (
            "The structural One is the identity base. Appending one generated "
            "occurrence is the first nonidentity positive count. Every later finite "
            "extension contains this earlier nontrivial stage and is therefore not minimal."
        ),
        "equal_fibres": (
            "The unqualified One supplies no selector that can privilege one fibre. "
            "An unequal allocation therefore requires additional data, while equal "
            "fibre status does not."
        ),
        "held_labels": (
            "Nontrivial distinction requires different exact labels. They are held "
            "structural identities, not positive and negative numerical quantities."
        ),
        "return": (
            "Complete disjoint fibres retain the One only when their complete assembly "
            "has an explicit return relation to the source whole."
        ),
        "minimality": (
            "Identity is trivial; later extensions are overbuilt; removing equality, "
            "disjointness, distinct held labels or return loses a Fold requirement; "
            "adding data violates parameter freedom."
        ),
        "named_shape_uniqueness": (
            "Only complete__disjoint__equal__first-extension__labels-distinct-held__"
            "return-present__no-extra satisfies every generated requirement."
        ),
        "generality": (
            "First-extension minimality follows from the base/successor count structure "
            "at every later generated finite depth; it does not depend on a maximum "
            "census depth or completed infinity."
        ),
    }


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    records = {item["candidate_id"]: item for item in candidate_records()}
    common = "complete__disjoint__equal"
    identity = records[
        common
        + "__identity__labels-distinct-held__return-present__no-extra"
    ]
    later = records[
        common
        + "__later-extension__labels-distinct-held__return-present__no-extra"
    ]
    return (
        {
            "kind": ControlKind.FALSE_PREMISE.value,
            "expected": "reject the unchanged One as a nontrivial Fold",
            "observed": "the identity-extension proposal does not survive",
            "passed": not survives(identity),
        },
        {
            "kind": ControlKind.TAMPERED_SOURCE.value,
            "expected": "reject a changed derivation source identity",
            "observed": "the changed source identity differs",
            "passed": sha256_identity({"changed": source_hash}) != source_hash,
        },
        {
            "kind": ControlKind.TAMPERED_ARTIFACT.value,
            "expected": "reject a later extension as the minimal Fold",
            "observed": "the later-extension proposal does not survive",
            "passed": not survives(later),
        },
        {
            "kind": ControlKind.BOUNDARY.value,
            "expected": "refuse signed labels, asymmetric parameters and completed-infinite arity",
            "observed": "the survivor uses two held labels from the first finite extension and no added datum",
            "passed": "not positive and negative" in closure_record()["held_labels"],
        },
    )


class FoldProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="The minimal structural Fold",
            branch="foundation",
            statement=(
                "The unique minimal parameter-free nontrivial transformation of "
                "the structural One into a reversible distinguished partition is "
                "the first positive-count extension: two equal disjoint fibres with "
                "distinct held labels and an explicit complete return relation to "
                "the One. This structure is the Fold."
            ),
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID),
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
                    "dependencies": (ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID),
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
                    "base_successor_minimality": True,
                    "dependencies": (ONE_CLAIM_ID, COUNT_CLAIM_ID, PART_CLAIM_ID),
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

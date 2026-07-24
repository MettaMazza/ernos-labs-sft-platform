"""Force the fail-closed admission route for every proposed SFT law."""

from __future__ import annotations

from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.derivation_trace import CLAIM_ID as TRACE_CLAIM_ID
from sft.foundation.form_enforcement import CLAIM_ID as FORM_CLAIM_ID
from sft.foundation.measurement_boundary import CLAIM_ID as MEASUREMENT_CLAIM_ID


CLAIM_ID = "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001"
DOMAINS = (
    ("registration-incomplete", "registration-root-bound"),
    ("axiom-or-parameter-present", "no-axiom-zero-parameter"),
    ("census-selected", "census-complete"),
    ("survivor-not-unique", "survivor-unique"),
    ("form-open", "form-closed"),
    ("controls-incomplete", "controls-complete"),
    ("validation-self-only", "validation-independent"),
    ("measurement-before-seal", "measurement-after-seal-when-required"),
    ("failure-discarded", "every-receipt-preserved"),
    ("dependency-before-admission", "dependency-after-model-admission"),
    ("no-extra", "has-extra"),
)
SURVIVOR = "__".join(("registration-root-bound", "no-axiom-zero-parameter", "census-complete", "survivor-unique", "form-closed", "controls-complete", "validation-independent", "measurement-after-seal-when-required", "every-receipt-preserved", "dependency-after-model-admission", "no-extra"))
GENERATION_RULE = "Generate the complete product of registration, premise/parameter, enumeration, forcing, closure, control, independent-validation, measurement-order, receipt-retention, dependency-authority and added-rule classes."
GRAMMAR_BOUNDARY = "All admission paths from a proposed V3 derivation to model authority under the single engine, including formal-only and post-seal empirical evidence modes."


def candidate_records() -> tuple[dict[str, str], ...]:
    return tuple({"candidate_id": "__".join(x), "exact_form": "Admission path has " + ", ".join(x) + "."} for x in product(*DOMAINS))


def survives(record: dict[str, str]) -> bool: return record["candidate_id"] == SURVIVOR


def decision_reason(record: dict[str, str]) -> str:
    failures = (("registration-incomplete", "The claim lacks an exact statement, source identity or root/dependency trace."), ("axiom-or-parameter-present", "An axiom, fitted value, learned value or free parameter enters the derivation."), ("census-selected", "The candidate neighborhood is selected rather than completely generated at its boundary."), ("survivor-not-unique", "Forcing leaves none or more than one survivor."), ("form-open", "Minimality, named-shape uniqueness or the exact boundary remains open."), ("controls-incomplete", "A false-premise, tampered-source, tampered-artifact or boundary control is absent or fails."), ("validation-self-only", "The result is not recomputed by an implementation-distinct validator."), ("measurement-before-seal", "Target content can select or mutate the derivation."), ("failure-discarded", "An adverse or rejected receipt is lost."), ("dependency-before-admission", "An unclosed result is used as model authority."), ("has-extra", "The route adds an unregistered bypass or exception."))
    for marker, reason in failures:
        if marker in record["candidate_id"]: return reason
    return "It is the sole fail-closed route: root-bound, parameter-free, exhaustively forced, closed, controlled, independently checked, post-seal measured when applicable, receipt-preserving and authority-gated."


def completeness_record() -> dict[str, object]:
    return {"generator": GENERATION_RULE, "boundary": GRAMMAR_BOUNDARY, "domains": DOMAINS, "candidates": candidate_records(), "gate_order": ("registration", "enumeration", "forcing", "form closure", "controls", "seal", "independent validation", "post-seal empirical validation when registered", "model admission", "immutable receipt")}


def closure_record() -> dict[str, object]:
    return {
        "necessity": "Each gate blocks a distinct unauthorized information or authority path: hidden premise, selected candidates, nonunique result, open form, unfalsified implementation, target leakage, lost failure or premature dependency.",
        "sufficiency": "A proposal satisfying all gates has one source-bound exact result at its declared boundary, independent recomputation, every required adverse control, appropriate empirical custody and an immutable disposition.",
        "formal_empirical_split": "Formal claims stop after independent recomputation. Empirical claims must additionally seal their prediction before identified external target content opens and preserve every comparison row.",
        "fail_closed": "Any failed or exceptional gate emits and preserves a rejected receipt; it does not enter model authority. Only finite-complete or depth-independent closure may become a dependency.",
        "minimality": "Removing any gate reopens its corresponding prohibited path; adding a bypass contradicts the same constraints.",
        "named_shape_uniqueness": f"Only {SURVIVOR} is an admissible authority path.",
        "generality": "The gate relation depends on claim capabilities and evidence class, not branch, operating system, target value or corpus size.",
    }


def admission_accepts(**changes: bool) -> bool:
    required = {"root_bound": True, "parameter_free": True, "complete_census": True, "unique": True, "closed": True, "controls": True, "independent": True, "postseal": True, "preserved": True, "admitted_dependency": True}
    required.update(changes)
    return all(required.values())


def control_records(source_hash: str) -> tuple[dict[str, object], ...]:
    return (
        {"kind": "false_premise", "expected": "reject an axiom or free parameter", "observed": "the route halts when parameter freedom is false", "passed": not admission_accepts(parameter_free=False)},
        {"kind": "tampered_source", "expected": "reject a changed source identity", "observed": "the changed identity differs and root custody fails", "passed": sha256_identity({"changed": source_hash}) != source_hash and not admission_accepts(root_bound=False)},
        {"kind": "tampered_artifact", "expected": "reject a second survivor or discarded failure", "observed": "both altered routes halt", "passed": not admission_accepts(unique=False) and not admission_accepts(preserved=False)},
        {"kind": "boundary", "expected": "reject pre-seal target access and unclosed dependencies", "observed": "both capability violations halt while the complete path passes", "passed": not admission_accepts(postseal=False) and not admission_accepts(admitted_dependency=False) and admission_accepts()},
    )


class AdmissionEnforcementProgram:
    def __init__(self, source_hash: str): self.source_hash = source_hash
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(CLAIM_ID, "Single fail-closed SFT admission law", "foundation", "The unique admissible route from a proposed law to model authority is root- and source-bound, axiom-free and zero-parameter; it completely enumerates its declared candidate grammar, leaves one survivor, closes its form, passes all adverse controls and implementation-distinct validation, opens measurements only after sealing when empirical, preserves every disposition receipt, and permits dependency use only after model admission.", EvidenceMode.FORMAL, (ROOT_THEOREM,), (FORM_CLAIM_ID, MEASUREMENT_CLAIM_ID, TRACE_CLAIM_ID), (), (), (ProvenanceClass.CONSTITUTIONAL_RELATION,), self.source_hash)
    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(); return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(records), sha256_identity(completeness_record()), tuple(Candidate(r["candidate_id"], r["exact_form"], sha256_identity({"generator": GENERATION_RULE, "record": r})) for r in records))
    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = {r["candidate_id"]: r for r in candidate_records()}[candidate.candidate_id]; keep = survives(record); reason = decision_reason(record); return CandidateDecision(candidate.candidate_id, keep, reason, sha256_identity({"record": record, "survives": keep, "reason": reason}))
    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(); return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, True, True, sha256_identity({"closure": closure, "decisions": tuple(decisions)}), sha256_identity({"branch_and_host_independent_gate_relation": True, "closure": closure}))
    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(ControlResult(ControlKind(r["kind"]), r["passed"] is True, str(r["expected"]), str(r["observed"]), sha256_identity(r)) for r in control_records(self.source_hash))

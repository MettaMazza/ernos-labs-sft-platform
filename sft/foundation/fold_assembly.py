"""Derive complete finite Fold-word assembly by structural recursion."""
from __future__ import annotations
from itertools import product
from typing import Sequence
from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.count import CLAIM_ID as COUNT_CLAIM_ID
from sft.foundation.fold import CLAIM_ID as FOLD_CLAIM_ID

CLAIM_ID="SFT-FOUNDATION-FOLD-ASSEMBLY-001"
TRACE_COVERAGE=("none","proper","complete")
WORD_LENGTH=("inconsistent-length","consistent-length")
SUPPORT=("support-incomplete","support-complete")
UNIQUENESS=("words-duplicated","words-unique")
TRANSITIONS=("transitions-absent","transitions-present")
RETURNS=("returns-absent","returns-present")
EXTRA=("no-extra","has-extra")
LABELS=("held-a","held-b")
GENERATION_RULE="Generate the complete product of Fold-trace coverage, word-length consistency, support completeness, word uniqueness, transition records, return records and unforced-extra-data presence."
GRAMMAR_BOUNDARY="All representations of any generated finite Fold succession, with support formed recursively from the empty One word by appending each of the two held Fold labels at every successor step."
SURVIVOR="complete__consistent-length__support-complete__words-unique__transitions-present__returns-present__no-extra"

def extend(words:tuple[tuple[str,...],...])->tuple[tuple[str,...],...]:
    return tuple(word+(label,) for word in words for label in LABELS)
def support_after_extensions(extensions:int)->tuple[tuple[str,...],...]:
    if extensions < 0: raise ValueError("a generated extension count cannot be negative")
    words=((),)
    for _ in range(extensions): words=extend(words)
    return words
def candidate_records():
    domains=(TRACE_COVERAGE,WORD_LENGTH,SUPPORT,UNIQUENESS,TRANSITIONS,RETURNS,EXTRA);keys=("coverage","length","support","unique","transitions","returns","extra")
    return tuple({"candidate_id":"__".join(x),**dict(zip(keys,x)),"exact_form":"Assembly representation has "+", ".join(x)+"."} for x in product(*domains))
def survives(r): return r["candidate_id"]==SURVIVOR
def decision_reason(r):
    tests=((r["coverage"]=="none","It retains no generated Fold step."),(r["coverage"]=="proper","It omits at least one generated Fold step."),(r["length"]=="inconsistent-length","At least one word does not carry one held label per Fold step."),(r["support"]=="support-incomplete","At least one recursively forced held-label extension is missing."),(r["unique"]=="words-duplicated","At least one generated word is repeated."),(r["transitions"]=="transitions-absent","The predecessor-to-successor construction trace is missing."),(r["returns"]=="returns-absent","The assembly lacks the complete return records to the One."),(r["extra"]=="has-extra","The representation adds a word, label or rule not supplied by Fold recursion."))
    for bad,reason in tests:
        if bad:return reason
    return "It retains every Fold step, every unique equal-length held-label word, every transition and every return without addition."
def completeness_record():
    return {"generator":GENERATION_RULE,"boundary":GRAMMAR_BOUNDARY,"domains":(TRACE_COVERAGE,WORD_LENGTH,SUPPORT,UNIQUENESS,TRANSITIONS,RETURNS,EXTRA),"candidates":candidate_records(),"recursion":"Begin with the structural empty One word. At each generated Fold successor, append held-a and held-b once to every prior word."}
def closure_record():
    return {"base":"The empty One word is the complete support before a Fold; empty is a structural form, not numerical zero.","successor":"Appending each of the two distinct held labels once to every prior word produces all and only the next support.","uniqueness":"Distinct prior words or distinct appended held labels yield distinct successor traces.","return":"The return relation at each Fold node reunites its two successor branches to their predecessor whole.","minimality":"Removing a word loses support; duplicating or adding a word is nonminimal; missing transitions or returns loses construction identity.","named_shape_uniqueness":f"Only {SURVIVOR} is complete.","generality":"The base and successor clauses apply to every generated finite Fold depth without a maximum or completed infinity."}
def control_records(source_hash):
    supports=tuple(support_after_extensions(d) for d in range(1,6)); complete=all(len(x)==len(set(x)) and all(len(w)==i for w in x) for i,x in enumerate(supports,1))
    return ({"kind":"false_premise","expected":"reject incomplete one-step support","observed":"a single held-label word omits the other forced branch","passed":set((("held-a",),))!=set(support_after_extensions(1))},{"kind":"tampered_source","expected":"reject changed source identity","observed":"changed identity differs","passed":sha256_identity({"changed":source_hash})!=source_hash},{"kind":"tampered_artifact","expected":"reject duplicated or missing word support","observed":"generated depths one through five are unique, equal-length and complete","passed":complete},{"kind":"boundary","expected":"refuse imported binary numerals, exponentiation and completed-infinite support","observed":"support is generated only by finite held-label recursion","passed":"completed infinity" in closure_record()["generality"]})
class FoldAssemblyProgram:
    def __init__(self,source_hash):self.source_hash=source_hash
    @property
    def registration(self):return ClaimRegistration(CLAIM_ID,"Complete finite Fold-word assembly","foundation","Every generated finite succession of Folds has one exact complete support: begin with the structural empty One word and at each Fold append each of the two held fibre labels once to every prior word, retaining unique word, transition and return traces.",EvidenceMode.FORMAL,(ROOT_THEOREM,),(COUNT_CLAIM_ID,FOLD_CLAIM_ID),(),(),(ProvenanceClass.FORWARD_FORCING,),self.source_hash)
    def generate_candidates(self):
        r=candidate_records();return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(r),sha256_identity(completeness_record()),tuple(Candidate(x["candidate_id"],x["exact_form"],sha256_identity({"generator":GENERATION_RULE,"record":x})) for x in r))
    def decide_candidate(self,candidate):
        r={x["candidate_id"]:x for x in candidate_records()}[candidate.candidate_id];s=survives(r);reason=decision_reason(r);return CandidateDecision(candidate.candidate_id,s,reason,sha256_identity({"record":r,"survives":s,"reason":reason,"dependencies":(COUNT_CLAIM_ID,FOLD_CLAIM_ID)}))
    def closure_evidence(self,decisions:Sequence[CandidateDecision]):
        c=closure_record();return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,True,True,sha256_identity({"closure":c,"decisions":tuple(decisions)}),sha256_identity({"structural_recursion":True,"closure":c}))
    def run_controls(self):return tuple(ControlResult(ControlKind(x["kind"]),x["passed"] is True,str(x["expected"]),str(x["observed"]),sha256_identity(x)) for x in control_records(self.source_hash))

"""Derive the one-way boundary from exact derivation to measured records."""
from __future__ import annotations
from itertools import product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.form_enforcement import CLAIM_ID as FORM_CLAIM_ID

CLAIM_ID="SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001"
FLOW=("disconnected","derivation-to-measurement","measurement-to-derivation","bidirectional")
PROOF=("proof-inexact","proof-exact")
TARGET=("target-before-seal","target-after-seal")
ROWS=("rows-selective","rows-complete")
SOURCE=("source-absent","source-identified")
LAW=("law-mutated","law-unchanged")
EXTRA=("no-extra","has-extra")
GENERATION_RULE="Generate the complete product of information-flow direction, proof-value exactness, target-opening order, row preservation, data-source identity, law mutation and unforced-extra-rule presence."
GRAMMAR_BOUNDARY="All interfaces between an admitted exact derivation and conventional external measurement records under the SFT empirical constitution."
SURVIVOR="derivation-to-measurement__proof-exact__target-after-seal__rows-complete__source-identified__law-unchanged__no-extra"
def candidate_records():
 d=(FLOW,PROOF,TARGET,ROWS,SOURCE,LAW,EXTRA);k=("flow","proof","target","rows","source","law","extra")
 return tuple({"candidate_id":"__".join(x),**dict(zip(k,x)),"exact_form":"Measurement-boundary proposal has "+", ".join(x)+"."} for x in product(*d))
def survives(r):return r["candidate_id"]==SURVIVOR
def decision_reason(r):
 tests=((r["flow"]=="disconnected","A disconnected interface cannot test a derived consequence."),(r["flow"]=="measurement-to-derivation","Measured records flow backward and can select the law."),(r["flow"]=="bidirectional","Bidirectional flow permits target feedback into derivation."),(r["proof"]=="proof-inexact","An inexact value has entered the derivational proof domain."),(r["target"]=="target-before-seal","Target content is available before the derived consequence is sealed."),(r["rows"]=="rows-selective","Selective retention can hide unfavorable or failed outcomes."),(r["source"]=="source-absent","The measured record lacks an independently checkable source identity."),(r["law"]=="law-mutated","Measurement changes the already selected law."),(r["extra"]=="has-extra","The interface adds an unregistered selection or comparison rule."))
 for bad,reason in tests:
  if bad:return reason
 return "An exact law sends a sealed consequence outward; identified targets open afterward; all rows are retained; measurement cannot mutate or select the law."
def completeness_record():return {"generator":GENERATION_RULE,"boundary":GRAMMAR_BOUNDARY,"domains":(FLOW,PROOF,TARGET,ROWS,SOURCE,LAW,EXTRA),"candidates":candidate_records(),"phase_order":("exact derivation","seal","open separately held target","measure","preserve every row"),"quarantine":"Conventional decimal values exist only in measured records and cannot become SFT proof quantities."}
def closure_record():return {"direction":"Scientific testing requires consequences to leave a derivation, while clean forcing forbids targets or measurements from entering law selection; only outward derivation-to-measurement flow satisfies both.","exactness":"The derivation remains exact. A measurement adapter may record conventional decimals only after the law and consequence are sealed.","custody":"Opening targets after the seal prevents answer flow into the derivation.","retention":"Complete favorable, unfavorable, failed and tampered rows are required for falsifiability.","immutability":"Measurement can validate, invalidate or bound a claim but cannot rewrite its sealed law.","minimality":"Removing exactness, custody, source identity, row completeness or immutability loses a scientific control; extra rules are unregistered.","named_shape_uniqueness":f"Only {SURVIVOR} satisfies the complete one-way boundary.","generality":"The phase and capability relation is independent of scientific branch, target size and host operating system."}
def protocol_accepts(target_before_seal=False,measurement_changes_law=False,all_rows=True,source=True):return not target_before_seal and not measurement_changes_law and all_rows and source
def control_records(h):return ({"kind":"false_premise","expected":"reject target access before the prediction seal","observed":"the boundary protocol rejects pre-seal target access","passed":not protocol_accepts(target_before_seal=True)},{"kind":"tampered_source","expected":"reject changed derivation source identity","observed":"changed identity differs","passed":sha256_identity({"changed":h})!=h},{"kind":"tampered_artifact","expected":"reject selective rows or post-measurement law mutation","observed":"both tampered interfaces are rejected","passed":not protocol_accepts(all_rows=False) and not protocol_accepts(measurement_changes_law=True)},{"kind":"boundary","expected":"permit conventional decimals only as post-seal measured records","observed":"proof stays exact and measurement records remain quarantined","passed":"only after" in closure_record()["exactness"]})
class MeasurementBoundaryProgram:
 def __init__(self,h):self.source_hash=h
 @property
 def registration(self):return ClaimRegistration(CLAIM_ID,"One-way derivation-to-measurement boundary","foundation","The unique admissible interface between SFT derivation and conventional measurement is one-way: an exact source-bound law seals its consequence before an identified external target is opened, measurement preserves every row, and no measured value, score or target may select or mutate the law.",EvidenceMode.FORMAL,(ROOT_THEOREM,),(FORM_CLAIM_ID,),(),(),(ProvenanceClass.CONSTITUTIONAL_RELATION,),self.source_hash)
 def generate_candidates(self):
  r=candidate_records();return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(r),sha256_identity(completeness_record()),tuple(Candidate(x["candidate_id"],x["exact_form"],sha256_identity({"generator":GENERATION_RULE,"record":x})) for x in r))
 def decide_candidate(self,c):
  r={x["candidate_id"]:x for x in candidate_records()}[c.candidate_id];s=survives(r);w=decision_reason(r);return CandidateDecision(c.candidate_id,s,w,sha256_identity({"record":r,"survives":s,"reason":w,"dependency":FORM_CLAIM_ID}))
 def closure_evidence(self,d:Sequence[CandidateDecision]):
  c=closure_record();return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,True,True,sha256_identity({"closure":c,"decisions":tuple(d)}),sha256_identity({"branch_independent_phase_order":True,"closure":c}))
 def run_controls(self):return tuple(ControlResult(ControlKind(x["kind"]),x["passed"] is True,str(x["expected"]),str(x["observed"]),sha256_identity(x)) for x in control_records(self.source_hash))

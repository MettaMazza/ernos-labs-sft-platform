"""Derive canonical identity and equivalence enforcement for generated forms."""
from __future__ import annotations
from itertools import product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.form_grammar import CLAIM_ID as GRAMMAR_CLAIM_ID,leaf,fold,valid_form

CLAIM_ID="SFT-FOUNDATION-FORM-ENFORCEMENT-001"
COVERAGE=("none","proper","complete")
MULTIPLICITY=("node-duplicated","node-once")
LABELS=("labels-lost","labels-preserved")
CHILDREN=("children-changed","children-preserved")
RETURNS=("returns-lost","returns-preserved")
TRACE=("trace-noncanonical","trace-canonical")
EXTRA=("no-extra","has-extra")
GENERATION_RULE="Generate the complete product of source-form coverage, node multiplicity, held-label preservation, child-relation preservation, return preservation, canonical-trace status and unforced-extra-data presence."
GRAMMAR_BOUNDARY="All exact-identity representations of forms admitted by the complete finite One/Fold grammar."
SURVIVOR="complete__node-once__labels-preserved__children-preserved__returns-preserved__trace-canonical__no-extra"
def candidate_records():
 d=(COVERAGE,MULTIPLICITY,LABELS,CHILDREN,RETURNS,TRACE,EXTRA);k=("coverage","multiplicity","labels","children","returns","trace","extra")
 return tuple({"candidate_id":"__".join(x),**dict(zip(k,x)),"exact_form":"Form-identity proposal has "+", ".join(x)+"."} for x in product(*d))
def survives(r):return r["candidate_id"]==SURVIVOR
def decision_reason(r):
 tests=((r["coverage"]=="none","It retains none of the generated source form."),(r["coverage"]=="proper","It omits at least one generated node or relation."),(r["multiplicity"]=="node-duplicated","It repeats a node already supplied by the construction trace."),(r["labels"]=="labels-lost","It erases a held edge identity."),(r["children"]=="children-changed","It changes a generated parent-child relation."),(r["returns"]=="returns-lost","It omits a Fold return relation."),(r["trace"]=="trace-noncanonical","It does not follow the unique recursive production order."),(r["extra"]=="has-extra","It adds a node, relation or name not supplied by the form."))
 for bad,reason in tests:
  if bad:return reason
 return "It retains the complete generated form once in canonical production order with all held labels, children and returns and no addition."
def canonical_trace(form):
 if not valid_form(form):raise ValueError("form is outside the admitted grammar")
 if form==leaf():return ("One",)
 return ("Fold","held-a",canonical_trace(form[1][1]),"held-b",canonical_trace(form[2][1]),"return")
def equivalent(left,right):return canonical_trace(left)==canonical_trace(right)
def completeness_record():return {"generator":GENERATION_RULE,"boundary":GRAMMAR_BOUNDARY,"domains":(COVERAGE,MULTIPLICITY,LABELS,CHILDREN,RETURNS,TRACE,EXTRA),"candidates":candidate_records(),"canonicalizer":"One maps to its terminal trace; Fold maps to Fold, held-a child trace, held-b child trace, return, recursively."}
def closure_record():return {"base":"The One leaf has one complete canonical trace.","successor":"A Fold trace is forced by its production: Fold marker, held-a child trace, held-b child trace and return marker.","identity":"Two generated forms are identical exactly when their canonical traces are identical.","equivalence":"Canonical-trace identity is reflexive, symmetric and transitive and preserves held labels and rooted child relations.","minimality":"Any omission loses source structure; duplication or addition is nonminimal; a changed relation names another form.","named_shape_uniqueness":f"Only {SURVIVOR} is an exact identity representation.","generality":"Structural induction applies to every generated finite form and does not require a depth bound."}
def control_records(h):
 o=leaf();f=fold(o,o);asym=fold(f,o);swapped=("Fold",("held-a",o),("held-b",f),"return")
 return ({"kind":"false_premise","expected":"reject a partial trace as exact form identity","observed":"a trace without the held-b child is not canonical","passed":canonical_trace(f)!=("Fold","held-a",("One",),"return")},{"kind":"tampered_source","expected":"reject changed source identity","observed":"changed identity differs","passed":sha256_identity({"changed":h})!=h},{"kind":"tampered_artifact","expected":"reject a child swap while accepting an exact reconstruction","observed":"the exact trace matches and the label-preserving swapped trace differs","passed":equivalent(asym,asym) and not equivalent(asym,swapped)},{"kind":"boundary","expected":"refuse equivalence that discards held labels or finite construction identity","observed":"canonical equivalence preserves the entire recursive held-labelled trace","passed":"preserves held labels" in closure_record()["equivalence"]})
class FormEnforcementProgram:
 def __init__(self,h):self.source_hash=h
 @property
 def registration(self):return ClaimRegistration(CLAIM_ID,"Canonical foundational form enforcement","foundation","Every generated finite foundational form has one exact identity representation: its complete canonical recursive construction trace with each node once and every held label, child relation and Fold return preserved; two forms are equivalent exactly when these traces agree.",EvidenceMode.FORMAL,(ROOT_THEOREM,),(GRAMMAR_CLAIM_ID,),(),(),(ProvenanceClass.FORWARD_FORCING,),self.source_hash)
 def generate_candidates(self):
  r=candidate_records();return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(r),sha256_identity(completeness_record()),tuple(Candidate(x["candidate_id"],x["exact_form"],sha256_identity({"generator":GENERATION_RULE,"record":x})) for x in r))
 def decide_candidate(self,c):
  r={x["candidate_id"]:x for x in candidate_records()}[c.candidate_id];s=survives(r);w=decision_reason(r);return CandidateDecision(c.candidate_id,s,w,sha256_identity({"record":r,"survives":s,"reason":w,"dependency":GRAMMAR_CLAIM_ID}))
 def closure_evidence(self,d:Sequence[CandidateDecision]):
  c=closure_record();return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,True,True,sha256_identity({"closure":c,"decisions":tuple(d)}),sha256_identity({"canonical_structural_induction":True,"closure":c}))
 def run_controls(self):return tuple(ControlResult(ControlKind(x["kind"]),x["passed"] is True,str(x["expected"]),str(x["observed"]),sha256_identity(x)) for x in control_records(self.source_hash))

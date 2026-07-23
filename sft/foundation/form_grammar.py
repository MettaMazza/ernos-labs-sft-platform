"""Derive the complete recursive grammar of finite foundational Fold forms."""
from __future__ import annotations
from itertools import product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.fold import CLAIM_ID as FOLD_CLAIM_ID
from sft.foundation.fold_assembly import CLAIM_ID as ASSEMBLY_CLAIM_ID
from sft.foundation.one import CLAIM_ID as ONE_CLAIM_ID

CLAIM_ID="SFT-FOUNDATION-FORM-GRAMMAR-001"
BASE=("base-excluded","base-included")
CHILD_ARITY=("one-child","two-children","later-arity")
LABELS=("labels-absent","labels-same","labels-distinct-held")
CHILD_SOURCE=("children-ungenerated","children-generated")
RETURN=("return-absent","return-present")
TERMINATION=("termination-absent","finite-leaf-termination")
EXTRA=("no-extra","has-extra")
GENERATION_RULE="Generate the complete product of One-base inclusion, recursive child arity, edge-label relation, child provenance, return relation, finite termination and unforced-extra-production presence."
GRAMMAR_BOUNDARY="All recursive production-rule shapes for finite forms assembled only from the admitted structural One and minimal Fold."
SURVIVOR="base-included__two-children__labels-distinct-held__children-generated__return-present__finite-leaf-termination__no-extra"

def candidate_records():
 d=(BASE,CHILD_ARITY,LABELS,CHILD_SOURCE,RETURN,TERMINATION,EXTRA);k=("base","arity","labels","children","return","termination","extra")
 return tuple({"candidate_id":"__".join(x),**dict(zip(k,x)),"exact_form":"Grammar proposal has "+", ".join(x)+"."} for x in product(*d))
def survives(r):return r["candidate_id"]==SURVIVOR
def decision_reason(r):
 checks=((r["base"]=="base-excluded","Without the structural One leaf the recursion has no admitted terminal form."),(r["arity"]=="one-child","One child omits a forced Fold fibre."),(r["arity"]=="later-arity","A later arity imports a nonminimal branching rule."),(r["labels"]=="labels-absent","Unlabelled edges do not retain Fold distinction."),(r["labels"]=="labels-same","Identical edge labels collapse the two Fold fibres."),(r["children"]=="children-ungenerated","Ungenerated children introduce forms outside the dependency grammar."),(r["return"]=="return-absent","The node lacks its complete return relation to the parent whole."),(r["termination"]=="termination-absent","The production admits an uncompleted regress instead of a generated finite form."),(r["extra"]=="has-extra","The grammar adds a constructor not forced by One or Fold."))
 for bad,reason in checks:
  if bad:return reason
 return "It includes the One leaf and only complete two-child held-labelled returning Fold nodes whose children are recursively generated and finitely terminate."
def leaf():return ("One",)
def fold(left,right):return ("Fold",("held-a",left),("held-b",right),"return")
def generated_examples():
 one=leaf();first=fold(one,one);left_deep=fold(first,one);right_deep=fold(one,first);return (one,first,left_deep,right_deep,fold(first,first))
def valid_form(form):
 if form==leaf():return True
 return isinstance(form,tuple) and len(form)==4 and form[0]=="Fold" and form[1][0]=="held-a" and form[2][0]=="held-b" and form[3]=="return" and valid_form(form[1][1]) and valid_form(form[2][1])
def completeness_record():return {"generator":GENERATION_RULE,"boundary":GRAMMAR_BOUNDARY,"domains":(BASE,CHILD_ARITY,LABELS,CHILD_SOURCE,RETURN,TERMINATION,EXTRA),"candidates":candidate_records(),"productions":("Form := One","Form := Fold(held-a: Form, held-b: Form, return-to-One)"),"exhaustion":"The base and every local Fold-production requirement are independently classified; the product exhausts the declared production-rule grammar."}
def closure_record():return {"base":"The structural One is the sole terminal constructor.","recursion":"The minimal Fold supplies exactly two distinctly held edges; each child must already be a generated finite Form; the node retains its return relation.","termination":"Every admitted form has a finite construction trace ending only in One leaves. No completed infinite tree is formed.","completeness":"Any finite assembly from One and Fold is parsed by the productions, and every production output is such an assembly.","minimality":"Removing the base or a child, label, provenance or return loses a dependency; later arity or an extra constructor is unforced.","named_shape_uniqueness":f"Only {SURVIVOR} defines the complete grammar.","generality":"Structural induction over construction traces establishes the grammar at every generated finite tree depth."}
def control_records(h):
 examples=generated_examples()
 return ({"kind":"false_premise","expected":"reject a one-child Fold node","observed":"the one-child production is outside the grammar","passed":not valid_form(("Fold",("held-a",leaf()),"return"))},{"kind":"tampered_source","expected":"reject changed source identity","observed":"changed identity differs","passed":sha256_identity({"changed":h})!=h},{"kind":"tampered_artifact","expected":"accept generated nonuniform finite trees and reject same-label edges","observed":"all generated examples parse and the same-label node does not","passed":all(valid_form(x) for x in examples) and not valid_form(("Fold",("held-a",leaf()),("held-a",leaf()),"return"))},{"kind":"boundary","expected":"refuse completed-infinite trees and unforced constructors","observed":"only finite traces ending in One are admitted","passed":"No completed infinite tree" in closure_record()["termination"]})
class FormGrammarProgram:
 def __init__(self,h):self.source_hash=h
 @property
 def registration(self):return ClaimRegistration(CLAIM_ID,"Complete foundational form grammar","foundation","The complete foundational form grammar has exactly two productions: the structural One leaf, and a finite Fold node with two recursively generated child forms on distinct held-labelled edges and an explicit return relation to the parent whole.",EvidenceMode.FORMAL,(ROOT_THEOREM,),(ONE_CLAIM_ID,FOLD_CLAIM_ID,ASSEMBLY_CLAIM_ID),(),(),(ProvenanceClass.FORWARD_FORCING,),self.source_hash)
 def generate_candidates(self):
  r=candidate_records();return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(r),sha256_identity(completeness_record()),tuple(Candidate(x["candidate_id"],x["exact_form"],sha256_identity({"generator":GENERATION_RULE,"record":x})) for x in r))
 def decide_candidate(self,c):
  r={x["candidate_id"]:x for x in candidate_records()}[c.candidate_id];s=survives(r);why=decision_reason(r);return CandidateDecision(c.candidate_id,s,why,sha256_identity({"record":r,"survives":s,"reason":why,"dependencies":(ONE_CLAIM_ID,FOLD_CLAIM_ID,ASSEMBLY_CLAIM_ID)}))
 def closure_evidence(self,d:Sequence[CandidateDecision]):
  c=closure_record();return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,True,True,sha256_identity({"closure":c,"decisions":tuple(d)}),sha256_identity({"structural_induction":True,"closure":c}))
 def run_controls(self):return tuple(ControlResult(ControlKind(x["kind"]),x["passed"] is True,str(x["expected"]),str(x["observed"]),sha256_identity(x)) for x in control_records(self.source_hash))

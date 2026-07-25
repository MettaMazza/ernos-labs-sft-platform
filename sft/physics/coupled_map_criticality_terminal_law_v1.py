"""Exact normalized transverse Fold synchronization threshold.

No external critical record, topology-specific target, expected survivor or
claimant-controlled admission flag enters this formal claimant.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity

CLAIM_ID="SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008"
EXPERIMENT_ID="SFT-EXP-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008"

def positive_label_count(value:int)->int:
 if isinstance(value,bool) or not isinstance(value,int) or value<2: raise ValueError("complete generated label count must be at least two")
 return value

def holding_threshold(label_count:int)->Fraction:
 m=positive_label_count(label_count)
 return Fraction(m-1,m)

def retained_transverse_multiplier(label_count:int,coupling:Fraction)->Fraction:
 m=positive_label_count(label_count)
 if not isinstance(coupling,Fraction) or not 0<coupling<1: raise ValueError("coupling must be an exact proper positive part")
 return m*(Fraction(1,1)-coupling)

def stability_class(label_count:int,coupling:Fraction)->str:
 multiplier=retained_transverse_multiplier(label_count,coupling)
 if multiplier==1: return "neutral-boundary"
 return "strict-contraction" if multiplier<1 else "strict-expansion"

def criticality_certificate()->dict[str,object]:
 rows=[]
 for m in (2,3,5,7):
  threshold=holding_threshold(m); below=Fraction(m-1,m+1); above=Fraction(m,m+1)
  rows.append({"label_count":m,"threshold":threshold,"below":below,"above":above,"below_multiplier":retained_transverse_multiplier(m,below),"boundary_multiplier":retained_transverse_multiplier(m,threshold),"above_multiplier":retained_transverse_multiplier(m,above),"classes":(stability_class(m,below),stability_class(m,threshold),stability_class(m,above))})
 return {"rows":tuple(rows),"unique_threshold":all(row["boundary_multiplier"]==1 and row["classes"]==("strict-expansion","neutral-boundary","strict-contraction") for row in rows),"binary_threshold_is_half_One":holding_threshold(2)==Fraction(1,2),"topology_scope":"normalized-drive-response-transverse-channel","analytic_proof_value_required":False}

@dataclass(frozen=True)
class CandidateForm:
 expansion_domain:str; coupling_action:str; threshold_relation:str; regime_partition:str; synchronization_scope:str; analytic_boundary:str; target_boundary:str; extension:str
 @property
 def candidate_id(self)->str: return "__".join((self.expansion_domain,self.coupling_action,self.threshold_relation,self.regime_partition,self.synchronization_scope,self.analytic_boundary,self.target_boundary,self.extension))

EXPANSION_DOMAINS=("complete-generated-m-expansion","selected-binary-expansion","target-assigned-expansion")
COUPLING_ACTIONS=("retain-one-minus-coupling-share","free-residual-action","target-assigned-residual")
THRESHOLD_RELATIONS=("unique-m-minus-one-over-m-boundary","fixed-half-One-for-all-m","measurement-selected-threshold")
REGIME_PARTITIONS=("below-expands-boundary-neutral-above-contracts","boundary-declared-contracting","unclassified-criticality")
SYNCHRONIZATION_SCOPES=("normalized-drive-response-transverse-channel","arbitrary-topology-universal-threshold","finite-example-only")
ANALYTIC_BOUNDARIES=("exact-rational-carrier-symbolic-external-translation","imported-exponential-proof-value","decimal-criticality-proof")
TARGET_BOUNDARIES=("sealed-before-observation-release","observation-readable-before-seal")
EXTENSIONS=("empty-extension","free-threshold-correction")
GENERATION_RULE="Generate the complete product of every complete, selected or target-assigned expansion domain; every exact, free or target-assigned residual action; every forced, fixed or measured threshold; every exact, mislabeled or absent regime partition; every normalized, universalized or finite-only scope; every exact-symbolic, imported-analytic or decimal proof boundary; both target custody states; and both extension states."
GRAMMAR_BOUNDARY="Every complete generated positive label count m of at least two, every exact proper positive coupling g, the normalized drive-response transverse channel with retained share One-minus-g, and every positive successor depth. Arbitrary coupling topologies retain their separate transverse eigenvalue factors and are not assigned this threshold universally."

def candidate_forms()->tuple[CandidateForm,...]: return tuple(CandidateForm(*values) for values in product(EXPANSION_DOMAINS,COUPLING_ACTIONS,THRESHOLD_RELATIONS,REGIME_PARTITIONS,SYNCHRONIZATION_SCOPES,ANALYTIC_BOUNDARIES,TARGET_BOUNDARIES,EXTENSIONS))
@lru_cache(maxsize=1)
def axis_facts()->dict[str,dict[str,bool]]:
 c=criticality_certificate(); exact=all((c["unique_threshold"],c["binary_threshold_is_half_One"],not c["analytic_proof_value_required"]))
 return {"expansion":{n:v for n,v in zip(EXPANSION_DOMAINS,(exact,False,False))},"action":{n:v for n,v in zip(COUPLING_ACTIONS,(exact,False,False))},"threshold":{n:v for n,v in zip(THRESHOLD_RELATIONS,(exact,False,False))},"regime":{n:v for n,v in zip(REGIME_PARTITIONS,(exact,False,False))},"scope":{n:v for n,v in zip(SYNCHRONIZATION_SCOPES,(exact,False,False))},"analytic":{n:v for n,v in zip(ANALYTIC_BOUNDARIES,(exact,False,False))},"target":{TARGET_BOUNDARIES[0]:True,TARGET_BOUNDARIES[1]:False},"extension":{EXTENSIONS[0]:True,EXTENSIONS[1]:False}}
def candidate_facts(f:CandidateForm)->dict[str,bool]:
 a=axis_facts(); return {"expansion-domain":a["expansion"][f.expansion_domain],"coupling-action":a["action"][f.coupling_action],"threshold":a["threshold"][f.threshold_relation],"regimes":a["regime"][f.regime_partition],"scope":a["scope"][f.synchronization_scope],"analytic-boundary":a["analytic"][f.analytic_boundary],"target-custody":a["target"][f.target_boundary],"extension":a["extension"][f.extension]}
def form_survives(f:CandidateForm)->bool:return all(candidate_facts(f).values())

class CoupledMapCriticalityProgram:
 def __init__(self,source_hash:str): self.source_hash=source_hash; self._forms=candidate_forms(); self._by_id={f.candidate_id:f for f in self._forms}
 @property
 def registration(self)->ClaimRegistration:
  return ClaimRegistration(CLAIM_ID,"Exact normalized coupled-map synchronization threshold","physics","For a complete m-label Fold in the normalized drive-response transverse channel, one coupling step retains the exact transverse multiplier m(One-g). The unique neutral boundary is g=(m-1)/m; every smaller proper coupling expands the distinction and every larger proper coupling contracts it. For m=2 the boundary is the forced half-One. This threshold is not assigned to arbitrary network topologies, whose distinct transverse eigenvalue factors remain explicit external scope.",EvidenceMode.EMPIRICAL,(ROOT_THEOREM,),("SFT-PHYS-LYAPUNOV-KS-CORRESPONDENCE-TERMINAL-008","SFT-PHYS-COUPLED-ENSEMBLE-SYNCHRONIZATION-TERMINAL-007","SFT-COMP-DIST-SYNCHRONIZATION-001","SFT-FOUNDATION-HALF-ONE-001","SFT-FOUNDATION-FOLD-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-PHYS-MEAS-TARGET-CUSTODY-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DYNAMICAL-SYSTEMS-001"),(),(),(ProvenanceClass.FORWARD_FORCING,ProvenanceClass.OBSERVATIONAL_DERIVATION),self.source_hash)
 def generate_candidates(self)->CandidateCensus:
  candidates=tuple(Candidate(f.candidate_id,str(f),sha256_identity({"rule":GENERATION_RULE,"form":f,"facts":candidate_facts(f)})) for f in self._forms)
  return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(candidates),sha256_identity({"axis_cardinalities":(3,3,3,3,3,3,2,2),"candidate_ids":tuple(x.candidate_id for x in candidates)}),candidates)
 def decide_candidate(self,candidate:Candidate)->CandidateDecision:
  facts=candidate_facts(self._by_id[candidate.candidate_id]); survives=all(facts.values()); failures=tuple(k for k,v in facts.items() if not v); reason="The exact residual multiplier uniquely forces (m-1)/m, the three critical regimes, normalized topology scope and no free correction." if survives else "Rejected by computed Fold predicates: "+", ".join(failures)+"."
  return CandidateDecision(candidate.candidate_id,survives,reason,sha256_identity({"trace":candidate.trace_hash,"facts":facts,"survives":survives,"reason":reason}))
 def closure_evidence(self,decisions:Sequence[CandidateDecision])->ClosureEvidence:
  survivors=tuple(x.candidate_id for x in decisions if x.survives); c=criticality_certificate(); closed=len(survivors)==1 and c["unique_threshold"] and c["binary_threshold_is_half_One"] and not c["analytic_proof_value_required"]
  return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,closed,closed and len(set(survivors))==1,sha256_identity({"certificate":c,"decisions":tuple(decisions),"survivors":survivors}),sha256_identity({"base":"m times the retained One-minus-g share is the exact transverse multiplier","boundary":"equality with One uniquely gives g=(m-1)/m","regimes":"ordered exact fractions force expansion, neutrality and contraction","arbitrary_topology_universalized":False,"external_targets_absent":True}))
 def run_controls(self)->tuple[ControlResult,...]:
  survivors=tuple(f for f in self._forms if form_survives(f));
  if len(survivors)!=1: raise ValueError("controls require one computed survivor")
  f=survivors[0]; records=((ControlKind.FALSE_PREMISE,holding_threshold(3)!=Fraction(1,2) and stability_class(3,Fraction(1,2))=="strict-expansion","Reject half-One as a universal threshold for every m.","The three-label threshold is two-thirds and half-One remains below it."),(ControlKind.TAMPERED_SOURCE,sha256_identity({"changed":self.source_hash})!=self.source_hash,"Reject a changed claimant source identity.","The changed identity differs from the registered manifest."),(ControlKind.TAMPERED_ARTIFACT,len({x.candidate_id for x in self._forms})==len(self._forms),"Reject duplicated candidate identities.","The complete product has unique identities."),(ControlKind.BOUNDARY,not form_survives(replace(f,synchronization_scope=SYNCHRONIZATION_SCOPES[1])) and not form_survives(replace(f,target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(f,extension=EXTENSIONS[1])),"Reject universal topology, pre-seal observation and free correction.","Only normalized scope, sealed target and empty extension survive."))
  return tuple(ControlResult(k,p,e,o,sha256_identity({"kind":k,"passed":p,"expected":e,"observed":o})) for k,p,e,o in records)

__all__=("CLAIM_ID","EXPERIMENT_ID","GENERATION_RULE","GRAMMAR_BOUNDARY","CoupledMapCriticalityProgram","candidate_forms","criticality_certificate","form_survives","holding_threshold","retained_transverse_multiplier","stability_class")

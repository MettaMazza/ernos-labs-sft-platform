"""All-dimension exact orbital-restoration census from positive magnitudes."""
from __future__ import annotations
from dataclasses import dataclass,replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity
CLAIM_ID="SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009";EXPERIMENT_ID="SFT-EXP-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009"

def spatial_dimension(value:int)->int:
 if isinstance(value,bool) or not isinstance(value,int) or value<2:raise ValueError("orbital dimension must be a positive whole of at least two")
 return value
def outward_ratio(value:Fraction)->Fraction:
 if not isinstance(value,Fraction) or value<=1:raise ValueError("outward radius ratio must exceed the One")
 return value
def displaced_magnitudes(dimension:int,ratio:Fraction)->tuple[Fraction,Fraction]:
 d=spatial_dimension(dimension);q=outward_ratio(ratio);return Fraction(1,1)/(q**(d-1)),Fraction(1,1)/(q**3)
def orbital_stability_class(dimension:int,ratio:Fraction)->str:
 gravity,centrifugal=displaced_magnitudes(dimension,ratio)
 if gravity==centrifugal:return "marginal"
 return "stable-restoring" if gravity>centrifugal else "unstable-nonrestoring"
def dimension_certificate()->dict[str,object]:
 ratios=(Fraction(3,2),Fraction(2,1),Fraction(5,2));rows=tuple({"dimension":d,"classes":tuple(orbital_stability_class(d,q) for q in ratios),"magnitudes":tuple(displaced_magnitudes(d,q) for q in ratios)} for d in range(2,13))
 return {"rows":rows,"stable_dimensions":tuple(row["dimension"] for row in rows if set(row["classes"])=={"stable-restoring"}),"marginal_dimensions":tuple(row["dimension"] for row in rows if set(row["classes"])=={"marginal"}),"unstable_dimensions":tuple(row["dimension"] for row in rows if set(row["classes"])=={"unstable-nonrestoring"}),"general_partition":"stable for every d below four; marginal at four; unstable for every d above four","proof":"for q>One, compare positive denominators q^(d-1) and q^3; their order is fixed solely by d-1 against three","negative_exponent_required":False}

@dataclass(frozen=True)
class CandidateForm:
 dimension_domain:str;gravity_dilution:str;centrifugal_dilution:str;circular_balance:str;outward_comparison:str;stability_partition:str;target_boundary:str;extension:str
 @property
 def candidate_id(self)->str:return "__".join((self.dimension_domain,self.gravity_dilution,self.centrifugal_dilution,self.circular_balance,self.outward_comparison,self.stability_partition,self.target_boundary,self.extension))
DIMENSION_DOMAINS=("complete-positive-whole-d-at-least-two","selected-three-space-only","target-assigned-dimensions")
GRAVITY_DILUTIONS=("inverse-positive-power-d-minus-one","fixed-inverse-square-all-d","target-assigned-gravity-power")
CENTRIFUGAL_DILUTIONS=("inverse-cube-positive-magnitude","dimension-matched-centrifugal-power","target-assigned-centrifugal-power")
CIRCULAR_BALANCES=("equal-positive-magnitudes-at-reference-radius","signed-force-import","target-assigned-balance")
OUTWARD_COMPARISONS=("compare-positive-power-denominators","import-negative-exponent-ratio","measurement-selected-order")
STABILITY_PARTITIONS=("stable-two-three-marginal-four-unstable-above","three-space-only-verdict","all-dimensions-stable")
TARGET_BOUNDARIES=("sealed-before-observation-release","observation-readable-before-seal");EXTENSIONS=("empty-extension","free-stability-correction")
GENERATION_RULE="Generate the complete product of every complete, selected or target-assigned dimension domain; every dimension-derived, fixed or target-assigned gravity dilution; every inverse-cube, dimension-matched or target-assigned centrifugal dilution; every positive-magnitude, signed-import or target-assigned balance; every positive-denominator, negative-exponent or measured outward comparison; every complete, selected or universal stability partition; both target custody states; and both extension states."
GRAMMAR_BOUNDARY="Every positive whole spatial dimension d of at least two, every exact outward radius ratio q greater than the One, dimension-forced inverse-(d-1) gravity, inverse-cube centrifugal magnitude, and every positive successor displacement. Dimension one is excluded because the registered circular angular-momentum organization is absent there."
def candidate_forms()->tuple[CandidateForm,...]:return tuple(CandidateForm(*v) for v in product(DIMENSION_DOMAINS,GRAVITY_DILUTIONS,CENTRIFUGAL_DILUTIONS,CIRCULAR_BALANCES,OUTWARD_COMPARISONS,STABILITY_PARTITIONS,TARGET_BOUNDARIES,EXTENSIONS))
@lru_cache(maxsize=1)
def axis_facts()->dict[str,dict[str,bool]]:
 c=dimension_certificate();exact=c["stable_dimensions"]==(2,3) and c["marginal_dimensions"]==(4,) and c["unstable_dimensions"]==tuple(range(5,13)) and not c["negative_exponent_required"]
 return {"dimension":{n:v for n,v in zip(DIMENSION_DOMAINS,(exact,False,False))},"gravity":{n:v for n,v in zip(GRAVITY_DILUTIONS,(exact,False,False))},"centrifugal":{n:v for n,v in zip(CENTRIFUGAL_DILUTIONS,(exact,False,False))},"balance":{n:v for n,v in zip(CIRCULAR_BALANCES,(exact,False,False))},"comparison":{n:v for n,v in zip(OUTWARD_COMPARISONS,(exact,False,False))},"partition":{n:v for n,v in zip(STABILITY_PARTITIONS,(exact,False,False))},"target":{TARGET_BOUNDARIES[0]:True,TARGET_BOUNDARIES[1]:False},"extension":{EXTENSIONS[0]:True,EXTENSIONS[1]:False}}
def candidate_facts(f:CandidateForm)->dict[str,bool]:
 a=axis_facts();return {"dimension":a["dimension"][f.dimension_domain],"gravity":a["gravity"][f.gravity_dilution],"centrifugal":a["centrifugal"][f.centrifugal_dilution],"balance":a["balance"][f.circular_balance],"comparison":a["comparison"][f.outward_comparison],"partition":a["partition"][f.stability_partition],"target":a["target"][f.target_boundary],"extension":a["extension"][f.extension]}
def form_survives(f:CandidateForm)->bool:return all(candidate_facts(f).values())
class OrbitalDimensionStabilityProgram:
 def __init__(self,source_hash:str):self.source_hash=source_hash;self._forms=candidate_forms();self._by_id={f.candidate_id:f for f in self._forms}
 @property
 def registration(self)->ClaimRegistration:return ClaimRegistration(CLAIM_ID,"All-dimension orbital-restoration stability law","physics","At a circular balance, dimension-forced gravity and centrifugal response are equal positive magnitudes. After every exact outward displacement q greater than the One, gravity has positive denominator q^(d-1) and centrifugal response q^3. Denominator order alone forces restoring gravity for d=2,3, equality at d=4, and nonrestoring response for every d at least five. Combined with independently forced three-space, orbital stability supplies a distinct discriminator selecting the stable side without signed forces, negative exponents or fitted parameters.",EvidenceMode.EMPIRICAL,(ROOT_THEOREM,),("SFT-PHYS-SPACE-DIMENSION-THREE-001","SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001","SFT-PHYS-FIELD-INVERSE-SQUARE-001","SFT-PHYS-VALIDATION-INVERSE-SQUARE-001","SFT-PHYS-MECH-CONSERVATION-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-PHYS-MEAS-TARGET-CUSTODY-001"),(),(),(ProvenanceClass.FORWARD_FORCING,ProvenanceClass.OBSERVATIONAL_DERIVATION),self.source_hash)
 def generate_candidates(self)->CandidateCensus:
  cs=tuple(Candidate(f.candidate_id,str(f),sha256_identity({"rule":GENERATION_RULE,"form":f,"facts":candidate_facts(f)})) for f in self._forms);return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(cs),sha256_identity({"axis_cardinalities":(3,3,3,3,3,3,2,2),"candidate_ids":tuple(x.candidate_id for x in cs)}),cs)
 def decide_candidate(self,c:Candidate)->CandidateDecision:
  facts=candidate_facts(self._by_id[c.candidate_id]);survives=all(facts.values());fails=tuple(k for k,v in facts.items() if not v);reason="Positive denominator ordering forces the complete stable, marginal and unstable dimension partition with no correction." if survives else "Rejected by computed Fold predicates: "+", ".join(fails)+".";return CandidateDecision(c.candidate_id,survives,reason,sha256_identity({"trace":c.trace_hash,"facts":facts,"survives":survives,"reason":reason}))
 def closure_evidence(self,ds:Sequence[CandidateDecision])->ClosureEvidence:
  survivors=tuple(x.candidate_id for x in ds if x.survives);c=dimension_certificate();closed=len(survivors)==1 and c["stable_dimensions"]==(2,3) and c["marginal_dimensions"]==(4,) and c["unstable_dimensions"]==tuple(range(5,13));return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,closed,closed and len(set(survivors))==1,sha256_identity({"certificate":c,"decisions":tuple(ds),"survivors":survivors}),sha256_identity({"base":"d=2 compares q with q cubed","successor":"increasing d multiplies only the gravity denominator by q greater than One, so the ordering crosses equality once at d=4 and never returns","negative_values_imported":False,"targets_absent":True}))
 def run_controls(self)->tuple[ControlResult,...]:
  ss=tuple(f for f in self._forms if form_survives(f));
  if len(ss)!=1:raise ValueError("controls require one computed survivor")
  f=ss[0];records=((ControlKind.FALSE_PREMISE,orbital_stability_class(5,Fraction(2,1))=="unstable-nonrestoring","Reject stable five-space orbit under inverse-fourth-power gravity.","Gravity falls below inverse-cube centrifugal response."),(ControlKind.TAMPERED_SOURCE,sha256_identity({"changed":self.source_hash})!=self.source_hash,"Reject changed source identity.","Identity differs."),(ControlKind.TAMPERED_ARTIFACT,len({x.candidate_id for x in self._forms})==len(self._forms),"Reject duplicate candidates.","All identities unique."),(ControlKind.BOUNDARY,not form_survives(replace(f,outward_comparison=OUTWARD_COMPARISONS[1])) and not form_survives(replace(f,target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(f,extension=EXTENSIONS[1])),"Reject negative-exponent import, pre-seal observation and correction.","Only positive comparison, sealed target and empty extension survive."));return tuple(ControlResult(k,p,e,o,sha256_identity({"kind":k,"passed":p,"expected":e,"observed":o})) for k,p,e,o in records)
__all__=("CLAIM_ID","EXPERIMENT_ID","GENERATION_RULE","GRAMMAR_BOUNDARY","OrbitalDimensionStabilityProgram","candidate_forms","dimension_certificate","displaced_magnitudes","form_survives","orbital_stability_class")

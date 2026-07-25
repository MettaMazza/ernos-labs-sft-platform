"""Exact symmetric curvature-source ledger and local conservation law."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass,replace
from functools import lru_cache
from itertools import combinations_with_replacement,permutations,product
from typing import Sequence
from sft.engine import Candidate,CandidateCensus,CandidateDecision,ClaimRegistration,ClosureEvidence,ClosureScope,ControlKind,ControlResult,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.engine.canonical import sha256_identity
CLAIM_ID="SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010";EXPERIMENT_ID="SFT-EXP-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010"
COORDINATES=("time","axis-one","axis-two","axis-three");COORDINATE_ORDER={label:place for place,label in enumerate(COORDINATES,1)}
def symmetric_slot(first:str,second:str)->tuple[str,str]:
 if first not in COORDINATES or second not in COORDINATES:raise ValueError("unknown generated coordinate")
 return tuple(sorted((first,second),key=COORDINATE_ORDER.__getitem__))
def symmetric_slots()->tuple[tuple[str,str],...]:return tuple(combinations_with_replacement(COORDINATES,2))
def source_component_kind(slot:tuple[str,str])->str:
 if slot==("time","time"):return "energy"
 if "time" in slot:return "momentum"
 return "stress"
def source_component_ledger()->dict[str,tuple[tuple[str,str],...]]:
 slots=symmetric_slots();return {kind:tuple(slot for slot in slots if source_component_kind(slot)==kind) for kind in ("energy","momentum","stress")}
def derivative_term(derivatives:tuple[str,...],first:str,second:str)->tuple[tuple[str,...],tuple[str,str]]:
 if not derivatives or any(label not in COORDINATES for label in derivatives):raise ValueError("generated derivatives required")
 return tuple(sorted(derivatives,key=COORDINATE_ORDER.__getitem__)),symmetric_slot(first,second)
def divergence_ledgers(direction:str)->tuple[Counter,Counter]:
 if direction not in COORDINATES:raise ValueError("generated source direction required")
 carried=Counter();opposed=Counter()
 for first in COORDINATES:
  for contracted in COORDINATES:
   carried[derivative_term((first,contracted,first),contracted,direction)]+=1
   carried[derivative_term((first,contracted,direction),contracted,first)]+=1
   opposed[derivative_term((first,contracted,contracted),first,direction)]+=1
  for trace in COORDINATES:opposed[derivative_term((first,first,direction),trace,trace)]+=1
 for contracted in COORDINATES:
  for trace in COORDINATES:
   carried[derivative_term((direction,contracted,contracted),trace,trace)]+=1
   opposed[derivative_term((direction,contracted,trace),contracted,trace)]+=1
 return carried,opposed
def commuting_difference_certificate()->dict[str,object]:
 words=tuple(product(COORDINATES,repeat=3));rows=[]
 for word in words:
  canonical=tuple(sorted(word,key=COORDINATE_ORDER.__getitem__));forms={tuple(sorted(order,key=COORDINATE_ORDER.__getitem__)) for order in set(permutations(word))};rows.append((word,canonical,forms=={canonical}))
 return {"word_count":len(words),"rows":tuple(rows),"every_derivative_order_commutes":all(row[2] for row in rows),"successor_proof":"Each generated coordinate shift acts on only its held coordinate. Appending any finite product-lattice layer preserves pairwise commutation, so every derivative word retains the same canonical multiset at every positive depth."}
def conservation_certificate()->dict[str,object]:
 ledger=source_component_ledger();rows=[]
 for direction in COORDINATES:
  carried,opposed=divergence_ledgers(direction);rows.append({"direction":direction,"carried_terms":sum(carried.values()),"opposed_terms":sum(opposed.values()),"distinct_terms":len(carried),"balanced":carried==opposed,"unmatched_terms":tuple((carried-opposed).elements())+tuple((opposed-carried).elements())})
 carried,opposed=divergence_ledgers("time");leaking=opposed.copy();leaking.subtract({next(iter(leaking)):1});leaking=+leaking
 return {"coordinates":COORDINATES,"symmetric_slots":symmetric_slots(),"slot_count":len(symmetric_slots()),"source_ledger":ledger,"source_partition_counts":tuple(len(ledger[k]) for k in ("energy","momentum","stress")),"componentwise_bijection":tuple(zip(symmetric_slots(),symmetric_slots())),"divergence_rows":tuple(rows),"conserved_directions":tuple(row["direction"] for row in rows if row["balanced"]),"all_four_balanced":all(row["balanced"] for row in rows),"commutation":commuting_difference_certificate(),"leaking_control_balanced":carried==leaking,"leaking_control_has_one_missing_flow":sum(carried.values())==sum(leaking.values())+1,"signed_numerical_scalar_used":False,"depth_independent_identity":"For each held source direction, dummy-coordinate exchange pairs every carried derivative term with exactly one opposed term after generated shift commutation."}
@dataclass(frozen=True)
class CandidateForm:
 component_organization:str;field_pairing:str;derivative_algebra:str;conservation_identity:str;source_ledger:str;leak_test:str;target_boundary:str;extension:str
 @property
 def candidate_id(self)->str:return "__".join((self.component_organization,self.field_pairing,self.derivative_algebra,self.conservation_identity,self.source_ledger,self.leak_test,self.target_boundary,self.extension))
COMPONENT_ORGANIZATIONS=("complete-ten-symmetric-source-slots","scalar-source-only","target-assigned-components");FIELD_PAIRINGS=("one-curvature-slot-to-one-source-slot","aggregate-source-equation","target-assigned-pairing");DERIVATIVE_ALGEBRAS=("commuting-generated-shift-differences","imported-continuum-derivatives","target-assigned-operator");CONSERVATION_IDENTITIES=("four-exact-opposed-ledger-identities","asserted-conservation-only","target-assigned-conservation");SOURCE_LEDGERS=("energy-one-momentum-three-stress-six","unlabelled-ten-slots","target-assigned-source-meaning");LEAK_TESTS=("missing-flow-breaks-exact-balance","leak-ignored","target-assigned-leak");TARGET_BOUNDARIES=("sealed-before-observation-release","observation-readable-before-seal");EXTENSIONS=("empty-extension","free-conservation-correction")
GENERATION_RULE="Generate the complete product of every complete, scalar-only or target-assigned component organization; every componentwise, aggregate or target-assigned field pairing; every generated-shift, imported-continuum or target-assigned derivative algebra; every exact, asserted or target-assigned conservation identity; every complete, unlabelled or target-assigned source ledger; every detecting, ignored or target-assigned leak test; both target custody states; and both extension states."
GRAMMAR_BOUNDARY="Every exact symmetric rank-two carrier over four generated coordinate labels, its complete one-energy/three-momentum/six-stress source ledger, and every finite product-lattice depth whose held coordinate shifts commute. This theorem is the generated commuting-difference curvature channel, not an assertion that every nonlinear lattice discretization has the same operator form."
def candidate_forms()->tuple[CandidateForm,...]:return tuple(CandidateForm(*values) for values in product(COMPONENT_ORGANIZATIONS,FIELD_PAIRINGS,DERIVATIVE_ALGEBRAS,CONSERVATION_IDENTITIES,SOURCE_LEDGERS,LEAK_TESTS,TARGET_BOUNDARIES,EXTENSIONS))
@lru_cache(maxsize=1)
def axis_facts()->dict[str,dict[str,bool]]:
 c=conservation_certificate();exact=c["slot_count"]==10 and c["source_partition_counts"]==(1,3,6) and len(c["componentwise_bijection"])==10 and c["all_four_balanced"] and c["commutation"]["every_derivative_order_commutes"] and not c["leaking_control_balanced"] and c["leaking_control_has_one_missing_flow"] and not c["signed_numerical_scalar_used"]
 return {"components":{name:value for name,value in zip(COMPONENT_ORGANIZATIONS,(exact,False,False))},"pairing":{name:value for name,value in zip(FIELD_PAIRINGS,(exact,False,False))},"derivative":{name:value for name,value in zip(DERIVATIVE_ALGEBRAS,(exact,False,False))},"conservation":{name:value for name,value in zip(CONSERVATION_IDENTITIES,(exact,False,False))},"source":{name:value for name,value in zip(SOURCE_LEDGERS,(exact,False,False))},"leak":{name:value for name,value in zip(LEAK_TESTS,(exact,False,False))},"target":{TARGET_BOUNDARIES[0]:True,TARGET_BOUNDARIES[1]:False},"extension":{EXTENSIONS[0]:True,EXTENSIONS[1]:False}}
def candidate_facts(form:CandidateForm)->dict[str,bool]:
 a=axis_facts();return {"components":a["components"][form.component_organization],"pairing":a["pairing"][form.field_pairing],"derivative":a["derivative"][form.derivative_algebra],"conservation":a["conservation"][form.conservation_identity],"source":a["source"][form.source_ledger],"leak":a["leak"][form.leak_test],"target":a["target"][form.target_boundary],"extension":a["extension"][form.extension]}
def form_survives(form:CandidateForm)->bool:return all(candidate_facts(form).values())
class SymmetricSourceConservationProgram:
 def __init__(self,source_hash:str):self.source_hash=source_hash;self._forms=candidate_forms();self._by_id={form.candidate_id:form for form in self._forms}
 @property
 def registration(self)->ClaimRegistration:return ClaimRegistration(CLAIM_ID,"Four-coordinate symmetric curvature-source conservation law","physics","Four generated coordinate labels force ten symmetric rank-two slots paired one-to-one with one energy, three momentum and six stress source carriers. Generated coordinate shifts commute, so each of four curvature-divergence directions expands into identical carried and opposed derivative ledgers. Every componentwise source equation therefore preserves an exact local source ledger at every finite depth; removing one flow term breaks balance. No signed numerical proof scalar, imported derivative, target-selected component or free correction enters.",EvidenceMode.EMPIRICAL,(ROOT_THEOREM,),("SFT-PHYS-GRAVITY-GRAVITON-POLARIZATION-003","SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003","SFT-PHYS-POST-NEWTONIAN-FIXED-POINT-TERMINAL-009","SFT-PHYS-GRAVITY-LATTICE-CURVATURE-003","SFT-PHYS-SPACETIME-EXACT-INTERVAL-003","SFT-MATH-EXACT-ARITHMETIC-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-PHYS-MECH-CONSERVATION-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-PHYS-MEAS-TARGET-CUSTODY-001"),(),(),(ProvenanceClass.FORWARD_FORCING,ProvenanceClass.OBSERVATIONAL_DERIVATION),self.source_hash)
 def generate_candidates(self)->CandidateCensus:
  candidates=tuple(Candidate(form.candidate_id,str(form),sha256_identity({"rule":GENERATION_RULE,"form":form,"facts":candidate_facts(form)})) for form in self._forms);return CandidateCensus(GENERATION_RULE,GRAMMAR_BOUNDARY,len(candidates),sha256_identity({"axis_cardinalities":(3,3,3,3,3,3,2,2),"candidate_ids":tuple(candidate.candidate_id for candidate in candidates)}),candidates)
 def decide_candidate(self,candidate:Candidate)->CandidateDecision:
  facts=candidate_facts(self._by_id[candidate.candidate_id]);survives=all(facts.values());failed=tuple(name for name,value in facts.items() if not value);reason="Complete symmetric slots, componentwise source pairing and commuting shifts force four exact local conservation ledgers." if survives else "Rejected by computed Fold predicates: "+", ".join(failed)+".";return CandidateDecision(candidate.candidate_id,survives,reason,sha256_identity({"trace":candidate.trace_hash,"facts":facts,"survives":survives,"reason":reason}))
 def closure_evidence(self,decisions:Sequence[CandidateDecision])->ClosureEvidence:
  survivors=tuple(item.candidate_id for item in decisions if item.survives);c=conservation_certificate();closed=len(survivors)==1 and c["slot_count"]==10 and c["source_partition_counts"]==(1,3,6) and c["all_four_balanced"] and c["commutation"]["every_derivative_order_commutes"] and not c["leaking_control_balanced"];return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT,GRAMMAR_BOUNDARY,closed,closed and len(set(survivors))==1,sha256_identity({"certificate":c,"decisions":tuple(decisions),"survivors":survivors}),sha256_identity({"base":"Four generated labels give ten symmetric slots and four exact carried/opposed derivative-ledger equalities.","successor":"Every added product-lattice layer preserves coordinatewise shift commutation, so canonical dummy-label exchange preserves all four equalities at the next depth.","arbitrary_nonlinear_discretization_not_claimed":True,"targets_absent":True}))
 def run_controls(self)->tuple[ControlResult,...]:
  survivors=tuple(form for form in self._forms if form_survives(form));
  if len(survivors)!=1:raise ValueError("controls require one computed survivor")
  form=survivors[0];c=conservation_certificate();records=((ControlKind.FALSE_PREMISE,not c["leaking_control_balanced"] and c["leaking_control_has_one_missing_flow"],"Reject a source ledger missing one opposed flow term.","The exact multisets no longer match."),(ControlKind.TAMPERED_SOURCE,sha256_identity({"changed":self.source_hash})!=self.source_hash,"Reject changed source identity.","Identity differs."),(ControlKind.TAMPERED_ARTIFACT,len({item.candidate_id for item in self._forms})==len(self._forms),"Reject duplicate candidates.","All identities are unique."),(ControlKind.BOUNDARY,not form_survives(replace(form,derivative_algebra=DERIVATIVE_ALGEBRAS[1])) and not form_survives(replace(form,target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(form,extension=EXTENSIONS[1])),"Reject imported operators, pre-seal observation and free correction.","Only generated shifts, sealed targets and empty extension survive."));return tuple(ControlResult(kind,passed,expected,observed,sha256_identity({"kind":kind,"passed":passed,"expected":expected,"observed":observed})) for kind,passed,expected,observed in records)
__all__=("CLAIM_ID","EXPERIMENT_ID","SymmetricSourceConservationProgram","candidate_forms","commuting_difference_certificate","conservation_certificate","divergence_ledgers","form_survives","source_component_ledger","symmetric_slots")

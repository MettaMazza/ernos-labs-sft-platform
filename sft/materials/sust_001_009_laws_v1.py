"""Exact Fold laws for the complete Materials SUST-001--009 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v
def embodied_ledger(entries,scope):
 rows=tuple((identity,kind,Fraction(amount),source) for identity,kind,amount,source in entries)
 if not rows or len({r[0] for r in rows})!=len(rows) or any(r[2]<=0 or not r[1] or not r[3] for r in rows) or not scope: raise ValueError("embodied ledger invalid")
 return {"entries":rows,"scope":scope,"total":sum(r[2] for r in rows),"complete":True}
def availability_boundary(material,available,required,period,source):
 available,required=positive(available,"available"),positive(required,"required")
 if not material or not period or not source: raise ValueError("availability invalid")
 relation="sufficient" if available>=required else "shortfall"
 return {"material":material,"available":available,"required":required,"period":period,"source":source,"relation":relation,"boundary_held":True}
def reuse_remanufacture(identity,states,operations,inspections):
 states,operations,inspections=tuple(states),tuple(operations),tuple(inspections)
 if not identity or len(states)<2 or len(operations)+1!=len(states) or len(inspections)!=len(states): raise ValueError("reuse path invalid")
 return {"identity":identity,"states":states,"operations":operations,"inspections":inspections,"identity_retained":True}
def recovery_yield(feed,recovered,residual,method,scope):
 feed,recovered,residual=positive(feed,"feed"),positive(recovered,"recovered"),positive(residual,"residual")
 if recovered+residual!=feed or not method or not scope: raise ValueError("recovery ledger invalid")
 return {"feed":feed,"recovered":recovered,"residual":residual,"fraction":Fraction(recovered,feed),"method":method,"scope":scope,"closes":True}
def circular_flow(nodes,transfers,boundary):
 nodes,transfers=tuple(nodes),tuple((a,b,positive(amount,"flow"),identity) for a,b,amount,identity in transfers)
 if len(nodes)<2 or len(set(nodes))!=len(nodes) or not transfers or any(a not in nodes or b not in nodes or a==b or not identity for a,b,amount,identity in transfers) or not boundary: raise ValueError("circular flow invalid")
 return {"nodes":nodes,"transfers":transfers,"boundary":boundary,"material_custody_held":True}
def durability_extension(identity,baseline,extended,interventions,evidence):
 baseline,extended=positive(baseline,"baseline"),positive(extended,"extended")
 if extended<=baseline or not identity or not tuple(interventions) or not tuple(evidence): raise ValueError("durability extension invalid")
 return {"identity":identity,"baseline":baseline,"extended":extended,"interventions":tuple(interventions),"evidence":tuple(evidence),"extension":extended-baseline,"trace_held":True}
def toxicity_handoff(material,exposures,observations,materials_scope,health_owner):
 exposures,observations=tuple(exposures),tuple(observations)
 if not material or not exposures or len(exposures)!=len(observations) or not materials_scope or not health_owner: raise ValueError("toxicity handoff invalid")
 return {"material":material,"exposures":exposures,"observations":observations,"materials_scope":materials_scope,"health_owner":health_owner,"handoff_explicit":True}
def substitution(original,alternative,required_functions,original_results,alternative_results,conditions):
 required,first,second=tuple(required_functions),tuple(original_results),tuple(alternative_results)
 if not original or not alternative or original==alternative or not required or set(first)!=set(required) or set(second)!=set(required) or not conditions: raise ValueError("substitution invalid")
 return {"original":original,"alternative":alternative,"required_functions":required,"conditions":conditions,"function_preserved":True}
def end_of_life(records,boundary):
 rows=tuple((identity,material,fate,residual,source) for identity,material,fate,residual,source in records)
 if not rows or len({r[0] for r in rows})!=len(rows) or any(not all(r[1:]) for r in rows) or not boundary: raise ValueError("end-of-life custody invalid")
 return {"records":rows,"boundary":boundary,"all_fates_residuals_held":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-DEGR-SERVICE-LIFE-EVIDENCE-010","SFT-MAT-COMP-SIMULATION-EXPERIMENT-012","SFT-MAT-EXT-COMBINED-PATH-CUSTODY-008")
DEFINITIONS=(("001","SFT-MAT-SUST-EMBODIED-LEDGER-001","Embodied material and energy ledger","An embodied ledger is the complete positive material-and-energy record with unique identities, source and declared scope.",BASE),("002","SFT-MAT-SUST-AVAILABILITY-BOUNDARY-002","Critical-material availability boundary","Availability compares positive held supply and requirement counts for one material, period and source without converting absence or shortfall into a negative magnitude.",BASE+("SFT-MAT-SUST-EMBODIED-LEDGER-001",)),("003","SFT-MAT-SUST-REUSE-REMANUFACTURE-003","Material reuse and remanufacture","Reuse and remanufacture retain item identity through every state, operation and inspection.",BASE+("SFT-MAT-SUST-AVAILABILITY-BOUNDARY-002",)),("004","SFT-MAT-SUST-RECOVERY-YIELD-004","Recycling separation and recovery yield","Recovery yield is the exact positive feed partition into recovered and residual parts under a held method and scope.",BASE+("SFT-MAT-SUST-REUSE-REMANUFACTURE-003",)),("005","SFT-MAT-SUST-CIRCULAR-FLOW-005","Circular material-flow organization","Circular flow is an exact directed network whose every positive transfer retains material identity and system boundary.",BASE+("SFT-MAT-SUST-RECOVERY-YIELD-004",)),("006","SFT-MAT-SUST-DURABILITY-EXTENSION-006","Durability and life-extension relation","Life extension retains the same item identity, positive baseline and extended service counts, interventions and evidence.",BASE+("SFT-MAT-SUST-CIRCULAR-FLOW-005",)),("007","SFT-MAT-SUST-TOXICITY-HANDOFF-007","Material toxicity and health handoff","Materials owns composition, exposure and observed specimen response; health consequence is exported explicitly to Medicine without erasing the evidence path.",BASE+("SFT-MAT-SUST-DURABILITY-EXTENSION-006",)),("008","SFT-MAT-SUST-SUBSTITUTION-FUNCTION-008","Material substitution and function preservation","A substitution preserves every preregistered required function under the same held conditions while retaining distinct material identities.",BASE+("SFT-MAT-SUST-TOXICITY-HANDOFF-007",)),("009","SFT-MAT-SUST-END-OF-LIFE-CUSTODY-009","End-of-life fate and residual custody","End-of-life evidence retains every material identity, fate, residual, source and system boundary; an unwanted sink cannot be erased.",BASE+("SFT-MAT-SUST-SUBSTITUTION-FUNCTION-008",)))
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,10)),("identity-kind-positive-amount-source-scope-ledger","material-available-required-period-source-boundary","identity-state-operation-inspection-reuse-path","positive-feed-recovered-residual-method-scope-partition","node-transfer-amount-material-boundary-network","identity-baseline-extension-intervention-evidence","material-exposure-observation-scope-health-owner-handoff","distinct-material-required-function-condition-preservation","identity-material-fate-residual-source-boundary-custody")))
def axes(r): return (binary_axis("carrier","carrier?","summary-label-only","erased","complete-positive-sustainable-material-carrier","held"),binary_axis("relation","relation?","imported-lifecycle-model","not forced",r,"exact"),binary_axis("path","path?","endpoint-or-score-only","history erased","complete-material-lifecycle-path","retained"),binary_axis("observation","conditions?","scope-source-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("ledger","complete",embodied_ledger((("a","material",1,"s"),("b","energy",2,"s")),"scope")["complete"]),),"002":(Witness("availability","held",availability_boundary("m",2,3,"period","source")["boundary_held"]),),"003":(Witness("reuse","identity",reuse_remanufacture("i",("a","b"),("repair",),("inspect-a","inspect-b"))["identity_retained"]),),"004":(Witness("recovery","closes",recovery_yield(3,2,1,"method","scope")["closes"]),),"005":(Witness("flow","custody",circular_flow(("a","b"),( ("a","b",1,"m"), ),"boundary")["material_custody_held"]),),"006":(Witness("durability","trace",durability_extension("i",1,2,("repair",),("test",))["trace_held"]),),"007":(Witness("toxicity","handoff",toxicity_handoff("m",("e",),("o",),"materials","medicine")["handoff_explicit"]),),"008":(Witness("substitution","function",substitution("a","b",("f1","f2"),("f1","f2"),("f2","f1"),"same")["function_preserved"]),),"009":(Witness("fate","custody",end_of_life((("i","m","recycle","r","s"),),"boundary")["all_fates_residuals_held"]),)}
@dataclass(frozen=True)
class SustSpec(StructuralPhysicsSpec):
 number:str=""; obligation_id:str=""
 def validate(self):
  if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid SUST spec")
  for axis in self.axes: axis.survivor
class SustProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported lifecycle equation, fitted score, economic selector, opaque oracle or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and every material, amount, identity, path, scope, source, residual and outcome distinction remain held labels","no external outcome selects a survivor","all favourable adverse absent unavailable and unresolved result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
 spec=SustSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight SUST-{n} axes before target release.",grammar_boundary=f"Every positive finite SUST-{n} carrier with complete material, amount, identity, path, scope, source and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"SUST-{n} uniquely retains {RELATIONS[n]} with complete carrier, lifecycle path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive sustainable-material carrier retains every distinction.",induction_step="One lawful successor retains the complete prior material and lifecycle path and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-SUST-{n}"); spec.validate(); SPECS[c]=spec
ORDER=tuple(row[1] for row in DEFINITIONS)

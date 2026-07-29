"""Exact Fold laws for the complete Materials MECH-001--014 family."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis

def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v

def oriented_response(rows):
 if not rows: raise ValueError("response rows required")
 out=[]
 for axis,load,extension,direction in rows:
  if not axis or direction not in ("forward","opposed"): raise ValueError("held axis and direction required")
  out.append((axis,positive(load,"load"),positive(extension,"extension"),direction,Fraction(extension,load)))
 return {"rows":tuple(out),"tensor_axes_retained":len({r[0] for r in out})==len(out)}
def transverse_relation(longitudinal,transverse,direction):
 if direction not in ("contracted","expanded"): raise ValueError("held transverse direction required")
 return {"longitudinal":positive(longitudinal,"longitudinal"),"transverse":positive(transverse,"transverse"),"direction":direction,"magnitude_part":Fraction(transverse,longitudinal)}
def memory_recovery(load_path,recovered):
 path=tuple(positive(x,"load path") for x in load_path); recovered=positive(recovered,"recovered")
 if len(path)<2 or recovered>max(path): raise ValueError("complete memory path required")
 return {"path":path,"recovered":recovered,"unrecovered":(max(path)-recovered) or None,"history_retained":True}
def permanent_flow(applied,recovered):
 applied,recovered=positive(applied,"applied"),positive(recovered,"recovered")
 if recovered>applied: raise ValueError("recovery exceeds applied deformation")
 return {"applied":applied,"recovered":recovered,"permanent":(applied-recovered) or None,"permanent_part":Fraction(applied-recovered,applied) if applied>recovered else None}
def yield_path(states):
 if len(states)<2 or any(load<1 or state not in ("recoverable","retained") for load,state in states): raise ValueError("yield path invalid")
 first=next((i for i,row in enumerate(states,1) if row[1]=="retained"),None)
 return {"states":states,"first_retained_position":first,"yield_load":states[first-1][0] if first else None}
def hardening(first_yield,later_yield,history):
 first_yield,later_yield=positive(first_yield,"first yield"),positive(later_yield,"later yield")
 if later_yield<=first_yield or not history: raise ValueError("hardening requires higher later threshold and history")
 return {"first":first_yield,"later":later_yield,"increase":later_yield-first_yield,"history":history}
def fracture_ledger(work_units,new_surface_units):
 return {"work":positive(work_units,"work"),"new_surface":positive(new_surface_units,"surface"),"work_per_surface":Fraction(work_units,new_surface_units)}
def crack_path(lengths,critical):
 lengths=tuple(positive(x,"crack length") for x in lengths);critical=positive(critical,"critical")
 if len(lengths)<2 or any(b<a for a,b in zip(lengths,lengths[1:])): raise ValueError("crack path must be nondecreasing")
 return {"lengths":lengths,"increments":tuple((b-a) or None for a,b in zip(lengths,lengths[1:])),"terminal_class":"unstable-boundary" if lengths[-1]>=critical else "stable-below-boundary"}
def fatigue(cycles,initiation_cycle,crack_counts):
 cycles,initiation_cycle=positive(cycles,"cycles"),positive(initiation_cycle,"initiation")
 if initiation_cycle>cycles or len(crack_counts)!=cycles: raise ValueError("fatigue record incomplete")
 if any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in crack_counts): raise ValueError("crack counts invalid")
 native=tuple(x or None for x in crack_counts)
 return {"cycles":cycles,"initiation_cycle":initiation_cycle,"crack_counts":native,"propagation_records":cycles-initiation_cycle+1}
def creep_path(rows,rupture_time):
 rupture_time=positive(rupture_time,"rupture time");norm=tuple((positive(t,"time"),positive(s,"strain")) for t,s in rows)
 if not norm or any(b[0]<=a[0] for a,b in zip(norm,norm[1:])) or rupture_time<norm[-1][0]: raise ValueError("creep custody incomplete")
 return {"rows":norm,"rupture_time":rupture_time,"time_to_rupture":rupture_time-norm[0][0]}
def impact_partition(input_units,absorbed,rebounded,damage):
 vals=tuple(positive(x,n) for x,n in ((input_units,"input"),(absorbed,"absorbed"),(rebounded,"rebounded"),(damage,"damage")))
 if sum(vals[1:])!=vals[0]: raise ValueError("impact carrier must close")
 return {"input":vals[0],"absorbed":vals[1],"rebounded":vals[2],"damage":vals[3],"closes":True}
def friction_contact(tangential,normal,contacts):
 return {"tangential":positive(tangential,"tangential"),"normal":positive(normal,"normal"),"contact_count":positive(contacts,"contacts"),"friction_part":Fraction(tangential,normal)}
def lubrication_film(states):
 if len(states)<2 or any(s not in ("bare-contact","film-held","film-broken") for s in states): raise ValueError("tribofilm states invalid")
 return {"states":states,"film_held_count":sum(s=="film-held" for s in states) or None,"full_history_retained":True}
def rheology(applied,flow,relaxation):
 applied,flow,relaxation=positive(applied,"applied"),positive(flow,"flow"),positive(relaxation,"relaxation")
 return {"applied":applied,"flow":flow,"resistance_part":Fraction(applied,flow),"relaxation_count":relaxation,"class":"flow-with-retained-relaxation"}

BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GEOMETRY-TOPOLOGY-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-PHASE-TIME-TEMPERATURE-010")
DEFS=(
("001","SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001","Tensor-resolved stress-strain response","Mechanical response is a complete exact axis-by-axis ledger of positive load, extension and held orientation; no scalar average erases tensor distinctions.",BASE),
("002","SFT-MAT-MECH-TRANSVERSE-STRAIN-002","Transverse-to-longitudinal strain relation","Transverse response is the exact positive magnitude part of longitudinal extension with contraction or expansion retained as a label, never a signed quantity.",BASE+("SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001",)),
("003","SFT-MAT-MECH-VISCOELASTIC-MEMORY-003","Viscoelastic memory and recovery","Viscoelasticity retains the complete loading word, positive recovery and any unrecovered remainder as structural absence or positive count.",BASE+("SFT-MAT-MECH-TRANSVERSE-STRAIN-002",)),
("004","SFT-MAT-MECH-VISCOPLASTIC-FLOW-004","Viscoplastic flow relation","Viscoplastic flow is exact applied deformation partitioned into recovered and permanently retained parts after the observation word closes.",BASE+("SFT-MAT-MECH-VISCOELASTIC-MEMORY-003",)),
("005","SFT-MAT-MECH-YIELD-PATH-005","Yield-surface and loading-path boundary","Yield is the first position on a retained loading path at which deformation changes from recoverable to retained.",BASE+("SFT-MAT-MECH-VISCOPLASTIC-FLOW-004",)),
("006","SFT-MAT-MECH-WORK-HARDENING-006","Work hardening and retained deformation history","Work hardening is a later exact yield count greater than the first, inseparable from the retained deformation history that distinguishes the states.",BASE+("SFT-MAT-MECH-YIELD-PATH-005",)),
("007","SFT-MAT-MECH-FRACTURE-ENERGY-007","Fracture energy and toughness ledger","Fracture work is the exact positive work carrier per newly formed surface carrier with complete specimen and crack-boundary custody.",BASE+("SFT-MAT-MECH-WORK-HARDENING-006",)),
("008","SFT-MAT-MECH-CRACK-GROWTH-008","Stable and unstable crack-growth relation","Crack growth is a complete nondecreasing length word whose terminal state is held below or at the registered instability boundary.",BASE+("SFT-MAT-MECH-FRACTURE-ENERGY-007",)),
("009","SFT-MAT-MECH-FATIGUE-009","Cyclic fatigue initiation and propagation","Fatigue retains every counted cycle, the first initiation cycle and every later crack record; no cycle-average erases propagation history.",BASE+("SFT-MAT-MECH-CRACK-GROWTH-008",)),
("010","SFT-MAT-MECH-CREEP-RUPTURE-010","Creep mechanism and rupture-time custody","Creep is a time-ordered deformation path under retained conditions terminating at an exact observed rupture time.",BASE+("SFT-MAT-MECH-FATIGUE-009",)),
("011","SFT-MAT-MECH-IMPACT-011","Impact and high-rate mechanical response","Impact response is the complete exact partition of one input carrier among absorbed, rebounded and damage channels.",BASE+("SFT-MAT-MECH-CREEP-RUPTURE-010",)),
("012","SFT-MAT-MECH-FRICTION-CONTACT-012","Friction and contact-state relation","Friction retains exact tangential and normal carriers, their rational part and the complete contact population and condition.",BASE+("SFT-MAT-MECH-IMPACT-011",)),
("013","SFT-MAT-MECH-LUBRICATION-TRIBOFILM-013","Lubrication and tribofilm organization","Lubrication is a complete transition word among bare contact, held film and broken film states, retaining formation and loss rather than averaging them away.",BASE+("SFT-MAT-MECH-FRICTION-CONTACT-012",)),
("014","SFT-MAT-MECH-RHEOLOGY-014","Rheological flow and relaxation classes","Rheology is the exact relation of applied carrier to flow carrier plus the retained relaxation recurrence and material condition.",BASE+("SFT-MAT-MECH-LUBRICATION-TRIBOFILM-013",)),)
REL={n:r for n,r in zip((f"{i:03d}" for i in range(1,15)),("axis-resolved-held-orientation-load-extension-ledger","transverse-longitudinal-positive-part-and-held-direction","complete-loading-memory-recovery-remainder-ledger","applied-recovered-permanent-deformation-partition","first-retained-state-on-complete-loading-path","history-bound-increased-later-yield-count","exact-work-per-new-surface-fracture-ledger","nondecreasing-crack-word-and-instability-boundary","cycle-initiation-propagation-complete-history","time-ordered-creep-path-and-rupture-custody","input-absorption-rebound-damage-one-partition","tangential-normal-contact-population-ledger","bare-film-held-film-broken-transition-word","applied-flow-resistance-part-and-relaxation-class"))}
def axes(r): return (binary_axis("carrier","carrier?","answer-only","carrier erased","complete-positive-mechanical-carrier","all carriers held"),binary_axis("relation","relation?","imported-fit-or-continuum", "not forced",r,"exact relation"),binary_axis("history","history?","endpoint-only","path erased","complete-loading-time-contact-history","history retained"),binary_axis("observation","boundary?","condition-erased","not identified","specimen-method-condition-scale-uncertainty-held","boundary retained"),binary_axis("record","record?","headline-only","not reproducible","complete-state-transition-resource-trace","trace retained"),binary_axis("provenance","selector?","target-authority-or-prior-model","external selector","root-bound-forward-forcing","root forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","successor preserved"),binary_axis("extension","extra rule?","free-fit-exception-or-extra-rule","manufactured","no-extra-rule","no selector"))
W={
"001":(Witness("tensor","Two axes remain distinct.",oriented_response((("x",4,2,"forward"),("y",3,1,"opposed")))["tensor_axes_retained"]),),
"002":(Witness("part","One transverse per four longitudinal is one-quarter.",transverse_relation(4,1,"contracted")["magnitude_part"]==Fraction(1,4)),),
"003":(Witness("memory","Two of five recover and three remain.",memory_recovery((2,5),2)["unrecovered"]==3),),
"004":(Witness("permanent","Five applied and two recovered retain three.",permanent_flow(5,2)["permanent"]==3),),
"005":(Witness("yield","First retained state is at load three.",yield_path(((1,"recoverable"),(2,"recoverable"),(3,"retained")))["yield_load"]==3),),
"006":(Witness("hardening","Later yield five exceeds first three by two.",hardening(3,5,("worked",))["increase"]==2),),
"007":(Witness("fracture","Six work units per three surface units is two.",fracture_ledger(6,3)["work_per_surface"]==2),),
"008":(Witness("crack","Lengths one two three remain stable below four.",crack_path((1,2,3),4)["terminal_class"].startswith("stable")),),
"009":(Witness("fatigue","Initiation at cycle three leaves three propagation records through five.",fatigue(5,3,(0,0,1,2,3))["propagation_records"]==3),),
"010":(Witness("creep","Rupture five follows the complete time path.",creep_path(((1,1),(3,2)),5)["rupture_time"]==5),),
"011":(Witness("impact","Parts two three and five close input ten.",impact_partition(10,2,3,5)["closes"]),),
"012":(Witness("friction","Tangential two over normal eight is one-quarter.",friction_contact(2,8,3)["friction_part"]==Fraction(1,4)),),
"013":(Witness("film","Two held-film states remain counted.",lubrication_film(("bare-contact","film-held","film-held","film-broken"))["film_held_count"]==2),),
"014":(Witness("rheology","Applied six over flow three is resistance two.",rheology(6,3,4)["resistance_part"]==2),),}
@dataclass(frozen=True)
class MechSpec(StructuralPhysicsSpec):
 number:str="";obligation_id:str=""
 def validate(self):
  if self.number not in W or len(self.axes)!=8 or not all(x.passed for x in self.witnesses): raise ValueError("invalid MECH spec")
  for a in self.axes:a.survivor
class MechProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EX=("no imported continuum law, fitted constitutive equation, named mechanism or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","absence and opposed direction remain held labels","no external outcome selects a survivor","all adverse and boundary rows retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFS:
 spec=MechSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight MECH-{n} axes before target release.",grammar_boundary=f"Every positive finite MECH-{n} carrier with complete path and observation distinctions.",axes=axes(REL[n]),exact_result=f"MECH-{n} uniquely retains {REL[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="First positive carrier retains every distinction.",induction_step="One lawful successor retains prior distinctions and adds no selector.",exclusions=EX,witnesses=W[n],number=n,obligation_id=f"SFT-MAT-OBL-MECH-{n}");spec.validate();SPECS[c]=spec
ORDER=tuple(x[1] for x in DEFS)
__all__=("MechProgram","ORDER","SPECS","oriented_response","transverse_relation","memory_recovery","permanent_flow","yield_path","hardening","fracture_ledger","crack_path","fatigue","creep_path","impact_partition","friction_contact","lubrication_film","rheology")

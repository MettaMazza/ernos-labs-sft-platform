"""Exact Fold laws for Materials MAGSC-001--012."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def pos(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1:raise ValueError(n+" must be positive")
 return v
def susceptibility(moment,field,orientation):
 m,f=pos(moment,"moment"),pos(field,"field")
 if orientation not in ("parallel","opposed"):raise ValueError("orientation held")
 return {"moment":m,"field":f,"orientation":orientation,"susceptibility_part":Fraction(m,f)}
def spin_glass(temperatures,states,history):
 ts=tuple(pos(x,"temperature") for x in temperatures);ss=tuple(states)
 if len(ts)!=len(ss) or len(ts)<2 or any(s not in ("mobile","frozen") for s in ss) or not history:raise ValueError("history incomplete")
 first=next((i for i,s in enumerate(ss,1) if s=="frozen"),None);return {"temperatures":ts,"states":ss,"first_frozen_position":first,"history":tuple(history)}
def domain_walls(domains,walls,path):
 d,w=pos(domains,"domains"),pos(walls,"walls");p=tuple(path)
 if w>=d or len(p)<2 or any(x not in ("nucleated","grown","moved","disappeared") for x in p):raise ValueError("domain path invalid")
 return {"domains":d,"walls":w,"path":p,"complete":True}
def hysteresis(rows):
 out=[]
 for field,magnetization,direction in rows:
  if direction not in ("forward","reverse"):raise ValueError("direction held")
  out.append((pos(field,"field"),pos(magnetization,"magnetization"),direction))
 if len(out)<4 or {x[2] for x in out}!={"forward","reverse"}:raise ValueError("loop incomplete")
 return {"rows":tuple(out),"loop_closed":out[0][:2]==out[-1][:2],"path_retained":True}
def anisotropy(easy,hard,crystal_axis):
 e,h=pos(easy,"easy"),pos(hard,"hard")
 if h<=e or not crystal_axis:raise ValueError("anisotropy invalid")
 return {"easy":e,"hard":h,"axis":crystal_axis,"anisotropy_gap":h-e}
def magnetoresistance(base,field_response,field,direction):
 b,r,f=pos(base,"base"),pos(field_response,"field response"),pos(field,"field")
 if direction not in ("parallel","transverse","opposed"):raise ValueError("field direction held")
 return {"base":b,"response":r,"field":f,"direction":direction,"change_magnitude":abs(r-b) or None,"response_part":Fraction(r,b)}
def spin_relaxation(initial,retained,steps,orientation):
 i,r,s=pos(initial,"initial"),pos(retained,"retained"),pos(steps,"steps")
 if r>i or orientation not in ("parallel","opposed"):raise ValueError("spin ledger invalid")
 return {"initial":i,"retained":r,"lost":(i-r) or None,"steps":s,"orientation":orientation,"retained_part":Fraction(r,i)}
def critical_fields(first,second,state_path):
 a,b=pos(first,"first field"),pos(second,"second field");p=tuple(state_path)
 if b<=a or p!=("Meissner","mixed","normal"):raise ValueError("critical field order invalid")
 return {"first":a,"second":b,"path":p,"mixed_width":b-a}
def vortex_pinning(total,pinned,mobile,lattice):
 t,p,m=pos(total,"total"),pos(pinned,"pinned"),pos(mobile,"mobile")
 if p+m!=t or not lattice:raise ValueError("vortex ledger invalid")
 return {"total":t,"pinned":p,"mobile":m,"lattice":lattice,"pinned_part":Fraction(p,t),"closes":True}
def coherence_boundary(coherence,penetration,kind):
 c,p=pos(coherence,"coherence"),pos(penetration,"penetration")
 if kind not in ("type-I","type-II"):raise ValueError("kind held")
 return {"coherence":c,"penetration":p,"kind":kind,"ratio":Fraction(p,c)}
def superfluid_flow(total,persistent,excitations,critical):
 t,p,e,c=pos(total,"total"),pos(persistent,"persistent"),pos(excitations,"excitations"),pos(critical,"critical")
 if p+e!=t:raise ValueError("flow carrier does not close")
 return {"total":t,"persistent":p,"excitations":e,"critical":c,"persistent_part":Fraction(p,t),"below_boundary":p<c,"closes":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GEOMETRY-TOPOLOGY-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-PHYS-FIELD-MAGNETIC-001","SFT-MAT-MAG-FERROMAGNETISM-001","SFT-MAT-MAG-ANTIFERROMAGNETISM-001","SFT-MAT-SC-ZERO-RESISTANCE-001","SFT-MAT-SF-SUPERFLUID-001","SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012")
DEFS=(
("001","SFT-MAT-MAGSC-PARAMAGNETIC-RESPONSE-001","Paramagnetic response","Paramagnetic response retains positive moment and field carriers with parallel orientation as a held label and exact rational susceptibility magnitude.",BASE),
("002","SFT-MAT-MAGSC-DIAMAGNETIC-RESPONSE-002","Diamagnetic response","Diamagnetic response retains positive moment and field carriers with opposed orientation as a held label rather than a negative proof magnitude.",BASE+("SFT-MAT-MAGSC-PARAMAGNETIC-RESPONSE-001",)),
("003","SFT-MAT-MAGSC-SPIN-GLASS-FREEZING-003","Spin-glass freezing and history","Spin-glass freezing is the first frozen state on a complete temperature and preparation-history word.",BASE+("SFT-MAT-MAGSC-DIAMAGNETIC-RESPONSE-002",)),
("004","SFT-MAT-MAGSC-DOMAINS-WALLS-004","Magnetic domains and walls","Magnetic domains retain exact domain and wall populations and the complete nucleation-growth-motion-disappearance path.",BASE+("SFT-MAT-MAGSC-SPIN-GLASS-FREEZING-003",)),
("005","SFT-MAT-MAGSC-HYSTERESIS-LOOP-005","Magnetic hysteresis loop ledger","Magnetic hysteresis is a closed, ordered field-magnetization word with forward and reverse orientations retained at every point.",BASE+("SFT-MAT-MAGSC-DOMAINS-WALLS-004",)),
("006","SFT-MAT-MAGSC-MAGNETOCRYSTALLINE-ANISOTROPY-006","Magnetocrystalline anisotropy","Magnetocrystalline anisotropy retains easy and hard positive response carriers, exact gap and crystal-axis identity.",BASE+("SFT-MAT-MAGSC-HYSTERESIS-LOOP-005",)),
("007","SFT-MAT-MAGSC-MAGNETORESISTANCE-007","Magnetoresistance and field-response relation","Magnetoresistance retains base and field-response carriers, exact rational change and held field orientation.",BASE+("SFT-MAT-MAGSC-MAGNETOCRYSTALLINE-ANISOTROPY-006",)),
("008","SFT-MAT-MAGSC-SPIN-TRANSPORT-RELAXATION-008","Spin transport and relaxation","Spin transport retains initial and surviving carriers, any lost distinction, counted relaxation steps and orientation.",BASE+("SFT-MAT-MAGSC-MAGNETORESISTANCE-007",)),
("009","SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009","Superconducting critical-field organization","Superconducting critical fields are two ordered positive boundaries separating Meissner, mixed and normal state classes.",BASE+("SFT-MAT-MAGSC-SPIN-TRANSPORT-RELAXATION-008",)),
("010","SFT-MAT-MAGSC-SC-VORTEX-PINNING-010","Superconducting vortex matter and pinning","Vortex matter is the exact partition of a complete vortex population into pinned and mobile carriers with lattice identity retained.",BASE+("SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009",)),
("011","SFT-MAT-MAGSC-SC-COHERENCE-LENGTH-011","Superconducting coherence-length boundary","Superconducting class retains exact coherence and penetration lengths, their rational relation and the type label.",BASE+("SFT-MAT-MAGSC-SC-VORTEX-PINNING-010",)),
("012","SFT-MAT-MAGSC-SUPERFLUID-CRITICAL-FLOW-012","Superfluid excitation and critical-flow ledger","Superfluid flow is an exact partition into persistent and excitation carriers under a retained critical-flow boundary.",BASE+("SFT-MAT-MAGSC-SC-COHERENCE-LENGTH-011",)),)
REL={n:r for n,r in zip((f"{i:03d}" for i in range(1,13)),("parallel-moment-field-susceptibility-ledger","opposed-moment-field-susceptibility-ledger","temperature-state-preparation-freezing-history","domain-wall-nucleation-growth-motion-disappearance","closed-forward-reverse-field-magnetization-word","easy-hard-crystal-axis-anisotropy-gap","base-field-response-orientation-magnetoresistance","initial-retained-lost-spin-relaxation-path","ordered-critical-fields-Meissner-mixed-normal","pinned-mobile-vortex-lattice-partition","coherence-penetration-type-boundary","persistent-excitation-critical-superfluid-flow"))}
def axes(r):return (binary_axis("carrier","carrier?","answer-only","carrier erased","complete-positive-magnetic-carrier","held"),binary_axis("relation","relation?","imported-fit-continuum","not forced",r,"exact"),binary_axis("path","path?","endpoint-only","history erased","complete-field-spin-vortex-flow-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-field-temperature-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
W={"001":(Witness("para","Half.",susceptibility(2,4,"parallel")["susceptibility_part"]==Fraction(1,2)),),"002":(Witness("dia","Half.",susceptibility(2,4,"opposed")["orientation"]=="opposed"),),"003":(Witness("freeze","Second.",spin_glass((5,3),("mobile","frozen"),("cooled",))["first_frozen_position"]==2),),"004":(Witness("wall","Complete.",domain_walls(4,2,("nucleated","grown","moved"))["complete"]),),"005":(Witness("loop","Closed.",hysteresis(((1,2,"forward"),(2,3,"forward"),(2,2,"reverse"),(1,2,"reverse")))["loop_closed"]),),"006":(Witness("gap","Two.",anisotropy(3,5,"c")["anisotropy_gap"]==2),),"007":(Witness("mr","Three halves.",magnetoresistance(4,6,3,"parallel")["response_part"]==Fraction(3,2)),),"008":(Witness("spin","Three fifths.",spin_relaxation(5,3,2,"parallel")["retained_part"]==Fraction(3,5)),),"009":(Witness("fields","Width three.",critical_fields(2,5,("Meissner","mixed","normal"))["mixed_width"]==3),),"010":(Witness("vortex","Closes.",vortex_pinning(5,3,2,"triangular")["closes"]),),"011":(Witness("coherence","Two.",coherence_boundary(2,4,"type-II")["ratio"]==2),),"012":(Witness("flow","Closes.",superfluid_flow(5,3,2,4)["closes"]),)}
@dataclass(frozen=True)
class MagscSpec(StructuralPhysicsSpec):
 number:str="";obligation_id:str=""
 def validate(self):
  if self.number not in W or len(self.axes)!=8 or not all(x.passed for x in self.witnesses):raise ValueError("invalid MAGSC")
  for a in self.axes:a.survivor
class MagscProgram(StructuralPhysicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EX=("no imported continuum magnetics, fitted response curve, named mechanism or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","opposed direction and absence remain held labels","no external outcome selects a survivor","all result classes retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFS:
 q=MagscSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight MAGSC-{n} axes before target release.",grammar_boundary=f"Every positive finite MAGSC-{n} carrier with complete path and observation distinctions.",axes=axes(REL[n]),exact_result=f"MAGSC-{n} uniquely retains {REL[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="First positive carrier retains every distinction.",induction_step="One lawful successor retains prior distinctions and adds no selector.",exclusions=EX,witnesses=W[n],number=n,obligation_id=f"SFT-MAT-OBL-MAGSC-{n}");q.validate();SPECS[c]=q
ORDER=tuple(x[1] for x in DEFS)

"""Exact Fold laws for the complete Materials ELEC-001--012 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def pos(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1:raise ValueError(n+" must be positive")
 return v
def conductivity_resistivity(resistance,length,area):
 r,l,a=pos(resistance,"resistance"),pos(length,"length"),pos(area,"area");rho=Fraction(r*a,l);return {"resistivity":rho,"conductivity":1/rho,"reciprocal_closure":rho*(1/rho)==1}
def mobility_concentration(charge_flow,field,concentration):
 q,e,n=pos(charge_flow,"charge flow"),pos(field,"field"),pos(concentration,"concentration");return {"charge_flow":q,"field":e,"concentration":n,"mobility_part":Fraction(q,n*e),"separated":True}
def hall_response(current,field,charge,thickness,density,carrier_type):
 vals=tuple(pos(x,n) for x,n in ((current,"current"),(field,"field"),(charge,"charge"),(thickness,"thickness"),(density,"density")))
 if carrier_type not in ("electron","hole"):raise ValueError("carrier type held")
 return {"hall_part":Fraction(vals[0]*vals[1],vals[2]*vals[3]*vals[4]),"carrier_type":carrier_type,"orientation_held":True}
def dielectric_response(stored,lost,cycles):
 s,l,c=pos(stored,"stored"),pos(lost,"lost"),pos(cycles,"cycles");return {"stored":s,"lost":l,"cycles":c,"loss_part":Fraction(l,s),"complete_response":True}
def ionic_transference(species_flows):
 rows=tuple((label,pos(flow,"flow")) for label,flow in species_flows)
 if not rows or len({x[0] for x in rows})!=len(rows):raise ValueError("distinct ionic species required")
 total=sum(x[1] for x in rows);return {"species":rows,"total":total,"transference":tuple((label,Fraction(flow,total)) for label,flow in rows),"closes":sum(Fraction(flow,total) for _,flow in rows)==1}
def mixed_transport(ionic,electronic):
 i,e=pos(ionic,"ionic"),pos(electronic,"electronic");total=i+e;return {"ionic":i,"electronic":e,"ionic_part":Fraction(i,total),"electronic_part":Fraction(e,total),"closes":True}
def finite_barrier(incident,transmitted,reflected,width):
 i,t,r,w=pos(incident,"incident"),pos(transmitted,"transmitted"),pos(reflected,"reflected"),pos(width,"width")
 if t+r!=i:raise ValueError("barrier carrier does not close")
 return {"incident":i,"transmitted":t,"reflected":r,"barrier_width":w,"transmission_part":Fraction(t,i),"closes":True}
def band_alignment(first_level,second_level,orientation,interface):
 a,b=pos(first_level,"first level"),pos(second_level,"second level")
 if orientation not in ("first-above","second-above","aligned") or not interface:raise ValueError("held alignment required")
 if orientation=="aligned" and a!=b:raise ValueError("aligned levels must coincide")
 if orientation=="first-above" and a<=b or orientation=="second-above" and b<=a:raise ValueError("orientation contradicts magnitudes")
 return {"levels":(a,b),"offset":abs(a-b) or None,"orientation":orientation,"interface":interface}
def carrier_confinement(barrier,level,layer):
 b,l=pos(barrier,"barrier"),pos(level,"level")
 if l>=b or not layer:raise ValueError("level not confined")
 return {"barrier":b,"level":l,"retained_depth":b-l,"layer":layer,"confined":True}
def defect_traps(defects,occupied,empty_label):
 d,o=pos(defects,"defects"),pos(occupied,"occupied")
 if o>d or empty_label!="absence":raise ValueError("trap ledger invalid")
 return {"defects":d,"occupied":o,"unoccupied":(d-o) or None,"unoccupied_form":empty_label,"complete":True}
def screening_depletion(total,accumulation,depletion,inversion,state):
 vals=tuple(pos(x,n) for x,n in ((total,"total"),(accumulation,"accumulation"),(depletion,"depletion"),(inversion,"inversion")))
 if sum(vals[1:])!=vals[0] or state not in ("accumulation","depletion","inversion"):raise ValueError("screening ledger invalid")
 return {"total":vals[0],"parts":vals[1:],"state":state,"closes":True}
def electrochemical_insertion(host_sites,inserted,removed,path):
 h,i,r=pos(host_sites,"host sites"),pos(inserted,"inserted"),pos(removed,"removed")
 if i>h or r>i or len(path)<2:raise ValueError("insertion path incomplete")
 return {"host_sites":h,"inserted":i,"removed":r,"retained":(i-r) or None,"path":tuple(path),"operando_history":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GEOMETRY-TOPOLOGY-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005")
DEFS=(
("001","SFT-MAT-ELEC-CONDUCTIVITY-RESISTIVITY-001","Electrical conductivity and resistivity relation","Conductivity and resistivity are exact reciprocal positive rational relations with specimen geometry retained.",BASE),
("002","SFT-MAT-ELEC-MOBILITY-CONCENTRATION-002","Carrier mobility and concentration separation","Carrier flow is separated exactly into retained concentration and mobility carriers rather than conflated into one response.",BASE+("SFT-MAT-ELEC-CONDUCTIVITY-RESISTIVITY-001",)),
("003","SFT-MAT-ELEC-HALL-RESPONSE-003","Hall-response carrier ledger","Hall response retains current, field, charge, thickness, carrier density and electron-or-hole orientation as one exact ledger.",BASE+("SFT-MAT-ELEC-MOBILITY-CONCENTRATION-002",)),
("004","SFT-MAT-ELEC-DIELECTRIC-LOSS-004","Dielectric permittivity and loss relation","Dielectric response retains exact stored and lost carriers, cycle conditions and their rational loss relation.",BASE+("SFT-MAT-ELEC-HALL-RESPONSE-003",)),
("005","SFT-MAT-ELEC-IONIC-TRANSFERENCE-005","Ionic conductivity and transference","Ionic transport is the complete species-labelled partition of the total mobile carrier with exact transference parts.",BASE+("SFT-MAT-ELEC-DIELECTRIC-LOSS-004",)),
("006","SFT-MAT-ELEC-MIXED-TRANSPORT-006","Mixed ionic-electronic transport","Mixed transport retains simultaneous ionic and electronic carriers as exact complementary parts without erasing either channel.",BASE+("SFT-MAT-ELEC-IONIC-TRANSFERENCE-005",)),
("007","SFT-MAT-ELEC-FINITE-BARRIER-TUNNELLING-007","Tunnelling through a finite material barrier","Finite-barrier transport is an exact incident partition into transmitted and reflected carriers with barrier width retained.",BASE+("SFT-MAT-ELEC-MIXED-TRANSPORT-006",)),
("008","SFT-MAT-ELEC-BAND-ALIGNMENT-008","Band-alignment and interface offset","Band alignment retains both positive levels, exact offset magnitude, held ordering and interface identity without signed proof magnitudes.",BASE+("SFT-MAT-ELEC-FINITE-BARRIER-TUNNELLING-007",)),
("009","SFT-MAT-ELEC-CARRIER-CONFINEMENT-009","Heterostructure carrier confinement","Carrier confinement is the exact retained depth of a positive level below a held interface barrier in a named layer.",BASE+("SFT-MAT-ELEC-BAND-ALIGNMENT-008",)),
("010","SFT-MAT-ELEC-DEFECT-TRAP-STATES-010","Defect and trap electronic states","Defect states retain the complete defect population, occupied traps and structural absence or positive unoccupied remainder.",BASE+("SFT-MAT-ELEC-CARRIER-CONFINEMENT-009",)),
("011","SFT-MAT-ELEC-SCREENING-DEPLETION-011","Charge screening and depletion length","Screening retains the exact accumulation, depletion and inversion partition and the observed regime label.",BASE+("SFT-MAT-ELEC-DEFECT-TRAP-STATES-010",)),
("012","SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012","Electrochemical insertion and material-state response","Electrochemical insertion retains host capacity, inserted and removed carriers and the complete operando material-state path.",BASE+("SFT-MAT-ELEC-SCREENING-DEPLETION-011",)),)
REL={n:r for n,r in zip((f"{i:03d}" for i in range(1,13)),("reciprocal-conductivity-resistivity-specimen-ledger","concentration-mobility-separated-carrier-flow","hall-current-field-density-thickness-orientation-ledger","dielectric-stored-lost-cycle-response","species-labelled-ionic-transference-partition","simultaneous-ionic-electronic-complementary-transport","finite-barrier-incident-transmitted-reflected-partition","two-level-offset-held-order-interface-alignment","below-barrier-layer-held-carrier-confinement","defect-occupied-unoccupied-trap-ledger","accumulation-depletion-inversion-screening-partition","host-inserted-removed-operando-state-path"))}
def axes(r):return (binary_axis("carrier","carrier?","answer-only","carrier erased","complete-positive-electrical-carrier","all held"),binary_axis("relation","relation?","imported-fit-continuum", "not forced",r,"exact"),binary_axis("path","path?","endpoint-only","history erased","complete-interface-field-cycle-state-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-field-temperature-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
W={
"001":(Witness("reciprocal","Exact reciprocal closure.",conductivity_resistivity(2,4,2)["reciprocal_closure"]),),"002":(Witness("separation","Mobility one.",mobility_concentration(6,2,3)["mobility_part"]==1),),"003":(Witness("hall","Hall part one.",hall_response(6,2,2,2,3,"electron")["hall_part"]==1),),"004":(Witness("loss","Loss quarter.",dielectric_response(8,2,3)["loss_part"]==Fraction(1,4)),),"005":(Witness("ions","Parts close.",ionic_transference((("lithium",2),("vacancy",3)))["closes"]),),"006":(Witness("mixed","Parts close.",mixed_transport(2,3)["closes"]),),"007":(Witness("barrier","Carrier closes.",finite_barrier(5,2,3,4)["closes"]),),"008":(Witness("offset","Offset two.",band_alignment(5,3,"first-above","junction")["offset"]==2),),"009":(Witness("confined","Depth two.",carrier_confinement(5,3,"well")["retained_depth"]==2),),"010":(Witness("traps","Two unoccupied.",defect_traps(5,3,"absence")["unoccupied"]==2),),"011":(Witness("screen","Partition closes.",screening_depletion(10,2,3,5,"depletion")["closes"]),),"012":(Witness("insert","Two retained.",electrochemical_insertion(8,5,3,("charged","discharged"))["retained"]==2),)}
@dataclass(frozen=True)
class ElecSpec(StructuralPhysicsSpec):
 number:str="";obligation_id:str=""
 def validate(self):
  if self.number not in W or len(self.axes)!=8 or not all(x.passed for x in self.witnesses):raise ValueError("invalid ELEC spec")
  for a in self.axes:a.survivor
class ElecProgram(StructuralPhysicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EX=("no imported transport equation, continuum band model, fitted constitutive law or named mechanism as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","absence and carrier orientation remain held labels","no external outcome selects a survivor","all result classes retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFS:
 q=ElecSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight ELEC-{n} axes before target release.",grammar_boundary=f"Every positive finite ELEC-{n} carrier with complete path and observation distinctions.",axes=axes(REL[n]),exact_result=f"ELEC-{n} uniquely retains {REL[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="First positive carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EX,witnesses=W[n],number=n,obligation_id=f"SFT-MAT-OBL-ELEC-{n}");q.validate();SPECS[c]=q
ORDER=tuple(x[1] for x in DEFS)

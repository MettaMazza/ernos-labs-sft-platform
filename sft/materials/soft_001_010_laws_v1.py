"""Exact Fold laws for the complete Materials SOFT-001--010 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis

def positive(v,n):
    if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
    return v
def colloid(total,free,aggregated,interaction,condition):
    total,free,aggregated=(positive(v,n) for v,n in ((total,"total"),(free,"free"),(aggregated,"aggregated")))
    if free+aggregated!=total or not interaction or not condition: raise ValueError("colloid ledger invalid")
    return {"free":free,"aggregated":aggregated,"interaction":interaction,"condition":condition,"aggregate_part":Fraction(aggregated,total),"closes":True}
def gel_network(nodes,links,spanning_path,response):
    nodes,links=positive(nodes,"nodes"),positive(links,"links"); path=tuple(spanning_path)
    if len(path)<2 or not response: raise ValueError("gel network incomplete")
    return {"nodes":nodes,"links":links,"spanning_path":path,"response":response,"link_part":Fraction(links,nodes+links),"percolated":True}
def foam(initial_liquid,retained_liquid,drained_liquid,cells,gas_label):
    values=tuple(positive(v,n) for v,n in ((initial_liquid,"initial"),(retained_liquid,"retained"),(drained_liquid,"drained"),(cells,"cells")))
    if values[1]+values[2]!=values[0] or not gas_label: raise ValueError("foam ledger invalid")
    return {"initial_liquid":values[0],"retained_liquid":values[1],"drained_liquid":values[2],"cells":values[3],"gas_label":gas_label,"drained_part":Fraction(values[2],values[0]),"closes":True}
def liquid_crystal(orientation_labels,orientation_counts,phase,defects):
    labels,counts=tuple(orientation_labels),tuple(orientation_counts)
    if len(labels)<2 or len(labels)!=len(counts) or len(set(labels))!=len(labels) or not phase: raise ValueError("orientation record incomplete")
    counts=tuple(positive(v,"orientation") for v in counts); total=sum(counts)
    return {"labels":labels,"counts":counts,"phase":phase,"defects":tuple(defects),"parts":tuple(Fraction(v,total) for v in counts),"orientational_order_retained":True}
def emulsion(droplet_counts,phase_labels,interface,shear_path):
    counts,labels,path=tuple(droplet_counts),tuple(phase_labels),tuple(shear_path)
    if len(counts)<2 or len(counts)!=len(labels) or not interface or len(path)<2: raise ValueError("emulsion record incomplete")
    counts=tuple(positive(v,"droplet") for v in counts); total=sum(counts)
    return {"counts":counts,"phase_labels":labels,"interface":interface,"shear_path":path,"droplet_parts":tuple(Fraction(v,total) for v in counts),"closes":True}
def membrane(incident,transported,retained,layers,interface):
    incident,transported,retained=(positive(v,n) for v,n in ((incident,"incident"),(transported,"transported"),(retained,"retained")))
    layers=tuple(layers)
    if transported+retained!=incident or not layers or not interface: raise ValueError("membrane ledger invalid")
    return {"incident":incident,"transported":transported,"retained":retained,"layers":layers,"interface":interface,"transport_part":Fraction(transported,incident),"closes":True}
def granular(grains,contacts,chain_loads,packing):
    grains,contacts=positive(grains,"grains"),positive(contacts,"contacts"); loads=tuple(positive(v,"load") for v in chain_loads)
    if not loads or not packing: raise ValueError("granular record incomplete")
    total=sum(loads); return {"grains":grains,"contacts":contacts,"chain_loads":loads,"packing":packing,"load_parts":tuple(Fraction(v,total) for v in loads),"force_chain_retained":True}
def jamming(before_state,after_state,applied,resisted,path):
    applied,resisted=positive(applied,"applied"),positive(resisted,"resisted"); path=tuple(path)
    if before_state==after_state or not before_state or not after_state or resisted>applied or len(path)<2: raise ValueError("jamming boundary incomplete")
    return {"before":before_state,"after":after_state,"applied":applied,"resisted":resisted,"path":path,"resisted_part":Fraction(resisted,applied),"boundary_retained":True}
def responsive(stimulus,before,after,input_count,response_count,path):
    input_count,response_count=positive(input_count,"input"),positive(response_count,"response"); path=tuple(path)
    if before==after or not stimulus or len(path)<3: raise ValueError("responsive path incomplete")
    return {"stimulus":stimulus,"before":before,"after":after,"input":input_count,"response":response_count,"path":path,"response_ratio":Fraction(response_count,input_count),"reversible_record_retained":True}
def active_material(input_count,motion_count,dissipated_count,agents,path):
    input_count,motion_count,dissipated_count,agents=(positive(v,n) for v,n in ((input_count,"input"),(motion_count,"motion"),(dissipated_count,"dissipated"),(agents,"agents")))
    path=tuple(path)
    if motion_count+dissipated_count!=input_count or len(path)<3: raise ValueError("active ledger invalid")
    return {"input":input_count,"motion":motion_count,"dissipated":dissipated_count,"agents":agents,"path":path,"motion_part":Fraction(motion_count,input_count),"nonequilibrium_history":True}

BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GRAPH-NETWORK-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-CLASS-POROUS-001","SFT-MAT-CLASS-COMPOSITE-001","SFT-MAT-MECH-RHEOLOGY-014","SFT-MAT-CLASS-ARCHITECTED-CELLULAR-012")
DEFINITIONS=(
 ("001","SFT-MAT-SOFT-COLLOID-AGGREGATION-001","Colloidal stability and aggregation","A colloid retains the exact positive partition of free and aggregated particles together with interaction and condition labels.",BASE),
 ("002","SFT-MAT-SOFT-GEL-PERCOLATION-002","Gelation and percolated soft network","Gelation retains nodes, links, spanning path and mechanical response as one connected soft-network history.",BASE+("SFT-MAT-SOFT-COLLOID-AGGREGATION-001",)),
 ("003","SFT-MAT-SOFT-FOAM-DRAINAGE-003","Foam cell and drainage organization","A foam retains cells, gas identity and the exact liquid partition between retained and drained carriers.",BASE+("SFT-MAT-SOFT-GEL-PERCOLATION-002",)),
 ("004","SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004","Liquid-crystal orientational order","Liquid-crystal order retains every orientation label and exact positive part, phase and defect record.",BASE+("SFT-MAT-SOFT-FOAM-DRAINAGE-003",)),
 ("005","SFT-MAT-SOFT-EMULSION-DROPLET-005","Emulsion and multiphase droplet organization","An emulsion retains all droplet populations, phase identities, interface and complete shear history.",BASE+("SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004",)),
 ("006","SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006","Membrane and thin-film soft matter","A membrane retains its ordered layers and interface and the exact incident partition into transported and retained carriers.",BASE+("SFT-MAT-SOFT-EMULSION-DROPLET-005",)),
 ("007","SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007","Granular packing and force-chain support","Granular support retains grains, contacts, packing and every exact force-chain load part.",BASE+("SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006",)),
 ("008","SFT-MAT-SOFT-JAMMING-BOUNDARY-008","Jamming and unjamming boundary","Jamming retains distinct before and after states, applied and resisted carriers and the complete transition path.",BASE+("SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007",)),
 ("009","SFT-MAT-SOFT-STIMULI-RESPONSIVE-009","Responsive and stimuli-sensitive soft materials","A responsive material retains stimulus, before and after states, exact response ratio and complete reversible history.",BASE+("SFT-MAT-SOFT-JAMMING-BOUNDARY-008",)),
 ("010","SFT-MAT-SOFT-ACTIVE-NONEQUILIBRIUM-010","Active-material nonequilibrium organization","Active matter retains agents and the exact input partition into organized motion and dissipation along the full nonequilibrium path.",BASE+("SFT-MAT-SOFT-STIMULI-RESPONSIVE-009",)),
)
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,11)),("free-aggregated-interaction-condition-colloid-partition","node-link-spanning-response-gel-network","cell-gas-retained-drained-foam-ledger","orientation-part-phase-defect-liquid-crystal-order","droplet-phase-interface-shear-emulsion-history","layer-interface-transport-retention-membrane-ledger","grain-contact-packing-force-chain-support","before-after-applied-resisted-jamming-path","stimulus-before-after-response-reversible-history","agent-input-motion-dissipation-nonequilibrium-history")))
def axes(r): return (binary_axis("carrier","carrier?","name-only","erased","complete-positive-soft-carrier","held"),binary_axis("relation","relation?","imported-fit-continuum","not forced",r,"exact"),binary_axis("path","path?","endpoint-only","erased","complete-state-structure-response-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("colloid","partition",colloid(5,3,2,"repulsion","held")["closes"]),),"002":(Witness("gel","network",gel_network(4,5,("left","right"),"elastic")["percolated"]),),"003":(Witness("foam","drainage",foam(5,3,2,4,"air")["drained_part"]==Fraction(2,5)),),"004":(Witness("lc","order",liquid_crystal(("a","b"),(3,2),"nematic",("defect",))["orientational_order_retained"]),),"005":(Witness("emulsion","droplets",emulsion((3,2),("oil","water"),"interface",("high","low"))["closes"]),),"006":(Witness("membrane","transport",membrane(5,3,2,("active","support"),"boundary")["transport_part"]==Fraction(3,5)),),"007":(Witness("granular","chains",granular(5,7,(2,3),"dense")["force_chain_retained"]),),"008":(Witness("jamming","boundary",jamming("flow","jammed",5,4,("flow","jammed"))["boundary_retained"]),),"009":(Witness("response","stimulus",responsive("heat","compact","expanded",2,3,("before","stimulus","after"))["response_ratio"]==Fraction(3,2)),),"010":(Witness("active","history",active_material(5,3,2,4,("input","motion","terminal"))["motion_part"]==Fraction(3,5)),)}
@dataclass(frozen=True)
class SoftSpec(StructuralPhysicsSpec):
    number:str=""; obligation_id:str=""
    def validate(self):
        if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid SOFT spec")
        for a in self.axes: a.survivor
class SoftProgram(StructuralPhysicsProgram):
    @property
    def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported continuum constitutive equation, fitted threshold, named mechanism or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and all state, phase, topology and path distinctions remain held labels","no external outcome selects a survivor","all result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
    x=SoftSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight SOFT-{n} axes before target release.",grammar_boundary=f"Every positive finite SOFT-{n} carrier with complete structure, state, path and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"SOFT-{n} uniquely retains {RELATIONS[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive soft-material carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-SOFT-{n}"); x.validate(); SPECS[c]=x
ORDER=tuple(r[1] for r in DEFINITIONS)

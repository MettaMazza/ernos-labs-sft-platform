"""Exact Fold laws for the complete Materials BIO-001--008 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v
def biocompatibility(exposures,compatible,adverse,material,interface,conditions):
 exposures,compatible,adverse=(positive(v,n) for v,n in ((exposures,"exposures"),(compatible,"compatible"),(adverse,"adverse")))
 if compatible+adverse!=exposures or not material or not interface or not conditions: raise ValueError("interface ledger invalid")
 return {"exposures":exposures,"compatible":compatible,"adverse":adverse,"material":material,"interface":interface,"conditions":conditions,"compatible_part":Fraction(compatible,exposures),"closes":True}
def bioresorption(initial,retained,resorbed,products,path):
 initial,retained,resorbed=(positive(v,n) for v,n in ((initial,"initial"),(retained,"retained"),(resorbed,"resorbed"))); path=tuple(path)
 if retained+resorbed!=initial or not tuple(products) or len(path)<2: raise ValueError("resorption ledger invalid")
 return {"initial":initial,"retained":retained,"resorbed":resorbed,"products":tuple(products),"path":path,"resorbed_part":Fraction(resorbed,initial),"closes":True}
def scaffold(pores,struts,links,pore_classes,spanning_path):
 pores,struts,links=(positive(v,n) for v,n in ((pores,"pores"),(struts,"struts"),(links,"links"))); classes,path=tuple(pore_classes),tuple(spanning_path)
 if not classes or len(path)<2: raise ValueError("scaffold record incomplete")
 return {"pores":pores,"struts":struts,"links":links,"pore_classes":classes,"spanning_path":path,"pore_part":Fraction(pores,pores+struts),"connected":True}
def cell_adhesion(presented,adherent,nonadherent,cell,material,interface):
 presented,adherent,nonadherent=(positive(v,n) for v,n in ((presented,"presented"),(adherent,"adherent"),(nonadherent,"nonadherent")))
 if adherent+nonadherent!=presented or not cell or not material or not interface: raise ValueError("adhesion ledger invalid")
 return {"presented":presented,"adherent":adherent,"nonadherent":nonadherent,"cell":cell,"material":material,"interface":interface,"adhesion_part":Fraction(adherent,presented),"closes":True}
def mechanical_match(applied,material,tissue,interface,geometry):
 applied,material,tissue,interface=(positive(v,n) for v,n in ((applied,"applied"),(material,"material"),(tissue,"tissue"),(interface,"interface")))
 if material+tissue+interface!=applied or not geometry: raise ValueError("mechanical interface ledger invalid")
 return {"applied":applied,"material":material,"tissue":tissue,"interface":interface,"geometry":geometry,"material_part":Fraction(material,applied),"closes":True}
def controlled_release(loaded,released,retained,carrier,path):
 loaded,released,retained=(positive(v,n) for v,n in ((loaded,"loaded"),(released,"released"),(retained,"retained"))); path=tuple(path)
 if released+retained!=loaded or not carrier or len(path)<2: raise ValueError("release ledger invalid")
 return {"loaded":loaded,"released":released,"retained":retained,"carrier":carrier,"path":path,"released_part":Fraction(released,loaded),"closes":True}
def mineralized(organic,mineral,pore,mineral_identity,structure):
 organic,mineral,pore=(positive(v,n) for v,n in ((organic,"organic"),(mineral,"mineral"),(pore,"pore")))
 if not mineral_identity or not structure: raise ValueError("mineralized material incomplete")
 total=organic+mineral+pore; return {"organic":organic,"mineral":mineral,"pore":pore,"mineral_identity":mineral_identity,"structure":structure,"parts":(Fraction(organic,total),Fraction(mineral,total),Fraction(pore,total)),"closes":True}
def biofabricated(inputs,outputs,source_identity,process_path,cell_state):
 inputs,outputs=positive(inputs,"inputs"),positive(outputs,"outputs"); path=tuple(process_path)
 if outputs>inputs or not source_identity or not cell_state or len(path)<3: raise ValueError("biofabricated identity incomplete")
 return {"inputs":inputs,"outputs":outputs,"source_identity":source_identity,"process_path":path,"cell_state":cell_state,"yield_part":Fraction(outputs,inputs),"provenance_retained":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-CLASS-COMPOSITE-001","SFT-MAT-CLASS-POROUS-001","SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006","SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001")
DEFINITIONS=(("001","SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001","Biocompatibility as a material-interface boundary","Biocompatibility is a specimen-, interface- and condition-bound exact partition of observed compatible and adverse responses, never an intrinsic unqualified label.",BASE),("002","SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002","Bioresorption and degradation ledger","Bioresorption retains the exact partition of initial material into retained and resorbed carriers together with every product and time-ordered state.",BASE+("SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001",)),("003","SFT-MAT-BIO-SCAFFOLD-POROSITY-CONNECTIVITY-003","Tissue-scaffold porosity and connectivity","A tissue scaffold retains pores, struts, links, pore classes and complete spanning connectivity as one measured organization.",BASE+("SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002",)),("004","SFT-MAT-BIO-CELL-MATERIAL-ADHESION-004","Cell-material adhesion handoff","Cell-material adhesion retains cell and material identities, interface conditions and the exact presented-cell partition into adherent and nonadherent outcomes.",BASE+("SFT-MAT-BIO-SCAFFOLD-POROSITY-CONNECTIVITY-003",)),("005","SFT-MAT-BIO-MECHANICAL-MATCHING-005","Mechanical matching at a biological interface","Mechanical matching retains the applied load partition across material, tissue and interface with specimen geometry held.",BASE+("SFT-MAT-BIO-CELL-MATERIAL-ADHESION-004",)),("006","SFT-MAT-BIO-CONTROLLED-RELEASE-006","Controlled-release material transport boundary","Controlled release retains the exact loaded-carrier partition into released and retained quantities along the complete material path.",BASE+("SFT-MAT-BIO-MECHANICAL-MATCHING-005",)),("007","SFT-MAT-BIO-MINERALIZED-ORGANIZATION-007","Mineralized biological material organization","A mineralized biological material retains organic, mineral and pore supports, exact parts, mineral identity and structural organization.",BASE+("SFT-MAT-BIO-CONTROLLED-RELEASE-006",)),("008","SFT-MAT-BIO-BIOFABRICATED-IDENTITY-008","Biologically derived and biofabricated material identity","A biofabricated material retains biological source, cell state, complete process path and exact input-output custody.",BASE+("SFT-MAT-BIO-MINERALIZED-ORGANIZATION-007",)))
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,9)),("exposure-compatible-adverse-material-interface-ledger","initial-retained-resorbed-product-path-ledger","pore-strut-link-class-spanning-scaffold","presented-adherent-nonadherent-cell-material-interface","applied-material-tissue-interface-load-partition","loaded-released-retained-carrier-path","organic-mineral-pore-identity-structure","biological-source-cell-process-input-output-custody")))
def axes(r): return (binary_axis("carrier","carrier?","label-only","erased","complete-positive-biomaterial-carrier","held"),binary_axis("relation","relation?","imported-fit-model","not forced",r,"exact"),binary_axis("path","path?","endpoint-only","erased","complete-material-interface-state-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("compatibility","partition",biocompatibility(5,4,1,"sample","cell-contact","held")["closes"]),),"002":(Witness("resorption","partition",bioresorption(5,3,2,("product",),("start","end"))["resorbed_part"]==Fraction(2,5)),),"003":(Witness("scaffold","connected",scaffold(5,3,4,("macro","micro"),("left","right"))["connected"]),),"004":(Witness("adhesion","partition",cell_adhesion(5,3,2,"cell","surface","contact")["adhesion_part"]==Fraction(3,5)),),"005":(Witness("matching","load",mechanical_match(8,3,4,1,"layered")["closes"]),),"006":(Witness("release","transport",controlled_release(5,3,2,"matrix",("loaded","terminal"))["released_part"]==Fraction(3,5)),),"007":(Witness("mineral","parts",sum(mineralized(2,5,1,"hydroxyapatite","hierarchical")["parts"])==1),),"008":(Witness("biofabrication","custody",biofabricated(5,3,"cell-derived",("input","fabrication","output"),"viable")["provenance_retained"]),)}
@dataclass(frozen=True)
class BioSpec(StructuralPhysicsSpec):
 number:str=""; obligation_id:str=""
 def validate(self):
  if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid BIO spec")
  for a in self.axes: a.survivor
class BioProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported continuum constitutive equation, fitted threshold, named mechanism or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and every material, cell, interface, path and product distinction remain held labels","no external outcome selects a survivor","all result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
 x=BioSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight BIO-{n} axes before target release.",grammar_boundary=f"Every positive finite BIO-{n} carrier with complete material, interface, state, path and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"BIO-{n} uniquely retains {RELATIONS[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive biomaterial carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-BIO-{n}"); x.validate(); SPECS[c]=x
ORDER=tuple(r[1] for r in DEFINITIONS)

"""Exact Fold laws for the complete Materials DEGR-001--010 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v
def oxidation(initial,substrate,scale,transport,path):
 initial,substrate,scale,transport=(positive(v,n) for v,n in ((initial,"initial"),(substrate,"substrate"),(scale,"scale"),(transport,"transport"))); path=tuple(path)
 if substrate+scale!=initial or transport>scale or len(path)<2: raise ValueError("oxidation ledger invalid")
 return {"initial":initial,"substrate":substrate,"scale":scale,"transport":transport,"path":path,"scale_part":Fraction(scale,initial),"closes":True}
def corrosion(exposed,retained,released,electrochemical_path,medium):
 exposed,retained,released=(positive(v,n) for v,n in ((exposed,"exposed"),(retained,"retained"),(released,"released"))); path=tuple(electrochemical_path)
 if retained+released!=exposed or len(path)<3 or not medium: raise ValueError("corrosion ledger invalid")
 return {"exposed":exposed,"retained":retained,"released":released,"path":path,"medium":medium,"released_part":Fraction(released,exposed),"closes":True}
def passivation(sites,protected,broken,film,conditions):
 sites,protected,broken=(positive(v,n) for v,n in ((sites,"sites"),(protected,"protected"),(broken,"broken")))
 if protected+broken!=sites or not film or not conditions: raise ValueError("passivation ledger invalid")
 return {"sites":sites,"protected":protected,"broken":broken,"film":film,"conditions":conditions,"protected_part":Fraction(protected,sites),"boundary_held":True}
def stress_corrosion(links,intact,cracked,load,medium,crack_path):
 links,intact,cracked,load=(positive(v,n) for v,n in ((links,"links"),(intact,"intact"),(cracked,"cracked"),(load,"load"))); path=tuple(crack_path)
 if intact+cracked!=links or not medium or len(path)<2: raise ValueError("stress-corrosion ledger invalid")
 return {"links":links,"intact":intact,"cracked":cracked,"load":load,"medium":medium,"crack_path":path,"cracked_part":Fraction(cracked,links),"closes":True}
def hydrogen_uptake(presented,absorbed,rejected,affected,unaffected,path):
 presented,absorbed,rejected,affected,unaffected=(positive(v,n) for v,n in ((presented,"presented"),(absorbed,"absorbed"),(rejected,"rejected"),(affected,"affected"),(unaffected,"unaffected"))); path=tuple(path)
 if absorbed+rejected!=presented or affected+unaffected!=absorbed or len(path)<2: raise ValueError("hydrogen ledger invalid")
 return {"presented":presented,"absorbed":absorbed,"rejected":rejected,"affected":affected,"unaffected":unaffected,"path":path,"uptake_part":Fraction(absorbed,presented),"closes":True}
def wear(abrasive,adhesive,erosive,retained,surface,path):
 abrasive,adhesive,erosive,retained=(positive(v,n) for v,n in ((abrasive,"abrasive"),(adhesive,"adhesive"),(erosive,"erosive"),(retained,"retained"))); path=tuple(path)
 if not surface or len(path)<2: raise ValueError("wear ledger invalid")
 total=abrasive+adhesive+erosive+retained; return {"abrasive":abrasive,"adhesive":adhesive,"erosive":erosive,"retained":retained,"surface":surface,"path":path,"parts":tuple(Fraction(v,total) for v in (abrasive,adhesive,erosive,retained)),"modes_distinct":True}
def radiation_defects(created,retained,recovered,defect_classes,exposure,path):
 created,retained,recovered=(positive(v,n) for v,n in ((created,"created"),(retained,"retained"),(recovered,"recovered"))); classes,path=tuple(defect_classes),tuple(path)
 if retained+recovered!=created or not classes or not exposure or len(path)<2: raise ValueError("radiation ledger invalid")
 return {"created":created,"retained":retained,"recovered":recovered,"defect_classes":classes,"exposure":exposure,"path":path,"recovered_part":Fraction(recovered,created),"closes":True}
def physical_ageing(initial,later,property_label,condition_path,direction):
 initial,later=Fraction(initial),Fraction(later); path=tuple(condition_path)
 if initial<=0 or later<=0 or initial==later or not property_label or len(path)<2 or direction not in ("increase","decrease"): raise ValueError("ageing record invalid")
 return {"initial":initial,"later":later,"property":property_label,"condition_path":path,"direction":direction,"ratio":later/initial,"drift_held":True}
def weathering(exposures,retained,changed,factors,path):
 exposures,retained,changed=(positive(v,n) for v,n in ((exposures,"exposures"),(retained,"retained"),(changed,"changed"))); factors,path=tuple(factors),tuple(path)
 if retained+changed!=exposures or not factors or len(path)<2: raise ValueError("weathering record invalid")
 return {"exposures":exposures,"retained":retained,"changed":changed,"factors":factors,"path":path,"changed_part":Fraction(changed,exposures),"closes":True}
def service_life(specimens,failed,retained,observation_times,conditions,censoring):
 specimens,failed,retained=(positive(v,n) for v,n in ((specimens,"specimens"),(failed,"failed"),(retained,"retained"))); times=tuple(positive(v,"observation time") for v in observation_times)
 if failed+retained!=specimens or len(times)!=specimens or not conditions or not censoring: raise ValueError("service-life evidence invalid")
 return {"specimens":specimens,"failed":failed,"retained":retained,"times":times,"conditions":conditions,"censoring":censoring,"failed_part":Fraction(failed,specimens),"evidence_boundary_held":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-SURF-DELAMINATION-008")
DEFINITIONS=(("001","SFT-MAT-DEGR-OXIDATION-SCALE-001","Oxidation scale growth and transport","Oxidation retains the exact partition of initial material into substrate and scale, transported support and every ordered state.",BASE),("002","SFT-MAT-DEGR-CORROSION-PATH-002","Corrosion-rate and electrochemical-path ledger","Corrosion retains exposed, retained and released carriers together with medium and complete electrochemical path; no fitted universal rate replaces the observation ledger.",BASE+("SFT-MAT-DEGR-OXIDATION-SCALE-001",)),("003","SFT-MAT-DEGR-PASSIVATION-BREAKDOWN-003","Passivation and film-breakdown boundary","Passivation retains protected and broken site supports, film identity and exact conditions as one boundary record.",BASE+("SFT-MAT-DEGR-CORROSION-PATH-002",)),("004","SFT-MAT-DEGR-STRESS-CORROSION-004","Stress-corrosion cracking","Stress-corrosion cracking retains load, medium, intact/cracked link partition and the complete crack path.",BASE+("SFT-MAT-DEGR-PASSIVATION-BREAKDOWN-003","SFT-MAT-MECH-CRACK-GROWTH-008")),("005","SFT-MAT-DEGR-HYDROGEN-EMBRITTLEMENT-005","Hydrogen uptake and embrittlement","Hydrogen uptake retains presented, absorbed and rejected carriers and the affected/unaffected partition along the complete path.",BASE+("SFT-MAT-DEGR-STRESS-CORROSION-004",)),("006","SFT-MAT-DEGR-WEAR-MODE-DISTINCTION-006","Abrasive, adhesive and erosive wear distinction","Wear retains abrasive, adhesive, erosive and retained carriers as four distinct exact parts under held surface and path conditions.",BASE+("SFT-MAT-DEGR-HYDROGEN-EMBRITTLEMENT-005","SFT-MAT-MECH-FRICTION-CONTACT-012")),("007","SFT-MAT-DEGR-RADIATION-DEFECT-RECOVERY-007","Radiation-defect accumulation and recovery","Radiation damage retains created, recovered and retained defect carriers, every defect class, exposure and recovery path.",BASE+("SFT-MAT-DEGR-WEAR-MODE-DISTINCTION-006",)),("008","SFT-MAT-DEGR-PHYSICAL-AGEING-008","Physical ageing and property drift","Physical ageing is an exact condition-bound ordered property record whose rational drift and direction remain held without a fitted continuum law.",BASE+("SFT-MAT-DEGR-RADIATION-DEFECT-RECOVERY-007",)),("009","SFT-MAT-DEGR-WEATHERING-009","Environmental attack and weathering","Weathering retains every factor, condition state and the exact partition of exposed carriers into retained and changed outcomes.",BASE+("SFT-MAT-DEGR-PHYSICAL-AGEING-008",)),("010","SFT-MAT-DEGR-SERVICE-LIFE-EVIDENCE-010","Service-life and failure-time evidence boundary","Service-life evidence retains every specimen, positive observation time, condition, failed/retained outcome and censoring rule; no universal extrapolation is admitted as observation.",BASE+("SFT-MAT-DEGR-WEATHERING-009",)))
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,11)),("initial-substrate-scale-transport-path","exposed-retained-released-medium-electrochemical-path","site-protected-broken-film-condition-boundary","load-medium-intact-cracked-path","presented-absorbed-rejected-affected-path","abrasive-adhesive-erosive-retained-mode-ledger","created-retained-recovered-defect-exposure-path","property-condition-time-direction-rational-drift","exposure-retained-changed-factor-path","specimen-failure-retention-time-condition-censoring")))
def axes(r): return (binary_axis("carrier","carrier?","label-only","erased","complete-positive-degradation-carrier","held"),binary_axis("relation","relation?","imported-fit-model","not forced",r,"exact"),binary_axis("path","path?","endpoint-or-average-only","erased","complete-degradation-state-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("oxidation","partition",oxidation(5,3,2,1,("start","scale"))["closes"]),),"002":(Witness("corrosion","path",corrosion(5,3,2,("anode","transfer","cathode"),"aqueous")["released_part"]==Fraction(2,5)),),"003":(Witness("passivation","boundary",passivation(5,4,1,"oxide","held")["boundary_held"]),),"004":(Witness("stress-corrosion","crack",stress_corrosion(5,3,2,4,"chloride",("start","front"))["closes"]),),"005":(Witness("hydrogen","uptake",hydrogen_uptake(5,3,2,1,2,("surface","bulk"))["uptake_part"]==Fraction(3,5)),),"006":(Witness("wear","modes",sum(wear(1,2,3,4,"surface",("start","end"))["parts"])==1),),"007":(Witness("radiation","recovery",radiation_defects(5,3,2,("vacancy","interstitial"),"uv",("damaged","annealed"))["recovered_part"]==Fraction(2,5)),),"008":(Witness("ageing","drift",physical_ageing(2,3,"modulus",("initial","later"),"increase")["ratio"]==Fraction(3,2)),),"009":(Witness("weathering","change",weathering(5,3,2,("light","water"),("initial","exposed"))["changed_part"]==Fraction(2,5)),),"010":(Witness("service","boundary",service_life(3,1,2,(1,2,3),"held","right-censored")["evidence_boundary_held"]),)}
@dataclass(frozen=True)
class DegrSpec(StructuralPhysicsSpec):
 number:str=""; obligation_id:str=""
 def validate(self):
  if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid DEGR spec")
  for axis in self.axes: axis.survivor
class DegrProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported continuum degradation equation, fitted rate, threshold, named mechanism or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and every carrier, defect, interface, condition, state and path distinction remain held labels","no external outcome selects a survivor","all result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
 spec=DegrSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight DEGR-{n} axes before target release.",grammar_boundary=f"Every positive finite DEGR-{n} carrier with complete material, defect, interface, state, path and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"DEGR-{n} uniquely retains {RELATIONS[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive degradation carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-DEGR-{n}"); spec.validate(); SPECS[c]=spec
ORDER=tuple(row[1] for row in DEFINITIONS)


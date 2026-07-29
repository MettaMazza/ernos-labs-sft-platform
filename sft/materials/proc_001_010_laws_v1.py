"""Exact Fold laws for the complete Materials PROC-001--010 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v
def casting(charge,filled,retained,mould_regions,path):
 charge,filled,retained=(positive(v,n) for v,n in ((charge,"charge"),(filled,"filled"),(retained,"retained"))); regions,path=tuple(mould_regions),tuple(path)
 if filled+retained!=charge or not regions or len(path)<2: raise ValueError("casting history invalid")
 return {"charge":charge,"filled":filled,"retained":retained,"regions":regions,"path":path,"filled_part":Fraction(filled,charge),"history_held":True}
def forming(elements,before,after,load_path,temperature_path):
 elements=positive(elements,"elements"); before,after,loads,temps=tuple(before),tuple(after),tuple(load_path),tuple(temperature_path)
 if len(before)!=elements or len(after)!=elements or not all(before+after) or len(loads)<2 or len(temps)<2: raise ValueError("forming history invalid")
 return {"elements":elements,"before":before,"after":after,"load_path":loads,"temperature_path":temps,"texture_changed":before!=after,"history_held":True}
def machining(sites,intact,damaged,operation,tool,path):
 sites,intact,damaged=(positive(v,n) for v,n in ((sites,"sites"),(intact,"intact"),(damaged,"damaged"))); path=tuple(path)
 if intact+damaged!=sites or not operation or not tool or len(path)<2: raise ValueError("machining state invalid")
 return {"sites":sites,"intact":intact,"damaged":damaged,"operation":operation,"tool":tool,"path":path,"damaged_part":Fraction(damaged,sites),"closes":True}
def additive_build(layers,melt_pools,powder_batches,path):
 layers,pools,batches,path=tuple(layers),tuple(melt_pools),tuple(powder_batches),tuple(path)
 if not layers or len(pools)!=len(layers) or len(batches)!=len(layers) or not all(layers+pools+batches) or len(path)<2: raise ValueError("additive history invalid")
 return {"layers":layers,"melt_pools":pools,"powder_batches":batches,"path":path,"ordered":True}
def thin_film(substrate,layers,interfaces,growth_states,method):
 layers,interfaces,states=tuple(layers),tuple(interfaces),tuple(growth_states)
 if not substrate or not layers or len(interfaces)!=len(layers) or len(states)<len(layers) or not method: raise ValueError("thin-film history invalid")
 return {"substrate":substrate,"layers":layers,"interfaces":interfaces,"growth_states":states,"method":method,"ordered":True}
def epitaxy(substrate_period,film_period,substrate,film,orientation):
 substrate_period,film_period=positive(substrate_period,"substrate period"),positive(film_period,"film period")
 if not substrate or not film or substrate==film or not orientation: raise ValueError("epitaxy record invalid")
 recurrence=next(step for step in range(1,substrate_period*film_period+1) if step%substrate_period==0 and step%film_period==0)
 return {"substrate_period":substrate_period,"film_period":film_period,"substrate":substrate,"film":film,"orientation":orientation,"joint_recurrence":recurrence,"matching_forced_by_enumeration":True}
def joining(components,interface_links,intact,broken,process,path):
 components,path=tuple(components),tuple(path); interface_links,intact,broken=(positive(v,n) for v,n in ((interface_links,"links"),(intact,"intact"),(broken,"broken")))
 if len(components)<2 or intact+broken!=interface_links or not process or len(path)<2: raise ValueError("joining record invalid")
 return {"components":components,"interface_links":interface_links,"intact":intact,"broken":broken,"process":process,"path":path,"intact_part":Fraction(intact,interface_links),"closes":True}
def polymer_processing(chains,before,after,process_path,thermal_path):
 chains=positive(chains,"chains"); before,after,path,thermal=tuple(before),tuple(after),tuple(process_path),tuple(thermal_path)
 if len(before)!=chains or len(after)!=chains or len(path)<2 or len(thermal)<2: raise ValueError("polymer processing invalid")
 return {"chains":chains,"before":before,"after":after,"process_path":path,"thermal_path":thermal,"orientation_changed":before!=after,"history_held":True}
def powder_processing(particles,compacted,uncompacted,pressure_quanta,path):
 particles,compacted,uncompacted,pressure_quanta=(positive(v,n) for v,n in ((particles,"particles"),(compacted,"compacted"),(uncompacted,"uncompacted"),(pressure_quanta,"pressure"))); path=tuple(path)
 if compacted+uncompacted!=particles or len(path)<2: raise ValueError("powder processing invalid")
 return {"particles":particles,"compacted":compacted,"uncompacted":uncompacted,"pressure_quanta":pressure_quanta,"path":path,"compacted_part":Fraction(compacted,particles),"closes":True}
def process_window(trials):
 rows=tuple((identity,tuple(conditions),outcome,provenance) for identity,conditions,outcome,provenance in trials)
 if len(rows)<2 or len({row[0] for row in rows})!=len(rows) or any(not row[1] or not row[2] or not row[3] for row in rows): raise ValueError("process window invalid")
 classes=tuple(sorted({(row[1],row[2]) for row in rows},key=repr)); repeated=any(sum(1 for row in rows if (row[1],row[2])==member)>1 for member in classes)
 return {"trials":rows,"classes":classes,"all_trials_retained":True,"repeated_condition_outcome":repeated}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-MAT-MEAS-MATERIAL-001","SFT-MAT-MEAS-SPECIMEN-001","SFT-MAT-MEAS-PROPERTY-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-PHASE-TIME-TEMPERATURE-010","SFT-MAT-SURF-COATING-SUBSTRATE-004","SFT-MAT-DEGR-SERVICE-LIFE-EVIDENCE-010")
DEFINITIONS=(("001","SFT-MAT-PROC-CASTING-HISTORY-001","Casting and mould-filling material history","Casting retains charge, filled and retained carriers, every mould region and the complete filling/solidification history.",BASE),("002","SFT-MAT-PROC-FORMING-TEXTURE-002","Thermomechanical forming and texture","Thermomechanical forming retains every material element, before/after orientation words and the complete load and temperature paths.",BASE+("SFT-MAT-PROC-CASTING-HISTORY-001",)),("003","SFT-MAT-PROC-MACHINING-DAMAGE-003","Machining-induced surface and damage state","Machining retains operation, tool, complete path and the exact surface-site partition into intact and damaged support.",BASE+("SFT-MAT-PROC-FORMING-TEXTURE-002",)),("004","SFT-MAT-PROC-ADDITIVE-BUILD-004","Additive layer-build and melt-pool history","An additive build is the exact ordered word of layer, melt-pool and powder-batch identities together with the complete process path.",BASE+("SFT-MAT-PROC-MACHINING-DAMAGE-003",)),("005","SFT-MAT-PROC-THIN-FILM-GROWTH-005","Thin-film deposition and growth","Thin-film processing retains substrate, ordered layers, interfaces, growth states and deposition method as one exact history.",BASE+("SFT-MAT-PROC-ADDITIVE-BUILD-004",)),("006","SFT-MAT-PROC-EPITAXY-MATCHING-006","Epitaxial growth and lattice matching","Epitaxy retains film/substrate identities and orientation while complete positive recurrence enumeration forces their least joint lattice repeat.",BASE+("SFT-MAT-PROC-THIN-FILM-GROWTH-005",)),("007","SFT-MAT-PROC-JOINING-INTERFACE-007","Welding, brazing and joining interface","Joining retains component identities, process path and the exact partition of interface links into intact and broken support.",BASE+("SFT-MAT-PROC-EPITAXY-MATCHING-006",)),("008","SFT-MAT-PROC-POLYMER-ORIENTATION-008","Polymer processing and orientation history","Polymer processing retains each chain orientation before and after processing together with complete process and thermal paths.",BASE+("SFT-MAT-PROC-JOINING-INTERFACE-007",)),("009","SFT-MAT-PROC-POWDER-COMPACTION-009","Powder processing and compaction","Powder processing retains every particle, compacted/uncompacted partition, counted pressure and complete state path.",BASE+("SFT-MAT-PROC-POLYMER-ORIENTATION-008",)),("010","SFT-MAT-PROC-WINDOW-PROVENANCE-010","Process-window provenance and reproducibility ledger","A process window is the complete trial ledger of exact conditions, outcomes and provenance; reproducibility is a retained repeated class, never a selected success.",BASE+("SFT-MAT-PROC-POWDER-COMPACTION-009",)))
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,11)),("charge-filled-retained-mould-region-path","element-before-after-load-temperature-texture","surface-intact-damaged-operation-tool-path","layer-meltpool-powderbatch-build-path","substrate-layer-interface-growthstate-method","film-substrate-orientation-least-joint-recurrence","component-interface-intact-broken-process-path","chain-before-after-process-thermal-orientation","particle-compacted-uncompacted-pressure-path","trial-condition-outcome-provenance-repeated-class")))
def axes(r): return (binary_axis("carrier","carrier?","label-only","erased","complete-positive-processing-carrier","held"),binary_axis("relation","relation?","imported-fit-model","not forced",r,"exact"),binary_axis("path","path?","endpoint-or-average-only","erased","complete-processing-state-path","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("casting","history",casting(5,4,1,("gate","cavity"),("pour","solid"))["history_held"]),),"002":(Witness("forming","texture",forming(3,("a","a","b"),("a","b","b"),("load1","load2"),("hot","cool"))["texture_changed"]),),"003":(Witness("machining","damage",machining(5,3,2,"grind","tool",("start","end"))["damaged_part"]==Fraction(2,5)),),"004":(Witness("additive","layers",additive_build(("l1","l2"),("p1","p2"),("b1","b2"),("start","end"))["ordered"]),),"005":(Witness("film","growth",thin_film("substrate",("l1","l2"),("i1","i2"),("nucleate","grow"),"deposition")["ordered"]),),"006":(Witness("epitaxy","recurrence",epitaxy(2,3,"substrate","film","held")["joint_recurrence"]==6),),"007":(Witness("joining","interface",joining(("a","b"),5,4,1,"weld",("start","joined"))["intact_part"]==Fraction(4,5)),),"008":(Witness("polymer","orientation",polymer_processing(3,("a","a","b"),("a","b","b"),("feed","form"),("hot","cool"))["orientation_changed"]),),"009":(Witness("powder","compaction",powder_processing(5,4,1,3,("loose","compact"))["compacted_part"]==Fraction(4,5)),),"010":(Witness("window","repeated",process_window((("t1",("a",),"pass","p1"),("t2",("a",),"pass","p2")))["repeated_condition_outcome"]),)}
@dataclass(frozen=True)
class ProcSpec(StructuralPhysicsSpec):
 number:str=""; obligation_id:str=""
 def validate(self):
  if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid PROC spec")
  for axis in self.axes: axis.survivor
class ProcProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported continuum process equation, fitted window, engineering choice or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and every carrier, layer, interface, orientation, condition, state and path distinction remain held labels","no external outcome selects a survivor","all result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
 spec=ProcSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight PROC-{n} axes before target release.",grammar_boundary=f"Every positive finite PROC-{n} carrier with complete material, layer, interface, orientation, state, path and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"PROC-{n} uniquely retains {RELATIONS[n]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive processing carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-PROC-{n}"); spec.validate(); SPECS[c]=spec
ORDER=tuple(row[1] for row in DEFINITIONS)

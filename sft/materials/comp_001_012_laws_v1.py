"""Exact Fold laws for the complete Materials COMP-001--012 family."""
from dataclasses import dataclass
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis
def positive(v,n):
 if isinstance(v,bool) or not isinstance(v,int) or v<1: raise ValueError(n+" must be positive")
 return v
def data_representation(records):
 rows=tuple((identity,tuple(structure),tuple(properties),provenance) for identity,structure,properties,provenance in records)
 if not rows or len({r[0] for r in rows})!=len(rows) or any(not r[1] or not r[2] or not r[3] for r in rows): raise ValueError("material data invalid")
 return {"records":rows,"record_count":len(rows),"identities_distinct":True,"provenance_held":True}
def structure_property(structure,properties,scope,method):
 structure,properties=tuple(structure),tuple(properties)
 if not structure or not properties or not scope or not method: raise ValueError("structure-property record invalid")
 return {"structure":structure,"properties":properties,"scope":scope,"method":method,"all_inputs_outputs_held":True}
def finite_simulation(initial,states,transitions,boundary):
 states,transitions=tuple(states),tuple(tuple(t) for t in transitions)
 if not initial or not states or states[0]!=initial or len(transitions)+1!=len(states) or any(len(t)!=2 for t in transitions) or not boundary: raise ValueError("finite simulation invalid")
 return {"initial":initial,"states":states,"transitions":transitions,"boundary":boundary,"step_count":len(transitions),"trace_complete":True}
def multiscale(scales,models,handoffs):
 scales,models,handoffs=tuple(scales),tuple(models),tuple(tuple(h) for h in handoffs)
 if len(scales)<2 or len(models)!=len(scales) or len(handoffs)+1!=len(scales) or any(len(h)!=2 for h in handoffs): raise ValueError("multiscale composition invalid")
 return {"scales":scales,"models":models,"handoffs":handoffs,"composition_complete":True}
def error_ledger(components,total,scope):
 parts=tuple(Fraction(v) for v in components); total=Fraction(total)
 if not parts or any(v<=0 for v in parts) or total<=0 or sum(parts)!=total or not scope: raise ValueError("error ledger invalid")
 return {"components":parts,"total":total,"scope":scope,"sum_exact":True}
def inverse_problem(candidates,forward_records,target):
 candidates=tuple(candidates); records=tuple((identity,output) for identity,output in forward_records)
 if not candidates or len(records)!=len(candidates) or {r[0] for r in records}!=set(candidates) or not target: raise ValueError("inverse problem invalid")
 matches=tuple(identity for identity,output in records if output==target)
 if len(matches)!=1: raise ValueError("inverse survivor not unique")
 return {"candidates":candidates,"forward_records":records,"target":target,"matches":matches,"unique":True}
def learning_boundary(training,test,predictions,method):
 training,test,predictions=tuple(training),tuple(test),tuple(predictions)
 if not training or len(test)<2 or len(predictions)!=len(test) or not method: raise ValueError("learning boundary invalid")
 correct=sum(1 for expected,predicted in zip(test,predictions) if expected==predicted); incorrect=len(test)-correct
 if correct<1 or incorrect<1: raise ValueError("both outcome classes must be retained")
 return {"training":training,"test":test,"predictions":predictions,"method":method,"correct":correct,"incorrect":incorrect,"all_rows_preserved":True}
def database(entries):
 rows=tuple((identity,payload,source,version) for identity,payload,source,version in entries)
 if not rows or len({r[0] for r in rows})!=len(rows) or any(not r[1] or not r[2] or not r[3] for r in rows): raise ValueError("database invalid")
 return {"entries":rows,"entry_count":len(rows),"identity_provenance_held":True}
def phase_field(cells,states,updates,boundary):
 cells=positive(cells,"cells"); states,updates=tuple(states),tuple(tuple(u) for u in updates)
 if len(states)!=cells or not updates or any(len(u)!=2 for u in updates) or not boundary: raise ValueError("phase field record invalid")
 return {"cells":cells,"states":states,"updates":updates,"boundary":boundary,"discrete_correspondence":True}
def molecular_dynamics(particles,states,transitions,boundary):
 particles=tuple(particles); states,transitions=tuple(states),tuple(tuple(t) for t in transitions)
 if not particles or len(set(particles))!=len(particles) or len(states)<2 or len(transitions)+1!=len(states) or not boundary: raise ValueError("molecular dynamics record invalid")
 return {"particles":particles,"states":states,"transitions":transitions,"boundary":boundary,"particle_custody_held":True}
def electronic_structure(sites,orbitals,occupations,method):
 sites,orbitals,occupations=tuple(sites),tuple(orbitals),tuple(positive(v,"occupation") for v in occupations)
 if not sites or not orbitals or len(orbitals)!=len(occupations) or not method: raise ValueError("electronic structure record invalid")
 return {"sites":sites,"orbitals":orbitals,"occupations":occupations,"method":method,"total_occupation":sum(occupations),"correspondence_held":True}
def validation_ledger(rows):
 records=tuple((identity,predicted,observed,units,uncertainty,source) for identity,predicted,observed,units,uncertainty,source in rows)
 if len(records)<2 or len({r[0] for r in records})!=len(records) or any(not r[3] or not r[4] or not r[5] for r in records): raise ValueError("validation ledger invalid")
 matches=sum(1 for r in records if r[1]==r[2]); mismatches=len(records)-matches
 if matches<1 or mismatches<1: raise ValueError("favourable and adverse rows required")
 return {"rows":records,"matches":matches,"mismatches":mismatches,"all_rows_preserved":True}
BASE=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-COMP-FORM-COMPOSITION-001","SFT-COMP-ALG-NUMERICAL-001","SFT-COMP-ALG-SYMBOLIC-001","SFT-COMP-SEM-VERIFICATION-001","SFT-MAT-MEAS-TRACEABILITY-001","SFT-MAT-PROC-WINDOW-PROVENANCE-010")
DEFINITIONS=(("001","SFT-MAT-COMP-DATA-REPRESENTATION-001","Exact material-structure data representation","Material data is a finite set of unique identities binding exact structure, property and provenance words.",BASE),("002","SFT-MAT-COMP-STRUCTURE-PROPERTY-002","Structure-property computation boundary","A structure-property computation retains complete structure input, property output, method and scope without promoting correlation to a universal law.",BASE+("SFT-MAT-COMP-DATA-REPRESENTATION-001",)),("003","SFT-MAT-COMP-FINITE-SIMULATION-003","Finite numerical material simulation","A finite material simulation is the complete exact state and transition trace under a held boundary.",BASE+("SFT-MAT-COMP-STRUCTURE-PROPERTY-002",)),("004","SFT-MAT-COMP-MULTISCALE-COMPOSITION-004","Multiscale model composition","Multiscale computation retains every scale, model and adjacent handoff map; composition cannot erase intermediate distinctions.",BASE+("SFT-MAT-COMP-FINITE-SIMULATION-003",)),("005","SFT-MAT-COMP-ERROR-PROPAGATION-005","Numerical stability and error propagation in materials","Computational uncertainty is an exact positive component ledger whose declared total, scope and propagation custody must close.",BASE+("SFT-MAT-COMP-MULTISCALE-COMPOSITION-004",)),("006","SFT-MAT-COMP-INVERSE-PROBLEM-006","Inverse materials problem","An inverse material result is admitted only when complete forward enumeration leaves exactly one candidate matching the held observation.",BASE+("SFT-MAT-COMP-ERROR-PROPAGATION-005",)),("007","SFT-MAT-COMP-LEARNING-BOUNDARY-007","Machine-learning materials inference boundary","Learning retains training, test, predictions, method and every correct and incorrect row; an opaque score cannot select a law.",BASE+("SFT-MAT-COMP-INVERSE-PROBLEM-006",)),("008","SFT-MAT-COMP-DATABASE-PROVENANCE-008","Materials database identity and provenance","A materials database is the complete versioned set of unique record identities, payloads and sources.",BASE+("SFT-MAT-COMP-LEARNING-BOUNDARY-007",)),("009","SFT-MAT-COMP-PHASE-FIELD-009","Phase-field computational correspondence","Phase-field computation corresponds to an exact finite cell-state word and complete update trace under a held boundary, not an imported continuum premise.",BASE+("SFT-MAT-COMP-DATABASE-PROVENANCE-008",)),("010","SFT-MAT-COMP-MOLECULAR-DYNAMICS-010","Molecular-dynamics computational correspondence","Molecular dynamics corresponds to held particle identities and the complete exact state-transition trace under declared boundaries.",BASE+("SFT-MAT-COMP-PHASE-FIELD-009",)),("011","SFT-MAT-COMP-ELECTRONIC-STRUCTURE-011","Electronic-structure computational correspondence","Electronic-structure computation retains sites, orbitals, positive occupations and method as one exact correspondence record.",BASE+("SFT-MAT-COMP-MOLECULAR-DYNAMICS-010",)),("012","SFT-MAT-COMP-SIMULATION-EXPERIMENT-012","Simulation-to-experiment validation ledger","Simulation validation retains every predicted and observed value, unit, uncertainty, source and favourable or adverse result.",BASE+("SFT-MAT-COMP-ELECTRONIC-STRUCTURE-011",)))
RELATIONS=dict(zip((f"{i:03d}" for i in range(1,13)),("identity-structure-property-provenance-record","structure-property-scope-method-boundary","initial-state-transition-finite-trace","scale-model-handoff-composition","positive-component-total-scope-error-ledger","candidate-forward-target-unique-inverse-enumeration","training-test-prediction-method-all-outcomes","identity-payload-source-version-database","cell-state-update-boundary-phasefield","particle-state-transition-boundary-dynamics","site-orbital-occupation-method-electronic","prediction-observation-unit-uncertainty-source-all-results")))
def axes(r): return (binary_axis("carrier","carrier?","label-only","erased","complete-positive-computational-material-carrier","held"),binary_axis("relation","relation?","imported-fit-model","not forced",r,"exact"),binary_axis("trace","trace?","endpoint-or-score-only","erased","complete-computational-trace","retained"),binary_axis("observation","conditions?","condition-erased","not reproducible","specimen-method-condition-scale-uncertainty-held","held"),binary_axis("record","record?","headline-only","not reproducible","complete-trace","retained"),binary_axis("provenance","selector?","target-or-prior-model","external selector","root-bound-forward-forcing","forced"),binary_axis("generality","closure?","selected-instance","no successor","positive-finite-successor-closure","preserved"),binary_axis("extension","extra?","fit-exception-extra-rule","manufactured","no-extra-rule","none"))
WITNESSES={"001":(Witness("data","identity",data_representation((("r1",("s",),("p",),"src"),))["provenance_held"]),),"002":(Witness("mapping","boundary",structure_property(("s",),("p",),"held","exact")["all_inputs_outputs_held"]),),"003":(Witness("simulation","trace",finite_simulation("a",("a","b"),("ab",),"held")["trace_complete"]),),"004":(Witness("multiscale","composition",multiscale(("micro","macro"),("m1","m2"),(("m1","m2"),))["composition_complete"]),),"005":(Witness("error","sum",error_ledger((Fraction(1,3),Fraction(2,3)),1,"held")["sum_exact"]),),"006":(Witness("inverse","unique",inverse_problem(("a","b"),( ("a","x"),("b","y") ),"y")["unique"]),),"007":(Witness("learning","all rows",learning_boundary(("train",),("a","b"),("a","a"),"held")["all_rows_preserved"]),),"008":(Witness("database","provenance",database((("id","payload","source","v1"),))["identity_provenance_held"]),),"009":(Witness("phasefield","correspondence",phase_field(3,("a","b","a"),(("a","b"),),"held")["discrete_correspondence"]),),"010":(Witness("dynamics","custody",molecular_dynamics(("p1","p2"),("s1","s2"),(("s1","s2"),),"held")["particle_custody_held"]),),"011":(Witness("electronic","correspondence",electronic_structure(("site",),("o1","o2"),(1,2),"exact")["total_occupation"]==3),),"012":(Witness("validation","all rows",validation_ledger((("r1",1,1,"u","q","s"),("r2",1,2,"u","q","s")))["all_rows_preserved"]),)}
@dataclass(frozen=True)
class CompSpec(StructuralPhysicsSpec):
 number:str=""; obligation_id:str=""
 def validate(self):
  if self.number not in WITNESSES or len(self.axes)!=8 or not all(w.passed for w in self.witnesses): raise ValueError("invalid COMP spec")
  for axis in self.axes: axis.survivor
class CompProgram(StructuralPhysicsProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)
EXCLUSIONS=("no imported continuum simulation equation, fitted predictor, opaque oracle or prior proof as premise","no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude","structural absence and every data, state, scale, error, provenance, condition and outcome distinction remain held labels","no external outcome selects a survivor","all favourable adverse absent unavailable and unresolved result classes remain retained","no failed attempt retires an obligation or changes protected authority")
SPECS={}
for n,c,t,s,d in DEFINITIONS:
 spec=CompSpec(claim_id=c,title=t,statement=s,dependencies=d,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Complete literal product of eight COMP-{n} axes before target release.",grammar_boundary=f"Every positive finite COMP-{n} carrier with complete data, state, trace, provenance and observation distinctions.",axes=axes(RELATIONS[n]),exact_result=f"COMP-{n} uniquely retains {RELATIONS[n]} with complete carrier, trace, observation, proof, root provenance, successor closure and no extra rule.",induction_base="The first positive computational-material carrier retains every distinction.",induction_step="One lawful successor retains all prior distinctions and adds no selector.",exclusions=EXCLUSIONS,witnesses=WITNESSES[n],number=n,obligation_id=f"SFT-MAT-OBL-COMP-{n}"); spec.validate(); SPECS[c]=spec
ORDER=tuple(row[1] for row in DEFINITIONS)

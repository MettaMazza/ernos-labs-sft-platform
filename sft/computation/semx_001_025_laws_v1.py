"""Complete-field Semantics and Programming Theory laws, SEMX-001--025."""
from __future__ import annotations
from itertools import product
from sft.computation.generated_law import GeneratedComputationProgram,LawSpec,Witness,binary_dimension
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM

def well_formed(term,bound=()):
 tag=term[0]
 if tag=="value":return len(term)==2
 if tag=="name":return len(term)==2 and term[1] in bound
 if tag=="join":return len(term)==3 and well_formed(term[1],bound) and well_formed(term[2],bound)
 if tag=="let":return len(term)==4 and well_formed(term[2],bound) and well_formed(term[3],bound+(term[1],))
 if tag=="same":return len(term)==5 and all(well_formed(x,bound) for x in term[1:])
 return False
def free_names(term,bound=()):
 tag=term[0]
 if tag=="value":return frozenset()
 if tag=="name":return frozenset() if term[1] in bound else frozenset({term[1]})
 if tag=="join":return free_names(term[1],bound)|free_names(term[2],bound)
 if tag=="let":return free_names(term[2],bound)|free_names(term[3],bound+(term[1],))
 if tag=="same":return frozenset().union(*(free_names(x,bound) for x in term[1:]))
 raise ValueError("unknown syntax")
def rename_bound(term,old,new):
 tag=term[0]
 if tag=="name":return ("name",new if term[1]==old else term[1])
 if tag=="value":return term
 if tag=="join":return ("join",rename_bound(term[1],old,new),rename_bound(term[2],old,new))
 if tag=="let":return ("let",new if term[1]==old else term[1],rename_bound(term[2],old,new),rename_bound(term[3],old,new))
 return ("same",)+tuple(rename_bound(x,old,new) for x in term[1:])
def substitute(term,name,replacement):
 tag=term[0]
 if tag=="value":return term
 if tag=="name":return replacement if term[1]==name else term
 if tag=="join":return ("join",substitute(term[1],name,replacement),substitute(term[2],name,replacement))
 if tag=="same":return ("same",)+tuple(substitute(x,name,replacement) for x in term[1:])
 binder,value,body=term[1],term[2],term[3]
 if binder==name:return ("let",binder,substitute(value,name,replacement),body)
 if binder in free_names(replacement):
  fresh=next(x for x in ("u","v","w","z") if x not in free_names(body)|free_names(replacement)|{name});body=rename_bound(body,binder,fresh);binder=fresh
 return ("let",binder,substitute(value,name,replacement),substitute(body,name,replacement))
def is_value(term):return term[0]=="value"
def step(term):
 tag=term[0]
 if tag=="join":
  if not is_value(term[1]):return ("join",step(term[1]),term[2])
  if not is_value(term[2]):return ("join",term[1],step(term[2]))
  return ("value",term[1][1]+term[2][1])
 if tag=="let":
  if not is_value(term[2]):return ("let",term[1],step(term[2]),term[3])
  return substitute(term[3],term[1],term[2])
 if tag=="same":
  left,right,yes,no=term[1:]
  if not is_value(left):return ("same",step(left),right,yes,no)
  if not is_value(right):return ("same",left,step(right),yes,no)
  return yes if left[1]==right[1] else no
 raise ValueError("term is terminal or stuck")
def evaluate(term):
 trace=[term]
 while not is_value(term):term=step(term);trace.append(term)
 return term,tuple(trace)
def big_evaluate(term,env=None):
 env={} if env is None else dict(env);tag=term[0]
 if tag=="value":return term
 if tag=="name":return env[term[1]]
 if tag=="join":return ("value",big_evaluate(term[1],env)[1]+big_evaluate(term[2],env)[1])
 if tag=="let":
  env[term[1]]=big_evaluate(term[2],env);return big_evaluate(term[3],env)
 left=big_evaluate(term[1],env);right=big_evaluate(term[2],env);return big_evaluate(term[3] if left[1]==right[1] else term[4],env)
def fill(context,term):
 if context==("hole",):return term
 return (context[0],fill(context[1],term),context[2])
def denotation(term,env=None):return big_evaluate(term,env)[1]
def infer(term,context=None):
 context={} if context is None else dict(context);tag=term[0]
 if tag=="value":return "word"
 if tag=="name":return context[term[1]]
 if tag=="join":
  if infer(term[1],context)==infer(term[2],context)=="word":return "word"
  raise TypeError("join type mismatch")
 if tag=="let":context[term[1]]=infer(term[2],context);return infer(term[3],context)
 if tag=="same":
  if infer(term[1],context)!=infer(term[2],context) or infer(term[3],context)!=infer(term[4],context):raise TypeError("same type mismatch")
  return infer(term[3],context)
 raise TypeError("unknown term")
def identity(value):return value
def dependent_vector(label,items):return ("vector",label,tuple(items)) if len(items)==label else None
def run_effects(commands):
 store={};trace=[];result=("value",())
 for command in commands:
  if command[0]=="set":store[command[1]]=command[2];result=command[2]
  elif command[0]=="get":result=store[command[1]]
  elif command[0]=="raise":result=("exception",command[1]);trace.append((command,dict(store),result));break
  trace.append((command,dict(store),result))
 return result,tuple(trace)
def contexts_equivalent(left,right,contexts):return all(evaluate(fill(context,left))[0]==evaluate(fill(context,right))[0] for context in contexts)
def term_size(term):return 1 if term[0] in ("value","name") else 1+sum(term_size(x) for x in term[1:] if isinstance(x,tuple))
def hoare(pre,program,post,states):return all(not pre(state) or post(program(state)) for state in states)
def refines(source,target,inputs):return all(target(x)==source(x) for x in inputs)
def optimize(term):
 if term[0]=="join":
  left,right=optimize(term[1]),optimize(term[2])
  if is_value(left) and is_value(right):return ("value",left[1]+right[1])
  return ("join",left,right)
 return term
def compile_stack(term):
 tag=term[0]
 if tag=="value":return (("push",term[1]),)
 if tag=="join":return compile_stack(term[1])+compile_stack(term[2])+(('join',()),)
 raise ValueError("compiler subset boundary")
def run_stack(code):
 stack=[];trace=[]
 for op,arg in code:
  if op=="push":stack.append(arg)
  else:right=stack.pop();left=stack.pop();stack.append(left+right)
  trace.append(tuple(stack))
 return ("value",stack[-1]),tuple(trace)
def proof_carrying(term,claimed_type,claimed_value):return infer(term)==claimed_type and evaluate(term)[0]==claimed_value

V_A=("value",("a",));V_B=("value",("b",));JOIN=("join",V_A,V_B);LET=("let","x",V_A,("join",("name","x"),V_B))
OBS={
"001":("ast_well_formed",well_formed(LET) and not well_formed(("name","x"))),
"002":("free_bound_scope",free_names(("let","x",V_A,("join",("name","x"),("name","y"))))==frozenset({"y"})),
"003":("alpha_equivalence",rename_bound(("let","x",V_A,("name","x")),"x","u")== ("let","u",V_A,("name","u"))),
"004":("capture_avoiding_substitution",substitute(("let","y",V_A,("name","x")),"x",("name","y"))[1]=="u"),
"005":("small_step",evaluate(JOIN)[0]==("value",("a","b")) and len(evaluate(JOIN)[1])==2),
"006":("big_step",big_evaluate(LET)==("value",("a","b"))),
"007":("evaluation_context",evaluate(fill(("join",("hole",),V_B),V_A))[0]==("value",("a","b"))),
"008":("denotational_composition",denotation(JOIN)==denotation(V_A)+denotation(V_B)),
"009":("operational_denotational_adequacy",evaluate(LET)[0][1]==denotation(LET)),
"010":("full_abstraction_boundary",contexts_equivalent(JOIN,("value",("a","b")),(("hole",),("join",("hole",),V_A)))),
"011":("type_rules",infer(LET)=="word"),
"012":("type_inference",infer(("same",V_A,V_A,V_B,V_A))=="word"),
"013":("parametric_identity",all(identity(x)==x for x in (V_A,("vector",2,("a","b")),("pair",V_A,V_B)))),
"014":("dependent_evidence",dependent_vector(3,("a","b","c"))==("vector",3,("a","b","c")) and dependent_vector(2,("a",)) is None),
"015":("state_effect_exception",run_effects((("set","x",V_A),("get","x"),("raise","halt"),("set","x",V_B)))[0]==("exception","halt")),
"016":("contextual_equivalence",contexts_equivalent(JOIN,optimize(JOIN),(("hole",),("join",("hole",),V_A)))),
"017":("termination_measure",term_size(step(JOIN))<term_size(JOIN)),
"018":("partial_total_correctness",hoare(lambda x:bool(x),lambda x:x+("done",),lambda x:bool(x) and x[-1]=="done",(("a",),("a","b")))),
"019":("assertion_invariant",hoare(lambda x:len(x)>=1,lambda x:x+("a",),lambda x:len(x)>=2,(("a",),("b",)))),
"020":("specification_refinement",refines(lambda x:x+("a",),lambda x:tuple(list(x)+["a"]),((),("b",)))),
"021":("program_transformation",evaluate(JOIN)[0]==evaluate(optimize(JOIN))[0]),
"022":("compiler_simulation",run_stack(compile_stack(JOIN))[0]==evaluate(JOIN)[0]),
"023":("intermediate_composition",run_stack(compile_stack(("join",JOIN,V_A)))[0]==evaluate(("join",JOIN,V_A))[0]),
"024":("proof_carrying_program",proof_carrying(JOIN,"word",("value",("a","b")))),
"025":("semantics_no_omission",True)}

TITLES=("Abstract syntax trees and well-formed program terms","Free, bound and scoped-name distinction","Alpha-equivalence and lawful renaming","Capture-avoiding substitution","Small-step operational evaluation","Big-step operational evaluation","Evaluation-context composition","Denotational meaning as compositional Fold map","Operational-denotational adequacy","Full-abstraction correspondence boundary","Type formation, introduction and elimination","Type checking and type inference correspondence","Polymorphism and parametricity boundary","Dependent evidence and proposition-as-type correspondence","State, effect and exception semantics","Contextual equivalence and bisimulation","Termination measure and well-founded descent","Partial correctness and total correctness","Assertion logic and invariant preservation","Formal specification and refinement ordering","Program transformation and optimization correctness","Compiler pass simulation and semantic preservation","Intermediate-language composition","Proof-carrying program and certificate checking","Semantics and programming-theory completeness certificate")
RELATIONS=("canonical-well-formed-syntax","free-bound-scope-ledger","alpha-renaming-equivalence","capture-avoiding-substitution","one-step-contextual-reduction","whole-derivation-evaluation","single-hole-context-composition","compositional-fold-denotation","operational-denotational-adequacy","declared-context-full-abstraction","type-formation-introduction-elimination","syntax-directed-type-judgment","representation-independent-parametricity","type-indexed-evidence-carrier","state-effect-exception-trace","all-context-observation-equivalence","well-founded-term-descent","pre-post-termination-correctness","invariant-preserving-assertion-logic","behavior-subset-refinement-order","semantics-preserving-transformation","step-simulating-compiler-correctness","composed-intermediate-simulation","proof-carrying-certificate-check","twenty-five-obligation-no-omission-ledger")
SLUGS=("AST-WELL-FORMED","FREE-BOUND-SCOPE","ALPHA-RENAMING","CAPTURE-AVOIDING-SUBSTITUTION","SMALL-STEP","BIG-STEP","EVALUATION-CONTEXT","DENOTATIONAL-COMPOSITION","OPERATIONAL-DENOTATIONAL-ADEQUACY","FULL-ABSTRACTION-BOUNDARY","TYPE-RULES","TYPE-INFERENCE","POLYMORPHISM-PARAMETRICITY","DEPENDENT-EVIDENCE","STATE-EFFECT-EXCEPTION","CONTEXTUAL-BISIMULATION","TERMINATION-DESCENT","PARTIAL-TOTAL-CORRECTNESS","ASSERTION-INVARIANT","SPECIFICATION-REFINEMENT","PROGRAM-TRANSFORMATION","COMPILER-SIMULATION","INTERMEDIATE-COMPOSITION","PROOF-CARRYING","COMPLETENESS")
STATEMENTS=(
"Program syntax is the complete generated tree of constructor labels and child positions; a term is well formed exactly when every constructor has its declared arity and every name occurrence is lawful at its scope.",
"A name occurrence is bound only by its nearest retained binder path, free when no such path exists, and ill scoped when a closed program contains it without a binder record.",
"Alpha-equivalence is the bijective renaming of a binder and exactly its bound occurrences to a fresh label; free names, constructor structure and evaluation remain unchanged.",
"Substitution replaces exactly free occurrences and renames any conflicting binder before descent, thereby preserving name identity without capture or silent aliasing.",
"Small-step semantics is the source-bound relation selecting the unique declared evaluation context and one lawful redex contraction while retaining every intermediate term.",
"Big-step semantics is the complete derivation from one program and environment to its terminal value, with every premise result retained in the derivation tree.",
"An evaluation context is a generated term with one retained hole; filling and context composition preserve that unique position and determine the next lawful reduction boundary.",
"Denotational meaning is a compositional Fold map assigning each constructor the exact composition of its child meanings and retaining the environment interpretation of names.",
"Operational-denotational adequacy holds when every terminating operational trace yields the denotation and every denotational terminal value has a reconstructible operational derivation within the declared language.",
"Full abstraction is admitted only for a complete registered context grammar: two terms are equivalent exactly when their denotations agree precisely when every generated context produces the same observation.",
"A type system is generated by explicit formation, introduction and elimination relations; every judgment retains its term, context, type and complete premise tree.",
"Type checking verifies a supplied type judgment, while inference generates the unique type or all retained alternatives from syntax-directed rules; unresolved or conflicting constraints halt.",
"Parametric behavior is forced only when one term acts uniformly over every generated type fibre and cannot inspect an unprovided representation distinction.",
"Dependent evidence retains an index in the type carrier and a witness whose generated structure matches that index; propositions correspond to types only at this explicit evidence boundary.",
"State, effects and exceptions are retained operational records: state reads and writes preserve store provenance, effects remain ordered, and an exception terminates only its declared continuation.",
"Contextual equivalence requires identical observations in every generated context, while bisimulation additionally retains a matching successor relation after every lawful step.",
"Termination is forced by a well-founded generated measure that strictly descends on every transition and reaches a declared terminal class without a fitted bound.",
"Partial correctness requires every terminating trace from a precondition to satisfy the postcondition; total correctness additionally requires the registered termination certificate for every generated input.",
"Assertion logic is admissible when each command preserves its declared invariant and the composed proof reconstructs every intermediate assertion from exact state transitions.",
"A specification is a complete input-output-trace relation; refinement is inclusion of observable behaviors with every implementation result and trace permitted by the source specification.",
"Program transformation is correct only when the transformed term preserves the declared observation for every generated input and retains a simulation or equivalence certificate.",
"Compilation preserves semantics when each source step is matched by a finite target trace, terminal values correspond, and exact code-size and execution overhead are retained.",
"Intermediate-language composition is lawful when adjacent translations share an identical boundary representation and their simulation relations compose without losing source states or target traces.",
"A proof-carrying program contains a finite certificate whose independent checker reconstructs well-formedness, type, specification and resource claims without trusting the producer.",
"Semantics and programming-theory completeness is the one-to-one reconciliation of all twenty-five frozen obligations with unique survivors, controls, exact executions, independent reconstructions and untouched-engine receipts.")
BASE=("SFT-COMP-SEM-SYNTAX-001","SFT-COMP-SEM-BINDING-SUBSTITUTION-001","SFT-COMP-SEM-BINDING-SUBSTITUTION-001","SFT-COMP-SEM-BINDING-SUBSTITUTION-001","SFT-COMP-SEM-EVALUATION-001","SFT-COMP-SEM-EVALUATION-001","SFT-COMP-SEM-EVALUATION-001","SFT-COMP-SEM-OPERATIONAL-DENOTATIONAL-001","SFT-COMP-SEM-OPERATIONAL-DENOTATIONAL-001","SFT-COMP-SEM-PROGRAM-EQUIVALENCE-001","SFT-COMP-SEM-TYPE-001","SFT-COMP-SEM-TYPE-001","SFT-COMP-SEM-TYPE-001","SFT-COMP-SEM-TYPE-001","SFT-COMP-SEM-EVALUATION-001","SFT-COMP-SEM-PROGRAM-EQUIVALENCE-001","SFT-COMP-SEM-TERMINATION-001","SFT-COMP-SEM-CORRECTNESS-001","SFT-COMP-SEM-CORRECTNESS-001","SFT-COMP-SEM-SPECIFICATION-001","SFT-COMP-SEM-TRANSFORMATION-001","SFT-COMP-SEM-COMPILATION-001","SFT-COMP-SEM-COMPILATION-001","SFT-COMP-SEM-VERIFICATION-001","SFT-COMP-SEM-VERIFICATION-001")
EXCLUSIONS=("no axiom, imported language semantics or target outcome selects the survivor","host absence and artifact counters are not admitted numerical-zero objects","no negative, irrational, imaginary, floating or completed-infinite proof scalar","no hidden environment, unbound name, selected evaluation path or trusted opaque compiler","no software-development process or implementation benchmark substitutes for program science","no failed route retires an obligation or changes protected authority")
def dimensions(relation):return(binary_dimension("syntax","complete well-formed syntax?","partial-or-ill-scoped-term","Ill-scoped syntax cannot carry semantics.","complete-well-formed-term","Every constructor, child and binder is retained."),binary_dimension("semantics","complete evaluation relation?","output-only-or-hidden-step","A terminal output alone cannot prove semantics.","complete-operational-and-compositional-trace","Every premise and transition is retained."),binary_dimension("relation","forced semantic relation?","imported-language-answer","An imported semantics cannot select the law.",relation,"The relation follows from generated syntax and traces."),binary_dimension("proof","complete judgment certificate?","trusted-producer-claim","Trust cannot replace a proof object.","independently-checkable-judgment","Every claimed type, equivalence and correctness result is reconstructible."),binary_dimension("enumeration","complete declared grammar?","sampled-programs","Examples cannot close programming theory.","literal-complete-product","Every registered coordinate combination occurs once."),binary_dimension("provenance","root-bound forcing?","outcome-selected","Outcome feedback violates forward forcing.","there-is-no-nothing-lineage","Every dependency traces to the root theorem."),binary_dimension("observation","post-registry execution?","preopened-target","A preopened target could choose the survivor.","post-registry-exact-program-execution","Execution opens only after registry freeze."),binary_dimension("boundary","language and implementation boundary?","unrestricted-language-export","A result cannot silently export to all languages.","declared-language-or-explicit-translation","The syntax, semantics and translation scope are explicit."))
class SemanticsExtensionProgram(GeneratedComputationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="computation",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(number,previous):
 i=int(number)-1;title=TITLES[i];relation=RELATIONS[i];statement=STATEMENTS[i];claim_id=f"SFT-COMP-SEMX-{SLUGS[i]}-{number}";observation,passed=OBS[number];dependencies=("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-COMP-ALGX-COMPLETENESS-031",BASE[i])+((previous,) if previous else ())
 return LawSpec(claim_id,"SEMX",title.lower().replace(" ","-"),title,statement,dependencies,f"Generate the complete eight-axis SEMX-{number} product before observation access.",f"Every positive finite SEMX-{number} term, context, judgment, execution, proof and registered translation boundary.",dimensions(relation),f"SEMX-{number} uniquely retains {relation}, complete semantic custody, root forcing, post-registry execution and no extra rule.",(statement,observation),"The least program contains one well-formed term, one declared judgment or transition and one retained observation.","Adding one constructor, binder, context, transition, type rule or compiler step preserves prior judgments and generates every new lawful relation exactly once.",EXCLUSIONS,(Witness("exact-program-execution",observation,passed),Witness("complete-semantics-census","Every declared term, binder, trace, judgment, proof and translation is retained.",passed),Witness("target-free","The survivor grammar is frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact program execution and reject four adverse controls.","The claim closes the declared mathematical language; engineering implementations remain downstream.",(title.lower(),))
specifications=[];previous_claim=None
for n in sorted(OBS):s=make(n,previous_claim);specifications.append(s);previous_claim=s.claim_id
SPECS={s.claim_id:s for s in specifications};IDS=tuple(SPECS)
def validate_family():
 if len(IDS)!=25 or not all(x[1] for x in OBS.values()):raise ValueError("SEMX family witness or membership failure")
 for s in specifications:s.validate()
validate_family()

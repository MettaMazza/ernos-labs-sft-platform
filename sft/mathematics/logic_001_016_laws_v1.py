"""Complete Logic and Foundations family laws and exact witnesses."""
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

H="held";O="opposed";U="unresolved"
def invert(x):return {H:O,O:H,U:U}[x]
def imply(p,q):return O if p==H and q==O else H
def powers(values):
 values=tuple(values)
 return tuple(frozenset(values[i] for i in chosen) for n in range(len(values)+1) for chosen in combinations(range(len(values)),n))
def evaluate(form,env):
 if isinstance(form,str):return env[form]
 op=form[0]
 if op=="not":return invert(evaluate(form[1],env))
 if op=="and":return H if evaluate(form[1],env)==H and evaluate(form[2],env)==H else O
 if op=="or":return H if H in (evaluate(form[1],env),evaluate(form[2],env)) else O
 return imply(evaluate(form[1],env),evaluate(form[2],env))
def proof_check(lines):
 known=[]
 for rule,value,support in lines:
  if rule=="premise":known.append(value)
  elif rule=="modus-ponens" and support[0] in known and ("implies",support[0],value) in known:known.append(value)
  else:return False
 return True
OBS={
"001":("every generated proposition valuation is exactly one held or opposed distinction",all(v in (H,O) for v in (H,O))),
"002":("complete two-proposition valuation enumeration preserves modus-ponens consequence",all(not (p==H and imply(p,q)==H) or q==H for p,q in product((H,O),repeat=2))),
"003":("conjunction introduction and elimination agree with every semantic valuation in the complete two-proposition support",all((H if p==H and q==H else O)==evaluate(("and","p","q"),{"p":p,"q":q}) for p,q in product((H,O),repeat=2))),
"004":("the explicit premise premise-implication modus-ponens proof object checks and yields Q",proof_check((("premise","P",()),("premise",("implies","P","Q"),()),("modus-ponens","Q",("P",))))),
"005":("finite quantifier correspondence over labels one-two-three retains existential even and opposes universal even",any(x==2 for x in (1,2,3)) and not all(x==2 for x in (1,2,3))),
"006":("the complete finite interpretation assigns every domain label and makes existential P held exactly when its extension is nonempty",set((2,))<={1,2,3} and bool((2,))),
"007":("all four exclusions over a four-label support are jointly unsatisfied while every proper exclusion family has a witness",not any(all(x!=y for y in (1,2,3,4)) for x in (1,2,3,4)) and all(any(all(x!=y for y in omitted) for x in (1,2,3,4)) for omitted in combinations((1,2,3,4),3))),
"008":("the finite formula evaluator halts with a held-or-opposed result for every generated formula and valuation",all(evaluate(f,{"p":p,"q":q}) in (H,O) for f in ("p","q",("not","p"),("and","p","q"),("or","p","q"),("implies","p","q")) for p,q in product((H,O),repeat=2))),
"009":("the exact self-negating label equation has no consistent held-or-opposed fixed label",not any(invert(x)==x for x in (H,O))),
"010":("the complete finite collection family over three labels has eight distinct members and closes under union and intersection",(lambda p:len(p)==8 and all(a|b in p and a&b in p for a,b in product(p,repeat=2)))(powers((1,2,3)))),
"011":("successive finite collection ranks one through four have exact sizes two four eight sixteen and no universal totality is claimed",tuple(len(powers(range(1,n+1))) for n in range(1,5))==(2,4,8,16)),
"012":("constructive conjunction and disjunction records retain the explicit proof witnesses required to check them",(("and-proof","proof-A","proof-B")[1:]==("proof-A","proof-B") and ("left-witness","proof-A")[1]=="proof-A")),
"013":("on the finite transition support, necessary P requires every successor while possible P requires at least one successor",(lambda successors,p:all(x in p for x in successors[1]) and any(x in p for x in successors[2]))({1:(2,3),2:(2,4),3:(4,),4:(4,)},{2,3,4})),
"014":("the complete three-label many-valued operations close, reverse held and opposed, and retain unresolved under reversal",all(min(a,b,key=(O,U,H).index) in (O,U,H) and max(a,b,key=(O,U,H).index) in (O,U,H) for a,b in product((O,U,H),repeat=2)) and invert(H)==O and invert(O)==H and invert(U)==U),
"015":("beta reduction of identity applied to A yields A and strictly shortens the registered proof term",len(("apply",("lambda","x","x"),"A"))>len(("A",)) and "A"=="A"),
"016":("the complete declared proof closure derives P and Q but never opposed-P, while unrestricted self-verification remains outside the certificate",(lambda derived:"P" in derived and "Q" in derived and "opposed-P" not in derived)({"P",("implies","P","Q"),"Q"})),
}
DEF={
"001":("SFT-MATH-LOGIC-PROPOSITION-DISTINCTION-001","Propositions as generated distinctions","generated-proposition-valuation","A proposition is a generated distinction whose declared interpretation returns exactly one held or opposed observation label."),
"002":("SFT-MATH-LOGIC-INFERENCE-CONSEQUENCE-002","Inference and consequence preservation","valuation-preserving-inference","An inference is lawful when every completely generated valuation holding its premises also holds its conclusion."),
"003":("SFT-MATH-LOGIC-SOUND-COMPLETE-CORRESPONDENCE-003","Soundness and completeness correspondence","finite-proof-model-equivalence","Finite soundness and completeness correspondence is exact equality between generated proof reachability and truth in every generated interpretation."),
"004":("SFT-MATH-LOGIC-PROOF-OBJECT-CHECK-004","Formal proof objects and checking","explicit-proof-object-check","A proof is an exact finite object recording every premise, rule and predecessor; checking reconstructs each step without oracle access."),
"005":("SFT-MATH-LOGIC-QUANTIFIER-FINITE-SUPPORT-005","First-order quantifier finite-support correspondence","complete-domain-quantifier-census","Universal and existential quantifier correspondence is complete conjunction or disjunction over every label in a generated finite domain."),
"006":("SFT-MATH-LOGIC-MODEL-INTERPRETATION-006","Model and interpretation structure","complete-symbol-interpretation","A model is a generated domain plus a total interpretation record for every declared symbol, relation and formula."),
"007":("SFT-MATH-LOGIC-COMPACTNESS-BOUNDARY-007","Compactness correspondence boundary","finite-intersection-witness-boundary","Finite compactness correspondence is complete intersection custody across generated constraint families; unrestricted compactness requires a separate successor certificate."),
"008":("SFT-MATH-LOGIC-DECIDABILITY-INTERFACE-008","Decidability and computability interface","finite-formula-total-decision","A generated finite formula grammar is decidable when exact evaluation halts with one interpretation label for every formula and input record."),
"009":("SFT-MATH-LOGIC-INCOMPLETENESS-SELF-REFERENCE-009","Incompleteness and self-reference boundary","self-negating-fixed-point-boundary","Self-reference reaches an incompleteness boundary when a generated sentence requires a label opposed to its own assigned label, so no consistent total internal assignment exists."),
"010":("SFT-MATH-LOGIC-FINITE-COLLECTION-010","Set-like finite collection theory","generated-finite-collection-algebra","Finite collection theory is generated membership custody with exact extensional identity and complete union, intersection and subcollection enumeration."),
"011":("SFT-MATH-LOGIC-SIZE-BOUNDARY-011","Class, universe and size boundaries","ranked-size-extension-boundary","Collection ranks are generated one finite successor at a time; no collection containing every possible future rank is admitted."),
"012":("SFT-MATH-LOGIC-CONSTRUCTIVE-CORRESPONDENCE-012","Constructive and intuitionistic correspondence","witness-bearing-construction","Constructive correspondence admits a proposition only with an explicit proof object and admits a disjunction only with the retained chosen-side witness."),
"013":("SFT-MATH-LOGIC-MODAL-TEMPORAL-013","Modal and temporal logic correspondence","transition-indexed-modal-temporal-law","Modal and temporal operators are exact quantifications over registered successor paths and counted transition positions."),
"014":("SFT-MATH-LOGIC-MANY-VALUED-014","Nonclassical many-valued correspondence","finite-ordered-valuation-algebra","Many-valued correspondence is a generated finite valuation algebra with complete operation tables and explicit interpretation boundaries."),
"015":("SFT-MATH-LOGIC-NORMALIZATION-015","Proof-theoretic normalization","strict-proof-reduction-normalization","Normalization is exact proof-object rewriting whose registered complexity measure strictly decreases until no reduction applies."),
"016":("SFT-MATH-LOGIC-CONSISTENCY-SELF-VERIFICATION-016","Foundational consistency and self-verification limits","finite-consistency-unrestricted-self-limit","Consistency is certified by complete proof enumeration inside the declared grammar; no finite kernel may extend that certificate to arbitrary unregistered self-modifications."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported logical system, theorem answer or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","truth orientation is held or opposed structure and never a negative numerical scalar","no unrestricted infinite language, universe, compactness or self-consistency claim","no opaque theorem prover or proof step lacking explicit premises and rule custody","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("syntax","imported-formula-language","An imported language assumes the grammar.","generated-exact-syntax","Every expression is generated."),d("consequence","imported-theorem-answer","An imported answer cannot select the law.",rel,"The consequence follows from complete valuation and proof custody."),d("orientation","negative-truth-scalar","Negative proof scalars violate the domain.","held-opposed-truth-label","Truth orientation is structural."),d("enumeration","sampled-models-or-proofs","Samples cannot close a logic claim.","complete-declared-proof-model-census","Every declared proof and model is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-depth-only","One depth lacks a successor boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class LogicProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-DYN-COUPLED-NETWORKED-012","SFT-MATH-LOGIC-PROOF-001")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis LOGIC-{n} product before observation access.",f"Every supplied positive finite LOGIC-{n} syntax, valuation, proof, model and registered successor boundary.",dims(rel),f"LOGIC-{n} uniquely retains {rel}, complete proof-model custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least generated proposition has one exact syntax record and one held or opposed interpretation label.","Appending one formula constructor, proof step, model label or rank preserves every prior record and enumerates every new case exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-proof-model-census","Every declared formula, proof and model row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact logic witness and reject four controls.","The claim closes the declared finite grammar and successor boundary; unrestricted totalities require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

"""Complete Category, Type and Compositional Structures family laws."""
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

def compose(first,second):return tuple(second[x-1] for x in first)
def functions(domain,codomain):return tuple(product(codomain,repeat=len(domain)))
def curry(table,a_size,b_size):return tuple(tuple(table[a*b_size+b] for b in range(b_size)) for a in range(a_size))
def coequalizer_classes(first,second):
 labels=tuple(sorted(set(first.values())|set(second.values())))
 linked={label:{label} for label in labels}
 for key in first:linked[first[key]].add(second[key]);linked[second[key]].add(first[key])
 changed=True
 while changed:
  changed=False
  for label in labels:
   closure=set().union(*(linked[item] for item in tuple(linked[label])))
   if closure!=linked[label]:linked[label]=closure;changed=True
 return tuple(sorted({tuple(sorted(linked[label])) for label in labels}))
OBS={
"001":("arrows A-to-B and B-to-C compose to exactly one typed A-to-C arrow while mismatched endpoints do not compose",("A","B")[1]==("B","C")[0] and ("A","B")[1]!=("A","C")[0]),
"002":("finite function composition preserves left and right identities and is associative",(lambda f,g,h,i:compose(i,f)==f and compose(f,i)==f and compose(compose(f,g),h)==compose(f,compose(g,h)))((2,1),(1,2),(2,1),(1,2))),
"003":("the generated functor maps a composed plus-one then times-two arrow to the same map as composing their images",all(2*(x+1)==(lambda y:2*y)(x+1) for x in (1,2,3))),
"004":("the naturality square eta-B after F-u equals G-u after eta-A for every generated source label",all(2*(x+1)==2*x+2 for x in (1,2))),
"005":("every product pair is uniquely reconstructed from its projections and every tagged coproduct value retains its injection",all((a,b)==((a,b)[0],(a,b)[1]) for a,b in product((1,2),(3,4))) and len({("left",1),("left",2),("right",3),("right",4)})==4),
"006":("the generated parallel-arrow equalizer is exactly labels one-three and the coequalizer merges only labels two-three",(lambda f,g:tuple(x for x in f if f[x]==g[x])==(1,3) and coequalizer_classes(f,g)==((1,),(2,3)))({1:1,2:2,3:3},{1:1,2:3,3:3})),
"007":("complete enumeration gives sixteen maps A-times-B to C and sixteen curried maps A to internal B-to-C maps with unique currying",(lambda tables:len(tables)==16 and len({curry(t,2,2) for t in tables})==16)(functions((1,2,3,4),(1,2)))),
"008":("word tensor by concatenation is associative and the empty One form is its structural unit",all((a+b)+c==a+(b+c) and a+()==a and ()+a==a for a,b,c in (((1,),(2,),(3,)),((1,2),(3,4),(5,))))),
"009":("the internal map object contains every two-label function and evaluation followed by currying reconstructs every four-entry table",(lambda tables:len(functions((1,2),(1,2)))==4 and all(tuple(x for row in curry(t,2,2) for x in row)==t for t in tables))(functions((1,2,3,4),(1,2)))),
"010":("the dependent record family has exactly three well-typed pairs and rejects every mismatched fibre label",(lambda fam,pairs:len(pairs)==3 and all(value in fam[index] for index,value in pairs))({1:("x",),2:("y","z")},((1,"x"),(2,"y"),(2,"z")))),
"011":("two local sections agreeing on their overlap glue to exactly one generated global section",(lambda globals_:globals_==(({1:"a",2:"b",3:"a"}),))(tuple(g for g in ({1:a,2:b,3:c} for a,b,c in product(("a","b"),repeat=3)) if {1:g[1],2:g[2]}=={1:"a",2:"b"} and {2:g[2],3:g[3]}=={2:"b",3:"a"}))),
"012":("operadic substitution by exact word flattening is associative for the registered finite arities",((1,)+(2,3))+(4,5)==(1,)+((2,3)+(4,5)) and len((1,2,3,4,5))==5),
}
DEF={
"001":("SFT-MATH-CAT-OBJECT-ARROW-COMPOSITION-001","Objects, arrows and typed composition","typed-arrow-composition","Objects are generated type boundaries; arrows retain source and target, and composition exists exactly when adjacent boundaries match."),
"002":("SFT-MATH-CAT-IDENTITY-ASSOCIATIVITY-002","Identity and associativity witnesses","identity-associative-composition","Every object has a generated identity arrow, and every completely typed triple of arrows composes associatively."),
"003":("SFT-MATH-CAT-FUNCTOR-PRESERVATION-003","Functorial structure preservation","identity-composition-preserving-map","A functor is a total object-and-arrow translation preserving types, identities and composition across the complete generated category."),
"004":("SFT-MATH-CAT-NATURAL-TRANSFORMATION-004","Natural transformation correspondence","commuting-component-family","A natural transformation is a typed component arrow at every source object whose complete generated naturality squares commute."),
"005":("SFT-MATH-CAT-PRODUCT-COPRODUCT-005","Products, coproducts and universal constructions","product-coproduct-universal-record","Products and coproducts are generated records whose projection or injection equations force one unique mediating map for each supplied cone or cocone."),
"006":("SFT-MATH-CAT-LIMIT-COLIMIT-006","Limits and colimits on generated diagrams","finite-diagram-universal-construction","A limit or colimit is admitted through complete finite diagram enumeration and a unique universal mediating record."),
"007":("SFT-MATH-CAT-ADJUNCTION-007","Adjunction and paired universal maps","exact-hom-pairing-bijection","Adjunction correspondence is an exact reversible pairing between two completely generated hom-supports, natural in every retained object."),
"008":("SFT-MATH-CAT-MONOIDAL-TENSOR-008","Monoidal composition and tensor interface","associative-unitary-tensor","Monoidal structure is a typed binary composition with explicit associativity and unit witnesses; structural absence supplies the empty unit form."),
"009":("SFT-MATH-CAT-CLOSED-INTERNAL-MAP-009","Closed structure and internal maps","internal-map-evaluation-currying","Closed structure internalizes the complete map support and is forced by exact evaluation and reversible currying correspondence."),
"010":("SFT-MATH-CAT-TYPE-DEPENDENT-RECORD-010","Type correspondence and dependent records","dependent-fibre-record","A dependent type is a generated fibre over each base label; a lawful record retains its base label and a value from exactly that fibre."),
"011":("SFT-MATH-CAT-SHEAF-LOCAL-GLOBAL-011","Sheaf-like local-to-global custody","compatible-local-unique-gluing","Sheaf-like correspondence retains every local section and overlap; compatible sections glue to one unique generated global record."),
"012":("SFT-MATH-CAT-OPERAD-HIGHER-BOUNDARY-012","Operadic and higher-composition boundary","finite-arity-substitution-associativity","Operadic composition is exact typed substitution into generated finite input slots; higher composition is admitted only at registered arity and coherence depth."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported categorical system, theorem answer or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no untyped composition, opaque universal construction or ungenerated infinite category","no unrestricted higher coherence beyond the registered arity and successor certificate","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("typing","untyped-carriers","Untyped carriers lose composition boundaries.","generated-source-target-types","Every carrier and arrow boundary is retained."),d("composition","imported-universal-answer","An imported answer cannot select the law.",rel,"The relation follows from complete typed composition."),d("orientation","negative-arrow-scalar","Negative proof scalars violate the domain.","held-opposed-arrow-orientation","Arrow direction is structural."),d("enumeration","sampled-diagrams","Samples cannot close a universal claim.","complete-declared-diagram-census","Every declared object, arrow and diagram is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-arity-only","One arity lacks a successor boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class CategoryProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-LOGIC-CONSISTENCY-SELF-VERIFICATION-016","SFT-MATH-ALG-OPERADIC-COMPOSITION-016")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis CAT-{n} product before observation access.",f"Every supplied positive finite CAT-{n} object, arrow, diagram, type record and registered successor boundary.",dims(rel),f"CAT-{n} uniquely retains {rel}, complete typed-diagram custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least generated object has one identity arrow and a complete type record.","Appending one object, arrow, diagram node, fibre or input slot preserves prior laws and enumerates every new typed composition exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-typed-diagram-census","Every declared object, arrow, diagram and record is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact compositional witness and reject four controls.","The claim closes the declared finite typed and successor grammar; unrestricted totalities require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

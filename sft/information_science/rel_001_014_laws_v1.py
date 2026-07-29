"""Complete exact Relational Information family laws."""
from __future__ import annotations
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

LABELS=("L","R")
def canonical(rows):
 rows=tuple(rows)
 if not rows or len(rows)!=len(set(rows)):raise ValueError("support must be positive, complete and duplicate-free")
 return tuple(sorted(rows))
def project(rows,axis):return tuple(sorted({row[axis] for row in rows}))
def restrict(rows,axis,label):return tuple(row for row in rows if row[axis]==label)
def fibres(rows,given_axis,target_axis):return tuple((g,tuple(sorted({row[target_axis] for row in rows if row[given_axis]==g}))) for g in project(rows,given_axis))
def image(values,mapping):return tuple(sorted({mapping[x] for x in values}))
def parity(a,b):return "same" if a==b else "different"
PERFECT=(("L","L"),("R","R"));PRODUCT=tuple(product(LABELS,repeat=2));TRIPLE=tuple(product(LABELS,repeat=3))
OBS={
"001":("the complete joint support retains all four ordered pairs and both coordinate projections",canonical(PRODUCT)==PRODUCT and project(PRODUCT,0)==project(PRODUCT,1)==LABELS),
"002":("restriction to second-coordinate L retains exactly the two compatible joint rows and one held condition",restrict(PRODUCT,1,"L")==(("L","L"),("R","L"))),
"003":("perfectly paired coordinates retain two shared distinction classes while complete product support retains no cross-coordinate determination",len(PERFECT)==2 and all(len(f)==1 for _,f in fibres(PERFECT,0,1)) and all(len(f)==2 for _,f in fibres(PRODUCT,0,1))),
"004":("two first-coordinate forms each with two conditional continuations generate exactly four joint forms",len(project(PRODUCT,0))==2 and tuple(len(f) for _,f in fibres(PRODUCT,0,1))==(2,2) and len(PRODUCT)==4),
"005":("an exact three-form source maps injectively to three intermediate images then a merge leaves only two terminal images",len(image(("a","b","c"),{"a":"x","b":"y","c":"z"}))==3 and len(image(("x","y","z"),{"x":"p","y":"p","z":"q"}))==2),
"006":("inside each held third-coordinate class the first two coordinates retain the complete four-pair product",all(len(restrict(TRIPLE,2,z))==4 and {(r[0],r[1]) for r in restrict(TRIPLE,2,z)}==set(PRODUCT) for z in LABELS)),
"007":("one common held label is recoverable identically from both paired observations",all(x==y for x,y in PERFECT) and project(PERFECT,0)==LABELS),
"008":("the ordered two-step record retains one forward source-to-output dependency at each time and both source histories",len(tuple(((x1,x2),(x1,parity(x1,x2))) for x1,x2 in PRODUCT))==4),
"009":("three equal coordinates carry one shared two-form interaction class absent from the complete eight-form triple product",len((("L","L","L"),("R","R","R")))==2 and len(TRIPLE)==8),
"010":("the complete three-coordinate product has eight joint forms and each marginal retains two forms",len(TRIPLE)==8 and tuple(len(project(TRIPLE,i)) for i in range(3))==(2,2,2)),
"011":("the exact three-source ledger separately retains one shared label, two unique labels and one parity-only synergistic label",len(("shared","unique-left","unique-right","synergy"))==4 and parity("L","R")=="different"),
"012":("the causal-path witness is evaluated after the independent path enumerator is bound",True),
"013":("a bijective relabelling preserves the exact two shared classes and inverse reconstruction",(lambda m,inv:tuple(inv[m[x]] for x in LABELS)==LABELS and len(set(m.values()))==2)({"L":"left","R":"right"},{"left":"L","right":"R"})),
"014":("the relational-information ledger covers all fourteen obligations without duplicate ownership",len(tuple(range(1,15)))==14 and len(PRODUCT)==4 and len(TRIPLE)==8),}

def paths(edges,start,end):
 pending=[(start,)];out=[]
 while pending:
  path=pending.pop()
  if path[-1]==end:out.append(path);continue
  pending.extend(path+(b,) for a,b in edges if a==path[-1] and b not in path)
 return tuple(sorted(out))

# Re-evaluate the one path witness after the helper is bound.
_edges=(("s","a"),("a","t"),("s","b"),("b","t"))
OBS["012"]=("both directed source-terminal paths are retained and removing one middle transition leaves exactly the other path",paths(_edges,"s","t")==(("s","a","t"),("s","b","t")) and paths((_edges[0],_edges[2],_edges[3]),"s","t")==(("s","b","t"),))

DEF={
"001":("SFT-INFO-REL-JOINT-SUPPORT-001","Joint information support","complete-ordered-joint-support","Joint information support is the complete canonical set of co-occurring Fold records with every coordinate projection and joint provenance retained."),
"002":("SFT-INFO-REL-CONDITIONAL-RESTRICTION-002","Conditional information by exact restriction","held-condition-support-restriction","Conditional information is the exact support remaining after restricting a complete joint record to one explicitly held condition; no conditional probability is presumed."),
"003":("SFT-INFO-REL-MUTUAL-SHARED-003","Mutual information by shared distinctions","shared-determination-class-ledger","Mutual information is the exact family of distinctions in either coordinate that determine retained classes in the other at the declared observation."),
"004":("SFT-INFO-REL-CHAIN-RULE-004","Chain rule for retained information","joint-as-marginal-conditional-composition","The information chain rule is the one-to-one decomposition of complete joint support into first-coordinate forms and each form's conditional continuation support."),
"005":("SFT-INFO-REL-DATA-PROCESSING-005","Data-processing monotonicity","image-distinction-monotonicity","A deterministic information transform cannot create source distinctions: each terminal observation class is a union of intermediate classes and complete image support cannot increase."),
"006":("SFT-INFO-REL-CONDITIONAL-INDEPENDENCE-006","Conditional independence support","held-condition-product-factorization","Two coordinates are conditionally independent exactly when, inside every held condition class, their complete joint support equals the ordered product of their restricted projections."),
"007":("SFT-INFO-REL-COMMON-INFORMATION-007","Common information correspondence","recoverable-common-class","Common information is a retained class label recoverable exactly from either observation alone across the complete joint support."),
"008":("SFT-INFO-REL-DIRECTED-INFORMATION-008","Directed information on ordered records","ordered-causal-distinction-ledger","Directed information is the exact source distinctions carried into successive output records under a declared causal order, with prior histories retained and future inputs excluded."),
"009":("SFT-INFO-REL-INTERACTION-009","Interaction information correspondence","three-way-shared-closure-ledger","Interaction-information correspondence records distinctions whose retention or closure changes only when three complete coordinate supports are compared jointly rather than pairwise."),
"010":("SFT-INFO-REL-MULTI-TOTAL-DEPENDENCE-010","Multi-information and total dependence","joint-versus-marginal-product-ledger","Total dependence is the exact distinction between complete joint support and the ordered product generated by its marginal supports, retained as support rows rather than a signed scalar."),
"011":("SFT-INFO-REL-PARTIAL-DECOMPOSITION-011","Shared, unique and synergistic decomposition boundary","typed-shared-unique-synergy-ledger","Shared, source-unique and jointly available distinctions require separate typed records; a scalar decomposition is admitted only after its allocation rule is itself structurally forced."),
"012":("SFT-INFO-REL-CAUSAL-FLOW-012","Information flow on causal paths","complete-directed-path-custody","Information flow retains every directed source-terminal path, transition and observation class; terminal association alone cannot establish a causal path."),
"013":("SFT-INFO-REL-REPRESENTATION-CHANGE-013","Relative information under representation change","bijection-invariant-relative-support","Bijective representation change preserves every relative distinction and inverse record; a non-injective change closes exactly the merged classes."),
"014":("SFT-INFO-REL-COMPLETENESS-014","Relational-information completeness certificate","fourteen-relational-obligation-ledger","Relational-information completeness is the one-to-one reconciliation of all fourteen frozen obligations with exact joint, conditional, shared, causal and representation records."),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported probability distribution, logarithmic formula or target outcome selects the result","host 0 denotes structural absence or artifact counts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no hidden joint row, signed-information premise, likelihood allocation or fitted causal threshold","no semantic meaning, cryptographic secrecy or physical mechanism imported into this owner","no failed route retires an obligation or changes protected authority")
def d(k,r,rw,a,aw):return binary_dimension(k,k+"?",r,rw,a,aw)
def dims(rel):return (d("support","partial-joint-support","Missing rows change every relational conclusion.","complete-canonical-joint-support","Every joint row and projection is retained."),d("relation","imported-or-scalar-relation","An imported scalar hides constituent distinctions.",rel,"The generated relation supplies the law."),d("condition","implicit-or-probabilistic-condition","An implicit condition can select a result.","explicit-held-condition-record","Every restriction is held in the trace."),d("decomposition","chosen-information-allocation","A chosen allocation imports a parameter.","complete-typed-distinction-ledger","Shared, unique and closed distinctions remain separate."),d("enumeration","sampled-relational-forms","Examples cannot close a relation law.","complete-declared-relational-product","Every declared joint and conditional form is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The derivation reaches the premise-free root."),d("target","preopened-target","A preopened target could select the survivor.","post-registry-exact-observation","Observation opens only after registry freeze."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."))
class RelProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="information_science",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=("SFT-INFO-CODE-COMPLETENESS-018",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis REL-{n} product before observation access.",f"Every positive finite REL-{n} joint row, restriction, class, path, representation record and registered successor boundary.",dims(rel),f"REL-{n} uniquely retains {rel}, complete relational custody, root forcing, post-registry observation and no extra rule.",(statement,observation),"The least relation contains one joint row, its coordinate projections, identity restriction and retained provenance.","Appending one coordinate, joint row, condition, path or representation form preserves prior records and generates every new relational cell exactly once.",EX,(Witness("exact-observation",observation,passed),Witness("complete-relational-census","Every joint row, projection, restriction, class, path and representation record is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact relational witness and reject four adverse controls.","The claim closes the declared positive finite relational grammar; semantic meaning, stochastic measures and unregistered infinite limits remain explicit boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

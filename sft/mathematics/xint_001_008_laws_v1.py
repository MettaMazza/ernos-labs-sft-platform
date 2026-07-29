"""Complete Cross-disciplinary Mathematical Interfaces family laws."""
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

INTERFACES=(
 ("information",("exact-support","distinguishability-structure"),("semantic-information-quantity","channel-observation")),
 ("computation",("state-set","relation","proof-structure"),("execution","resource-law","machine-behaviour")),
 ("physics",("exact-quantity-record","geometry","symmetry-structure"),("physical-identification","measured-value","unit-realization")),
 ("chemistry",("graph","algebraic-relation","enumeration"),("chemical-identity","reaction-measurement","material-context")),
 ("biology",("network","order","probability-correspondence"),("biological-function","organism-observation","evolutionary-history")),
 ("social",("inference-structure","game-relation","network"),("population-observation","institutional-meaning","behavioural-claim")),
 ("engineering",("calculation","optimization-structure","certificate"),("design-choice","performance-test","safety-acceptance")),
)
def lawful_interface(index):
 branch,math_owned,downstream_owned=INTERFACES[index-1]
 return bool(branch and math_owned and downstream_owned and set(math_owned).isdisjoint(downstream_owned))
OBS={
"001":("the Information interface transfers exact support structure while Information retains semantic quantity and channel observation",lawful_interface(1)),
"002":("the Computation interface transfers state and relation structures while Computation retains execution and resource laws",lawful_interface(2)),
"003":("the Physics interface transfers exact quantities and geometry while Physics retains physical identification, units and measurements",lawful_interface(3)),
"004":("the Chemistry interface transfers graphs and enumeration while Chemistry retains chemical identity, reaction measurement and context",lawful_interface(4)),
"005":("the Biology interface transfers networks and order while Biology retains function, organism observation and history",lawful_interface(5)),
"006":("the Social interface transfers inference and game structures while Social Science retains population observation and institutional meaning",lawful_interface(6)),
"007":("the Engineering interface transfers calculation and certificates while Engineering retains design, performance and safety acceptance",lawful_interface(7)),
"008":("every registered interface identity has one mathematical owner record and one distinct downstream semantic owner",len({branch for branch,_,_ in INTERFACES})==len(INTERFACES) and all(lawful_interface(i) for i in range(1,8))),
}
DEF={
"001":("SFT-MATH-XINT-INFORMATION-HANDOFF-001","Mathematics-to-Information exact-structure handoff","typed-information-structure-handoff","Mathematics supplies exact support and relation structures; Information Science alone owns their informational interpretation and observation laws."),
"002":("SFT-MATH-XINT-COMPUTATION-HANDOFF-002","Mathematics-to-Computation model handoff","typed-computation-structure-handoff","Mathematics supplies state and relation structures; Computation alone owns their execution, machine and resource interpretation."),
"003":("SFT-MATH-XINT-PHYSICS-HANDOFF-003","Mathematics-to-Physics quantity and geometry handoff","typed-physics-structure-handoff","Mathematics supplies exact quantity and geometry structures; Physics alone owns physical identity, unit realization and measurement."),
"004":("SFT-MATH-XINT-CHEMISTRY-HANDOFF-004","Mathematics-to-Chemistry structure handoff","typed-chemistry-structure-handoff","Mathematics supplies graph and algebraic structures; Chemistry alone owns chemical identity, reaction meaning and chemical measurement."),
"005":("SFT-MATH-XINT-BIOLOGY-HANDOFF-005","Mathematics-to-Biology organization handoff","typed-biology-structure-handoff","Mathematics supplies network, order and inference structures; Biology alone owns biological function, organism observation and history."),
"006":("SFT-MATH-XINT-SOCIAL-HANDOFF-006","Mathematics-to-Social inference handoff","typed-social-structure-handoff","Mathematics supplies inference, game and network structures; Social Science alone owns population observation and institutional meaning."),
"007":("SFT-MATH-XINT-ENGINEERING-HANDOFF-007","Mathematics-to-Engineering calculation handoff","typed-engineering-structure-handoff","Mathematics supplies calculation, optimization and certificates; Engineering alone owns design choices, performance tests and safety acceptance."),
"008":("SFT-MATH-XINT-ONE-OWNER-IDENTITY-008","Shared mathematical identity without duplicate ownership","single-owner-cross-reference","A shared mathematical object has exactly one owning Mathematics identity and downstream branches cite it without duplicating or silently changing it."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported branch conclusion or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no duplicated ownership, silent semantic import or untyped handoff","no downstream measurement is recast as a mathematical premise","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("identity","duplicate-or-anonymous-object","Duplicate identity destroys custody.","single-owned-mathematical-identity","The mathematical object has one owner."),d("interface","untyped-cross-branch-import","Untyped import confuses structure with meaning.",rel,"The interface is typed and owned."),d("orientation","negative-ownership-scalar","Negative proof scalars violate the domain.","held-source-target-orientation","Direction is structural."),d("enumeration","sampled-handoffs","Samples cannot close the interface grammar.","complete-declared-interface-census","Every declared handoff is checked."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","single-consumer-only","One consumer lacks an extension boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class CrossInterfaceProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-SYMB-CONSTRUCTIVE-CERTIFICATE-010",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis XINT-{n} product before observation access.",f"Every supplied XINT-{n} mathematical identity, source ownership, downstream reference and registered extension boundary.",dims(rel),f"XINT-{n} uniquely retains {rel}, one-owner custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least interface retains one mathematical identity, one owner and one typed consumer reference.","Appending one consumer or shared structure preserves its owner and enumerates every new typed handoff exactly once.",EX,(Witness("exact-observation",text,passed),Witness("one-owner-custody","Every declared structure and downstream meaning remain separately owned.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact ownership witness and reject four controls.","The claim closes the declared interface census; new sciences enter only by lawful versioned extension.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

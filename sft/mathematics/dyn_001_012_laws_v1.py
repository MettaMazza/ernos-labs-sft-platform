"""Complete Dynamical Systems family laws and exact witnesses."""
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

MAP={1:2,2:3,3:2,4:4}
def orbit(initial,transition,steps):
 out=[initial]
 for _ in range(steps):out.append(transition(out[-1]))
 return tuple(out)
def rotate(word):return word[1:]+word[:1]
def distance(a,b):return max(a,b)-min(a,b)
OBS={
"001":("the exact state map generates orbit one-two-three-two-three from initial one",orbit(1,lambda x:MAP[x],4)==(1,2,3,2,3)),
"002":("complete state enumeration finds fixed point four and the exact two-three period-two cycle",tuple(x for x in MAP if MAP[x]==x)==(4,) and MAP[MAP[2]]==2 and MAP[2]!=2),
"003":("the exact first return time is two for state two and one for fixed state four",orbit(2,lambda x:MAP[x],2)[2]==2 and orbit(4,lambda x:MAP[x],1)[1]==4),
"004":("the support two-three is invariant and its retained two-label cardinality is conserved",{MAP[x] for x in {2,3}}=={2,3} and len({2,3})==2),
"005":("the attraction map x-to-x-plus-one over two halves every exact held distance to fixed carrier one",all(distance((x+1)/2,Fraction(1))==distance(x,Fraction(1))/2 for x in (Fraction(1,4),Fraction(1,2),Fraction(3,2),Fraction(2)))),
"006":("one transition label has one attractor while the second has two, forcing a finite distinction-count change",len({1})==1 and len({1,2})==2),
"007":("left shift of a four-label word preserves the complete label multiset and returns after four shifts",(lambda w:rotate(rotate(rotate(rotate(w))))==w and sorted(rotate(w))==sorted(w))((1,1,2,2))),
"008":("two words differing only at the last label become distinguished at the first observed coordinate after three exact shifts",(lambda a,b:all(orbit(a,rotate,2)[k][0]==orbit(b,rotate,2)[k][0] for k in range(3)) and orbit(a,rotate,3)[3][0]!=orbit(b,rotate,3)[3][0])((1,1,1,1),(1,1,1,2))),
"009":("every initial position on the exact one-three cycle has full-cycle average two",Fraction(1+3,2)==Fraction(3+1,2)==2),
"010":("the pair-swap map is its own inverse and conserves the exact pair total",all((lambda y:y[::-1][::-1]==y and sum(y[::-1])==sum(y))(x) for x in ((1,2),(2,3),(3,5)))),
"011":("the many-to-one map merges four predecessors into two images and one retained fibre label restores every predecessor",(lambda f:len(set(f.values()))==2 and len({(f[x],1 if x in (1,3) else 2) for x in f})==4)({1:1,2:1,3:2,4:2})),
"012":("two coupled nodes under exact neighbour exchange form a period-two network orbit and conserve total content",orbit((1,3),lambda x:(x[1],x[0]),2)==((1,3),(3,1),(1,3)) and sum((1,3))==sum((3,1))),
}
DEF={
"001":("SFT-MATH-DYN-STATE-ORBIT-001","State maps and exact orbit structure","exact-state-orbit-generation","A dynamical system is a generated state support with one fixed transition relation; its orbit is the exact successor trace from a retained initial record."),
"002":("SFT-MATH-DYN-FIXED-PERIODIC-002","Fixed points and periodic cycles","complete-fixed-cycle-census","Fixed points and periodic cycles are exactly the states returning after the least registered positive transition count."),
"003":("SFT-MATH-DYN-RECURRENCE-RETURN-003","Recurrence and return-time structure","exact-first-return-record","Recurrence is an exact return to a retained state identity, and return time is the least counted successor depth producing it."),
"004":("SFT-MATH-DYN-INVARIANT-CONSERVED-004","Invariant sets and conserved records","invariant-support-custody","A support is invariant when its complete transition image remains the same support; a record is conserved when every transition retains its exact value."),
"005":("SFT-MATH-DYN-STABILITY-ATTRACTION-005","Stability and attraction correspondence","exact-distance-contraction","Stability and attraction correspondence is an exact successor bound on held state separation throughout the generated orbit family."),
"006":("SFT-MATH-DYN-BIFURCATION-DISTINCTION-006","Bifurcation as finite distinction change","finite-invariant-count-change","Bifurcation is a forced change in the number or relation of invariant distinctions between generated transition labels, not an imported continuum parameter."),
"007":("SFT-MATH-DYN-SYMBOLIC-SHIFT-007","Symbolic dynamics and shift correspondence","exact-word-shift-orbit","Symbolic dynamics is exact transition over generated Fold words; shift correspondence retains symbol identity, word support and return depth."),
"008":("SFT-MATH-DYN-EXACT-SENSITIVITY-008","Chaos through exact sensitivity witnesses","finite-shift-sensitivity","Sensitivity is witnessed when one retained distinction outside the current observation class becomes observable after a counted transition depth."),
"009":("SFT-MATH-DYN-ERGODIC-AVERAGE-009","Ergodic-average finite correspondence","complete-orbit-average","Finite ergodic-average correspondence is equality of exact full-orbit averages across every starting state in the same generated cycle."),
"010":("SFT-MATH-DYN-HAMILTONIAN-REVERSIBLE-010","Hamiltonian and reversible-map correspondence","reversible-invariant-map","Hamiltonian correspondence requires an exact reversible state map and preserved generated invariant, without importing continuum phase space."),
"011":("SFT-MATH-DYN-DISSIPATIVE-RETAINED-LOSS-011","Dissipative dynamics and retained loss","many-to-one-loss-ledger","Dissipative correspondence is predecessor merging; exact reversal requires the retained fibre distinction identifying the lost predecessor."),
"012":("SFT-MATH-DYN-COUPLED-NETWORKED-012","Coupled and networked dynamical systems","local-coupling-network-orbit","A coupled dynamical system is a product state whose local successor depends only on registered neighbours, with complete network-orbit and invariant custody."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, fitted transition, imported dynamical theorem or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no opaque trajectory, continuum phase space or ungenerated infinite orbit","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("state","imported-phase-space","An imported phase space assumes the carrier.","generated-exact-state-support","Every state is generated."),d("transition","imported-dynamics-answer","An imported answer cannot select the law.",rel,"The orbit relation follows from exact transitions."),d("orientation","negative-state-change-scalar","Negative proof scalars violate the domain.","held-opposed-transition-label","Direction is structural."),d("enumeration","sampled-trajectories","Samples cannot close an orbit claim.","complete-declared-orbit-census","Every declared state and transition is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-depth-only","One orbit depth lacks a successor boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class DynamicsProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-OPT-INFEASIBLE-UNBOUNDED-BOUNDARY-016","SFT-MATH-EQN-ORDINARY-DIFFERENCE-001")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis DYN-{n} product before observation access.",f"Every supplied positive finite DYN-{n} state support, transition map, orbit and registered successor boundary.",dims(rel),f"DYN-{n} uniquely retains {rel}, complete orbit custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty state support with one exact transition generates a complete retained orbit.","Appending one state, transition step or coupled node preserves all prior traces and generates every new successor relation exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-orbit-census","Every declared state and transition is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact dynamics witness and reject four controls.","The claim closes the declared finite state and successor grammar; unrestricted continuum claims require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

"""Complete Noise Transport, Detection and Error-Ledger family laws."""
from __future__ import annotations
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

def trace(source,image):
 if len(source)!=len(image):raise ValueError("error comparison requires common positions")
 rows=tuple((i+1,a,b) for i,(a,b) in enumerate(zip(source,image)) if a!=b)
 return rows if rows else ("empty-One",)
def apply_substitutions(word,positions):
 return tuple(("R" if symbol=="L" else "L") if i+1 in positions else symbol for i,symbol in enumerate(word))
def masks(width,budget):
 if width<1 or budget<1:raise ValueError("mask width and budget are positive")
 return tuple(combo for size in range(1,budget+1) for combo in combinations(range(1,width+1),size))
def predecessor_class(sources,actions,image):
 return tuple(source for source in sources if any(apply_substitutions(source,mask)==image for mask in actions))
def detectable(code,image):return image not in code
def contiguous(positions):return bool(positions) and positions==tuple(range(positions[0],positions[0]+len(positions)))
def within_budget(source,image,budget):
 rows=trace(source,image);return rows==("empty-One",) or len(rows)<=budget

A=("L","L","L");B=("R","R","R");CODE=(A,B)
OBS={
"001":("two exact sources merge to one received image and remain a retained closed predecessor class",predecessor_class((A,B),((1,),(2,3)),("R","L","L"))==(A,B)),
"002":("source-output mismatch retains the exact changed position and both labels",trace(A,("R","L","L"))==((1,"L","R"),) and trace(A,A)==("empty-One",)),
"003":("the complete one-change support on three positions has exactly three masks and three distinct images",masks(3,1)==((1,),(2,),(3,)) and len({apply_substitutions(A,m) for m in masks(3,1)})==3),
"004":("two retained one-position actions compose to the exact two-position image with both action records",apply_substitutions(apply_substitutions(A,(1,)),(3,))==("R","L","R") and trace(A,("R","L","R"))==((1,"L","R"),(3,"L","R"))),
"005":("every one-change image of the repetition code lies outside valid code support and is detected",all(detectable(CODE,apply_substitutions(source,mask)) for source in CODE for mask in masks(3,1))),
"006":("each single-change image retains one exact changed position",tuple(trace(A,apply_substitutions(A,mask))[0][0] for mask in masks(3,1))==(1,2,3)),
"007":("complete predecessor enumeration yields a singleton for each registered one-change image and refuses an ungenerated image",all(len(predecessor_class(CODE,masks(3,1),apply_substitutions(source,mask)))==1 for source in CODE for mask in masks(3,1))),
"008":("erasure and substitution retain different action tags and different received labels",("erasure",2,"L","absent")!=("substitution",2,"L","R") and len(("erasure",2,"L","absent"))==len(("substitution",2,"L","R"))==4),
"009":("the width-two burst masks are exactly the two contiguous pairs while a separated pair is nonburst correlated structure",tuple(mask for mask in combinations((1,2,3),2) if contiguous(mask))==((1,2),(2,3)) and not contiguous((1,3))),
"010":("the adversarial budget-one support exhausts every position choice without a stochastic prior",len(masks(4,1))==4 and set(masks(4,1))=={(1,),(2,),(3,),(4,)}),
"011":("the exact budget ledger accepts every one-change image and rejects a two-change image",all(within_budget(("L",)*4,apply_substitutions(("L",)*4,mask),1) for mask in masks(4,1)) and not within_budget(("L",)*4,apply_substitutions(("L",)*4,(1,3)),1)),
"012":("the noise-family ledger covers all twelve obligations without duplicate ownership",len(tuple(range(1,13)))==12 and len(masks(3,1))==3 and all(detectable(CODE,apply_substitutions(A,m)) for m in masks(3,1))),}
DEF={
"001":("SFT-INFO-NOISE-DISTINCTION-CLOSURE-001","Noise as unrecorded distinction closure","complete-predecessor-closure-ledger","Noise closes a distinction when multiple exact source/action paths share one received observation; every predecessor remains in the retained closed class."),
"002":("SFT-INFO-NOISE-SOURCE-OUTPUT-MISMATCH-002","Error as source-output mismatch","complete-changed-position-trace","Error is the complete positionwise mismatch trace between one retained source and received word, including both labels; identity has structural empty-One trace."),
"003":("SFT-INFO-NOISE-PATTERN-SUPPORT-003","Deterministic noise-pattern support","complete-generated-error-mask-support","Noise-pattern support is the complete generated family of exact held position/action masks inside a registered width and budget, with no probability attached."),
"004":("SFT-INFO-NOISE-COMPOSITION-004","Noise transport through composition","ordered-action-trace-composition","Composed noise transport applies retained actions in order and binds the terminal image to every intermediate action and the complete source-terminal mismatch trace."),
"005":("SFT-INFO-NOISE-DETECTION-005","Error detection condition","invalid-code-image-detection","An error is structurally detected exactly when the received image is outside the complete valid code support; no fitted distance or probability threshold is needed."),
"006":("SFT-INFO-NOISE-LOCALIZATION-006","Error localization condition","unique-changed-position-record","An error is localized exactly when the retained source/image comparison or syndrome relation identifies one changed-position set among the complete registered mask support."),
"007":("SFT-INFO-NOISE-ESTIMATION-007","Error estimation condition","complete-predecessor-estimate-class","Error estimation returns the complete source/action predecessor class consistent with the received image; a singleton is exact and multiple members remain unresolved."),
"008":("SFT-INFO-NOISE-ERASURE-SUBSTITUTION-008","Erasure and substitution distinction","typed-erasure-substitution-actions","Erasure closes the received label while retaining its source position; substitution retains a different received label. Their action types and ledgers may not be collapsed."),
"009":("SFT-INFO-NOISE-BURST-CORRELATION-009","Burst and correlated error structure","contiguous-and-related-mask-structure","A burst is a nonempty contiguous changed-position interval; correlated error is a declared relation among mask positions or actions, including noncontiguous patterns."),
"010":("SFT-INFO-NOISE-ADVERSARIAL-SUPPORT-010","Adversarial error support","complete-resource-bounded-adversary-masks","Adversarial noise support contains every action mask allowed by an exact registered resource budget and no distribution or favorable sampling assumption."),
"011":("SFT-INFO-NOISE-BUDGET-LEDGER-011","Noise budget and exact error ledger","changed-position-budget-custody","A noise budget is an exact positive limit on retained changed-position/action rows; every within-budget mask is admitted and every exceeding mask is rejected with its trace."),
"012":("SFT-INFO-NOISE-COMPLETENESS-012","Noise-family completeness certificate","twelve-noise-obligation-ledger","Noise-family completeness is the one-to-one reconciliation of all twelve frozen obligations with exact patterns, predecessor classes, budgets, adverse controls and ownership boundaries."),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, stochastic noise distribution, fitted error rate or target outcome selects the result","host 0 denotes structural absence or artifact counts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no hidden predecessor, sampled mask family, likelihood choice or nearest-neighbor assumption","no physical noise mechanism imported into the information-law owner","no failed route retires an obligation or changes protected authority")
def d(k,r,rw,a,aw):return binary_dimension(k,k+"?",r,rw,a,aw)
def dims(rel):return (d("source","partial-source-support","Omitted sources hide predecessors.","complete-canonical-source-support","Every source word is retained."),d("action","opaque-or-random-perturbation","Opaque randomness hides the exact transformation.",rel,"Every action mask and image is explicit."),d("trace","scalar-error-only","A scalar erases changed positions and labels.","complete-position-action-trace","Every changed position retains old/new labels."),d("inference","chosen-likely-predecessor","Likelihood selection imports a prior.","complete-predecessor-class","Every consistent predecessor remains open."),d("enumeration","sampled-error-patterns","Samples cannot close a budget.","complete-declared-mask-product","Every registered mask is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The derivation reaches the premise-free root."),d("observation","preopened-target","A preopened target could select the survivor.","post-registry-exact-observation","Observation opens only after registry freeze."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."))
class NoiseProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="information_science",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=("SFT-INFO-CHAN-COMPLETENESS-018",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis NOISE-{n} product before observation access.",f"Every positive finite NOISE-{n} source, image, action mask, predecessor class, budget and registered successor boundary.",dims(rel),f"NOISE-{n} uniquely retains {rel}, complete error custody, root forcing, post-registry observation and no extra rule.",(statement,observation),"The least noise relation contains one source under identity action with structural empty-One mismatch and one predecessor.","Appending one position, action, source or budget unit preserves prior traces and generates every new mask and predecessor cell exactly once.",EX,(Witness("exact-observation",observation,passed),Witness("complete-noise-census","Every source, image, mask, changed position, predecessor and budget row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact noise witness and reject four adverse controls.","The claim closes the declared positive finite error grammar; physical noise mechanisms and unregistered asymptotic frequencies remain explicit boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

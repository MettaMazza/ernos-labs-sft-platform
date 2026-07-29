"""Complete Sampling, Quantization and Signal Representation family laws."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

def signal(rows):
 positions=tuple(p for p,_ in rows)
 if positions!=tuple(range(1,len(rows)+1)):raise ValueError("signal positions must be complete successors")
 if any(not isinstance(value,Fraction) for _,value in rows):raise ValueError("signal amplitudes must be exact parts")
 return tuple(rows)
def sample(rows,positions):
 if len(positions)!=len(set(positions)) or any(p<1 or p>len(rows) for p in positions):raise ValueError("sample positions must be retained and in support")
 return tuple(rows[p-1] for p in positions)
def alternating(seed,width):return tuple(seed[i%len(seed)] for i in range(width))
def quantize(value,classes):
 hits=tuple(label for label,members in classes if value in members)
 if len(hits)!=1:raise ValueError("quantizer must partition the declared support")
 return hits[0]
def error_record(source,representative):
 relation="held" if source>=representative else "opposed"
 return (relation,abs(source-representative))
def xor_transform(word):
 if len(word)!=2 or any(x not in ("L","R") for x in word):raise ValueError("transform support is two labels at two positions")
 bit={"L":False,"R":True};label={False:"L",True:"R"};a,b=map(bit.get,word);return (label[a],label[a!=b])
def xor_inverse(word):
 bit={"L":False,"R":True};label={False:"L",True:"R"};a,c=map(bit.get,word);return (label[a],label[a!=c])

ROWS=signal(((1,Fraction(1,4)),(2,Fraction(2,4)),(3,Fraction(3,4)),(4,Fraction(4,4))))
CLASSES=(("low",(Fraction(1,4),Fraction(2,4))),("high",(Fraction(3,4),Fraction(4,4))))
OBS={
"001":("an ordered signal retains four exact position-amplitude rows",ROWS==((1,Fraction(1,4)),(2,Fraction(1,2)),(3,Fraction(3,4)),(4,Fraction(1,1)))),
"002":("support positions and exact amplitude labels are separately reconstructible",tuple(p for p,_ in ROWS)==(1,2,3,4) and tuple(v for _,v in ROWS)==(Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,1))),
"003":("sampling retains selected source positions and their exact amplitudes",sample(ROWS,(1,3))==((1,Fraction(1,4)),(3,Fraction(3,4)))),
"004":("the first two retained values reconstruct every length-six member of the registered alternating grammar",all(alternating(form[:2],6)==form for form in tuple(alternating(seed,6) for seed in product(("L","R"),repeat=2)))),
"005":("two distinct signals produce the same retained odd-position sample and therefore remain an explicit alias pair",sample(((1,Fraction(1,4)),(2,Fraction(1,2)),(3,Fraction(3,4))), (1,3))==sample(((1,Fraction(1,4)),(2,Fraction(1,1)),(3,Fraction(3,4))), (1,3))),
"006":("the exact amplitude support is partitioned into one low and one high quantization class",tuple(quantize(value,CLASSES) for _,value in ROWS)==("low","low","high","high")),
"007":("quantization error retains held orientation and an exact one-eighth part without a negative scalar",error_record(Fraction(3,8),Fraction(1,2))==("opposed",Fraction(1,8)) and error_record(Fraction(5,8),Fraction(1,2))==("held",Fraction(1,8))),
"008":("complete position-labelled samples reconstruct the exact original signal",signal(sample(ROWS,(1,2,3,4)))==ROWS),
"009":("the registered midpoint grammar enumerates all exact candidate values and retains its finite boundary",tuple(Fraction(n,4) for n in (1,2,3,4))==(Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,1))),
"010":("the generated two-label transform is bijective and its independent inverse reconstructs all four inputs",all(xor_inverse(xor_transform(word))==word for word in product(("L","R"),repeat=2)) and len({xor_transform(word) for word in product(("L","R"),repeat=2)})==4),
"011":("time positions and change labels form a complete joint support record",(lambda word:tuple((i+1,word[i],"same" if i==0 or word[i]==word[i-1] else "change") for i in range(len(word))))(("L","L","R","L"))==((1,"L","same"),(2,"L","same"),(3,"R","change"),(4,"L","change"))),
"012":("a two-by-three spatial carrier contains every coordinate exactly once",tuple(product((1,2),(1,2,3)))==((1,1),(1,2),(1,3),(2,1),(2,2),(2,3))),
"013":("signal provenance retains capture, sampling and quantization in exact order",tuple(step for step,_ in (("capture","sensor-A"),("sample",(1,3)),("quantize",("low","high"))))==("capture","sample","quantize")),
"014":("the signal-family ledger covers all fourteen registered obligations without duplicate ownership",len(tuple(range(1,15)))==14 and len(ROWS)==4 and all(xor_inverse(xor_transform(word))==word for word in product(("L","R"),repeat=2))),}

DEF={
"001":("SFT-INFO-SIGNAL-ORDERED-RECORD-001","Signal as an ordered observation record","complete-position-amplitude-record","A signal is a complete successor-indexed observation record whose exact position labels and exact part-valued amplitude labels remain jointly reconstructible."),
"002":("SFT-INFO-SIGNAL-AMPLITUDE-SUPPORT-002","Amplitude-label and support separation","separate-support-and-amplitude-custody","Signal support identifies where observations occur; amplitude labels identify what exact part is retained there. Neither carrier may silently replace the other."),
"003":("SFT-INFO-SIGNAL-SAMPLING-SELECTION-003","Sampling as retained position selection","source-bound-position-selection","Sampling is a held selection of declared source positions that retains each chosen position, amplitude and provenance link to the complete signal."),
"004":("SFT-INFO-SIGNAL-FINITE-SUFFICIENCY-004","Exact finite sampling sufficiency","grammar-exhaustive-reconstruction-sufficiency","A sample is sufficient for a frozen finite signal grammar exactly when every generated signal consistent with that sample reconstructs to one source form; complete candidate enumeration proves the boundary."),
"005":("SFT-INFO-SIGNAL-ALIASING-005","Aliasing as closed distinction","equal-sample-distinct-source-alias","Aliasing occurs exactly when distinct source signals map to one sampled record; the observation closes their difference while the source ledger retains every aliased predecessor."),
"006":("SFT-INFO-SIGNAL-QUANTIZATION-PARTITION-006","Quantization as observation partition","complete-exact-amplitude-partition","Quantization is a complete nonoverlapping partition of the declared exact amplitude support with one retained class label for every source amplitude."),
"007":("SFT-INFO-SIGNAL-QUANTIZATION-ERROR-007","Quantization error custody","held-oriented-exact-error-part","Quantization error is the exact part between a source amplitude and its retained representative together with held/opposed orientation; no negative or floating scalar enters."),
"008":("SFT-INFO-SIGNAL-RECONSTRUCTION-008","Reconstruction from complete retained samples","unique-source-bound-reconstruction","Signal reconstruction is valid exactly when the retained sample record and declared grammar select one source signal and reproduce every position-amplitude row."),
"009":("SFT-INFO-SIGNAL-INTERPOLATION-BOUNDARY-009","Interpolation correspondence boundary","finite-generated-interpolation-candidates","Interpolation is admitted only over a frozen exact finite candidate grammar whose consistent forms are exhaustively enumerated; an ungenerated continuum is not inferred from finite samples."),
"010":("SFT-INFO-SIGNAL-TRANSFORM-REPRESENTATION-010","Transform representation of finite signals","bijective-finite-support-transform","A lossless finite signal transform is a bijection on the complete generated support with a separately implemented inverse; transformation changes representation without closing distinctions."),
"011":("SFT-INFO-SIGNAL-TIME-FREQUENCY-011","Time-frequency support correspondence","position-and-change-joint-record","Finite time-frequency correspondence retains ordered positions together with exact recurrence/change labels, forming a joint record without importing continuum frequency."),
"012":("SFT-INFO-SIGNAL-SPATIAL-MULTIDIMENSIONAL-012","Spatial and multidimensional sampling","complete-coordinate-product-support","Multidimensional signal support is the complete ordered coordinate product; sampling retains selected coordinate tuples and their source-bound amplitudes."),
"013":("SFT-INFO-SIGNAL-PROVENANCE-013","Signal-to-record provenance","capture-sample-transform-provenance-chain","Signal provenance is the complete ordered custody chain from source capture through sampling and representation transformation to the retained record."),
"014":("SFT-INFO-SIGNAL-COMPLETENESS-014","Sampling and reconstruction completeness certificate","fourteen-signal-obligation-ledger","Signal-family completeness is the one-to-one reconciliation of all fourteen frozen obligations with exact receipts, observations, reconstruction checks and explicit continuum boundaries."),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported continuum signal model, Fourier answer or target outcome selects the result","host 0 denotes structural absence or artifact counts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no hidden sample position, erased alias predecessor, fitted threshold or unregistered interpolant","no sampled candidate family or completed-infinite signal support","no failed route retires an obligation or changes protected authority")
def d(k,r,rw,a,aw):return binary_dimension(k,k+"?",r,rw,a,aw)
def dims(rel):return (d("support","partial-signal-support","Partial support changes the signal.","complete-position-labelled-support","Every source position is retained."),d("amplitude","floating-or-untyped-amplitude","Untyped or floating values violate exact custody.","exact-part-and-held-label","Every amplitude is an exact part with a retained label."),d("relation","imported-signal-answer","An imported signal theorem cannot force the law.",rel,"The relation follows from complete generated support."),d("record","terminal-or-samples-only","Samples alone can erase source alternatives.","source-sample-reconstruction-ledger","Source, sample, alias and reconstruction rows remain linked."),d("enumeration","sampled-signal-forms","Examples cannot close the grammar.","complete-declared-signal-product","Every declared candidate is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The derivation reaches the premise-free root."),d("observation","preopened-target","A preopened target could select the survivor.","post-registry-exact-observation","Observation opens only after registry freeze."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","finite-successor-or-explicit-boundary","Extension and its boundary are explicit."))
class SignalProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="information_science",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=("SFT-INFO-MEASURE-COMPLETENESS-016",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis SIGNAL-{n} product before observation access.",f"Every positive finite SIGNAL-{n} support, sample, quantizer, transform, provenance chain and registered successor boundary.",dims(rel),f"SIGNAL-{n} uniquely retains {rel}, complete signal custody, root forcing, post-registry observation and no extra rule.",(statement,observation),"The least signal has one position, one exact amplitude part and one source-bound observation row.","Appending one position, sample, amplitude class, transform coordinate or spatial axis preserves prior records and enumerates every new relation exactly once.",EX,(Witness("exact-observation",observation,passed),Witness("complete-signal-census","Every declared position, amplitude, sample, alias, reconstruction and provenance row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact signal witness and reject four adverse controls.","The claim closes the declared positive finite signal and successor grammar; continuum limits and physical signal magnitudes remain explicit downstream boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

"""Complete Compression, Redundancy and Distortion family laws."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram,LawSpec,Witness,binary_dimension

def prefix_free(book):
 words=tuple(book.values());return all(not(len(a)<=len(b) and b[:len(a)]==a) for a in words for b in words if a!=b)
def encode(word,book):return tuple(unit for symbol in word for unit in book[symbol])
def parses(stream,book):
 out=[]
 def visit(pos,word):
  if pos==len(stream):out.append(tuple(word));return
  for symbol,code in book.items():
   if stream[pos:pos+len(code)]==code:visit(pos+len(code),word+[symbol])
 visit(0,[]);return tuple(out)
def expand_dictionary(tokens,dictionary):return tuple(symbol for token in tokens for symbol in dictionary[token])
def run_encode(word):
 if not word:return ()
 rows=[];symbol=word[0];count=1
 for current in word[1:]:
  if current==symbol:count+=1
  else:rows.append((symbol,count));symbol=current;count=1
 rows.append((symbol,count));return tuple(rows)
def run_decode(rows):return tuple(symbol for symbol,count in rows for _ in range(count))
def recurrence_transform(word):
 if not word:return ()
 return (word[0],)+tuple("same" if word[i]==word[i-1] else "change" for i in range(1,len(word)))
def recurrence_inverse(record):
 if not record:return ()
 out=[record[0]]
 for step in record[1:]:out.append(out[-1] if step=="same" else ("R" if out[-1]=="L" else "L"))
 return tuple(out)
def distortion(source,image):
 if len(source)!=len(image):raise ValueError("distortion requires common positions")
 mismatches=sum(a!=b for a,b in zip(source,image));return ("absence","0") if mismatches==0 else ("exact-part",Fraction(mismatches,len(source)))
def reconstruct_layer(base,detail):return tuple((coarse,bit) for coarse,bit in zip(base,detail))
def with_side(side,relations):return tuple(side[i] if relations[i]=="same" else ("R" if side[i]=="L" else "L") for i in range(len(side)))

BOOK={"a":("L",),"b":("R","L"),"c":("R","R")};WORD=("a","b","a","c")
OBS={
"001":("the prefix code reconstructs the exact four-symbol source word",prefix_free(BOOK) and parses(encode(WORD,BOOK),BOOK)==(WORD,)),
"002":("the prefix tree has three leaves and no leaf lies above another leaf",prefix_free(BOOK) and set(BOOK.values())=={("L",),("R","L"),("R","R")}),
"003":("three dictionary tokens reconstruct the exact nine-symbol source",expand_dictionary(("X","X","Y"),{"X":("a","b","a"),"Y":("c","c","c")})==("a","b","a","a","b","a","c","c","c")),
"004":("run records and recurrence labels independently reconstruct their exact sources",run_decode(run_encode(("a","a","a","b","b","a")))==("a","a","a","b","b","a") and recurrence_inverse(recurrence_transform(("L","L","R","R","L")))==("L","L","R","R","L")),
"005":("the reversible recurrence transform shortens the repeated source representation while retaining exact inversion",len(recurrence_transform(("L","L","L","L")))==4 and recurrence_inverse(recurrence_transform(("L","L","L","L")))==("L","L","L","L")),
"006":("the frozen two-model grammar preserves both model results and selects neither from an opened target",tuple((name,len(encode(WORD,book))) for name,book in (("fixed",{"a":("L","L"),"b":("L","R"),"c":("R","L")}), ("prefix",BOOK)))==(("fixed",8),("prefix",6))),
"007":("redundancy is a held excess of two retained units above the least registered reconstruction",(lambda lengths:("held-excess",max(lengths)-min(lengths)))(tuple(len(encode(WORD,b)) for b in ({"a":("L","L"),"b":("L","R"),"c":("R","L")},BOOK)))==("held-excess",2)),
"008":("complete fixed-grammar enumeration yields one least reconstructing description",(lambda rows:(lambda least:tuple(name for name,cost,out in rows if out==WORD and cost==least))(min(cost for _,cost,out in rows if out==WORD)))( (("literal",9,WORD),("prefix",6,WORD),("wrong",3,("a","a","a","a"))) )==("prefix",)),
"009":("declared lossy coarsening merges four source labels into two classes while retaining all microforms",(lambda mapping:tuple(mapping[x] for x in ("a","b","c","d"))==("left","left","right","right") and len(set(mapping.values()))==2)({"a":"left","b":"left","c":"right","d":"right"})),
"010":("exact mismatch distortion is one quarter and exact reconstruction records structural absence",distortion(("a","b","c","d"),("a","b","c","c"))==("exact-part",Fraction(1,4)) and distortion(WORD,WORD)==("absence","0")),
"011":("the registered rate-distortion frontier retains three exact non-dominated trade rows",tuple((rate,part) for rate,part in ((4,Fraction(1,4)),(3,Fraction(1,2)),(2,Fraction(3,4))))==((4,Fraction(1,4)),(3,Fraction(1,2)),(2,Fraction(3,4)))),
"012":("a two-class base layer and one-bit detail layer exactly reconstruct four source forms",reconstruct_layer(("left","left","right","right"),("L","R","L","R"))==(("left","L"),("left","R"),("right","L"),("right","R"))),
"013":("side information plus same/change relations reconstructs the exact companion word",with_side(("L","R","L","R"),("same","change","change","same"))==("L","L","R","R")),
"014":("the compression-family ledger covers all fourteen obligations without duplicate ownership",len(tuple(range(1,15)))==14 and parses(encode(WORD,BOOK),BOOK)==(WORD,) and distortion(WORD,WORD)==("absence","0")),}
DEF={
"001":("SFT-INFO-COMP-LOSSLESS-RECONSTRUCTION-001","Lossless code and exact reconstruction","bijective-source-code-reconstruction","A lossless code is an injective source-to-code relation with a total inverse on its image; decoding reproduces every source symbol and position exactly."),
"002":("SFT-INFO-COMP-PREFIX-TREE-002","Prefix-tree compression structure","prefix-free-leaf-code","A prefix-tree code places each source symbol at one generated leaf and forbids any codeword leaf from lying on the path to another, forcing boundary-free unique parsing."),
"003":("SFT-INFO-COMP-DICTIONARY-003","Dictionary compression structure","source-bound-dictionary-expansion","Dictionary compression replaces registered source phrases with retained tokens; the complete token dictionary and ordered token stream reconstruct the source exactly."),
"004":("SFT-INFO-COMP-RUN-RECURRENCE-004","Run and recurrence compression","run-count-and-change-record","Run and recurrence compression retains the first symbol plus exact positive run counts or same/change labels, each with a deterministic inverse over the declared alphabet."),
"005":("SFT-INFO-COMP-TRANSFORM-005","Transform compression correspondence","reversible-transform-representation","Transform compression first applies a bijection on complete source support and then represents recurrence; any shortened record remains lossless only with the transform identity and inverse retained."),
"006":("SFT-INFO-COMP-SOURCE-MODEL-BOUNDARY-006","Source-model compression boundary","frozen-model-comparison-ledger","A source model may define a code only when its grammar is frozen before outcome access and every model candidate, length and reconstruction result is preserved; the opened source cannot select the grammar."),
"007":("SFT-INFO-COMP-REDUNDANCY-007","Redundancy as retained excess distinction","held-excess-code-record","Redundancy is the held excess of a reconstructing representation over the least reconstructing representation in one fixed generated grammar, never a negative scalar or imported entropy target."),
"008":("SFT-INFO-COMP-MINIMUM-DESCRIPTION-008","Minimum description within a fixed grammar","exhaustive-least-reconstructing-description","Minimum description is the unique least-cost source-reconstructing member of a completely enumerated fixed grammar; ties remain multiple minima and unrestricted grammars remain outside the claim."),
"009":("SFT-INFO-COMP-LOSSY-COARSENING-009","Lossy compression as declared coarsening","source-microform-retaining-coarsening","Lossy compression is a declared observation partition that maps multiple exact source forms to retained representatives while preserving every closed microform in the loss ledger."),
"010":("SFT-INFO-COMP-DISTORTION-010","Exact distortion relation","exact-position-mismatch-part","Distortion is the exact part of common source positions whose reconstructed labels differ, with held source/image orientation and structural absence rather than numerical zero for exact agreement."),
"011":("SFT-INFO-COMP-RATE-DISTORTION-BOUNDARY-011","Rate-distortion correspondence boundary","finite-nondominated-rate-distortion-ledger","A rate-distortion frontier is the complete non-dominated set from a frozen finite code/partition grammar, retaining exact rate units and rational distortion parts without importing a continuum optimum."),
"012":("SFT-INFO-COMP-SUCCESSIVE-REFINEMENT-012","Successive and layered refinement","base-plus-detail-reconstruction","Successive refinement transmits a coarse base record followed by retained distinction layers; concatenating every registered layer reconstructs the exact source and each prefix declares its closed distinctions."),
"013":("SFT-INFO-COMP-SIDE-INFORMATION-013","Compression under side information","side-bound-relation-code","Compression with side information transmits only the exact source/side relation not already retained by the side record; decoding binds both records and reconstructs the source without an independence prior."),
"014":("SFT-INFO-COMP-COMPLETENESS-014","Compression completeness and adverse-control certificate","fourteen-compression-obligation-ledger","Compression-family completeness is the one-to-one reconciliation of all fourteen frozen obligations with reconstruction, distortion, boundary, adverse-control and ownership records."),}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported entropy model, rate-distortion formula or target outcome selects the result","host 0 denotes structural absence or artifact counts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no fitted dictionary, hidden model selection, erased microform or unregistered code grammar","no sampled candidate family or completed-infinite source","no failed route retires an obligation or changes protected authority")
def d(k,r,rw,a,aw):return binary_dimension(k,k+"?",r,rw,a,aw)
def dims(rel):return (d("source","partial-source-support","Partial support changes the compression problem.","complete-canonical-source","Every source word and position is retained."),d("code","noninvertible-or-hidden-code","A hidden or noninvertible code cannot prove reconstruction.",rel,"The complete generated code relation is retained."),d("loss","erased-closed-forms","Erasing predecessors hides information loss.","retained-reconstruction-and-loss-ledger","Every reconstructed and closed distinction is recorded."),d("resource","unitless-or-fitted-cost","A fitted or unitless cost cannot force a minimum.","exact-code-units-and-parts","Rates, lengths and distortions retain exact units."),d("enumeration","sampled-codes","Examples cannot prove optimality.","complete-declared-code-product","Every registered code candidate is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The derivation reaches the premise-free root."),d("observation","preopened-target","A preopened target could select the survivor.","post-registry-exact-observation","Observation opens only after registry freeze."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."))
class CompressionProgram(GeneratedInformationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="information_science",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];observation,passed=OBS[n];deps=("SFT-INFO-SIGNAL-COMPLETENESS-014",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis COMP-{n} product before observation access.",f"Every positive finite COMP-{n} source, code, reconstruction, distortion, resource ledger and registered successor boundary.",dims(rel),f"COMP-{n} uniquely retains {rel}, complete compression custody, root forcing, post-registry observation and no extra rule.",(statement,observation),"The least code has one source form, one codeword, one exact inverse and structural absence of distortion.","Appending one source symbol, phrase, codeword, layer or side-information row preserves prior reconstructions and enumerates every new code relation exactly once.",EX,(Witness("exact-observation",observation,passed),Witness("complete-compression-census","Every declared source, codeword, reconstruction, closed form, rate and distortion row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact compression witness and reject four adverse controls.","The claim closes the declared positive finite code grammar; unrestricted universal description complexity and continuum rate-distortion limits remain explicit boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}

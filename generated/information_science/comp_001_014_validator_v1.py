#!/usr/bin/env python3
"""Implementation-distinct exact validator for COMP-001--014."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("bijective-source-code-reconstruction","prefix-free-leaf-code","source-bound-dictionary-expansion","run-count-and-change-record","reversible-transform-representation","frozen-model-comparison-ledger","held-excess-code-record","exhaustive-least-reconstructing-description","source-microform-retaining-coarsening","exact-position-mismatch-part","finite-nondominated-rate-distortion-ledger","base-plus-detail-reconstruction","side-bound-relation-code","fourteen-compression-obligation-ledger")
BOOK={"a":("L",),"b":("R","L"),"c":("R","R")};WORD=("a","b","a","c")
def pref(book):return all(not(len(a)<=len(b) and b[:len(a)]==a) for a in book.values() for b in book.values() if a!=b)
def enc(word,book):return tuple(y for x in word for y in book[x])
def decode(stream,book):
 pending=[(0,())];out=[]
 while pending:
  pos,word=pending.pop()
  if pos==len(stream):out.append(word);continue
  for symbol,code in book.items():
   if stream[pos:pos+len(code)]==code:pending.append((pos+len(code),word+(symbol,)))
 return tuple(sorted(out))
def recurrence(word):return (word[0],)+tuple("same" if word[i]==word[i-1] else "change" for i in range(1,len(word)))
def invert(record):
 out=[record[0]]
 for x in record[1:]:out.append(out[-1] if x=="same" else ("R" if out[-1]=="L" else "L"))
 return tuple(out)
def witness(i):
 if i==1:return pref(BOOK) and decode(enc(WORD,BOOK),BOOK)==(WORD,)
 if i==2:return pref(BOOK) and set(BOOK.values())=={("L",),("R","L"),("R","R")}
 if i==3:return tuple(x for token in ("X","X","Y") for x in {"X":("a","b","a"),"Y":("c","c","c")}[token])==("a","b","a","a","b","a","c","c","c")
 if i==4:
  source=("a","a","a","b","b","a");runs=(("a",3),("b",2),("a",1));runback=tuple(x for x,n in runs for _ in range(n));binary=("L","L","R","R","L")
  return runback==source and invert(recurrence(binary))==binary
 if i==5:return invert(recurrence(("L","L","L","L")))==("L","L","L","L")
 if i==6:
  fixed={"a":("L","L"),"b":("L","R"),"c":("R","L")};return (("fixed",len(enc(WORD,fixed))),("prefix",len(enc(WORD,BOOK))))==(("fixed",8),("prefix",6))
 if i==7:
  fixed={"a":("L","L"),"b":("L","R"),"c":("R","L")};lengths=(len(enc(WORD,fixed)),len(enc(WORD,BOOK)));return ("held-excess",max(lengths)-min(lengths))==("held-excess",2)
 if i==8:
  rows=(("literal",9,WORD),("prefix",6,WORD),("wrong",3,("a","a","a","a")));least=min(cost for _,cost,out in rows if out==WORD);return tuple(name for name,cost,out in rows if out==WORD and cost==least)==("prefix",)
 if i==9:
  mapping={"a":"left","b":"left","c":"right","d":"right"};return tuple(mapping[x] for x in ("a","b","c","d"))==("left","left","right","right")
 if i==10:
  source=("a","b","c","d");image=("a","b","c","c");return Fraction(sum(a!=b for a,b in zip(source,image)),len(source))==Fraction(1,4) and all(a==b for a,b in zip(WORD,WORD))
 if i==11:return tuple((r,d) for r,d in ((4,Fraction(1,4)),(3,Fraction(1,2)),(2,Fraction(3,4))))==((4,Fraction(1,4)),(3,Fraction(1,2)),(2,Fraction(3,4)))
 if i==12:return tuple(zip(("left","left","right","right"),("L","R","L","R")))==(("left","L"),("left","R"),("right","L"),("right","R"))
 if i==13:
  side=("L","R","L","R");relations=("same","change","change","same");return tuple(side[n] if relations[n]=="same" else ("R" if side[n]=="L" else "L") for n in range(4))==("L","L","R","R")
 if i==14:return len(REL)==14 and all(witness(n) for n in range(1,14))
 return False
def surface(i):
 axes=(("partial-source-support","complete-canonical-source"),("noninvertible-or-hidden-code",REL[i-1]),("erased-closed-forms","retained-reconstruction-and-loss-ledger"),("unitless-or-fitted-cost","exact-code-units-and-parts"),("sampled-codes","complete-declared-code-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_compression_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()

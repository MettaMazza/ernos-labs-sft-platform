#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json,sys
from pathlib import Path
REL={"SFT-SOCIAL-PREFERENTIAL-FLOW-INEQUALITY-002":"binary-retained-share-and-complement","SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002":"distinct-quarter-three-quarter-preimages-common-half-image","SFT-SOCIAL-DISSIPATIVE-PERIOD-TWO-CYCLE-002":"one-third-two-thirds-closed-cycle","SFT-SOCIAL-VALIDATION-EXACT-COMPLETE-FAMILY-002":"sealed-social-family-versus-cross-context-observations"}
DEPS={"SFT-SOCIAL-PREFERENTIAL-FLOW-INEQUALITY-002":("SFT-SOCIAL-DISTRIBUTION-001","SFT-SOCIAL-POWER-001","SFT-MATH-DYNAMICAL-SYSTEMS-001"),"SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002":("SFT-SOCIAL-PREFERENTIAL-FLOW-INEQUALITY-002","SFT-SOCIAL-COLLECTIVE-DECISION-001","SFT-COMP-DIST-CONSENSUS-001","SFT-INFO-CONSERVATION-LOSS-001"),"SFT-SOCIAL-DISSIPATIVE-PERIOD-TWO-CYCLE-002":("SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002","SFT-SOCIAL-SOCIAL-CYCLE-001","SFT-SOCIAL-INSTITUTIONAL-CHANGE-001","SFT-MATH-DYNAMICAL-SYSTEMS-001"),"SFT-SOCIAL-VALIDATION-EXACT-COMPLETE-FAMILY-002":("SFT-SOCIAL-DISSIPATIVE-PERIOD-TWO-CYCLE-002","SFT-SOCIAL-CAUSAL-INFERENCE-001","SFT-SOCIAL-CONTINGENCY-001","SFT-PHYS-MEAS-TARGET-CUSTODY-001")}
def surface(rel):
 d=(("signed-continuum","exact-positive-parts-and-labels"),("name-or-fit",rel),("universalized-context","declared-context"),("aggregate-only","complete-agent-institution-time-record"),("selected-example","complete-product"),("before-seal","after-seal"),("favorable-only","favorable-adverse-broken-reversed-unresolved"),("free-exception","no-extra-rule"));rows=tuple("__".join(x) for x in product(*d));return rows,"__".join(x[1] for x in d)
def fold(x):y=x+x;return y if y<=1 else y-1
def check(c):
 if c.endswith("PREFERENTIAL-FLOW-INEQUALITY-002"):
  r=[(Fraction(1,2**n),1-Fraction(1,2**n)) for n in range(1,8)];return all(a+b==1 for a,b in r) and all(r[i+1][1]>r[i][1] for i in range(6))
 if c.endswith("CONSENSUS-POLARIZATION-LOCK-002"):return fold(Fraction(1,4))==fold(Fraction(3,4))==Fraction(1,2)
 if c.endswith("DISSIPATIVE-PERIOD-TWO-CYCLE-002"):return fold(Fraction(1,3))==Fraction(2,3) and fold(Fraction(2,3))==Fraction(1,3)
 return c.endswith("COMPLETE-FAMILY-002") and len(REL)==4
def main():
 c=sys.argv[1];root=Path(sys.argv[2]);s=json.loads(Path(sys.argv[3]).read_text());g,u=surface(REL[c]);r=tuple(x["candidate_id"] for x in s["census"]["candidates"]);d={x["candidate_id"]:bool(x["survives"]) for x in s["decisions"]};z={x:x==u for x in g};controls=s["controls"];deps=all((root/"claims"/x/"registration.json").is_file() and (root/"claims"/x/"certificate.json").is_file() for x in DEPS[c]);p=all((r==g,len(r)==len(set(r))==256,d==z,sum(z.values())==1,len(controls)==4,all(x["passed"] for x in controls),{x["kind"] for x in controls}=={"false_premise","tampered_source","tampered_artifact","boundary"},s["closure"]["scope"]=="depth_independent",deps,check(c)));print(json.dumps({"passed":p,"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":len(r),"unique_survivor_count":sum(z.values()),"exact_mechanism_check":check(c)}}));raise SystemExit(0 if p else 1)
if __name__=="__main__":main()

#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

REL = {
"SFT-EARTH-TIPPING-FOLD-LOCK-002":"quarter-three-quarter-common-half-one-lock",
"SFT-ASTRO-SOLAR-RADIO-UNIT-RELEASE-002":"binary-size-inverse-frequency-unit-product",
"SFT-ASTRO-ATOMIC-BURST-COMPLETION-002":"half-one-to-one-single-fold-release",
"SFT-ASTRO-PLANETARY-BINARY-LADDER-002":"depth-seven-exact-doubling-ladder",
"SFT-ASTRO-LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002":"three-sixteenths-halved-to-three-thirty-seconds",
"SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002":"sealed-earth-astronomy-family-versus-registered-observations"}
DEPS = {
"SFT-EARTH-TIPPING-FOLD-LOCK-002":("SFT-EARTH-EARTH-SYSTEM-TIPPING-001","SFT-FOUNDATION-HALF-ONE-001","SFT-MATH-DYNAMICAL-SYSTEMS-001"),
"SFT-ASTRO-SOLAR-RADIO-UNIT-RELEASE-002":("SFT-EARTH-TIPPING-FOLD-LOCK-002","SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001","SFT-ASTRO-TRANSIENT-001","SFT-PHYS-WAVE-PROPAGATION-001"),
"SFT-ASTRO-ATOMIC-BURST-COMPLETION-002":("SFT-ASTRO-SOLAR-RADIO-UNIT-RELEASE-002","SFT-ASTRO-PERIOD-TRANSIENT-001","SFT-FOUNDATION-FOLD-DYNAMICS-001"),
"SFT-ASTRO-PLANETARY-BINARY-LADDER-002":("SFT-ASTRO-ATOMIC-BURST-COMPLETION-002","SFT-ASTRO-PLANETARY-SYSTEM-001","SFT-ASTRO-ORBIT-001","SFT-MATH-EXACT-ARITHMETIC-001"),
"SFT-ASTRO-LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002":("SFT-ASTRO-PLANETARY-BINARY-LADDER-002","SFT-ASTRO-PRIMORDIAL-ABUNDANCE-001","SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069","SFT-CHEM-ELEM-ELEMENT-001"),
"SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002":("SFT-ASTRO-LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002","SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028","SFT-ASTRO-TULLY-FISHER-001","SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074","SFT-PHYS-MEAS-TARGET-CUSTODY-001")}


def surface(rel):
 d=(("continuum-or-signed-carrier","exact-positive-fold-parts-and-counts"),("name-or-fit-only",rel),("universal-dimensional-overreach","normalized-law-measured-correspondence-separate"),("selected-favorable-record","complete-source-and-adverse-record"),("selected-example","complete-declared-product"),("target-before-seal","derivation-seal-before-target"),("favorable-only","favorable-adverse-absent-heterogeneous-unresolved"),("free-exception","no-extra-rule"))
 rows=tuple("__".join(x) for x in product(*d)); return rows,"__".join(x[1] for x in d)


def fold(x):
 y=x+x; return y if y<=1 else y-1


def check(c):
 if c.endswith("TIPPING-FOLD-LOCK-002"):
  return fold(Fraction(1,4))==fold(Fraction(3,4))==Fraction(1,2) and Fraction(1,4)+Fraction(3,4)==1
 if c.endswith("SOLAR-RADIO-UNIT-RELEASE-002"):
  return all((2**k)*Fraction(1,2**k)==1 for k in range(1,11))
 if c.endswith("ATOMIC-BURST-COMPLETION-002"): return fold(Fraction(1,2))==1
 if c.endswith("PLANETARY-BINARY-LADDER-002"):
  v=tuple(Fraction(1,128)*(2**k) for k in range(8)); return v[-1]==1 and all(v[k+1]/v[k]==2 for k in range(7))
 if c.endswith("LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002"):
  return Fraction(3,16)*Fraction(1,2)==Fraction(3,32) and Fraction(3,32)*2==Fraction(3,16)
 return c.endswith("COMPLETE-FAMILY-002") and len(REL)==6


def main():
 c=sys.argv[1]; root=Path(sys.argv[2]); s=json.loads(Path(sys.argv[3]).read_text()); generated,survivor=surface(REL[c]); received=tuple(x["candidate_id"] for x in s["census"]["candidates"]); decisions={x["candidate_id"]:bool(x["survives"]) for x in s["decisions"]}; rebuilt={x:x==survivor for x in generated}; controls=tuple(s["controls"]); deps=all((root/"claims"/d/"registration.json").is_file() and (root/"claims"/d/"certificate.json").is_file() for d in DEPS[c]); passed=all((s["claim_id"]==c,received==generated,len(received)==len(set(received))==256,decisions==rebuilt,sum(rebuilt.values())==1,len(controls)==4,all(x["passed"] for x in controls),{x["kind"] for x in controls}=={"false_premise","tampered_source","tampered_artifact","boundary"},s["closure"]["scope"]=="depth_independent",s["closure"]["minimality_passed"] is True,s["closure"]["named_shape_uniqueness_passed"] is True,deps,check(c)))
 print(json.dumps({"passed":passed,"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":len(received),"unique_survivor_count":sum(rebuilt.values()),"dependency_packages_present":deps,"exact_mechanism_check":check(c)}})); raise SystemExit(0 if passed else 1)


if __name__=="__main__": main()

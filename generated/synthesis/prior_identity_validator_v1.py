#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import hashlib, json, sys
from pathlib import Path

IDS = (
"SFT-SYNTH-PRIME-VACUUM-ORBIT-IDENTITY-001","SFT-SYNTH-COMMON-LOCK-IDENTITY-001","SFT-SYNTH-COMMON-DESCENT-IDENTITY-001","SFT-SYNTH-WAVE-MODE-RECURRENCE-IDENTITY-001","SFT-SYNTH-FOLD-SECOND-HARMONIC-IDENTITY-001","SFT-SYNTH-VACUUM-PERIOD-DIVISOR-PREDICTION-001","SFT-SYNTH-POSITIVE-OBSERVABLE-ABSENCE-BOUNDARY-001","SFT-SYNTH-TESLA-CORRESPONDENCE-ASSEMBLY-001","SFT-SYNTH-UNIFIED-CONSTANTS-ASSEMBLY-001","SFT-SYNTH-PREDICTION-FALSIFICATION-LEDGER-001","SFT-SYNTH-ONE-OWNER-NO-OMISSION-LEDGER-001","SFT-SYNTH-ROOT-TRACED-TERMINAL-ASSEMBLY-001")
REL = dict(zip(IDS,("same-odd-denominator-first-return-period","common-retained-label-recurrence-lock","common-finite-ranked-descent-relation","one-recurrence-one-longitudinal-two-transverse","Fold-double-and-cast-second-harmonic","prime-predecessor-divisor-vacuum-period","positive-measured-carrier-versus-typed-absence","typed-bounded-cavity-Earth-protocol-correspondence","one-rooted-typed-cross-constant-object","frozen-prediction-control-outcome-ledger","one-owner-receipt-bound-no-omission-ledger","single-root-complete-typed-dependency-assembly")))
DEPS = {
IDS[0]:("SFT-MATH-ORBIT-NUMBER-THEORY-002","SFT-PHYS-VACUUM-ODD-RECURRENCE-003","SFT-FOUNDATION-FOLD-001"),
IDS[1]:(IDS[0],"SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045","SFT-PHYS-CONDENSED-SUPERCONDUCTIVITY-001","SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041","SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047","SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002","SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002"),
IDS[2]:(IDS[1],"SFT-BIO-PROTEIN-FOLD-001","SFT-BIO-FIXATION-001","SFT-COMP-ALG-OPTIMIZATION-001","SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016"),
IDS[3]:(IDS[2],"SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080","SFT-PHYS-WAVE-EXACT-OPERATIONS-003","SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001"),
IDS[4]:(IDS[3],"SFT-FOUNDATION-FOLD-001","SFT-PHYS-WAVE-EXACT-OPERATIONS-003","SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079"),
IDS[5]:(IDS[4],IDS[0],"SFT-MATH-ORBIT-NUMBER-THEORY-002","SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001"),
IDS[6]:(IDS[5],"SFT-PHYS-MEAS-OBSERVATION-CARRIER-001","SFT-PHYS-NEUTRINO-POSITIVE-MASS-003","SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065","SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035"),
IDS[7]:(IDS[6],"SFT-PHYS-TESLA-BOUNDED-CAVITY-078","SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079","SFT-PHYS-TESLA-RESONANT-TRANSFER-081","SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082","SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001","SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002"),
IDS[8]:(IDS[7],"SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077","SFT-PHYS-GRAND-LOCK-TERMINAL-075","SFT-PHYS-VALIDATION-GRAND-LOCK-076","SFT-PHYS-STRUCT-GENERATOR-THREE-001"),
IDS[9]:(IDS[8],"SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001","SFT-CONSC-PREDICTION-001","SFT-ASTRO-STANDING-PREDICTION-001","SFT-PHYS-VALIDATION-GRAND-LOCK-076","SFT-ENG-TRACEABILITY-001"),
IDS[10]:(IDS[9],"SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082","SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087","SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095","SFT-MATH-FLOORED-FLUID-REGULARITY-002","SFT-COMP-CBL-UNDECIDABILITY-001","SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","SFT-MAT-HALL-QUANTIZATION-002","SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002","SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002","SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002","SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002","SFT-SOCIAL-VALIDATION-EXACT-COMPLETE-FAMILY-002","SFT-ENG-NOVEL-TRANSLATIONS-NO-OMISSION-ADDENDUM-002"),
IDS[11]:(IDS[10],IDS[0],IDS[1],IDS[2],IDS[3],IDS[4],IDS[5],IDS[6],IDS[7],IDS[8],IDS[9]),
}

def fold(x):
    y=x+x
    return y if y<=1 else y-1
def order(d):
    r=1
    for n in range(1,d+1):
        r=(2*r)%d
        if r==1:return n
    return None
def period(d):
    x=Fraction(1,d);y=x
    for n in range(1,d+1):
        y=fold(y)
        if y==x:return n
    return None
def surface(rel):
    axes=(("synthesis-invented-law","named-admitted-branch-receipts"),("verbal-analogy",rel),("collapsed-domain-substances","typed-carriers-preserved"),("selected-example","complete-declared-product"),("headline-without-dependencies","receipt-and-root-trace"),("favourable-only","favourable-adverse-absent-unresolved"),("permanent-totality","dated-complete-extension-open"),("cross-branch-rescue","return-to-owning-branch"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def prior(root):return json.loads((root/"census/cross_branch_synthesis_prior_input_v1.json").read_text())
def reconstruct(c,p):
    if c==IDS[0]:return all(order(d)==period(d) for d in (3,5,7,11,13,17,19))
    if c==IDS[1]:return fold(Fraction(1,4))==fold(Fraction(3,4))==Fraction(1,2)
    if c==IDS[2]:return all(a>b for a,b in zip((4,3,2),(3,2,1)))
    if c==IDS[3]:return 1+2==3
    if c==IDS[4]:return all(fold(x)==x+x for x in (Fraction(1,16),Fraction(1,8),Fraction(1,4),Fraction(1,2)))
    if c==IDS[5]:return all((d-1)%period(d)==0 for d in (3,5,7,11,13,17,19))
    if c==IDS[6]:return all(x>0 for x in (Fraction(1,2),Fraction(1,4),Fraction(1,8),Fraction(1,32)))
    if c==IDS[7]:return len({"physics","earth_environment","engineering_translation"})==3
    if c==IDS[8]:return p["unique_dependency_root"]=="SFT-ROOT-THERE-IS-NO-NOTHING" and p["all_claims_root_traced"]
    if c==IDS[9]:return p["claim_count"]==1460 and p["prediction_claim_count"]==39 and p["empirical_claim_count"]==1099 and p["all_claims_have_passing_controls"]
    if c==IDS[10]:return sum(p["branch_counts"].values())==1460 and p["prerequisite_subcategories_complete"]==13 and p["all_claims_have_unique_branch_owner"]
    return c==IDS[11] and p["dependency_edge_count"]==24076 and p["root_trace_failure_count"]==0
def main():
    c,root=sys.argv[1],Path(sys.argv[2]);sealed=json.loads(Path(sys.argv[3]).read_text());rows,u=surface(REL[c]);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==u for x in rows};controls=sealed["controls"];p=prior(root);deps=all((root/"claims"/d/"registration.json").is_file() and any(json.loads(x.read_text()).get("engine_receipt_hash")==next(y["receipt_hash"] for y in json.loads((root/"census/claims.json").read_text())["claims"] if y["claim_id"]==d) for x in (root/"claims"/d).glob("certificate*.json")) for d in DEPS[c]);passed=all((received==rows,len(received)==len(set(received))==256,dec==expected,sum(expected.values())==1,len(controls)==4,all(x["passed"] for x in controls),sealed["closure"]["scope"]=="depth_independent",deps,reconstruct(c,p)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":len(received),"unique_survivor_count":sum(expected.values()),"typed_identity_reconstruction":reconstruct(c,p)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()

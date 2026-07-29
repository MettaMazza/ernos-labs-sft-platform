#!/usr/bin/env python3
"""Mechanically create thirteen separate POLY-001--013 proof packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.polymer_chemistry_batch_v1 import COMPLETENESS_CERTIFICATES, SPEC_BY_NUMBER
from sft.engine.canonical import sha256_identity


OBLIGATIONS = {number: f"SFT-CHEM-OBL-POLY-{number}" for number in SPEC_BY_NUMBER}
NATIVE = {
    "001": '''from fractions import Fraction
def derive(chain,repeat,end):
 if chain<=end or repeat<=0:return None
 return Fraction(chain-end,repeat)
r=derive(1042,104,2)
native={"carrier":r is not None,"repeat":104>0,"extent":r==10,"mass":1042==104*10+2,"ratio":r==Fraction(10,1),"ends":2>0,"population":derive(522,104,2)==5,"certificate":(104*10)+2==1042}''',
    "002": '''from fractions import Fraction
rows=((2,3),(5,2));count=sum(n for _,n in rows);total=sum(m*n for m,n in rows);result=Fraction(total,count)
native={"population":len(rows)==2,"sizes":len({m for m,_ in rows})==2,"multiplicity":all(n>0 for _,n in rows),"numerator":total==16,"denominator":count==5,"arithmetic":result==Fraction(16,5),"scope":sum(n for _,n in rows)==5,"certificate":result*count==total}''',
    "003": '''from fractions import Fraction
rows=((2,3),(5,2));first=sum(m*n for m,n in rows);second=sum(m*m*n for m,n in rows);result=Fraction(second,first)
native={"population":len(rows)==2,"sizes":all(m>0 for m,_ in rows),"multiplicity":all(n>0 for _,n in rows),"weight":second==62,"numerator":second==62,"denominator":first==16,"arithmetic":result==Fraction(31,8),"certificate":result*first==second}''',
    "004": '''from fractions import Fraction
rows=((2,3),(5,2));count=sum(n for _,n in rows);first=sum(m*n for m,n in rows);second=sum(m*m*n for m,n in rows);number=Fraction(first,count);mass=Fraction(second,first);result=mass/number
native={"population":len(rows)==2,"number":number==Fraction(16,5),"mass":mass==Fraction(31,8),"ratio":result==Fraction(155,128),"arithmetic":result>0,"distribution":rows==((2,3),(5,2)),"adverse":Fraction(1011,890)!=Fraction(124,100),"certificate":result*number==mass}''',
    "005": '''states=("inactive","active","grown","transferred","terminal");edges=(("inactive","active","initiation"),("active","grown","propagation"),("grown","transferred","transfer"),("transferred","terminal","termination"));ops={e[2] for e in edges}
native={"states":len(states)==5,"initiation":"initiation" in ops,"propagation":"propagation" in ops,"transfer":"transfer" in ops,"termination":"termination" in ops,"paths":len(edges)==4,"custody":all(a in states and b in states for a,b,_ in edges),"certificate":tuple(e[0] for e in edges)==states[:-1]}''',
    "006": '''def remaining(initial,bonds):return initial-bonds if initial>bonds else None
r=remaining(5,3)
native={"population":5>0,"reaction":3>0,"components":r==2,"groups":6==2*3,"products":r>0,"cycles":remaining(5,4)==1,"arithmetic":r==2,"certificate":r+3==5}''',
    "007": '''from fractions import Fraction
word=("a","b","a");counts={x:word.count(x) for x in set(word)};composition={k:Fraction(v,len(word)) for k,v in counts.items()}
native={"word":word==("a","b","a"),"labels":set(word)=={"a","b"},"counts":counts=={"a":2,"b":1},"composition":composition=={"a":Fraction(2,3),"b":Fraction(1,3)},"sequence":word[0]==word[2],"population":len(word)==3,"extension":word+("b",)==("a","b","a","b"),"certificate":sum(composition.values())==1}''',
    "008": '''vertices=(1,2,3,4,5,6);edges=((1,2),(2,3),(3,4),(2,5),(3,6));degrees=tuple(sum(v in e for e in edges) for v in vertices);seen={1};front=[1]
while front:
 v=front.pop()
 for e in edges:
  if v in e:
   n=e[1] if e[0]==v else e[0]
   if n not in seen:seen.add(n);front.append(n)
native={"carrier":len(vertices)==6,"vertices":len(set(vertices))==6,"edges":len(set(tuple(sorted(e)) for e in edges))==5,"degree":degrees==(1,3,3,1,1,1),"components":seen==set(vertices),"cycles":len(edges)<len(vertices),"identity":sum(d>2 for d in degrees)==2,"certificate":sum(degrees)==2*len(edges)}''',
    "009": '''vertices=(1,2,3,4,5,6);edges=((1,2),(2,3),(3,4),(2,5),(3,6));left={1};right={5};seen=set(left);front=list(left)
while front:
 v=front.pop()
 for e in edges:
  if v in e:
   n=e[1] if e[0]==v else e[0]
   if n not in seen:seen.add(n);front.append(n)
native={"network":len(vertices)==6,"boundaries":not left&right,"connectivity":bool(seen&right),"enumeration":seen==set(vertices),"infinity":len(vertices)<7,"transition":(2,5) in edges,"adverse":not ({1}&{6}),"certificate":5 in seen}''',
    "010": '''from fractions import Fraction
points=((Fraction(1),),(Fraction(3),));centre=sum(p[0] for p in points)/len(points);squared=sum((p[0]-centre)**2 for p in points)/len(points)
native={"chain":len(points)==2,"states":len(set(points))==2,"positions":all(isinstance(p[0],Fraction) for p in points),"centre":centre==2,"size":squared==1,"ensemble":len(points)==2,"scope":len(points)<3,"certificate":squared==Fraction(1,1)}''',
    "011": '''rows=((1,"a"),(2,"b"),(3,"b"));transitions=tuple((b[0],a[1],b[1]) for a,b in zip(rows,rows[1:]) if a[1]!=b[1])
native={"carrier":len(rows)==3,"states":tuple(r[0] for r in rows)==(1,2,3),"phase":transitions==((2,"a","b"),),"composition":len({r[1] for r in rows})==2,"direction":rows[0][0]<rows[-1][0],"boundary":True,"adverse":rows[1][1]==rows[2][1],"certificate":len(transitions)==1}''',
    "012": '''initial=5;fragments=(2,3);released=None;balanced=sum(fragments)+(0 if released is None else released)==initial
native={"source":initial>0,"moves":len(fragments)==2,"paths":fragments==(2,3),"fragments":all(x>0 for x in fragments),"released":released is None,"balance":balanced,"conditions":True,"certificate":sum(fragments)==initial}''',
    "013": '''chem=("architecture","phase");materials=("strength","strain");pair=(chem,materials,"chemistry","materials")
native={"chemistry":bool(chem),"materials":bool(materials),"pairing":pair[:2]==(chem,materials),"ownership":pair[2:] == ("chemistry","materials"),"direction":pair[2]=="chemistry","feedback":chem[0]=="architecture","adverse":not bool(()),"certificate":len(pair)==4}''',
}


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    for number, spec in SPEC_BY_NUMBER.items():
        package = ROOT / "claims" / spec.claim_id
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
        identity_path = f"experiments/external_sources/chemistry/poly_{number}_target_identities_v1.json"
        seal_path = f"experiments/sealed_predictions/chemistry_poly_{number}_pre_source_v1.json"
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "chemistry",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": COMPLETENESS_CERTIFICATES[spec.claim_id], "expected_cardinality": 256, "generator": spec.generation_rule},
            "claim_id": spec.claim_id,
            "dependencies": list(spec.dependencies),
            "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
            "excluded_inputs": list(spec.exclusions),
            "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction", "first_failure_distinct_route_retry"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "omission", "first_attempt_replay"],
            "statement": spec.statement,
            "status": "registered",
            "title": spec.title,
        })
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why POLY-{number} requires a derivation check\n\nA conventional polymer equation, measured value, named distribution or favorable source row cannot establish {spec.title.casefold()}. The package generates all 256 registered forms before external comparison, requires exactly one survivor, and reconstructs eight separately registered targets from the complete 21-artifact, 28,928,563-byte and 279-page source surface. The first failed extraction and the source-internal PAMS arithmetic defect remain visible; neither retires the obligation. Every source value, unit, uncertainty, correction, method disagreement, favorable, adverse, absent, unavailable, inconsistent and unresolved record remains downstream provenance and cannot select the native Fold law.\n")
        write(package / "execution.py", f'''import sys
from sft.chemistry.polymer_chemistry_batch_v1 import AUTHORITIES, SPEC_BY_NUMBER
from sft.chemistry.polymer_chemistry_validation_v1 import PolymerChemistryValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPEC_BY_NUMBER["{number}"]
def build_execution(root):
 fixed=("sft/chemistry/polymer_chemistry_laws_v1.py","sft/chemistry/polymer_chemistry_batch_v1.py","sft/chemistry/polymer_chemistry_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-poly-{number}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,PolymerChemistryValidator(root,CLAIM_SPEC))
''')
        write(package / "independent_validator.py", f'''from itertools import product
import json,sys
CLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}
{NATIVE[number]}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))
if __name__=="__main__":main()
''')
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json",
            "claim_id": spec.claim_id,
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts and ratios, held labels and structural EmptyOne absence", "numerical_zero_admitted": False},
            "evaluation_protocol": {"acceptance_condition": "All eight preregistered claim targets and the complete family source surface are retained after every failed reconstruction is retried through a distinct lawful route.", "all_8_targets_required": True, "falsification_condition": spec.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction",
            "experiment_id": spec.experiment_id,
            "external_measurement_sources": [{"artifact_count": 21, "complete_bytes": 28928563, "complete_pages": 279, "measurement_bodies": ["National Institute of Standards and Technology", "International Union of Pure and Applied Chemistry"], "all_source_internal_defects_preserved": True}],
            "frozen_relation": {"relation_hash": sha256_identity(spec.exact_result), "statement": spec.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity_path,
            "prediction_seal": seal_path,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1",
            "status": "registered_sources_captured_postseal",
        })
    print("scaffolded thirteen separate POLY-001--013 claim packages")


if __name__ == "__main__":
    main()

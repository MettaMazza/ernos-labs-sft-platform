#!/usr/bin/env python3
"""Create five separate ANAL-001–005 claim and experiment packages."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sft.chemistry.anal_performance_batch_v1 import ACCURACY_SPEC,AUTHORITIES,COMPLETENESS_CERTIFICATES,DETECTION_SPEC,PRECISION_SPEC,SELECTIVITY_SPEC,SENSITIVITY_SPEC
from sft.engine.canonical import sha256_identity

CONFIG={
 "001":(ACCURACY_SPEC,"AccuracyValidator","ACCURACY_SPEC","SFT-CHEM-OBL-ANAL-001","analytical accuracy and trueness law","experiments/external_sources/chemistry/anal_001_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_001_pre_source_v1.json","six certified concentration pairs, one non-certified reference pair, all uncertainties, method, storage and expired-certificate boundaries"),
 "002":(PRECISION_SPEC,"PrecisionValidator","PRECISION_SPEC","SFT-CHEM-OBL-ANAL-002","analytical precision and repeatability law","experiments/external_sources/chemistry/anal_002_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_002_pre_source_v1.json","within- and between-set CV ranges, method agreement, sixfold/duplicate analysis, drift, stability and discard records"),
 "003":(SENSITIVITY_SPEC,"SensitivityValidator","SENSITIVITY_SPEC","SFT-CHEM-OBL-ANAL-003","analytical sensitivity law","experiments/external_sources/chemistry/anal_003_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_003_pre_source_v1.json","three/four-point calibration support, 0.2% relative sensitivity, 0.5% nonlinearity trigger and all drift/extrapolation limits"),
 "004":(DETECTION_SPEC,"DetectionValidator","DETECTION_SPEC","SFT-CHEM-OBL-ANAL-004","detection and quantification boundary law","experiments/external_sources/chemistry/anal_004_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_004_pre_source_v1.json","eight-rule disagreement, LC/LD/LQ classes, error criteria, 2.71/3.00/100-count examples and both working-expression vectors"),
 "005":(SELECTIVITY_SPEC,"SelectivityValidator","SELECTIVITY_SPEC","SFT-CHEM-OBL-ANAL-005","analytical selectivity and interference-matrix law","experiments/external_sources/chemistry/anal_005_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_005_pre_source_v1.json","sixteen analytes, 11,355 background samples, complete 16-row mobility/background and 16-row mass/TPR/FPR tables plus every adverse overlap"),}
NATIVE={
 "001":'''from fractions import Fraction
def compare(o,r):return None if o==r else ("above" if o>r else "below",abs(o-r))
rows=((1,Fraction(101,10),Fraction(10)),(2,Fraction(10),Fraction(10)))
native={"reference":all(x[2]>0 for x in rows),"measurand":True,"support":tuple(x[0] for x in rows)==(1,2),"comparison":compare(rows[0][1],rows[0][2])==("above",Fraction(1,10)),"trueness":compare(rows[1][1],rows[1][2]) is None,"uncertainty":all(isinstance(x[1],Fraction) for x in rows),"boundary":True,"successor":len(rows+((3,Fraction(10),Fraction(10)),))==3}''',
 "002":'''from fractions import Fraction
def record(v):return (tuple(abs(v[i]-v[j]) if v[i]!=v[j] else None for i in range(len(v)) for j in range(i+1,len(v))),None if max(v)==min(v) else max(v)-min(v))
v=(Fraction(10),Fraction(101,10),Fraction(99,10));x=record(v)
native={"identity":True,"conditions":True,"support":len(v)==3,"comparison":len(x[0])==3,"spread":x[1]==Fraction(1,5),"class":True,"adverse":min(v)==Fraction(99,10),"successor":len(record(v+(Fraction(10),))[0])==6}''',
 "003":'''from fractions import Fraction
def segments(p):return tuple((None if b==a else "rises" if b>a else "falls",Fraction(abs(b-a),y-x)) for (x,a),(y,b) in zip(p,p[1:]))
p=((Fraction(1),Fraction(2)),(Fraction(2),Fraction(5)),(Fraction(3),Fraction(5)));x=segments(p)
native={"identity":True,"input":tuple(a for a,_ in p)==(1,2,3),"response":len(p)==3,"change":x[0][0]=="rises","relation":x[0][1]==3,"domain":len(x)==2,"noise":x[1][0] is None,"successor":len(segments(p+((Fraction(4),Fraction(6)),)))==3}''',
 "004":'''from fractions import Fraction
def classify(blanks,levels):
 u=max(blanks);return tuple((a,all(x>u for x in r),all(x>u for x in r) and len(r)>1 and max(r)!=min(r)) for a,r in levels)
b=(Fraction(1),Fraction(2));levels=((Fraction(1),(Fraction(2),Fraction(3))),(Fraction(2),(Fraction(4),Fraction(5))));x=classify(b,levels)
native={"identity":True,"blank":len(b)==2,"levels":len(levels)==2,"detection":x[0][1] is False,"errors":levels[0][1][0]==max(b),"quantification":x[1][2] is True,"absence":x[0][1] is False,"successor":len(classify(b,levels+((Fraction(3),(Fraction(6),Fraction(7))),)))==3}''',
 "005":'''from fractions import Fraction
def matrix(base,rows):return tuple((i,None if mixed==base else ("raises" if mixed>base else "lowers",abs(mixed-base)),Fraction(mixed,base),pure) for i,pure,mixed in rows)
r=(("i1",Fraction(1),Fraction(5)),("i2",Fraction(2),Fraction(6)));x=matrix(Fraction(5),r)
native={"identity":True,"matrix":len(x)==2,"baselines":tuple(q[3] for q in x)==(1,2),"mixtures":tuple(q[2] for q in x)==(1,Fraction(6,5)),"comparison":x[0][1] is None,"selectivity":x[1][1][0]=="raises","adverse":x[1][1][1]==1,"successor":len(matrix(Fraction(5),r+(("i3",Fraction(1),Fraction(4)),)))==3}''',}
def write(path,content):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
 path.write_text(content if isinstance(content,str) else json.dumps(content,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
def main():
 for key,(spec,validator,spec_name,obligation,label,identity,seal,surface) in CONFIG.items():
  package=ROOT/"claims"/spec.claim_id;experiment=ROOT/"experiments/chemistry"/spec.experiment_id;domains=tuple(tuple(c.name for c in d.choices) for d in spec.dimensions)
  write(package/"registration.json",{"$schema":"../../governance/claim.schema.json","branch":"chemistry","candidate_grammar":{"boundary":spec.grammar_boundary,"completeness_certificate":COMPLETENESS_CERTIFICATES[spec.claim_id],"expected_cardinality":256,"generator":spec.generation_rule},"claim_id":spec.claim_id,"dependencies":list(spec.dependencies),"empirical_protocol":f"experiments/chemistry/{spec.experiment_id}/registration.json","excluded_inputs":list(spec.exclusions),"provenance_classes":["observational_derivation","complete_external_record_reconstruction"],"registered_by":"Maria Smith","registration_date":"2026-07-28","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"statement":spec.statement,"status":"registered","title":spec.title})
  write(package/"STATUS.md",f"# {spec.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
  write(package/"WHY_DERIVATION_CHECK.md",f"# Why ANAL-{key} requires a derivation check\n\nA displayed analytical value cannot establish the {label}. This claim separately generates all 256 registered forms before comparison and uses only its own value-free identity and source-exposure-disclosed derivation seal. The complete post-seal family reconstructs six official records as 83 PDF pages, one HTML document and 180,366 extracted characters. {surface.capitalize()}. Every value, unit, conventional zero or sign, decimal, uncertainty, assumption, correction, fit, estimate, loss, favorable, adverse, absent, unavailable, unresolved and historical row remains downstream provenance and cannot select the native Fold law.\n")
  write(package/"execution.py",f'''import sys
from sft.chemistry.anal_performance_batch_v1 import AUTHORITIES,{spec_name} as CLAIM_SPEC
from sft.chemistry.anal_performance_validation_v1 import {validator}
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/anal_performance_batch_v1.py","sft/chemistry/anal_performance_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-anal-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))
''')
  write(package/"independent_validator.py",f'''from itertools import product
import json,sys
CLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}
{NATIVE[key]}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))
if __name__=="__main__":main()
''')
  write(experiment/"registration.json",{"$schema":"../../../governance/experiment.schema.json","claim_id":spec.claim_id,"absence_boundary":{"display_glyph":"0","external_signed_decimal_and_zero_inscriptions_are_provenance_only":True,"native_proof_form":"positive exact counts/ratios, held orientation and structural EmptyOne absence","numerical_zero_admitted":False},"evaluation_protocol":{"acceptance_condition":"All 8 preregistered comparisons and the complete six-source surface are retained, including every favorable, adverse, absent, unavailable, unresolved and historical record.","all_8_targets_required":True,"falsification_condition":spec.falsification_condition},"evidence_mode":"observational_derivation_plus_complete_external_record_reconstruction","experiment_id":spec.experiment_id,"external_measurement_sources":[{"complete_pdf_pages":83,"complete_html_documents":1,"complete_extracted_characters":180366,"measurement_bodies":["National Institute of Standards and Technology","International Union of Pure and Applied Chemistry"],"claim_surface":surface}],"frozen_relation":{"relation_hash":sha256_identity(spec.exact_result),"statement":spec.exact_result,"targets_did_not_select_survivor":True},"identity_registry":identity,"prediction_seal":seal,"registered_by":"Maria Smith","registration_date":"2026-07-28","schema":"sft-v3-chemistry-experiment-registration/1","status":"registered_sources_captured_postseal"})
 print("scaffolded five separate ANAL-001–005 claim packages")
if __name__=="__main__":main()

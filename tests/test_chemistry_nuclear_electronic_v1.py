from pathlib import Path
from types import SimpleNamespace
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.nuclear_electronic_batch_v1 import NUCLEAR_ELECTRONIC_SPEC
from sft.chemistry.nuclear_electronic_validation_v1 import NuclearElectronicValidator
from sft.engine.source import build_source_manifest
ROOT=Path(__file__).resolve().parents[1]
def test_candidate_census_and_depth_independent_closure():
 p=GeneratedObservationalChemistryProgram(NUCLEAR_ELECTRONIC_SPEC,build_source_manifest(ROOT,(ROOT/"sft/chemistry/nuclear_electronic_law_v1.py",)).manifest_hash);c=p.generate_candidates();d=tuple(p.decide_candidate(x) for x in c.candidates);e=p.closure_evidence(d);assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and e.scope.value=="depth_independent"
def test_complete_nist_h2_hd_d2_surface():
 r=NuclearElectronicValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:"+"e"*64));assert r.passed and r.all_rows_preserved and len(r.measurements)==433

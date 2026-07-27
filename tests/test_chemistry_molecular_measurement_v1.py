from pathlib import Path
from types import SimpleNamespace
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_measurement_batch_v1 import MOLECULAR_MEASUREMENT_SPEC
from sft.chemistry.molecular_measurement_validation_v1 import MolecularMeasurementValidator
from sft.engine.source import build_source_manifest
ROOT=Path(__file__).resolve().parents[1]
def test_candidate_census_and_depth_independent_closure():
 p=GeneratedObservationalChemistryProgram(MOLECULAR_MEASUREMENT_SPEC,build_source_manifest(ROOT,(ROOT/"sft/chemistry/molecular_measurement_law_v1.py",)).manifest_hash);c=p.generate_candidates();d=tuple(p.decide_candidate(x) for x in c.candidates);e=p.closure_evidence(d);assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and e.scope.value=="depth_independent"
def test_complete_nist_molecular_measurement_package():
 r=MolecularMeasurementValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:"+"c"*64));assert r.passed and r.all_rows_preserved and len(r.measurements)==345

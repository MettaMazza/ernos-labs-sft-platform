import sys
from sft.chemistry.computational_chemistry_batch_v1 import AUTHORITIES,SOURCE_ARTIFACTS,SPECS_BY_NUMBER
from sft.chemistry.computational_chemistry_validation_v1 import ComputationalChemistryValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPECS_BY_NUMBER['009']
def build_execution(root):
 fixed=("sft/chemistry/computational_chemistry_batch_v1.py","sft/chemistry/computational_chemistry_validation_v1.py","sft/chemistry/computational_chemistry_laws_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),*(p for p,_ in SOURCE_ARTIFACTS),"claims/SFT-CHEM-MECHANISM-SEARCH-PROOF-TRACE-009/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-MECHANISM-SEARCH-PROOF-TRACE-009/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-comp-009-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,ComputationalChemistryValidator(root,CLAIM_SPEC))

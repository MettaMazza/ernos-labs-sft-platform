import sys
from sft.chemistry.computational_chemistry_batch_v1 import AUTHORITIES,SOURCE_ARTIFACTS,SPECS_BY_NUMBER
from sft.chemistry.computational_chemistry_validation_v2 import ComputationalChemistryValidatorV2
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPECS_BY_NUMBER['001']
def build_execution(root):
 fixed=("sft/chemistry/computational_chemistry_batch_v1.py","sft/chemistry/computational_chemistry_validation_v1.py","sft/chemistry/computational_chemistry_validation_v2.py","sft/chemistry/computational_chemistry_laws_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),*(p for p,_ in SOURCE_ARTIFACTS),"claims/SFT-CHEM-CANONICAL-MOLECULAR-GRAPH-ENCODING-001/execution_v2.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-CANONICAL-MOLECULAR-GRAPH-ENCODING-001/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-comp-001-independent-python/2",(sys.executable,str(independent)),independent.parent,(independent,)),files,ComputationalChemistryValidatorV2(root,CLAIM_SPEC))

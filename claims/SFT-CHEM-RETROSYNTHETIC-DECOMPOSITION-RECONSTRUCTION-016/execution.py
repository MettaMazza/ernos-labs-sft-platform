import sys
from sft.chemistry.retrosynthetic_reconstruction_batch_v1 import AUTHORITIES,RETROSYNTHESIS_SPEC
from sft.chemistry.retrosynthetic_reconstruction_validation_v1 import RetrosynthesisValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/retrosynthetic_reconstruction_law_v1.py","sft/chemistry/retrosynthetic_reconstruction_batch_v1.py","sft/chemistry/retrosynthetic_reconstruction_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-RETROSYNTHETIC-DECOMPOSITION-RECONSTRUCTION-016/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-RETROSYNTHETIC-DECOMPOSITION-RECONSTRUCTION-016/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(RETROSYNTHESIS_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-retrosynthesis-016-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,RetrosynthesisValidator(root))

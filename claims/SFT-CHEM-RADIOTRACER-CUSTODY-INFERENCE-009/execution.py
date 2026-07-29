import sys
from sft.chemistry.nuchem_terminal_batch_v1 import AUTHORITIES, RADIOTRACER_SPEC as CLAIM_SPEC
from sft.chemistry.nuchem_terminal_validation_v1 import RadiotracerValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/nuchem_terminal_batch_v1.py","sft/chemistry/nuchem_terminal_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-nuchem-009-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,RadiotracerValidator(root))

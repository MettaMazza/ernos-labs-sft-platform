import sys
from sft.chemistry.nmr_family_batch_v1 import AUTHORITIES,SHIFT_SPEC as CLAIM_SPEC
from sft.chemistry.nmr_family_validation_v1 import ShiftValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/nmr_family_batch_v1.py","sft/chemistry/nmr_family_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-NMR-CHEMICAL-SHIFT-006/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-NMR-CHEMICAL-SHIFT-006/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-anal-006-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,ShiftValidator(root))

import sys
from sft.chemistry.protecting_group_reversible_batch_v1 import AUTHORITIES,PROTECTING_GROUP_SPEC
from sft.chemistry.protecting_group_reversible_validation_v1 import ProtectingGroupValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root):
 fixed=("sft/chemistry/protecting_group_reversible_law_v1.py","sft/chemistry/protecting_group_reversible_batch_v1.py","sft/chemistry/protecting_group_reversible_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015/execution.py")
 files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(PROTECTING_GROUP_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-protecting-group-015-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,ProtectingGroupValidator(root))

from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.configuration_order_batch_v1 import CONFIGURATION_ORDER_SPEC
from sft.chemistry.configuration_order_validation_v1 import ConfigurationOrderValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=CONFIGURATION_ORDER_SPEC;files=(root/"sft/chemistry/configuration_order_law_v1.py",root/"sft/chemistry/configuration_order_batch_v1.py",root/"sft/chemistry/configuration_order_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-CONFIGURATION-ORDER-PATH-011/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-CHEM-CONFIGURATION-ORDER-PATH-011/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(s,h),ExternalCommandValidator("sft-chem-configuration-order-path-011-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,ConfigurationOrderValidator(root))

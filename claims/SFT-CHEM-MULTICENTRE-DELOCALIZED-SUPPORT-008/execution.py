from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.multicentre_support_batch_v1 import MULTICENTRE_SUPPORT_SPEC
from sft.chemistry.multicentre_support_validation_v1 import MulticentreSupportValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=MULTICENTRE_SUPPORT_SPEC; files=(root/"sft/chemistry/multicentre_support_law_v1.py",root/"sft/chemistry/multicentre_support_batch_v1.py",root/"sft/chemistry/multicentre_support_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("sft-chem-multicentre-delocalized-support-008-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,MulticentreSupportValidator(root))

from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rovibronic_joint_batch_v1 import ROVIBRONIC_JOINT_SPEC
from sft.chemistry.rovibronic_joint_validation_v1 import RovibronicJointValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=ROVIBRONIC_JOINT_SPEC;files=(root/"sft/chemistry/rovibronic_joint_law_v1.py",root/"sft/chemistry/rovibronic_joint_batch_v1.py",root/"sft/chemistry/rovibronic_joint_validation_v1.py",root/"sft/chemistry/nuclear_electronic_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(s,h),ExternalCommandValidator("sft-chem-resolved-rovibronic-spin-composition-013-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,RovibronicJointValidator(root))

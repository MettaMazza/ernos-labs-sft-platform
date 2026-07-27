"""Official execution binding for SFT-CHEM-REACTION-DYNAMICS-SCATTERING-PRODUCT-STATE-013."""
from pathlib import Path
import sys
from sft.chemistry.reaction_dynamics_scattering_batch_v1 import REACTION_DYNAMICS_SCATTERING_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.reaction_dynamics_scattering_validation_v1 import ReactionDynamicsScatteringValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/reaction_dynamics_scattering_law_v1.py",root/"sft/chemistry/reaction_dynamics_scattering_batch_v1.py",root/"sft/chemistry/reaction_dynamics_scattering_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_reaction_dynamics_scattering_sources_v1.py",root/"tools/register_chemistry_reaction_dynamics_scattering_identities_v1.py",root/"tools/capture_chemistry_reaction_dynamics_scattering_targets_v1.py",root/"tools/build_chemistry_reaction_dynamics_scattering_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/SFT-CHEM-REACTION-DYNAMICS-SCATTERING-PRODUCT-STATE-013/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-REACTION-DYNAMICS-SCATTERING-PRODUCT-STATE-013/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(REACTION_DYNAMICS_SCATTERING_SPEC,source_hash),ExternalCommandValidator("sft-chem-reaction-dynamics-scattering-013-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,ReactionDynamicsScatteringValidator(root))

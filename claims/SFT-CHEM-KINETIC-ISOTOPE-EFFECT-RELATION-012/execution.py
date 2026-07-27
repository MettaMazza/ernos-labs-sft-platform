"""Official execution binding for SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012."""
from pathlib import Path
import sys
from sft.chemistry.kinetic_isotope_effect_batch_v1 import KINETIC_ISOTOPE_EFFECT_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.kinetic_isotope_effect_validation_v1 import KineticIsotopeEffectValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/kinetic_isotope_effect_law_v1.py",root/"sft/chemistry/kinetic_isotope_effect_batch_v1.py",root/"sft/chemistry/kinetic_isotope_effect_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_kinetic_isotope_effect_sources_v1.py",root/"tools/register_chemistry_kinetic_isotope_effect_identities_v1.py",root/"tools/capture_chemistry_kinetic_isotope_effect_targets_v1.py",root/"tools/build_chemistry_kinetic_isotope_effect_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(KINETIC_ISOTOPE_EFFECT_SPEC,source_hash),ExternalCommandValidator("sft-chem-kinetic-isotope-effect-012-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,KineticIsotopeEffectValidator(root))

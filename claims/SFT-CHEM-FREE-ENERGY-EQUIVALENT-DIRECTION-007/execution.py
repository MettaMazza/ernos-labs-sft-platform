"""Official execution binding for SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.free_energy_equivalent_direction_batch_v1 import FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC,SPEC_PATH,NO2_HTML,NO2_TAB,N2O4_HTML,N2O4_TAB,PRIMARY_PATH,IDENTITY_PATH,TARGET_PATH
from sft.chemistry.free_energy_equivalent_direction_validation_v1 import FreeEnergyEquivalentDirectionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.verification import ClaimExecution
def build_execution(root:Path)->ClaimExecution:
    source_files=(root/"sft/chemistry/free_energy_equivalent_direction_law_v1.py",root/"sft/chemistry/free_energy_equivalent_direction_batch_v1.py",root/"sft/chemistry/free_energy_equivalent_direction_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_reaction_direction_sources_v1.py",root/SPEC_PATH,root/NO2_HTML,root/NO2_TAB,root/N2O4_HTML,root/N2O4_TAB,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,root/"claims/SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007/execution.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash;validator=root/"claims/SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007/independent_validator.py"
    return ClaimExecution(program=GeneratedObservationalChemistryProgram(FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC,source_hash),independent_validator=ExternalCommandValidator("sft-chem-free-energy-equivalent-direction-007-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=FreeEnergyEquivalentDirectionValidator(root))

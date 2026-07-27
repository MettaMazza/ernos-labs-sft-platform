"""Official execution binding for INORG-002."""
from pathlib import Path
import sys
from sft.chemistry.coordination_number_batch_v1 import COORDINATION_NUMBER_SPEC,IDENTITY_PATH,INVENTORY_PATH,PRIMARY_PATH,SOURCE_FILES,SPEC_PATH,TARGET_PATH
from sft.chemistry.coordination_number_validation_v1 import CoordinationNumberValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root:Path):
    files=(root/"sft/chemistry/coordination_number_law_v1.py",root/"sft/chemistry/coordination_number_batch_v1.py",root/"sft/chemistry/coordination_number_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_coordination_number_sources_v1.py",root/"tools/register_chemistry_coordination_number_identities_v1.py",root/"tools/build_chemistry_coordination_number_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002/execution.py")
    source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002/independent_validator.py"
    return ClaimExecution(GeneratedObservationalChemistryProgram(COORDINATION_NUMBER_SPEC,source_hash),ExternalCommandValidator("sft-chem-coordination-number-002-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,CoordinationNumberValidator(root))

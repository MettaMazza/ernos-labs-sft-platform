"""Official execution binding for SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010."""
from pathlib import Path
import sys
from sft.chemistry.catalytic_turnover_batch_v1 import CATALYTIC_TURNOVER_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.catalytic_turnover_validation_v1 import CatalyticTurnoverValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/catalytic_turnover_law_v1.py",root/"sft/chemistry/catalytic_turnover_batch_v1.py",root/"sft/chemistry/catalytic_turnover_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_catalytic_turnover_sources_v1.py",root/"tools/register_chemistry_catalytic_turnover_identities_v1.py",root/"tools/capture_chemistry_catalytic_turnover_targets_v1.py",root/"tools/build_chemistry_catalytic_turnover_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(CATALYTIC_TURNOVER_SPEC,source_hash),ExternalCommandValidator("sft-chem-catalytic-turnover-010-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,CatalyticTurnoverValidator(root))

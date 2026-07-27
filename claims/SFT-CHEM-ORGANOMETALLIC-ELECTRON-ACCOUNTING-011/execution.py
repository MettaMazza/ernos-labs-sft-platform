"""Official execution binding for Chemistry INORG-011."""
from pathlib import Path
import json,sys
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.organometallic_electron_accounting_batch_v1 import FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,IDENTITY_PATH,ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC,PRIMARY_PATH,TARGET_PATH
from sft.chemistry.organometallic_electron_accounting_validation_v1 import OrganometallicElectronAccountingValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 identities=json.loads((root/IDENTITY_PATH).read_text()); snapshots=tuple(dict.fromkeys(x["snapshot_path"] for x in identities["rows"])); files=(root/"sft/chemistry/organometallic_electron_accounting_law_v1.py",root/"sft/chemistry/organometallic_electron_accounting_batch_v1.py",root/"sft/chemistry/organometallic_electron_accounting_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/build_chemistry_inorg_010_013_identities_v1.py",root/"tools/build_chemistry_inorg_010_013_primary_v1.py",root/FAMILY_BOUNDARY_PATH,root/FAMILY_REGISTRY_PATH,root/FAMILY_INVENTORY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,root/PRIMARY_PATH,*(root/x for x in snapshots),root/"claims/SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011/execution.py"); files=tuple(dict.fromkeys(files)); h=build_source_manifest(root,files).manifest_hash; v=root/"claims/SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC,h),ExternalCommandValidator("sft-chem-organometallic-electron-account-011-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,OrganometallicElectronAccountingValidator(root))

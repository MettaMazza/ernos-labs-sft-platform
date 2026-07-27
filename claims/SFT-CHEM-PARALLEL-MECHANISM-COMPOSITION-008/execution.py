"""Official execution binding for SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008."""
from pathlib import Path
import sys
from sft.chemistry.parallel_mechanism_batch_v1 import PARALLEL_MECHANISM_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.parallel_mechanism_validation_v1 import ParallelMechanismValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/parallel_mechanism_law_v1.py",root/"sft/chemistry/parallel_mechanism_batch_v1.py",root/"sft/chemistry/parallel_mechanism_validation_v1.py",root/"sft/chemistry/sequential_mechanism_law_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_parallel_mechanism_sources_v1.py",root/"tools/register_chemistry_parallel_mechanism_identities_v1.py",root/"tools/capture_chemistry_parallel_mechanism_targets_v1.py",root/"tools/build_chemistry_parallel_mechanism_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(PARALLEL_MECHANISM_SPEC,source_hash),ExternalCommandValidator("sft-chem-parallel-mechanism-008-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,ParallelMechanismValidator(root))

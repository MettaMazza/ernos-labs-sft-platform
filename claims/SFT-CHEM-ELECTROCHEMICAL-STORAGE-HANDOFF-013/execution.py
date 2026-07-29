import sys

from sft.chemistry.echem_storage_handoff_batch_v1 import AUTHORITIES, STORAGE_SPEC as CLAIM_SPEC
from sft.chemistry.echem_storage_handoff_validation_v1 import StorageHandoffValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root):
    fixed = ("sft/chemistry/echem_storage_handoff_batch_v1.py", "sft/chemistry/echem_storage_handoff_validation_v1.py", "sft/chemistry/generated_law.py", "sft/chemistry/generated_observational_law.py", "sft/physics/generated_empirical_law.py", *(path for path, _ in AUTHORITIES), "claims/SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013/execution.py")
    files = tuple(dict.fromkeys(root / path for path in fixed if (root / path).is_file()))
    independent = root / "claims/SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013/independent_validator.py"
    return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC, build_source_manifest(root, files).manifest_hash), ExternalCommandValidator("sft-chem-echem-013-independent-python/1", (sys.executable, str(independent)), independent.parent, (independent,)), files, StorageHandoffValidator(root))

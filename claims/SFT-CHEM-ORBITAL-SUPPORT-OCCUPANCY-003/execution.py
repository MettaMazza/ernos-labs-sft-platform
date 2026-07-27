"""Official execution binding for SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.orbital_support_batch_v1 import ORBITAL_SUPPORT_SPEC
from sft.chemistry.orbital_support_validation_v1 import OrbitalSupportValidator
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=ORBITAL_SUPPORT_SPEC
    source_files=(root/"sft/chemistry/electron_count_spin_law_v1.py",root/"sft/chemistry/electron_count_spin_validation_v1.py",root/"sft/chemistry/orbital_support_law_v1.py",root/"sft/chemistry/orbital_support_batch_v1.py",root/"sft/chemistry/orbital_support_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003/independent_validator.py"
    return ClaimExecution(GeneratedObservationalChemistryProgram(spec,source_hash),ExternalCommandValidator("sft-chem-orbital-support-occupancy-003-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),source_files,OrbitalSupportValidator(root))

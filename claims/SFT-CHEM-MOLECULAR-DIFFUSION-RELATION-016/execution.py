"""Official execution binding for SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_diffusion_batch_v1 import (
    IDENTITY_PATH, MOLECULAR_DIFFUSION_SPEC, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.molecular_diffusion_validation_v1 import MolecularDiffusionValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_diffusion_law_v1.py",
        root / "sft/chemistry/molecular_diffusion_batch_v1.py",
        root / "sft/chemistry/molecular_diffusion_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_diffusion_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _hash in SOURCE_FILES),
        root / "claims/SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_DIFFUSION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-diffusion-016-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularDiffusionValidator(root),
    )

"""Corrected official execution binding for KIN-011; rejected v1 is preserved."""

from pathlib import Path
import sys

from sft.chemistry.diffusion_limited_reaction_batch_v1 import (
    DIFFUSION_LIMITED_REACTION_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH,
    SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.diffusion_limited_reaction_validation_v1 import DiffusionLimitedReactionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    package = root / "claims/SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011"
    files = (
        root / "sft/chemistry/diffusion_limited_reaction_law_v1.py",
        root / "sft/chemistry/diffusion_limited_reaction_batch_v1.py",
        root / "sft/chemistry/diffusion_limited_reaction_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_diffusion_limited_reaction_sources_v1.py",
        root / "tools/register_chemistry_diffusion_limited_reaction_identities_v1.py",
        root / "tools/capture_chemistry_diffusion_limited_reaction_targets_v1.py",
        root / "tools/build_chemistry_diffusion_limited_reaction_primary_v1.py",
        root / SPEC_PATH,
        root / INVENTORY_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        package / "execution_v2.py",
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = package / "independent_validator_v2.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(DIFFUSION_LIMITED_REACTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-diffusion-limited-reaction-011-independent-python/2",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        files,
        DiffusionLimitedReactionValidator(root),
    )

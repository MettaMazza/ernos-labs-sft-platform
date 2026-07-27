"""Official execution binding for INORG-003."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.ligand_denticity_chelation_batch_v1 import (
    IDENTITY_PATH,
    INVENTORY_PATH,
    LIGAND_DENTICITY_CHELATION_SPEC,
    PRIMARY_PATH,
    SOURCE_FILES,
    SPEC_PATH,
    TARGET_PATH,
)
from sft.chemistry.ligand_denticity_chelation_validation_v1 import LigandDenticityChelationValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    files = (
        root / "sft/chemistry/ligand_denticity_chelation_law_v1.py",
        root / "sft/chemistry/ligand_denticity_chelation_batch_v1.py",
        root / "sft/chemistry/ligand_denticity_chelation_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_ligand_denticity_chelation_sources_v1.py",
        root / "tools/register_chemistry_ligand_denticity_chelation_identities_v1.py",
        root / "tools/build_chemistry_ligand_denticity_chelation_primary_v1.py",
        root / SPEC_PATH,
        root / INVENTORY_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003/execution.py",
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "claims/SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(LIGAND_DENTICITY_CHELATION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-ligand-denticity-chelation-003-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        files,
        LigandDenticityChelationValidator(root),
    )

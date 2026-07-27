"""Official execution binding for SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.formation_energy_batch_v1 import (
    FORMATION_ENERGY_SPEC, LIST_PATH, CHOICE_PATH, RESULT_PATH, REFERENCE_PATH,
    PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.formation_energy_validation_v1 import FormationEnergyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/formation_energy_law_v1.py",
        root / "sft/chemistry/formation_energy_batch_v1.py",
        root / "sft/chemistry/formation_energy_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_formation_energy_sources_v1.py",
        root / LIST_PATH, root / CHOICE_PATH, root / RESULT_PATH, root / REFERENCE_PATH,
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(FORMATION_ENERGY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-formation-energy-013-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=FormationEnergyValidator(root),
    )

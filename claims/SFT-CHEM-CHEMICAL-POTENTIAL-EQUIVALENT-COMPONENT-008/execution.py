"""Official execution binding for SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008."""

from pathlib import Path
import sys

from sft.chemistry.component_exchange_batch_v1 import (
    COMPONENT_EXCHANGE_SPEC,
    IDENTITY_PATH,
    LANDING_PATH,
    PRIMARY_PATH,
    RAW_PATH,
    SPEC_PATH,
    TARGET_PATH,
)
from sft.chemistry.component_exchange_validation_v1 import ComponentExchangeValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/component_exchange_law_v1.py",
        root / "sft/chemistry/component_exchange_batch_v1.py",
        root / "sft/chemistry/component_exchange_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_component_exchange_sources_v1.py",
        root / SPEC_PATH,
        root / RAW_PATH,
        root / LANDING_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / "claims/SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = (
        root
        / "claims/SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008/independent_validator.py"
    )
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(COMPONENT_EXCHANGE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-component-exchange-008-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ComponentExchangeValidator(root),
    )

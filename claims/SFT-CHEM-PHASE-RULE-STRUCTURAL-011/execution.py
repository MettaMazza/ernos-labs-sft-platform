"""Official execution binding for SFT-CHEM-PHASE-RULE-STRUCTURAL-011."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.phase_rule_batch_v1 import (
    IDENTITY_PATH, IUPAC_PATH, NIST_PATH, NIST_TEXT_PATH, PHASE_RULE_SPEC,
    PRIMARY_PATH, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.phase_rule_validation_v1 import PhaseRuleValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/phase_rule_law_v1.py",
        root / "sft/chemistry/phase_rule_batch_v1.py",
        root / "sft/chemistry/phase_rule_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_phase_rule_sources_v2.py",
        root / SPEC_PATH,
        root / "experiments/external_sources/chemistry/phase_rule_capture_spec_v1.json",
        root / "experiments/external_sources/chemistry/phase_rule_capture_spec_v1_halt.json",
        root / IUPAC_PATH,
        root / NIST_PATH,
        root / NIST_TEXT_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / "claims/SFT-CHEM-PHASE-RULE-STRUCTURAL-011/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-PHASE-RULE-STRUCTURAL-011/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(PHASE_RULE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-phase-rule-011-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=PhaseRuleValidator(root),
    )

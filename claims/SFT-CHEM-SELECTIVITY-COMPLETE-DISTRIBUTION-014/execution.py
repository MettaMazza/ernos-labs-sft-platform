from pathlib import Path
import sys

from sft.chemistry.selectivity_distribution_batch_v1 import AUTHORITIES, SELECTIVITY_DISTRIBUTION_SPEC
from sft.chemistry.selectivity_distribution_validation_v1 import SelectivityDistributionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root):
    fixed = (
        "sft/chemistry/selectivity_distribution_law_v1.py", "sft/chemistry/selectivity_distribution_batch_v1.py",
        "sft/chemistry/selectivity_distribution_validation_v1.py", "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py", "sft/physics/generated_empirical_law.py",
        *(path for path, _ in AUTHORITIES), "claims/SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in fixed if (root / path).is_file()))
    independent = root / "claims/SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(SELECTIVITY_DISTRIBUTION_SPEC, build_source_manifest(root, files).manifest_hash),
        ExternalCommandValidator("sft-chem-selectivity-distribution-014-independent-python/1", (sys.executable, str(independent)), independent.parent, (independent,)),
        files, SelectivityDistributionValidator(root),
    )

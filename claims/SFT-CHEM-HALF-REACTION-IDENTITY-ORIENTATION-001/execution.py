import sys
from sft.chemistry.half_reaction_orientation_batch_v1 import AUTHORITIES, HALF_REACTION_SPEC
from sft.chemistry.half_reaction_orientation_validation_v1 import HalfReactionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root):
    fixed = (
        "sft/chemistry/half_reaction_orientation_law_v1.py",
        "sft/chemistry/half_reaction_orientation_batch_v1.py",
        "sft/chemistry/half_reaction_orientation_validation_v1.py",
        "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py",
        "sft/physics/generated_empirical_law.py",
        *(path for path, _ in AUTHORITIES),
        "claims/SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in fixed if (root / path).is_file()))
    independent = root / "claims/SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(HALF_REACTION_SPEC, build_source_manifest(root, files).manifest_hash),
        ExternalCommandValidator(
            "sft-chem-half-reaction-001-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        HalfReactionValidator(root),
    )

from pathlib import Path
import json
import sys

from sft.chemistry.rearrangement_reaction_batch_v1 import (
    ANALYSIS_PATH,
    AUTHORITIES,
    REARRANGEMENT_REACTION_SPEC,
)
from sft.chemistry.rearrangement_reaction_validation_v1 import RearrangementReactionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def _paths(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from _paths(item)
    elif isinstance(value, str) and not value.startswith("sha256:") and "/" in value and len(value) < 512:
        yield Path(value)


def build_execution(root):
    inventory = json.loads((root / AUTHORITIES[10][0]).read_text(encoding="utf-8"))
    referenced = tuple(path for path in _paths(inventory) if (root / path).is_file())
    fixed = (
        "sft/chemistry/addition_reaction_law_v1.py",
        "sft/chemistry/rearrangement_reaction_law_v1.py",
        "sft/chemistry/rearrangement_reaction_batch_v1.py",
        "sft/chemistry/rearrangement_reaction_validation_v1.py",
        "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py",
        "sft/physics/generated_empirical_law.py",
        *(path for path, _ in AUTHORITIES),
        ANALYSIS_PATH,
        "claims/SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in (*fixed, *referenced) if (root / path).is_file()))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(REARRANGEMENT_REACTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-rearrangement-reaction-011-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        RearrangementReactionValidator(root),
    )

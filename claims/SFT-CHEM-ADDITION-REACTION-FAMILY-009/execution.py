from pathlib import Path
import json
import sys

from sft.chemistry.addition_reaction_batch_v3 import (
    ADDITION_REACTION_SPEC,
    COMPARISON_PATH,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    HISTORY_PATHS,
    IDENTITY_PATH,
    INVENTORY_PATH,
    METADATA_PATH,
    PRESEAL_PATH,
    SELECTION_PATH,
    SELECTION_SEAL_PATH,
    TOOL_PATHS,
)
from sft.chemistry.addition_reaction_validation_v3 import AdditionReactionValidator
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
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    referenced = tuple(path for path in _paths(inventory) if (root / path).is_file())
    fixed = (
        "sft/chemistry/addition_reaction_law_v1.py",
        "sft/chemistry/addition_reaction_law_v2.py",
        "sft/chemistry/addition_reaction_law_v3.py",
        "sft/chemistry/addition_reaction_batch_v3.py",
        "sft/chemistry/addition_reaction_validation_v3.py",
        "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py",
        "sft/physics/generated_empirical_law.py",
        FAMILY_BOUNDARY_PATH,
        FAMILY_REGISTRY_PATH,
        FAMILY_INVENTORY_PATH,
        IDENTITY_PATH,
        PRESEAL_PATH,
        METADATA_PATH,
        INVENTORY_PATH,
        SELECTION_PATH,
        SELECTION_SEAL_PATH,
        COMPARISON_PATH,
        *HISTORY_PATHS,
        *TOOL_PATHS,
        "claims/SFT-CHEM-ADDITION-REACTION-FAMILY-009/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in (*fixed, *referenced)))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-ADDITION-REACTION-FAMILY-009/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(ADDITION_REACTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-addition-reaction-009-independent-python/3",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        AdditionReactionValidator(root),
    )

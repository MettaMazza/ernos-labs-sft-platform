from pathlib import Path
import json
import sys

from sft.chemistry.elimination_reaction_batch_v1 import (
    ANALYSIS_PATH,
    CAPTURE_TOOL_PATH,
    ELIMINATION_REACTION_SPEC,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_PATH,
    INVENTORY_PATH,
    IUPAC_PATH,
    PRESEAL_PATH,
)
from sft.chemistry.elimination_reaction_validation_v1 import EliminationReactionValidator
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
        "sft/chemistry/addition_reaction_law_v3.py",
        "sft/chemistry/elimination_reaction_law_v1.py",
        "sft/chemistry/elimination_reaction_batch_v1.py",
        "sft/chemistry/elimination_reaction_validation_v1.py",
        "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py",
        "sft/physics/generated_empirical_law.py",
        FAMILY_BOUNDARY_PATH,
        FAMILY_REGISTRY_PATH,
        FAMILY_INVENTORY_PATH,
        IDENTITY_PATH,
        PRESEAL_PATH,
        INVENTORY_PATH,
        ANALYSIS_PATH,
        IUPAC_PATH,
        CAPTURE_TOOL_PATH,
        "tools/build_chemistry_org_010_external_v1.py",
        "claims/SFT-CHEM-ELIMINATION-REACTION-FAMILY-010/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in (*fixed, *referenced)))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-ELIMINATION-REACTION-FAMILY-010/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(ELIMINATION_REACTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-elimination-reaction-010-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        EliminationReactionValidator(root),
    )

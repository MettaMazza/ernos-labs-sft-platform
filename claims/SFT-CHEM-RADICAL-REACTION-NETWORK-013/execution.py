from pathlib import Path
import json
import sys

from sft.chemistry.radical_reaction_network_batch_v1 import AUTHORITIES, RADICAL_REACTION_NETWORK_SPEC
from sft.chemistry.radical_reaction_network_validation_v1 import RadicalReactionNetworkValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def _paths(value):
    if isinstance(value, dict):
        for item in value.values(): yield from _paths(item)
    elif isinstance(value, list):
        for item in value: yield from _paths(item)
    elif isinstance(value, str) and not value.startswith("sha256:") and "/" in value and len(value) < 512:
        yield Path(value)


def build_execution(root):
    inventory = json.loads((root / AUTHORITIES[5][0]).read_text())
    referenced = tuple(path for path in _paths(inventory) if (root / path).is_file())
    member_root = Path("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/members")
    members = tuple(member_root / row["name"] for row in inventory["archive_members_in_source_order"] if row["member_type"] == "file")
    fixed = (
        "sft/chemistry/addition_reaction_law_v1.py", "sft/chemistry/radical_reaction_network_law_v1.py",
        "sft/chemistry/radical_reaction_network_batch_v1.py", "sft/chemistry/radical_reaction_network_validation_v1.py",
        "sft/chemistry/generated_law.py", "sft/chemistry/generated_observational_law.py",
        "sft/physics/generated_empirical_law.py", *(path for path, _ in AUTHORITIES),
        "claims/SFT-CHEM-RADICAL-REACTION-NETWORK-013/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in (*fixed, *referenced, *members) if (root / path).is_file()))
    independent = root / "claims/SFT-CHEM-RADICAL-REACTION-NETWORK-013/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(RADICAL_REACTION_NETWORK_SPEC, build_source_manifest(root, files).manifest_hash),
        ExternalCommandValidator("sft-chem-radical-network-013-independent-python/1", (sys.executable, str(independent)), independent.parent, (independent,)),
        files, RadicalReactionNetworkValidator(root),
    )

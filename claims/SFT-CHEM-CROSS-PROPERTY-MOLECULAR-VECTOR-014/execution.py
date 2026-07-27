"""Official execution binding for SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.cross_property_batch_v1 import CROSS_PROPERTY_SPEC, MANIFEST_PATH, SUMMARY_PATH, IDENTITY_PATH, TARGET_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.cross_property_validation_v1 import CrossPropertyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    identity_manifest=json.loads((root/MANIFEST_PATH).read_text(encoding="utf-8"))
    target_manifest=json.loads((root/TARGET_PATH).read_text(encoding="utf-8"))
    prior_sources=tuple(root/row["identity_path"] for row in identity_manifest["sources"])+tuple(
        root/row["withheld_target_path"] for row in target_manifest["source_target_files_first_opened_after_identity_seal"]
    )
    source_files=(
        root/"sft/chemistry/cross_property_law_v1.py", root/"sft/chemistry/cross_property_batch_v1.py",
        root/"sft/chemistry/cross_property_validation_v1.py", root/"sft/chemistry/generated_law.py",
        root/"sft/chemistry/generated_observational_law.py", root/"sft/physics/generated_empirical_law.py",
        root/"tools/build_chemistry_cross_property_sources_v1.py", root/MANIFEST_PATH, root/SUMMARY_PATH,
        root/IDENTITY_PATH, root/TARGET_PATH, *prior_sources, root/"claims/SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014/execution.py",
    )
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(CROSS_PROPERTY_SPEC,source_hash),
        independent_validator=ExternalCommandValidator("sft-chem-cross-property-014-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),
        source_files=source_files, empirical_validator=CrossPropertyValidator(root),
    )

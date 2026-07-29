from pathlib import Path
import sys
from sft.astronomy.prior_return_laws_v1 import EMPIRICAL_ID, SPECS, StructuralAstroProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    files = (root / "sft/astronomy/prior_return_laws_v1.py", root / "sft/astronomy/prior_return_execution_v1.py", root / "sft/physics/structural_constants.py", execution_file)
    empirical = None
    if claim_id == EMPIRICAL_ID:
        from sft.astronomy.prior_return_external_v1 import BlindPriorReturnExternalValidator
        files += (root / "sft/astronomy/prior_return_external_v1.py",)
        empirical = BlindPriorReturnExternalValidator(root)
    files += tuple(p for dep in spec.dependencies for p in (root / "claims" / dep / "registration.json", root / "claims" / dep / "certificate.json"))
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/astronomy/prior_return_validator_v1.py"
    independent = ExternalCommandValidator("sft-earth-astro-prior-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(StructuralAstroProgram(spec, source_hash), independent, files, empirical)

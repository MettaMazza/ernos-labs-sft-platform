"""Official execution binding for SFT-CHEM-INTERMOLECULAR-BINDING-011."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.intermolecular_binding_batch_v1 import INTERMOLECULAR_BINDING_SPEC, PRIMARY_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.intermolecular_binding_validation_v1 import IntermolecularBindingValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    dimer_pages = tuple(root / row["snapshot_path"] for row in primary["dimer_pages"])
    source_files = (
        root / "sft/chemistry/intermolecular_binding_law_v1.py",
        root / "sft/chemistry/intermolecular_binding_batch_v1.py",
        root / "sft/chemistry/intermolecular_binding_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_intermolecular_binding_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1/nist-cccbdb-complete-hydrogen-bonded-dimer-list.html',
        *dimer_pages,
        root / 'experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1/nist-water-cluster-dissociation-values-2018.pdf', root / 'experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1/nist-ion-cluster-thermochemistry-complete-1986.pdf',
        root / 'experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1/intermolecular-binding-primary-records-v1.json', root / 'experiments/external_sources/chemistry/intermolecular_binding_target_identities_v1.json', root / 'experiments/external_sources/chemistry/intermolecular_binding_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-INTERMOLECULAR-BINDING-011/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-INTERMOLECULAR-BINDING-011/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(INTERMOLECULAR_BINDING_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-intermolecular-binding-011-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=IntermolecularBindingValidator(root),
    )

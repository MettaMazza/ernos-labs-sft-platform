"""Official execution binding for SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008."""
import json
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_electron_affinity_batch_v1 import MOLECULAR_ELECTRON_AFFINITY_SPEC, PAGE_MANIFEST_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_electron_affinity_validation_v1 import MolecularElectronAffinityValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    page_manifest = json.loads((root / PAGE_MANIFEST_PATH).read_text(encoding="utf-8"))
    source_pages = tuple(root / row["snapshot_path"] for row in page_manifest["pages"])
    source_files = (
        root / "sft/chemistry/molecular_electron_affinity_law_v1.py",
        root / "sft/chemistry/molecular_electron_affinity_batch_v1.py",
        root / "sft/chemistry/molecular_electron_affinity_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_electron_affinity_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/nist-cccbdb-electron-affinity-catalog.html', root / 'experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/nist-webbook-gas-phase-ion-thermochemistry.html', root / 'experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/molecular-electron-affinity-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/molecular_electron_affinity_target_identities_v1.json', root / 'experiments/external_sources/chemistry/molecular_electron_affinity_withheld_targets_v1.json', root / 'experiments/external_sources/chemistry/molecular_electron_affinity_source_page_manifest_v1.json',
        root / "claims/SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008/execution.py",
    ) + source_pages
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_ELECTRON_AFFINITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-electron-affinity-008-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularElectronAffinityValidator(root),
    )

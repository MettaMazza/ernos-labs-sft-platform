"""Official execution binding for SFT-CHEM-BOND-DISSOCIATION-ENERGY-002."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.bond_dissociation_energy_batch_v1 import BOND_DISSOCIATION_ENERGY_SPEC, GeneratedFiniteDissociationChemistryProgram
from sft.chemistry.bond_dissociation_energy_validation_v1 import BondDissociationEnergyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/bond_dissociation_energy_law_v1.py",
        root / "sft/chemistry/bond_dissociation_energy_batch_v1.py",
        root / "sft/chemistry/bond_dissociation_energy_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/prior_value_laws.py",
        root / "tools/capture_chemistry_bond_dissociation_energy_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-002-atomic-1s-2s-primary-records-v1.json', root / 'experiments/external_sources/chemistry/snapshots/aps-hydrogen-dissociation-1994.json', root / 'experiments/external_sources/chemistry/snapshots/prop-002-current-dissociation-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/bond_dissociation_energy_target_identities_v1.json', root / 'experiments/external_sources/chemistry/bond_dissociation_energy_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-BOND-DISSOCIATION-ENERGY-002/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-BOND-DISSOCIATION-ENERGY-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteDissociationChemistryProgram(BOND_DISSOCIATION_ENERGY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-bond-dissociation-energy-002-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=BondDissociationEnergyValidator(root),
    )

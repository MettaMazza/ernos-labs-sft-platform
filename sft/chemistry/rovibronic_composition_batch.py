"""Chemistry specification for exact nuclear/electronic and rovibronic composition."""

from __future__ import annotations

from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.rovibronic_composition_derivation import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file
from sft.physics.molecular_spectroscopy_successor_validation_v1 import MEASURED_LABEL


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = "experiments/external_sources/physics/snapshots/molecular-spectroscopy-successor-source-record.json"
SOURCE_HASH = "sha256:211fb30414204bcc61f9fb4a69a451db24cb5d5aaaacb2bb3b85fc83429388a9"

if hash_file(ROOT / SOURCE_PATH) != SOURCE_HASH:
    raise ValueError("registered H2/D2 molecular spectroscopy record changed")


ROVIBRONIC_COMPOSITION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ROVIBRONIC-COMPOSITION-001",
    title="Exact nuclear-electronic, vibronic and rovibronic state composition",
    statement=(
        "An exact molecular rovibronic state is the complete finite joint carrier of one admitted molecular "
        "electronic state, every retained nuclear occurrence and isotope label, positive vibrational and rotational "
        "recurrence coordinates, one held spin state and one declared observation record. The admitted electronic-"
        "over-vibrational-over-rotational hierarchy distinguishes the coordinates without importing a separation "
        "approximation; the H2/D2 isotope transport and resolved rotational/vibrational relations remain the exact "
        "measured consequence supplied by the admitted Physics dependency."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal eight-axis product of carrier, nuclear-electronic composition, scale order, "
        "vibrational recurrence, rotational recurrence, held spin, observation and extension forms; decide every "
        "form by preservation of the admitted dependency chain."
    ),
    grammar_boundary=(
        "Every positive-finite molecular electronic carrier with positive-finite retained nuclei, isotope labels, "
        "positive vibration and rotation ordinals, held spin and a declared finite observation resolution."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One electronic carrier, one retained nuclear support, the first positive vibrational and rotational "
        "ordinals, one held spin label and one readout record form the least complete joint molecular state."
    ),
    induction_step=(
        "Adjoining one nuclear occurrence or one positive recurrence ordinal preserves all prior coordinates and "
        "forces exactly its new isotope, recurrence and observation distinction; no measured scalar or new rule is introduced."
    ),
    exclusions=(
        "no source value, NIST inscription or comparison interval in candidate generation or survivor selection",
        "no imported wavefunction, Hamiltonian, Born-Oppenheimer approximation, continuum surface or rigid-rotor premise",
        "no numerical-zero state, negative, irrational, imaginary or floating proof value",
        "no fitted molecular constant, isotope factor, species exception or target-derived parameter",
        "no absolute bond length, frequency or rotational constant claimed by this compositional prerequisite",
        "all earlier Physics and Chemistry receipts remain immutable and separately owned",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ROVIBRONIC-COMPOSITION-001",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ChemistryTargetReference(
            target_id="NIST-MOLECULAR-H2-D2-COMPLETE-VECTOR",
            source_id="NIST-MOLECULAR-SPECTROSCOPY-H2-D2-SUCCESSOR",
            source_locator="NIST Chemistry WebBook SRD 69 H2 and D2 X 1Sigma_g+ ground-state omega_e, omega_e*x_e, B_e and r_e rows",
            snapshot_path=SOURCE_PATH,
            snapshot_hash=SOURCE_HASH,
        ),
    ),
    observation_registry_path=SOURCE_PATH,
    falsification_condition=(
        "The claim fails if any retained nucleus, isotope, electronic, vibrational, rotational, spin or observation "
        "coordinate can be erased without merging a registered state; if the exact admitted H2/D2 ladder or isotope "
        "relations leave the complete NIST displayed-resolution vector; if a source is opened before the prediction "
        "seal; or if any favorable, unfavorable, predecessor or tampered row is omitted."
    ),
)

ROVIBRONIC_COMPOSITION_SPEC.validate()


__all__ = ("ROVIBRONIC_COMPOSITION_SPEC", "SOURCE_HASH", "SOURCE_PATH")

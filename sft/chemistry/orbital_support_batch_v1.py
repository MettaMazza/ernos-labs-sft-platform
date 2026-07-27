"""Registered ELEC-003 molecular support-composition specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.orbital_support_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_REGISTRY_PATH = "experiments/external_sources/chemistry/orbital_support_target_identities_v1.json"
IDENTITY_REGISTRY_HASH = "sha256:9e3a77634e9871ecd6716cf40face2bfad6a39b3b7720afbb33468a9e27b1fdc"
TARGET_REGISTRY_PATH = "experiments/external_sources/chemistry/orbital_support_withheld_targets_v1.json"
TARGET_REGISTRY_HASH = "sha256:6f3773b443f9376bc4eee04c99cc35f49515684c8e418df46106ca846ac7095d"
ELECTRON_INPUT_PATH = "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
ELECTRON_INPUT_HASH = "sha256:9972d91da982bdae04b8a19e6eeb2c6d22e145b5597e0ca6ba613bae0150b54b"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025"


for _path, _identity in (
    (IDENTITY_REGISTRY_PATH, IDENTITY_REGISTRY_HASH),
    (TARGET_REGISTRY_PATH, TARGET_REGISTRY_HASH),
    (ELECTRON_INPUT_PATH, ELECTRON_INPUT_HASH),
):
    if hash_file(ROOT / _path) != _identity:
        raise ValueError(f"registered ELEC-003 artifact changed: {_path}")


_identities = json.loads((ROOT / IDENTITY_REGISTRY_PATH).read_text(encoding="utf-8"))
if _identities.get("schema") != "sft-v3-orbital-support-target-identities/1" or len(_identities.get("rows", ())) != 360:
    raise ValueError("ELEC-003 target identity registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=SOURCE_ID,
        source_locator=str(row["source_url"]) + f" :: diatomic state row {row['state_row_ordinal']}",
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identities["rows"]
)


ORBITAL_SUPPORT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    title="Fold-native molecular support composition and fermionic occupancy",
    statement=(
        "A molecular electronic support cell is a molecule-bound composition of positive radial recurrence, "
        "structural empty-One or positive axis recurrence, one of two held joining phases and applicable held symmetry "
        "observations. Its fermionic occupancy is structural empty One, one held electron occurrence or one "
        "complementary-spin pair, and the complete occupied support partitions every molecular electron occurrence "
        "exactly once."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal Cartesian product of carrier, joining, axis organization, held symmetry, occupancy, "
        "spin, completeness and extension forms. Decide all 256 forms only by admitted molecular composition, exact "
        "recurrence, two-fibre, spin, indistinguishability, exclusion, electron-count and information-retention laws."
    ),
    grammar_boundary=(
        "Every positive finite molecular carrier; every positive radial recurrence; the structural axis-invariant "
        "boundary and every positive axis recurrence; both held joining phases; applicable held exchange/reflection "
        "labels; and every positive finite electron support. Closure is depth-independent because each newly generated "
        "cell and occurrence repeats the same coordinate-identity, occupancy, complementary-spin and complete-partition checks."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One molecular carrier and one positive radial support at the axis-invariant boundary generate the two joining "
        "phase fibres. One electron occurrence occupies one phase/spatial cell with one held spin fibre."
    ),
    induction_step=(
        "Advancing radial or axis recurrence creates a new exact support coordinate; adjoining its complementary "
        "joining phase completes the two-fibre pair; adjoining a second electron requires the complementary spin; "
        "adjoining another occupied cell retains each new occurrence once and preserves the complete electron census."
    ),
    exclusions=(
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no continuum angular coordinate or imported molecular wavefunction",
        "no conventional sigma/pi/delta/phi symbol in candidate generation or survivor selection",
        "no imported molecular-orbital energy ordering or species configuration table",
        "no occupancy above one complementary spin pair in a spatial support cell",
        "no measured NIST state or configuration assignment before prediction seal",
        "no fitted, learned, species-specific or target-derived parameter",
        "no selected, omitted or silently normalized spectroscopic assignment row",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    expected_observation_label="fold-native-support-occupancy-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_REGISTRY_PATH,
    falsification_condition=(
        "The claim fails if a joined molecular support lacks one of the two phase fibres; if a required axis class "
        "cannot be represented by structural empty One or positive recurrence; if a spatial cell admits a third "
        "electron or same-spin pair; if complete occupied support loses or duplicates an electron occurrence; if any "
        "of the 360 registered NIST state rows or 362 term assignments leaves the generated axis-support grammar; if "
        "any of the 87 explicit spectroscopic configuration assignments leaves the occupancy grammar; if a measured "
        "state multiplicity violates the ELEC-002 electron-count parity law; or if any source, row or adverse control is altered."
    ),
)


ORBITAL_SUPPORT_SPEC.validate()


__all__ = (
    "ELECTRON_INPUT_HASH",
    "ELECTRON_INPUT_PATH",
    "IDENTITY_REGISTRY_HASH",
    "IDENTITY_REGISTRY_PATH",
    "ORBITAL_SUPPORT_SPEC",
    "SOURCE_ID",
    "TARGET_REFERENCES",
    "TARGET_REGISTRY_HASH",
    "TARGET_REGISTRY_PATH",
)

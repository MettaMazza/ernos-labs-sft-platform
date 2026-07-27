"""Registered THERMO-016 law and complete binary/self/tracer diffusion surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.molecular_diffusion_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-016-molecular-diffusion-v1"
SPEC_PATH = "experiments/external_sources/chemistry/molecular_diffusion_capture_spec_v1.json"
SPEC_HASH = "sha256:2e6bfea67b91d063ff050104232e3985942ede546f6698750b3ab3abd7a6c397"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/molecular-diffusion-primary-records-v1.json"
PRIMARY_HASH = "sha256:cb806a34d7b156bdf563531be4f18afb0ce8add91d1aa7379c9e200d5e5bf245"
IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_diffusion_target_identities_v1.json"
IDENTITY_HASH = "sha256:bf6ff47b2681d29543df8c77db765b60b5d1bf9e86ff44011f100464ffcb5147"
TARGET_PATH = "experiments/external_sources/chemistry/molecular_diffusion_withheld_targets_v1.json"
TARGET_HASH = "sha256:a27bc3e17bd894c06dd946ec2eb757c0f227c1b5f9a42f11008056f71a787eb3"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2011-56-4840-4848.json", "sha256:41316f4f631f83a8a026c9352219560c50003c78f5fe1d6e7e20b0d8cd1bf5c0"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2011-56-4840-4848.html", "sha256:e0a4280a5126e875507c98f2326c3e2d7a9e9d7ae83972f23756bb6e3eb9770d"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2017-437-34-42.json", "sha256:3a9761de05acfefc97d0fdd39e7d9d2071d392c1e47ba224b75d72e766814296"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2017-437-34-42.html", "sha256:d3deb7187c92094bf75f9811a5d3acea283f84060fa875c88b7c3ec431139423"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2008-271-43-52.json", "sha256:783229adc9ce9ce003681fbc518c61afdb5919b5cbb4b6a37c9fba4ea925c333"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2008-271-43-52.html", "sha256:c1f56606c8a6c1f3531e2bdbd2a92d3c8a127f2278da05f042a46b0ee93b208d"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-016 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 3
    or _primary.get("complete_dataset_count_across_sources") != 30
    or _primary.get("complete_all_property_point_count_across_sources") != 373
    or _primary.get("complete_target_count") != 164
    or _primary.get("diffusion_class_counts") != {"binary": 138, "self": 4, "tracer": 22}
    or _identities.get("complete_target_count") != 164
    or _identities.get("diffusion_class_counts") != {"binary": 138, "self": 4, "tracer": 22}
    or _identities.get("all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 164
):
    raise ValueError("THERMO-016 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"POMD {row['dataset_ordinal']} point {row['source_point_ordinal']} ({row['diffusion_class']})",
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


MOLECULAR_DIFFUSION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016",
    title="Exact counted molecular-diffusion law",
    statement=(
        "Molecular diffusion is counted adjacent-cell redistribution of a retained molecular identity within a complete "
        "constituent, phase, condition, time and spatial carrier. Binary, self and tracer observations share this relation. "
        "Measured diffusion magnitude is exact positive post-seal support; no stochastic premise, continuum field, Fick law, "
        "Brownian/random-walk model, Stokes-Einstein relation, activation fit or transport coefficient is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, identity, adjacency, conservation, resource, magnitude, prediction and "
        "extension forms; decide all 256 candidates only from admitted identity, adjacency, state-transition, resource, "
        "conservation, structural absence and finite-successor laws."
    ),
    grammar_boundary=(
        "Every finite binary, self or tracer diffusion record with complete constituent identities, held phase, exact "
        "conditions, counted adjacent cells, transitions and ticks. External testing preserves every direct diffusion point "
        "from three complete NIST sources and every non-diffusion companion dataset as excluded provenance."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One retained migrating identity, one complete constituent carrier, two adjacent generated cells, one counted "
        "transition, one counted tick and one exact condition form the least molecular-diffusion record."
    ),
    induction_step=(
        "Appending a complete transition or measurement record preserves every earlier identity and condition; common "
        "positive replication of transition and tick counts preserves exact density and held orientation without refitting."
    ),
    exclusions=(
        "no numerical zero; absent external condition coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Fick equation, Brownian continuum, random-walk probability, Stokes-Einstein relation or fitted activation/transport coefficient",
        "no interpolation, regression, fit, selected species/medium/phase/condition/method/dataset/row or target correction",
        "no species, medium, phase, composition, temperature, pressure, method, value, uncertainty or target hash before prediction seal",
        "every complete source and non-diffusion companion dataset remains preserved; companions never become diffusion measurements",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-DIFFUSION-RELATION-016",
    expected_observation_label="complete-binary-self-tracer-diffusion-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any migrating or medium identity, phase, condition, cell, transition or tick is erased; if "
        "adjacency or constituent conservation fails; if a random premise, signed/numerical-zero proof value, continuum, "
        "Fick/Brownian/random-walk/Stokes-Einstein model, activation/transport fit, interpolation, regression, selection or "
        "target correction enters; if target content opens before all 164 identities seal; if any direct binary, self or "
        "tracer row, uncertainty, method, dataset, complete source or companion provenance is omitted; or if any target is tampered."
    ),
)
MOLECULAR_DIFFUSION_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "MOLECULAR_DIFFUSION_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)

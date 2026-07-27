"""Registered THERMO-017 law and complete pure/binary/ternary viscosity surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.viscous_transport_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-017-viscous-transport-v1"
SPEC_PATH = "experiments/external_sources/chemistry/viscous_transport_capture_spec_v1.json"
SPEC_HASH = "sha256:4f104a72d58f72540f07fdd73ce993945cedd35dc6f638bb647d4195cb1dfc50"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/viscous-transport-primary-records-v1.json"
PRIMARY_HASH = "sha256:15cdede034228b66f80fc93db2d15b0945691a37ad769f828b2b1122c3400262"
IDENTITY_PATH = "experiments/external_sources/chemistry/viscous_transport_target_identities_v1.json"
IDENTITY_HASH = "sha256:d72d566d09ff74c4259059317e10c36819eb51adb4f0e00b7bb5c4dc1262ab0d"
TARGET_PATH = "experiments/external_sources/chemistry/viscous_transport_withheld_targets_v1.json"
TARGET_HASH = "sha256:c451fa8de56e8aaded861be2a61c2c1ec9316291926cb6c67cdd5434a69691a4"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2018-474-6-13.json", "sha256:789d33700a7663a67907e758bc1313c0ff9cee20fafd68333e66165067778571"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2018-474-6-13.html", "sha256:44c0d340796c4477e27e386a85ecd5ce41dc4ae092953924d9d7985aa5a00d43"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2005-50-1038-1042.json", "sha256:6fc99d3da6684956bdeb368b879f8d74cc09a6950ede5a624ba9333d3589d6ec"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2005-50-1038-1042.html", "sha256:5f7a9d2a4c7875becd64488117ec66e1ebd67760efc50ad4a9a42ab7a4e1675a"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2017-453-13-23.json", "sha256:5af0da5ce4afc3dccf6f836f3e0010edf82620d0d0ec9220ff8b7f9d1bcb2e8a"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2017-453-13-23.html", "sha256:c8360ae629ebdebf8a62df9164feba8f4e6132d846093c2c5574c6a011ecbeb2"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-017 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text()); _identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 3 or _primary.get("complete_dataset_count_across_sources") != 17
    or _primary.get("complete_all_property_point_count_across_sources") != 900
    or _primary.get("complete_target_count") != 425
    or _primary.get("mixture_class_counts") != {"pure": 11, "binary": 364, "ternary": 50}
    or _identities.get("complete_target_count") != 425
    or _identities.get("mixture_class_counts") != {"pure": 11, "binary": 364, "ternary": 50}
    or _identities.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 425
):
    raise ValueError("THERMO-017 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"POMD {row['dataset_ordinal']} point {row['source_point_ordinal']} (viscosity)",
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    ) for row in _identities["rows"]
)


VISCOUS_TRANSPORT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017", title="Exact composition-bound viscous transport law",
    statement=(
        "Chemical viscosity is counted adjacent-layer momentum-packet exchange whose carrier retains every component, "
        "phase, condition and time/space resource. Chemistry owns the composition-bound relation while the momentum carrier "
        "is inherited explicitly from Physics. Measured viscosity is exact positive post-seal support; no continuum velocity "
        "gradient, Newtonian constitutive equation, Arrhenius/WLF/VFT form, logarithm or fitted coefficient is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, identity, transfer, orientation, resource, magnitude, prediction and extension forms; decide all 256 candidates only from admitted momentum, adjacency, transition, conservation, exact-resource, composition, EmptyOne and finite-successor laws.",
    grammar_boundary="Every finite pure, binary or ternary viscosity record with complete component identities, phase, exact conditions, counted adjacent layers, momentum packets, exchanges and ticks. External testing preserves all 425 direct viscosity points and all companion datasets from three complete NIST sources.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="One complete component carrier, one phase, two adjacent layers, one momentum packet, one exchange, one tick and one exact condition form the least viscous chemical record.",
    induction_step="Appending one complete component, exchange or measurement record preserves all earlier distinctions; common exchange/tick replication preserves exact density and held direction without refitting.",
    exclusions=(
        "no numerical zero; absent external condition coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Newtonian constitutive equation, continuum velocity gradient, Arrhenius, WLF, VFT or fitted viscosity law",
        "no interpolation, regression, selected substance/mixture/phase/condition/method/dataset/row or target correction",
        "no substance, composition, phase, temperature, pressure, method, value, uncertainty or target hash before prediction seal",
        "every complete source and non-viscosity companion dataset remains preserved; companions never become viscosity measurements",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-VISCOUS-TRANSPORT-RELATION-017",
    expected_observation_label="complete-pure-binary-ternary-viscosity-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any component, phase, condition, layer, momentum packet, exchange or tick is erased; if adjacency "
        "or momentum conservation fails; if signed/numerical-zero proof value, continuum velocity gradient, Newtonian, "
        "Arrhenius/WLF/VFT form, fit, logarithm, interpolation, regression, selection or target correction enters; if target "
        "content opens before all 425 identities seal; if any direct viscosity row, uncertainty, method, dataset, complete "
        "source or companion provenance is omitted; or if any target is tampered."
    ),
)
VISCOUS_TRANSPORT_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES", "VISCOUS_TRANSPORT_SPEC",
)

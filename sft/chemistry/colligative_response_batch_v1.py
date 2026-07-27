"""Registered THERMO-014 law and complete boiling/freezing/osmotic surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.colligative_response_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-014-colligative-response-v1"
SPEC_PATH = "experiments/external_sources/chemistry/colligative_response_capture_spec_v1.json"
SPEC_HASH = "sha256:f4b45418ce4fd5b961e457c8ac7ce9d9bbc001bbacfb11a9d0c61395f945e0c5"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/colligative-response-primary-records-v1.json"
PRIMARY_HASH = "sha256:c5291e5cc0a9ef4911c4bd00833184325e3f7ec325664fa6a00751c6e9f1f7d6"
IDENTITY_PATH = "experiments/external_sources/chemistry/colligative_response_target_identities_v1.json"
IDENTITY_HASH = "sha256:2303d467bfe09cddfce8092c9fd90cf8837ea7f7259dfcbfd82d19f202487635"
TARGET_PATH = "experiments/external_sources/chemistry/colligative_response_withheld_targets_v1.json"
TARGET_HASH = "sha256:9b50fb6cf8344faf08d1e608078414ab86b936652a06b0de0c4172ee6151e336"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2013-337-60-66.json", "sha256:a541f0712463b973f1bca0ffbdb41bd071082970b1b9cb09993255750c4ff541"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2013-337-60-66.html", "sha256:dc5bc2ea536d68f5d16cf06235800146dbe90e6d6665d8b14a09ee3ec8b6b3a9"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2016-420-14-19.json", "sha256:ea32fea454422d7534e9083a79b6d80d7e7aee92a2ca948f41828f65b347f49b"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2016-420-14-19.html", "sha256:c0f7c4f54da84d16b85a2a643928d745abb10f63329029f1cc38267719231787"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2009-41-1439-1445.json", "sha256:7be6731063d2903fb14b391bb2caf825c099b28791de4d7035ee8439795fd3c1"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2009-41-1439-1445.html", "sha256:a2e207dd6b491af37d66e45876657a2aaf36bb06502184b1a3b8fd3c01908eaf"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-014 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 3
    or _primary.get("complete_compound_record_count_across_sources") != 19
    or _primary.get("complete_dataset_count") != 28
    or _primary.get("complete_point_count") != 276
    or _primary.get("response_class_counts") != {"boiling": 144, "freezing": 37, "osmotic": 95}
    or _identities.get("complete_target_count") != 276
    or _identities.get("response_class_counts") != {"boiling": 144, "freezing": 37, "osmotic": 95}
    or _identities.get("all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 276
):
    raise ValueError("THERMO-014 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"POMD {row['dataset_ordinal']} point {row['source_point_ordinal']} ({row['response_class']})",
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


COLLIGATIVE_RESPONSE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014",
    title="Exact colligative composition-response law",
    statement=(
        "A colligative response is the exact held relation produced when a distinct solute particle identity is "
        "retained while solvent exchange remains the transmitted carrier. Solute retention forces a held boiling, "
        "freezing or osmotic orientation; measured magnitude is an exact positive reference-response separation "
        "opened only after the law seals. Pure solvent uses structural EmptyOne. No conventional response equation, "
        "constant, dissociation factor, continuum, regression or fit enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, identity, boundary, direction, magnitude, absence, prediction "
        "and extension forms; decide all 256 candidates only from admitted particle distinction, component exchange, "
        "phase balance, exact order, EmptyOne and finite successor laws."
    ),
    grammar_boundary=(
        "Every finite positive boiling, freezing or osmotic record with distinct held solvent/solute identities, an "
        "exact composition coordinate or EmptyOne reference, exact positive environment and response support, and a "
        "declared solvent-transmission/solute-retention boundary. External testing preserves all 16 boiling datasets "
        "and 144 rows, six freezing datasets and 37 rows, six osmotic datasets and 95 rows, and all three complete sources."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One solvent identity, one distinct solute identity, one exact positive composition, one generated response "
        "boundary and one exact positive environment form the least colligative response record."
    ),
    induction_step=(
        "Appending any complete response record preserves the finite vector; common positive replication of particle "
        "and response supports preserves the held orientation without refitting."
    ),
    exclusions=(
        "no numerical zero; absent solute composition is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported van't Hoff factor, dissociation parameter, Raoult law, boiling/freezing constant or osmotic equation",
        "no molality/molarity response equation, interpolation, regression, fit, selected system/row or target correction",
        "no compound, solvent, solute, phase, temperature, pressure, composition, response, uncertainty or target hash before prediction seal",
        "every source decimal remains a post-seal external inscription and every source row remains preserved",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014",
    expected_observation_label="complete-boiling-freezing-osmotic-response-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if solvent or solute identity is erased or duplicated; if the boundary does not retain solute "
        "while transmitting solvent exchange; if boiling, freezing or osmotic orientation requires signed magnitude; "
        "if pure solvent is represented by numerical zero; if any conventional colligative equation, constant, factor, "
        "continuum, interpolation, regression, fit, selection or target correction enters; if targets open before all "
        "276 identities seal; if any of 144 boiling, 37 freezing or 95 osmotic records, any uncertainty, method, compound, "
        "dataset or complete source is omitted; or if any measured coordinate or response is tampered."
    ),
)
COLLIGATIVE_RESPONSE_SPEC.validate()


__all__ = (
    "COLLIGATIVE_RESPONSE_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)

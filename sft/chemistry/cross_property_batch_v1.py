"""Registered complete cross-property molecular vector for Chemistry PROP-014."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.cross_property_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/prop-014-cross-property-v1"
MANIFEST_PATH = f"{SNAPSHOT_ROOT}/cross-property-source-manifest-v1.json"
MANIFEST_HASH = "sha256:a516de625e47d6274375ee7481c3cd2692912d02ba441857f2b22462ce129608"
SUMMARY_PATH = f"{SNAPSHOT_ROOT}/cross-property-overlap-summary-v1.json"
SUMMARY_HASH = "sha256:d8dd86e21952813e6fc2dd412b4bea94f03baa09df2850046eb458ea3c540d40"
IDENTITY_PATH = "experiments/external_sources/chemistry/cross_property_target_identities_v1.json"
IDENTITY_HASH = "sha256:723b5edee82d4de38eb177345483e0b1ea74f58d9728dc3f7a6f74b28a616fcd"
TARGET_PATH = "experiments/external_sources/chemistry/cross_property_withheld_targets_v1.json"
TARGET_HASH = "sha256:f4a266604115883a3b93b82021ce85f993139d920b68a3fe3d8172c3e6e47e6d"


for _path, _hash in ((MANIFEST_PATH, MANIFEST_HASH), (SUMMARY_PATH, SUMMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-014 registered source changed: {_path}")


_manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
_summary = json.loads((ROOT / SUMMARY_PATH).read_text(encoding="utf-8"))
_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_forbidden = {"source_target_payload", "source_target_payload_hash", "withheld_target_hash", "source_value_inscription", "native_value", "measurement_present", "external_measurement_absence"}
if (
    _manifest.get("schema") != "sft-v3-cross-property-source-manifest/1"
    or _manifest.get("identity_seal_before_target_open") != IDENTITY_HASH
    or len(_manifest.get("sources", ())) != 13
    or any(row.get("withheld_target_hash_absent_until_identity_seal") is not True or "withheld_target_hash" in row for row in _manifest["sources"])
    or _summary.get("complete_source_identity_row_count") != 9025
    or _summary.get("complete_structural_carrier_count") != 1104
    or _summary.get("multi_property_structural_carrier_count") != 676
    or _summary.get("multi_property_source_row_count") != 6676
    or _summary.get("maximum_property_family_count_on_one_carrier") != 8
    or _identities.get("schema") != "sft-v3-cross-property-identities/1"
    or _identities.get("complete_property_family_count") != 13
    or _identities.get("complete_source_identity_row_count") != 9025
    or _identities.get("all_target_values_presence_flags_and_source_orientations_absent") is not True
    or len(_identities.get("rows", ())) != 9025
    or any(row.get("target_value_presence_and_orientation_absent") is not True or _forbidden.intersection(row) for row in _identities["rows"])
    or _targets.get("schema") != "sft-v3-cross-property-withheld-targets/1"
    or _targets.get("identity_seal") != IDENTITY_HASH
    or _targets.get("complete_target_row_count") != 9025
    or len(_targets.get("source_target_files_first_opened_after_identity_seal", ())) != 13
    or len(_targets.get("rows", ())) != 9025
):
    raise ValueError("PROP-014 complete cross-property source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["cross_property_target_id"]),
        source_id="SFT-V3-ADMITTED-" + str(row["property_family"]),
        source_locator=f"{row['source_identity_path']} :: {row['source_target_id']}",
        snapshot_path=TARGET_PATH,
        snapshot_hash=TARGET_HASH,
    )
    for row in _identities["rows"]
)


CROSS_PROPERTY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014",
    title="Complete zero-parameter cross-property molecular vector",
    statement=(
        "One complete retained structural molecular carrier supplies every applicable property projection through "
        "the already admitted PROP-001 through PROP-013 relations. Each result remains attached to its named "
        "generating law and no property receives a fitted coefficient or target-derived carrier. All 9,025 source "
        "identities across all 13 property families seal before withheld target payloads or hashes open; 676 exact "
        "carriers support multiple property families and retain all 6,676 overlapping rows."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, support, projection, parameter, absence, prediction, record and "
        "extension forms; decide all 256 candidates from admitted property relations, exact compositional laws and "
        "the complete value-free cross-property identity surface."
    ),
    grammar_boundary=(
        "The depth-independent append-only projection law for every finite exact structural carrier, tested against "
        "all 9,025 registered PROP-001 through PROP-013 source rows, all 1,104 carriers, all 676 multi-property "
        "carriers, all 6,676 overlap rows and every explicit nonjoined or bound-composite custody row."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One completely retained structural carrier with one applicable admitted property relation forces one exact "
        "named projection without a fitted coefficient."
    ),
    induction_step=(
        "Appending one new applicable admitted property relation extends the vector by one named projection and "
        "leaves every existing projection exactly unchanged."
    ),
    exclusions=(
        "no numerical zero; absent or inapplicable native results remain structural EmptyOne",
        "no negative, irrational, imaginary, floating or continuum SFT proof value",
        "no target payload, target hash, presence flag or source orientation before the complete identity seal",
        "no per-property fit, correction, residual, coefficient or target-derived structural field",
        "no selected species, showcase molecule, favorable property family or agreeing-row subset",
        "no guessed synonym, formula, species join or conflation of a bound composite with a constituent molecule",
        "no deletion of single-property, nonjoinable, absent, adverse or bound-composite custody rows",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014",
    expected_observation_label="complete-named-projection-vector-from-one-structural-carrier-without-per-property-fit",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if one property requires a separately fitted carrier or coefficient; if adding a lawful "
        "property changes any existing projection; if any of 13 families, 9,025 rows, 1,104 carriers, 676 overlap "
        "carriers or 6,676 overlap rows is omitted; if a nonjoinable row is guessed into a species group; if a "
        "target payload or hash opens before the complete identity seal; or if any favorable subset replaces the "
        "complete source custody surface."
    ),
)
CROSS_PROPERTY_SPEC.validate()


__all__ = (
    "CROSS_PROPERTY_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "MANIFEST_HASH", "MANIFEST_PATH",
    "SUMMARY_HASH", "SUMMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)

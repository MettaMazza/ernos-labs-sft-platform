"""Registered INORG-006 law and complete sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.ligand_state_splitting_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/ligand_state_splitting_law_v1.py"
LAW_HASH = "sha256:b1d1350aff301a5cb2e58471e00021897dedc3a771660f574dbbe54ef8038079"
ADDENDUM_FILES = (
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v1.json", "sha256:7c3e63016b4f52a0cf2a84b8076ac954ba61649580d2459ed826e40a5aff0693"),
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v2.json", "sha256:fa25c3d9d170254de760bc3778af9dd89793b902729ca0314bc0ececa08ff7e8"),
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v3.json", "sha256:eeca900246f02c7b8d32fa77e5060adbc1033f99dbe2df103c4d8f4d2cb0c17b"),
)
INVENTORY_FILES = (
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v1/source-inventory-v1.json", "sha256:d76d5b6a898ce98a45c97ea936a5fe7902356701474f54ca6443b752f124d1f2"),
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v2/source-inventory-v1.json", "sha256:d9d0e0255439404dcb82a4b585de24d4b6fafbc51d3ae64f2c893985a30fc752"),
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v3/source-inventory-v1.json", "sha256:fe95562bfb5e930c37b17a9fd9ee25d17031c36c7ee9b7949441a533f17acc7b"),
)
IDENTITY_PATH = "experiments/external_sources/chemistry/ligand_state_splitting_target_identities_v1.json"
IDENTITY_HASH = "sha256:70188a12aa368cf39624142b408b4895f933a194dced0ff99b6a984a2cef19c3"
TARGET_PATH = "experiments/external_sources/chemistry/ligand_state_splitting_withheld_targets_v1.json"
TARGET_HASH = "sha256:2a843c7924c4f332c60c72dbb6338f9284fff6674d5f1ad76619388218c0d554"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v3/ligand-state-splitting-primary-records-v1.json"
PRIMARY_HASH = "sha256:35c1680746e462bbfcee6f960ffdb4adfe5bcb7e814b4c029d04154bd19b70f4"
IUPAC_FILES = (
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-lt06764.json", "sha256:dad6da4049a23236e040e7219d1d81d8730e732a72ac63e05da91d3bad410155"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-l03517.json", "sha256:9ad080420481e49ee9e66b397b7eddc83398087877f9016eae0d9a287ae6aab8"),
)


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    *ADDENDUM_FILES,
    *INVENTORY_FILES,
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    *IUPAC_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-006 registered authority changed: {path}")


_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_rows = tuple(_identities.get("rows", ()))
if (
    _identities.get("complete_registered_target_count") != 32
    or _identities.get("target_values_peak_positions_intensities_band_counts_definitions_and_outcomes_present") is not False
    or _identities.get("all_family_development_adverse_absent_blind_and_ancillary_rows_registered") is not True
    or len(_rows) != 32
    or tuple(row["source_record_ordinal"] for row in _rows) != tuple(range(1, 33))
):
    raise ValueError("INORG-006 value-free target identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        f"{row['authority']}::{row['source_id']}::{row['source_record_role']}::{row['custody_class']}",
        f"{row['source_id']} :: {row['source_record_role']} :: {row['custody_class']}",
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _rows
)


LIGAND_STATE_SPLITTING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-LIGAND-STATE-SPLITTING-006",
    title="Exact ligand-incidence state partition and balanced splitting",
    statement="The forced three-direction carrier and rank-two boundary generate exactly five second-rank state supports: two independent held axis contrasts and three complete boundary pairs. Attaching a complete finite ligand geometry assigns each support its exact XOR or joint-boundary incidence signature; equal signatures remain one level and unequal signatures split. Six direct-axis occurrences force positive multiplicities three and two, exact normalized structural separation two-thirds, and complementary balance distances two-fifths and three-fifths. Four complete-axis occurrences reverse the multiplicities to two and three with unit structural separation and balance distances three-fifths and two-fifths. Removing the interaction restores one five-member class.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the complete literal product of carrier, interaction, partition, multiplicity, separation, balance, observation and extension choices; decide all 256 candidates solely from admitted exact arithmetic, generator-three, space-rank, boundary-rank, state-equivalence, geometry and prior INORG receipts.",
    grammar_boundary="Every finite three-axis ligand word formed only from the two forced Fold fibres and structural EmptyOne; the complete two-contrast plus three-boundary-pair state support; every exact interaction-signature partition; all thirty-two registered definition, development, ancillary, adverse absence and law-sealed blind spectrum surfaces.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="Before attachment, structural EmptyOne interaction leaves all five generated supports in one complete equivalence class. For the first positive ligand occurrence, each support receives exactly its XOR or joint-boundary incidence and no member is created, lost or duplicated.",
    induction_step="Appending the next distinct ligand word preserves every prior incidence and adds exactly one incidence decision to every support. Equality classes are refined only when the new decision distinguishes members; all five members remain exactly once, every new separation is a positive exact excess over complete ligand count, and removing every distinguishing occurrence remerges the class.",
    exclusions=(
        "no numerical zero; external glyph 0 is only a source inscription and native absence is structural EmptyOne",
        "no negative irrational imaginary floating signed continuum or opposite-signed displacement in a proof object",
        "no imported d-orbital, crystal-field, ligand-field, point-group, geometry or spectrochemical table in the law or survivor decision",
        "no free field strength, fitted splitting parameter, dimensional wavelength anchor, selected peak, smoothing threshold or target-derived tolerance",
        "no deletion of the twelve ancillary development captures, two law-sealed absent spectra, boundary maxima, adverse rows or unresolved dimensional correspondence",
        "no claim that the exact structural separation is an absolute wavelength; the external vector tests distinguishable spectral support after seal",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-LIGAND-STATE-SPLITTING-006",
    expected_observation_label="complete-ligand-state-partition-and-sealed-spectral-distinguishability-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if generator three and boundary rank two do not generate exactly five supports; if any ligand word, support, incidence or partition block is omitted; if equal signatures split or unequal signatures merge; if member multiplicity is not conserved; if the six-direct-axis and four-complete-axis partitions, exact separations or complementary balance identities fail; if numerical zero, a third fibre, signed displacement, field parameter, orbital table, selected peak, smoothing or fitted tolerance enters forcing; if any of thirty-two source surfaces is removed; if either adverse spectrum absence or ancillary capture is hidden; or if the law-sealed blind spectrum lacks the preregistered positive distinguishability condition.",
)
LIGAND_STATE_SPLITTING_SPEC.validate()


__all__ = (
    "ADDENDUM_FILES", "IDENTITY_HASH", "IDENTITY_PATH", "INVENTORY_FILES", "IUPAC_FILES",
    "LIGAND_STATE_SPLITTING_SPEC", "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES",
)

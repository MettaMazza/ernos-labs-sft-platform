"""Registered ELEC-008 multicentre and delocalized-support specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.multicentre_support_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/multicentre_target_identities_v1.json"
IDENTITY_HASH = "sha256:c77b359440bb7f44259974e34ce23b13de0ff2057f4c859c9015a27f033958c4"
TARGET_PATH = "experiments/external_sources/chemistry/multicentre_withheld_targets_v1.json"
TARGET_HASH = "sha256:d3188205f896f7ad4719a25d2367bbc98d262c7c66424a02c05ae5dec863c445"
SOURCE_IDS = ("IUPAC-GOLD-BOOK-08789-2026", "NIST-CCCBDB-SRD101-DIBORANE", "NIST-CCCBDB-SRD101-BENZENE")


for path, expected in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError("ELEC-008 registered source changed: " + path)
document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if document.get("schema") != "sft-v3-multicentre-identities/1" or len(document.get("rows", ())) != 20:
    raise ValueError("ELEC-008 identity registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(str(row["target_id"]), str(row["source_id"]), str(row["source_url"]) + " :: " + str(row["record_role"]), str(row["snapshot_path"]), str(row["snapshot_hash"]))
    for row in document["rows"]
)


MULTICENTRE_SUPPORT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
    title="Connected multicentre and delocalized molecular support",
    statement="A delocalized molecular electron support is one retained Fold word spanning every centre of a connected generated graph. At three or more centres it is not reducible to one localized two-centre support without losing the complete support identity. Path, cycle and polyhedral incidence force ribbon, surface and volume forms without an imported bonding model.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of molecular carrier, centre count, electron support, connection, topology, reduction, external record and extension forms. Decide all 256 forms solely by admitted Fold graph, joint-support, exchange and exclusion laws.",
    grammar_boundary="Every positive finite connected molecular support containing at least three retained centres, with post-seal testing against all four IUPAC delocalization records, all nine NIST neutral-diborane geometry/bond-count records and all seven NIST benzene geometry/bond-count records.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="Three distinct centres joined as one path force the first support word that spans more than one localized pair.",
    induction_step="Appending one centre by at least one generated edge preserves connectedness and the single complete support word; closing an endpoint pair yields a cycle and adding an independent branch yields a polyhedral volume without an extra law.",
    exclusions=("no numerical zero; glyph 0 denotes source/interface absence only", "no negative, irrational, imaginary, floating, signed-amplitude or continuum proof magnitude", "no imported valence-bond, molecular-orbital, aromaticity, resonance, Wade, Hückel or two-centre bonding model", "no measured NIST geometry, IUPAC example or species name before prediction seal", "no fitted bond length, angle, order, topology or species correction", "no selected-source or selected-row validation"),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
    expected_observation_label="connected-multicentre-delocalized-support-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if the complete support is disconnected; if fewer than three centres are relabelled multicentre; if a one-pair support retains the same complete identity as a support spanning three or more centres; if path, cycle or polyhedral incidence requires an imported chemical model; if the measured B-H-B bridge or equal six-link benzene cycle is absent; if any of four IUPAC, nine diborane or seven benzene registered rows is omitted or changed; or if an absence glyph is treated as an SFT number.",
)


MULTICENTRE_SUPPORT_SPEC.validate()


__all__ = ("IDENTITY_HASH", "IDENTITY_PATH", "MULTICENTRE_SUPPORT_SPEC", "SOURCE_IDS", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES")

"""Registered ELEC-012 nuclear-electronic composition specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.nuclear_electronic_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/nuclear_electronic_target_identities_v1.json"
IDENTITY_HASH = "sha256:316d3d94aa9a82a529c574e6029a9c05c5f3814683478bd184205e0b21806680"
TARGET_PATH = "experiments/external_sources/chemistry/nuclear_electronic_withheld_targets_v1.json"
TARGET_HASH = "sha256:b8a3cb16b0fbdc53a01846492e71b38585d0a7c5336b755f3f9ea21ba48d7421"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-HD-D2-DIATOMIC-CONSTANTS-2026"
for path, expected in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError("ELEC-012 registered source changed: " + path)
document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if document.get("schema") != "sft-v3-nuclear-electronic-identities/1" or len(document.get("rows", ())) != 95:
    raise ValueError("ELEC-012 identity registry is incomplete")
TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        str(row["target_id"]), SOURCE_ID,
        str(row["source_url"]) + " :: complete state row " + str(row["state_row_ordinal"]),
        str(row["snapshot_path"]), str(row["snapshot_hash"]),
    ) for row in document["rows"]
)


NUCLEAR_ELECTRONIC_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    title="Exact nuclear-electronic joint composition and isotopologue scale-separation law",
    statement="A molecular isotopologue is one retained joint carrier whose nuclear occurrences and isotope labels compose with, but do not erase, its electronic support and state. Their distinct exact coordinate families force lawful scale separation without a continuum approximation or fitted separation parameter; equal-electronic-support isotopologues transport distinct exact vibronic records while every absence remains structural EmptyOne and every external signed inscription remains held provenance.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, nuclear, electronic, composition, scale, transport, absence and record forms. Decide all 256 only from admitted exact composition, isotope, electronic-state and configuration laws.",
    grammar_boundary="Every positive finite nuclear occurrence word jointly composed with one admitted molecular electronic state; externally tested against every state and cell in the complete NIST H2, HD and D2 diatomic tables.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="One molecular carrier with one positive nuclear occurrence requires one retained isotope label and one retained electronic support/state pair; neither factor can identify the joint state after the other is erased.",
    induction_step="Appending one nuclear occurrence with its held isotope label extends only the nuclear factor of the finite joint product; the electronic factor, coordinate-family partition, existing records and absence boundary remain unchanged.",
    exclusions=("no numerical zero; source glyph 0 denotes structural EmptyOne only", "no negative, irrational, imaginary, floating, signed or continuum proof magnitude", "no Born-Oppenheimer, continuum potential, differential equation, fitted mass, fitted scale or isotope coefficient", "no NIST molecular weights, state cells or isotopologue outcomes before prediction seal", "no common-state-only or favorable-value-only subset"),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    expected_observation_label="complete-H2-HD-D2-nuclear-electronic-vibronic-correspondence",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition="Reject if any molecular carrier, nuclear occurrence, isotope label, electronic support, electronic state or source record is erased; if a continuum or fitted scale selects the law; if any of 95 NIST state rows or 1,235 cells is omitted or changed; if H2, HD and D2 fail distinct exact nuclear support and ordered positive molecular-weight inscriptions; if any of 330 jointly reported positive vibronic coordinate pairs fails isotope-labelled distinction; if any of 450 blank cells or three source-zero inscriptions becomes a number; if any of eight external negative inscriptions is consumed as an SFT proof value; or if target content enters before sealing.",
)
NUCLEAR_ELECTRONIC_SPEC.validate()


__all__ = ("IDENTITY_HASH", "IDENTITY_PATH", "NUCLEAR_ELECTRONIC_SPEC", "SOURCE_ID", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES")

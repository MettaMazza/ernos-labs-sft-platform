"""Registered ELEC-006 molecular exclusion and exchange specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.pair_exchange_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/pair_exchange_target_identities_v1.json"
IDENTITY_HASH = "sha256:3b108e98b7060047bd3e7a1e24cfb474579a5d5a235c2a4b76096ef8c1280574"
TARGET_PATH = "experiments/external_sources/chemistry/pair_exchange_withheld_targets_v1.json"
TARGET_HASH = "sha256:204dd9ddc92ae70ab9b89461bd4d86b59bb90ac87add8af34fcbf1dfb906d085"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-EXCHANGE-2025"


for path, expected_hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError("ELEC-006 registered source changed: " + path)
identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if identity_document.get("schema") != "sft-v3-pair-exchange-identities/1" or len(identity_document.get("rows", ())) != 60:
    raise ValueError("ELEC-006 identity registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        str(row["target_id"]),
        SOURCE_ID,
        str(row["source_url"])
        + (
            f" :: state row {row['state_row_ordinal']}"
            if row["target_type"] == "state-exchange-assignment"
            else f" :: exchange pair rows {row['singlet_state_row_ordinal']} and {row['triplet_state_row_ordinal']}"
        ),
        str(row["snapshot_path"]),
        str(row["snapshot_hash"]),
    )
    for row in identity_document["rows"]
)


PAIR_EXCHANGE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006",
    title="Molecular exclusion and complementary electron-pair exchange organization",
    statement=(
        "For every identical two-electron molecular pair, the total exchange word is alternating. The complete "
        "two-label spin census forces a positive One-width alternating spin sector with preserving spatial support "
        "and a positive three-width preserving spin sector with alternating spatial support. Same-cell pairing is "
        "admitted only in the preserving spatial sector; the complementary sectors remain distinct on the same "
        "orbital support. No signed, negative, imaginary, continuum or numerical-zero proof value is used."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, constituent identity, total exchange, spin sector, complementary "
        "composition, same-cell support, complete record and extension forms. Decide all 256 forms solely by the "
        "admitted Fold indistinguishability, exclusion, spin-census, orbital-support and state-symmetry laws."
    ),
    grammar_boundary=(
        "Every molecular carrier containing an identical electron pair; both complete two-label spin-composition "
        "sectors; every retained spatial support and pairwise successor in a larger molecule. External closure uses "
        "the complete 46-state NIST molecular-hydrogen term census, both explicit same-cell pair records and all "
        "14 same-configuration singlet/triplet observation pairs."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two identical electrons generate four complete held spin words: one alternating word and three preserving "
        "words. Alternating total exchange therefore leaves exactly the complementary spatial fibre for each sector."
    ),
    induction_step=(
        "Adding a molecular support or another identical-electron pair retains every prior exchange word and applies "
        "the same two-fibre product locally; preserving spatial support may retain the paired cell, alternating "
        "spatial support may not, and no third exchange class is generated."
    ),
    exclusions=(
        "no numerical zero; glyph 0 denotes source/interface absence only",
        "no negative, irrational, imaginary, floating, signed-wavefunction or continuum proof magnitude",
        "no imported Pauli sign rule, antisymmetrized orbital equation, exchange integral or Hund ordering premise",
        "no measured NIST multiplicity, occupancy, energy order or separation before prediction seal",
        "no asserted energy-order sign or fitted exchange splitting",
        "no named-electron distinction, species exception, selected state or omitted unfavorable pair",
        "source energy inscription 0 remains an absence-baseline record and never becomes an SFT number",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006",
    expected_observation_label="complete-molecular-pair-exchange-organization",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a molecular electron pair is not exchange-equivalent; if its total exchange is not "
        "alternating; if a positive One-width spin sector is not paired with preserving spatial exchange; if a "
        "positive three-width spin sector is not paired with alternating spatial exchange; if a same-cell pair is "
        "accepted in the alternating spatial sector; if any of 46 NIST H2 states, 25 singlets, 21 triplets, two "
        "explicit same-cell singlet records, 14 same-configuration exchange pairs, 13 triplet-below-singlet records "
        "or the one retained opposite-order record is omitted or altered; if any positive measured separation is "
        "replaced by a fitted value; or if source glyph 0 is treated as a number rather than absence."
    ),
)


PAIR_EXCHANGE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PAIR_EXCHANGE_SPEC",
    "SOURCE_ID",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)

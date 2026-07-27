"""Registered ELEC-007 joint molecular correlation specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.joint_correlation_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/joint_correlation_target_identities_v1.json"
IDENTITY_HASH = "sha256:52c9f872da74817277f48aacaa8536b3dbf972f9cbee8b6d05bf96aa0e181c31"
TARGET_PATH = "experiments/external_sources/chemistry/joint_correlation_withheld_targets_v1.json"
TARGET_HASH = "sha256:f7043a52c1c2bd95fc49ab2457f9ab64ad6879e8c835e2fc818dadcd0cbced5c"
SOURCE_IDS = (
    "APS-PRA-49-2460-1994",
    "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-DISSOCIATION",
)


for path, expected_hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError("ELEC-007 registered source changed: " + path)
identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if identity_document.get("schema") != "sft-v3-joint-correlation-identities/1" or len(identity_document.get("rows", ())) != 9:
    raise ValueError("ELEC-007 identity registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        str(row["target_id"]),
        str(row["source_id"]),
        str(row["source_url"])
        + (
            f" :: record {row['record_ordinal']}"
            if "record_ordinal" in row
            else f" :: source note {row['note_id']}"
        ),
        str(row["snapshot_path"]),
        str(row["snapshot_hash"]),
    )
    for row in identity_document["rows"]
)


JOINT_CORRELATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-JOINT-CORRELATION-DISSOCIATION-007",
    title="Nonfactorizable molecular joint support and dissociation correspondence",
    statement=(
        "Electron correlation is the retained exact joint-support distinction not reconstructible from independent "
        "one-carrier marginals. At a two-centre dissociation boundary, the complete indistinguishable-pair support "
        "contains both complementary cross-centre assignments, excludes both same-centre Cartesian words, and "
        "retains the bound carrier, separated product identities and transition trace. No fitted correction "
        "coefficient, signed amplitude, numerical zero or imported correlation functional enters the law."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, support, relation, exchange, transition, energy, record and "
        "extension forms. Decide all 256 forms solely by admitted indistinguishability, exclusion, joint-state, "
        "molecular-support, state-order and exchange laws."
    ),
    grammar_boundary=(
        "Every identical molecular electron pair at a two-centre separated-product boundary and every pairwise "
        "successor in a larger finite support graph. External closure uses all nine pre-registered APS and NIST "
        "hydrogen/deuterium neutral, ionic, ground-state, excited-state and threshold dissociation records."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two held electron fibres and two separated product centres generate four marginal Cartesian words; "
        "exchange and same-cell exclusion retain exactly the two complementary cross-centre words."
    ),
    induction_step=(
        "Adding a pair or centre preserves every existing joint word and appends the complete exchange-lawful "
        "cross-centre assignments. The construction uses a finite support census rather than an adjustable weight "
        "or correction coefficient."
    ),
    exclusions=(
        "no numerical zero; glyph 0 denotes source/interface absence only",
        "no negative, irrational, imaginary, floating, signed-amplitude or continuum proof magnitude",
        "no Hartree-Fock, configuration-interaction, coupled-cluster, density-functional or correlation-energy formula imported as a premise",
        "no fitted correlation coefficient, empirical functional, basis correction or dissociation-energy parameter",
        "no APS or NIST target value, uncertainty, isotope trend or ionic value before prediction seal",
        "no single-product factorization presented as complete joint support",
        "no omission of direct, compiled, derived-ion, older-reference or uncertainty records",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-JOINT-CORRELATION-DISSOCIATION-007",
    expected_observation_label="complete-joint-support-dissociation-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if independent marginals reconstruct the exact joint support; if either complementary "
        "cross-centre word is missing; if either same-centre Cartesian word is admitted; if constituent names, "
        "fitted coefficients or imported correlation models select the support; if the bound-to-separated trace "
        "loses carrier or product identity; if any of nine APS/NIST records, six APS values, three NIST values, "
        "seven direct measured/compiled records, two explicitly derived ionic records, every uncertainty or exact "
        "positive inscription is omitted or changed; or if any source absence glyph is treated as an SFT number."
    ),
)


JOINT_CORRELATION_SPEC.validate()


__all__ = (
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "JOINT_CORRELATION_SPEC",
    "SOURCE_IDS",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)

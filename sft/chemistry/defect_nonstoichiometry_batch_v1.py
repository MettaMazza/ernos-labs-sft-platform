"""Registered INORG-016 law and versioned complete authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.defect_nonstoichiometry_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/defect_nonstoichiometry_law_v1.py"
LAW_HASH = "sha256:89485a387bf7a993c6a5f395300a2ae5edfd10d60c963d653e5633550be3a40c"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorg_016_target_identities_v1.json"
IDENTITY_HASH = "sha256:f2f97dc76295f1007d6cc6868080129839ff0e1b9d5e3f0b757092e0086f3328"
V1_TARGET_PATH = "experiments/external_sources/chemistry/inorg_016_withheld_targets_v1.json"
V1_TARGET_HASH = "sha256:c170a932926c96fb479ae43777663db2e865a3e64f83ff4cb28c5ce4a667c3cd"
V1_PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-016-primary-records-v1.json"
V1_PRIMARY_HASH = "sha256:ecec2d5bc15b307013c8a53b805dd373abb9cc6016b6b30c5c4d542acaf3cdba"
TARGET_PATH = "experiments/external_sources/chemistry/inorg_016_withheld_targets_v2.json"
TARGET_HASH = "sha256:79176a9fb158fefd1f66f22773f72df98c6a07947f90107db8abb8a7f961e80b"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-016-primary-records-v2.json"
PRIMARY_HASH = "sha256:962d67de394c6ff524ad027b1d7d685c3b00541440100024459e8bb5cd10c042"

for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (V1_TARGET_PATH, V1_TARGET_HASH),
    (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"INORG-016 authority changed: {path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 15
    or _identity_document.get(
        "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 15
):
    raise ValueError("INORG-016 identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        "::".join(
            (
                row["authority"],
                row["source_id"],
                row["source_record_role"],
                row["custody_class"],
            )
        ),
        row["registered_identity"],
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identity_rows
)

DEFECT_NONSTOICHIOMETRY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-DEFECT-NONSTOICHIOMETRY-016",
    title="Exact defect chemistry and non-stoichiometry law",
    statement=(
        "A local solid defect is the exact interruption between one complete reference-site "
        "motif and one complete observed motif. A vacancy is a retained reference site with "
        "structural EmptyOne occupancy. Missing and added species are separate positive supports, "
        "never a signed difference; their primitive count vectors force exact reference and "
        "observed formulas, defect class and intrinsic/extrinsic origin."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, reference, vacancy, difference, class, "
        "composition, origin and extension alternatives; decide all 256 forms from admitted "
        "exact arithmetic, discrete support, stoichiometry and local-solid coordination."
    ),
    grammar_boundary=(
        "Every finite complete reference-site and observed local motif with explicit vacancy, "
        "substitution and interstitial supports, exact positive reconciliation and primitive "
        "formulas; all fifteen frozen solid-solution, lattice-defect, noncrystal-scope, extrinsic "
        "and intrinsic-defect surfaces including two definition-note surfaces."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "A positive finite reference motif and its complete occupancy record uniquely distinguish "
        "an occupied site from a retained site with structural EmptyOne."
    ),
    induction_step=(
        "Appending one fresh reference site, occupied occurrence or interstitial occurrence "
        "preserves all earlier records and recomputes separate positive missing and added supports "
        "under the same occurrence reconciliation."
    ),
    exclusions=(
        "no numerical zero; a vacancy is structural EmptyOne at a retained site",
        "no negative irrational imaginary signed continuum fitted free or imported parameter",
        "no signed stoichiometric subtraction or fitted non-stoichiometric variable",
        "no defect catalogue selected in place of complete local support",
        "no external dimensional zero inscription used as native arithmetic",
        "no source definition, note, example or identity redirect used to select the law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-DEFECT-NONSTOICHIOMETRY-016",
    expected_observation_label="complete-defect-and-nonstoichiometry-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a site or occurrence is omitted, if vacancy is numerical zero, if "
        "missing and added support is signed or fitted, if primitive formulas or defect/origin "
        "classes do not reconstruct, if either V1 missing note surface is hidden, if the V1 "
        "predecessor is overwritten, if either scope mismatch is concealed, if any of fifteen "
        "rows is removed, or if outcomes open before sealing."
    ),
)
DEFECT_NONSTOICHIOMETRY_SPEC.validate()

__all__ = (
    "DEFECT_NONSTOICHIOMETRY_SPEC",
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
    "V1_PRIMARY_HASH",
    "V1_PRIMARY_PATH",
    "V1_TARGET_HASH",
    "V1_TARGET_PATH",
)

"""Registered INORG-005 law and complete authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.coordination_isomerism_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_005_linkage_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:980b2752e4617f217b145a491a786baa035d18170db88dbdd6c75783b068a6ba"
ADDENDUM_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/source-inventory-v1.json"
ADDENDUM_INVENTORY_HASH = "sha256:9b647ea38a27cc5484b50fc0af2dbdca8798facc7eed0f093305c4733c787a53"
PRELIMINARY_IDENTITY_PATH = "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v1.json"
PRELIMINARY_IDENTITY_HASH = "sha256:7f5508970550449115ceb997b6e3d340a3bba3c27878bd83b2ea98b6892b5290"
IDENTITY_PATH = "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v2.json"
IDENTITY_HASH = "sha256:7264542ef42da0fab309f6fd94cc1d7560202767417784bd8b92a1744957bd95"
TARGET_PATH = "experiments/external_sources/chemistry/coordination_isomerism_withheld_targets_v1.json"
TARGET_HASH = "sha256:6a36cc12e39bd64feb4961f3f2e137f940bb833cb5f878406a4eeecc709829c2"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/coordination-isomerism-primary-records-v1.json"
PRIMARY_HASH = "sha256:399785a3d0401f2c2d65295c29d3a153f334648d01b6ad8f84183c5d76bbb751"

SOURCE_FILES = (
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-i03294.json", "sha256:32ea1e227a6ce189a09d759909248c367b075c76ac3759fa77497f114ce9c8b9"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-g02620.json", "sha256:796412f38c7b2bd8a48fa24bcc6f522643acba4565d7943f7c1ba4ae997c7f05"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-o04308.json", "sha256:ac846f06d05251b9463aaa2d80d2c6b64b1128bbb6f242918837f16a16da1702"),
    ("experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/iupac-red-book-2005-complete.pdf", "sha256:3595c86a1b288b82be6d74061315592b89fe3eb17ffa80bb3df3e970e622890f"),
)

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (ADDENDUM_PATH, ADDENDUM_HASH),
    (ADDENDUM_INVENTORY_PATH, ADDENDUM_INVENTORY_HASH),
    (PRELIMINARY_IDENTITY_PATH, PRELIMINARY_IDENTITY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-005 registered authority changed: {path}")

_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identities.get("complete_registered_target_count") != 17
    or _identities.get("target_values_or_payload_hashes_present") is not False
):
    raise ValueError("INORG-005 identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        f"{row['authority']}::{row['source_id']}::{row['source_record_role']}",
        f"{row['source_locator']} :: {row['source_record_role']}",
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identities["rows"]
)

COORDINATION_ISOMERISM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005",
    title="Exact coordination-form equivalence and native isomer distinction classes",
    statement="For two positive finite complete coordination forms of the same retained composition, exact equivalence holds exactly when an exhaustively generated occurrence bijection preserves every composition label, attachment mode, boundary adjacency and three-axis word made only from the two forced Fold fibres and structural EmptyOne. A first attachment or graph failure forces an attachment-class distinction; an exact global fibre complement forces a mirror-complement distinction; every remaining held orientation or adjacency failure forces an orientation-adjacency distinction. No conventional isomer catalogue selects these classes.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, composition, bijection, graph, orientation, native-class, observation and successor forms; decide all 256 candidates solely from admitted finite-form, exact-combinatorial, graph, information-retention, stereochemical and INORG-004 geometry dependencies.",
    grammar_boundary="Every pair of positive finite complete coordination forms with the same complete composition multiset, every occurrence permutation, every retained attachment and adjacency, every three-axis word using only fibre-one, fibre-two or structural EmptyOne, the generated global fibre complement, all seventeen sealed IUPAC surfaces, both preserved Gold Book identity redirects and the explicitly absent literal linkage term.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="For one retained occurrence there is exactly one occurrence bijection. Exact equivalence therefore reduces to equality of its complete composition, attachment and three-axis two-fibre word; a complement-related word remains separately identifiable and no absent relation is represented by numerical zero.",
    induction_step="Adjoining the next occurrence preserves every prior composition label, attachment, word and adjacency as an induced subform. The complete mapping census extends by placing the new occurrence at each positive image ordinal and retains every prior mapping among the remaining occurrences; no prior relation is erased, and only the new occurrence and its generated adjacencies are added.",
    exclusions=(
        "no numerical zero; the glyph 0 in an external inscription is not an SFT number and native absence is structural EmptyOne",
        "no negative irrational imaginary floating signed or continuum proof value or transformation",
        "no third fibre label; the three generated axes are positions containing only the two forced fibre labels or EmptyOne",
        "no imported linkage, geometric, optical, cis-trans, enantiomer, diastereomer, point-group or shape catalogue in candidate forcing",
        "no selected occurrence map, favourable source row, deleted redirect, hidden absent term, fitted class or target-derived condition",
        "no silent claim that the literal phrase linkage isomer occurs in the captured Red Book when the complete extracted document does not contain it",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005",
    expected_observation_label="complete-coordination-form-equivalence-and-native-isomer-class-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if any occurrence, attachment, adjacency, orientation cell or occurrence bijection is omitted; if a third fibre or numerical zero enters a proof object; if different composition is admitted as an isomer pair; if a selected mapping, imported isomer name or continuum transform chooses equivalence; if linkage, geometric or mirror classes are asserted without their forced failed invariant; if a successor erases a prior relation; if any of seventeen source surfaces, either redirected presented identity or the explicit literal-term absence is omitted or altered; or if any source outcome enters the candidate generator or eliminator.",
)
COORDINATION_ISOMERISM_SPEC.validate()


__all__ = (
    "ADDENDUM_HASH",
    "ADDENDUM_INVENTORY_HASH",
    "COORDINATION_ISOMERISM_SPEC",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRELIMINARY_IDENTITY_HASH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "SOURCE_FILES",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)

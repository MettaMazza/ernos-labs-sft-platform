"""Registered KIN-013 law and complete state-resolved reaction-dynamics source surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.reaction_dynamics_scattering_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-013-reaction-dynamics-scattering-v1"
SPEC_PATH = "experiments/external_sources/chemistry/reaction_dynamics_scattering_capture_spec_v1.json"
SPEC_HASH = "sha256:322156cd58ad49e84dc23db779e9a64c83bfb63646048d7e0b9eb59ae75077e9"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:9b5de6c728811033d8214e90a33d6366e2985fdfa970f0684082d5ae533aac4f"
IDENTITY_PATH = "experiments/external_sources/chemistry/reaction_dynamics_scattering_target_identities_v1.json"
IDENTITY_HASH = "sha256:24ef82847fe2b0c1695d4790507f34b5bb5ef05b93b9c762e0b751d3813b61da"
TARGET_PATH = "experiments/external_sources/chemistry/reaction_dynamics_scattering_withheld_targets_v1.json"
TARGET_HASH = "sha256:c5750aa621918e16c76e4610ddfab4e1e88dcbf3da6c5b24fc34cc9ee0890374"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/reaction-dynamics-scattering-primary-records-v1.json"
PRIMARY_HASH = "sha256:0d59248920520f9f99d0c498df137476afc89876bc89fdd102fa36c769ea0a89"

SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/article.html", "sha256:971e21091fc003c1c4e43411b3bba69e250e22febc95f76bc94abca36b04cc2b"),
    (f"{SNAPSHOT_ROOT}/article.pdf", "sha256:f734cb9c818eed2b1c1a480b9f6dfde094418072ccff4977d9fbfd1670d9a36a"),
    (f"{SNAPSHOT_ROOT}/supplementary-information.pdf", "sha256:e483633ffc8487fdd21d873cab723ed61bf19d12ae0be5cdc80a8ba48f2f60f4"),
    (f"{SNAPSHOT_ROOT}/transparent-peer-review.pdf", "sha256:5fbcbd8cd8ef0ea04e3f7ac3cd01c5c44c3e0962a17cad48ca301339dbf1c60d"),
    (f"{SNAPSHOT_ROOT}/source-data.xlsx", "sha256:bd18c375a5fde55a8b7b64dacf7160cf4eaeadd7a794097a6eeec785e314be17"),
)
SOURCE_HASH_BY_DOCUMENT = {Path(path).name: (path, expected) for path, expected in SOURCE_FILES}

for path, expected in (
    (SPEC_PATH, SPEC_HASH),
    (INVENTORY_PATH, INVENTORY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-013 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 51
    or _primary.get("complete_pdf_page_count") != 36
    or _primary.get("complete_source_data_worksheet_count") != 14
    or _primary.get("complete_source_data_nonempty_cell_count") != 978591
    or _primary.get("complete_key_state_resolved_product_and_scattering_cell_count") != 6408
    or not all(_primary.get("source_experimental_theoretical_and_processing_statuses_retained_separately", {}).values())
    or not all(_primary.get("transparent_peer_review_adverse_surface", {}).values())
    or _identities.get("complete_registered_target_count") != 51
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 51
):
    raise ValueError("KIN-013 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-025-66587-x; complete source record {row['source_record_ordinal']}; "
            f"document {row['source_document_identity']}; record {row['source_record_identity']}"
        ),
        snapshot_path=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][0],
        snapshot_hash=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][1],
    )
    for row in _identities["rows"]
)

REACTION_DYNAMICS_SCATTERING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-REACTION-DYNAMICS-SCATTERING-PRODUCT-STATE-013",
    title="Exact reaction-dynamics scattering and product-state law",
    statement=(
        "One finite held incoming reaction channel and preparation compose with the complete finite support of distinct "
        "outgoing joint product-state words. Completed events in each retained state per complete positive event support "
        "force exact positive state shares, while each incoming/outgoing orientation remains a held relation. No scattering "
        "equation, cross-section law, angular continuum, probability amplitude, fitted potential or distribution is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of incoming, outgoing, composition, quantity, orientation, observation, provenance "
        "and prediction forms; decide all 256 candidates only from admitted finite channel, state, transition, mechanism "
        "and exact-count laws."
    ),
    grammar_boundary=(
        "Every finite held incoming reaction channel and preparation; every complete finite, source-ordered support of "
        "distinct joint coproduct-state words; exact positive completed-event shares; held incoming/outgoing orientations; "
        "and every favorable, adverse, control, fitted, normalized, estimated, tentative or unresolved status. External "
        "testing binds all 51 pre-registered records: article landing, 36 PDF pages and all 14 source-data worksheets "
        "containing 978,591 nonempty cells and 6,408 key state-resolved product, branching and scattering cells."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One finite held incoming channel with the first complete finite outgoing joint product-state support forces exact "
        "positive state shares and one held orientation per retained outgoing state."
    ),
    induction_step=(
        "Append the next complete scattering occurrence at the next positive source occurrence. Every prior incoming and "
        "outgoing identity, joint product state, exact share, orientation and evidence status remains unchanged."
    ),
    exclusions=(
        "numerical zero",
        "negative proof quantity",
        "irrational quantity",
        "imaginary quantity",
        "scattering equation",
        "cross-section law",
        "angular continuum",
        "probability amplitude",
        "fitted potential or distribution",
        "imported energy or momentum equation",
        "selected product state, channel or orientation",
        "selected page, worksheet, cell or row",
        "omitted weak, adverse, reviewer or unresolved record",
        "average",
        "digitization",
        "interpolation",
        "renormalization",
        "target-derived correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-REACTION-DYNAMICS-SCATTERING-013",
    expected_observation_label="complete-state-resolved-product-and-scattering-source-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any incoming carrier, preparation, outgoing product carrier, product-state coordinate or joint "
        "pair identity is erased; if outgoing support is selected, duplicated or incomplete; if a state share is not forced "
        "from exact positive completed events and complete positive support; if orientation becomes a signed angle or continuum; "
        "if any of the 51 source records, 36 pages, 14 worksheets, 978,591 nonempty cells, 6,408 key state-resolved cells, "
        "weak or tentative channel, fitted or normalized record, experimental/theoretical discrepancy, limitation, reviewer "
        "challenge or correction record is omitted; if a scattering equation, cross-section law, amplitude, potential, "
        "continuum, fit, selection, averaging, interpolation or target correction enters; if target content opens before all "
        "51 identities and the consequence seal; or if omission or mismatched-reaction tampering passes."
    ),
)
REACTION_DYNAMICS_SCATTERING_SPEC.validate()


__all__ = (
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "INVENTORY_HASH",
    "INVENTORY_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "REACTION_DYNAMICS_SCATTERING_SPEC",
    "SNAPSHOT_ROOT",
    "SOURCE_FILES",
    "SPEC_HASH",
    "SPEC_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)

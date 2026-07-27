"""Registered KIN-011 law and complete diffusion-limited reaction source surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.diffusion_limited_reaction_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-011-diffusion-limited-reaction-v1"
SPEC_PATH = "experiments/external_sources/chemistry/diffusion_limited_reaction_capture_spec_v1.json"
SPEC_HASH = "sha256:c75f6820adff1a1ec7b3057033d0a563f98ec6a69df80c9c4e985385fb011f24"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:40a4ecfacbba80be1c0f9ed3e307ae65493dc5b975ad34c1f1ddd60be961fa21"
IDENTITY_PATH = "experiments/external_sources/chemistry/diffusion_limited_reaction_target_identities_v1.json"
IDENTITY_HASH = "sha256:a25e15f60b000b37b523d117c9aee657d7b3d65e710246a71024ec384689cd49"
TARGET_PATH = "experiments/external_sources/chemistry/diffusion_limited_reaction_withheld_targets_v1.json"
TARGET_HASH = "sha256:3d48691bf24fc9eecd2298d8f34c4bffe947622b7637c2d67e16e73f5d60047e"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/diffusion-limited-reaction-primary-records-v1.json"
PRIMARY_HASH = "sha256:0a969d97f86841e709db1887151852e279afd31da39cb1f168aca0ce2254389c"

SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/article.html", "sha256:7a6bfd1252ead9473d89edd459aee19580bfab524d62bc3aab271961c5be1fcf"),
    (f"{SNAPSHOT_ROOT}/article.pdf", "sha256:620eca8233bc084fd8763c26cdcd47cdefea8540e36b2b5d74f34a354acee22a"),
    (f"{SNAPSHOT_ROOT}/supplementary-information.pdf", "sha256:a9af0426f8d4ef793e1daaf3d8d94992b68fada22ce9e43ce881599f00c96d00"),
    (f"{SNAPSHOT_ROOT}/additional-supplementary.pdf", "sha256:f1320edb79b1f869b1e41a276f26b3eb18ee0c741d1997d3376b2a39b17493df"),
    (f"{SNAPSHOT_ROOT}/supplementary-video-one.avi", "sha256:337f8f6b8729e59fc4fc8619392cecee586f6933cf80215b325785103fa85e4c"),
    (f"{SNAPSHOT_ROOT}/supplementary-video-two.avi", "sha256:1b8a9492ae19df644d4d4bb8604212918aa9d952cde504663e68119709779efb"),
    (f"{SNAPSHOT_ROOT}/reporting-summary.pdf", "sha256:9f1a756eb3becda24241bc61845ff01355d1e3e59d7346febd692fd42a2a86dc"),
    (f"{SNAPSHOT_ROOT}/nature-source-data.zip", "sha256:fe70df65f96b3c7d4ca1d85932cd21ac1b3dd16e2e085192a7c7513780900584"),
    (f"{SNAPSHOT_ROOT}/figshare-record-metadata.json", "sha256:bd22d8d4a6c3934b18f57755d22435295f8bd54155cf4e079d604ba801206c07"),
    (f"{SNAPSHOT_ROOT}/figshare-source-data.zip", "sha256:fe70df65f96b3c7d4ca1d85932cd21ac1b3dd16e2e085192a7c7513780900584"),
)
SOURCE_HASH_BY_DOCUMENT = {Path(path).name: (path, expected) for path, expected in SOURCE_FILES}

for path, expected in (
    (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-011 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 251
    or _primary.get("complete_pdf_page_count") != 43
    or _primary.get("complete_supplementary_video_frame_count") != 1350
    or _primary.get("complete_archive_member_count") != 204
    or _primary.get("complete_key_raw_data_row_count") != 11512
    or len(_primary.get("complete_fifteen_row_radius_total_reaction_time_vector", ())) != 15
    or _primary.get("independently_hosted_nature_and_figshare_archive_bytes_identical") is not True
    or _primary.get("structural_transport_reaction_path", {}).get("transport_exit_equals_reaction_entry") is not True
    or _identities.get("complete_registered_target_count") != 251
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 251
):
    raise ValueError("KIN-011 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-025-68008-5; repository DOI 10.6084/m9.figshare.30344179; "
            f"complete source record {row['source_record_ordinal']}; document {row['source_document_identity']}; "
            f"record {row['source_record_identity']}"
        ),
        snapshot_path=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][0],
        snapshot_hash=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][1],
    )
    for row in _identities["rows"]
)

DIFFUSION_LIMITED_REACTION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011",
    title="Exact diffusion-limited reaction boundary",
    statement=(
        "A diffusion-limited reaction occurrence is admissible only after one complete finite transport word carries "
        "the same held reactant identity to an encounter state that is exactly the reaction entry state. The exact "
        "completion relation counts completed reaction occurrences per positive held observation partition. No diffusion "
        "equation, continuum concentration field, Fick or Smoluchowski law, fitted coefficient or stochastic collision "
        "weight is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, composition, limitation, rate, path, status, provenance and prediction "
        "forms; decide all 256 candidates only from admitted finite state-transition, transport and reaction composition laws."
    ),
    grammar_boundary=(
        "Every finite source-ordered transport-reaction family retaining the same reactant through two or more registered "
        "transport states, every adjacent transition, one exact transport exit/reaction-entry state, one held condition, "
        "one product state and every favorable, adverse, control or unresolved status. External testing binds all 251 "
        "pre-registered records: article landing, 43 PDF pages, two videos containing 1,350 frames, Figshare metadata and "
        "all 204 member identities from two byte-identical independently hosted archives."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One complete finite transport word whose exit is the exact reaction encounter entry forces one diffusion-limited "
        "reaction boundary and one positive completed-reaction count."
    ),
    induction_step=(
        "Append the next complete transport-reaction occurrence at the next positive source position. Every prior path, "
        "transition, held identity, encounter boundary, reaction and exact result remains unchanged."
    ),
    exclusions=(
        "numerical zero", "negative proof quantity", "irrational quantity", "imaginary quantity", "continuum field",
        "continuum concentration", "diffusion equation", "Fick law", "Smoluchowski law", "stochastic collision weight",
        "fitted diffusion coefficient", "fitted rate constant", "selected time, path, species or condition",
        "selected method, page, frame, member or row", "omitted adverse or unresolved record", "average", "interpolation",
        "renormalization", "target-derived correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-DIFFUSION-LIMITED-REACTION-011",
    expected_observation_label="complete-finite-transport-reaction-boundary-source-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the transported identity changes; if any transport state or adjacent transition is omitted; "
        "if transport exit differs from reaction encounter entry; if reaction is admitted before transport closure; if any "
        "page, video, archive member, raw row, radius/time row, velocity discrepancy, large-droplet deviation, resolution "
        "limit or reviewer adverse question is omitted; if a diffusion equation, continuum, Fick or Smoluchowski law, fitted "
        "coefficient, stochastic collision weight, selection, averaging, interpolation or target correction enters; if target "
        "content opens before all 251 identities and the consequence seal; or if omission or broken-boundary tampering passes."
    ),
)
DIFFUSION_LIMITED_REACTION_SPEC.validate()


__all__ = (
    "DIFFUSION_LIMITED_REACTION_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "INVENTORY_HASH", "INVENTORY_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_ROOT", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH",
    "TARGET_PATH", "TARGET_REFERENCES",
)

#!/usr/bin/env python3
"""Normalize the complete post-seal KIN-011 diffusion-limited reaction source record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-011-diffusion-limited-reaction-v1"
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_capture_spec_v1.json"
SPEC_HASH = "sha256:c75f6820adff1a1ec7b3057033d0a563f98ec6a69df80c9c4e985385fb011f24"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:40a4ecfacbba80be1c0f9ed3e307ae65493dc5b975ad34c1f1ddd60be961fa21"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_target_identities_v1.json"
IDENTITY_HASH = "sha256:a25e15f60b000b37b523d117c9aee657d7b3d65e710246a71024ec384689cd49"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_withheld_targets_v1.json"
TARGET_HASH = "sha256:3d48691bf24fc9eecd2298d8f34c4bffe947622b7637c2d67e16e73f5d60047e"
OUTPUT_PATH = SNAPSHOT_ROOT / "diffusion-limited-reaction-primary-records-v1.json"
NATURE_ARCHIVE = "nature-source-data.zip"
FIGSHARE_ARCHIVE = "figshare-source-data.zip"


def sha_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def source_lines(payload: bytes, delimiter: str | None = None) -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(cell.strip() for cell in line.split(delimiter)) for line in payload.decode().splitlines() if line.strip())


def main() -> None:
    for path, expected in (
        (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH),
        (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"KIN-011 sealed source boundary changed: {path}")
    inventory = json.loads(INVENTORY_PATH.read_text())
    identities = json.loads(IDENTITY_PATH.read_text())
    targets = json.loads(TARGET_PATH.read_text())
    identity_rows = tuple(identities["rows"])
    target_rows = tuple(targets["rows"])
    if (
        len(identity_rows) != 251 or len(target_rows) != 251
        or tuple(row["source_record_ordinal"] for row in identity_rows) != tuple(range(1, 252))
        or any(
            identity["target_id"] != target["target_id"]
            or identity["source_record_identity"] != target["source_record_identity"]
            for identity, target in zip(identity_rows, target_rows)
        )
    ):
        raise ValueError("KIN-011 complete source-ordered target vector changed")
    source_class_census: dict[str, int] = {}
    for row in target_rows:
        key = row["source_record_class"]
        source_class_census[key] = source_class_census.get(key, 0) + 1
    expected_source_class_census = {
        "complete-article-landing-record": 1, "complete-pdf-page": 43,
        "complete-supplementary-video": 2, "complete-figshare-metadata-record": 1,
        "complete-source-data-archive-member": 204,
    }
    if source_class_census != expected_source_class_census:
        raise ValueError("KIN-011 complete source-class census changed")
    pages = {
        (row["source_document_identity"], row["source_page_ordinal"]):
        " ".join(row["target_payload"]["complete_extracted_page_text"].split())
        for row in target_rows if row["source_record_class"] == "complete-pdf-page"
    }
    required_page_fragments = {
        ("article.pdf", 2): ("initially accelerates into the droplet", "constant velocity", "formation of the Li +Bz2 complex"),
        ("article.pdf", 4): ("three contributions", "solvation time", "diffusion time", "bond formation time"),
        ("article.pdf", 5): ("diffusion-limited reaction", "5×10 12", "time resolution of our technique is insuf"),
        ("supplementary-information.pdf", 8): ("motion of the Li+ ion can be divided into three steps", "constant velocity", "accelerated approach and reaction"),
        ("supplementary-information.pdf", 9): ("helium must provide a drag", "43 m/s", "not included in the simulations"),
        ("supplementary-information.pdf", 12): ("Four reactive RPMD trajectories", "times at which the cation-π complex is formed"),
        ("supplementary-information.pdf", 13): ("uncertainty", "43 m/s", "±5 m/s"),
        ("supplementary-information.pdf", 14): ("Estimating the rate constant", "22 ps", "5 ⋅ 1012"),
        ("supplementary-information.pdf", 18): ("Extraction method", "Co(Li +Bz, Bz+)", "Source data are provided"),
        ("supplementary-information.pdf", 20): ("Effect of doping on mean droplet radius", "Source data are provided"),
        ("reporting-summary.pdf", 1): ("some systems may remain for a long time", "Why not for ever", "100% reactive"),
    }
    for key, fragments in required_page_fragments.items():
        if key not in pages or any(fragment not in pages[key] for fragment in fragments):
            raise ValueError(f"KIN-011 decisive PDF page changed: {key}")

    target_member = {
        (row.get("archive_identity"), row["source_record_identity"]): row["target_payload"]
        for row in target_rows if row["source_record_class"] == "complete-source-data-archive-member"
    }
    selected_members = (
        "Source Data/Manuscript/Fig1/Li-He3600_average_40ps.dat",
        "Source Data/Manuscript/Fig1/LiBenzene2-He3600_average.dat",
        "Source Data/Manuscript/Fig1/properties_LiBenzene2-He3600_theta10_final.dat",
        "Source Data/Manuscript/Fig2/Li+_Ion_signal.dat",
        "Source Data/Manuscript/Fig3/Co(Li+Bz_Bz).dat.dat",
        "Source Data/Manuscript/Fig3/Li+BzCoincidenceFiltered.dat",
        "Source Data/Manuscript/Fig3/t_total.dat",
    )
    archives: dict[str, dict[str, bytes]] = {}
    for archive_identity in (NATURE_ARCHIVE, FIGSHARE_ARCHIVE):
        with zipfile.ZipFile(SNAPSHOT_ROOT / archive_identity) as archive:
            archives[archive_identity] = {name: archive.read(name) for name in selected_members}
    for name in selected_members:
        nature_payload = archives[NATURE_ARCHIVE][name]
        figshare_payload = archives[FIGSHARE_ARCHIVE][name]
        if nature_payload != figshare_payload:
            raise ValueError(f"KIN-011 independently hosted archive member differs: {name}")
        for archive_identity, payload in ((NATURE_ARCHIVE, nature_payload), (FIGSHARE_ARCHIVE, figshare_payload)):
            registered = target_member[(archive_identity, name)]
            if sha_bytes(payload) != registered["complete_member_hash"] or len(payload) != registered["complete_member_byte_count"]:
                raise ValueError(f"KIN-011 source-data member changed: {archive_identity}:{name}")
    raw = archives[NATURE_ARCHIVE]
    parsed = {
        selected_members[0]: source_lines(raw[selected_members[0]]),
        selected_members[1]: source_lines(raw[selected_members[1]]),
        selected_members[2]: source_lines(raw[selected_members[2]]),
        selected_members[3]: source_lines(raw[selected_members[3]], ","),
        selected_members[4]: source_lines(raw[selected_members[4]], ","),
        selected_members[5]: source_lines(raw[selected_members[5]], ","),
        selected_members[6]: source_lines(raw[selected_members[6]], ","),
    }
    expected_shapes = ((800, 4), (4000, 4), (6500, 4), (24, 2), (23, 15), (150, 23), (15, 4))
    for name, (row_count, width) in zip(selected_members, expected_shapes):
        if len(parsed[name]) != row_count or any(len(row) != width for row in parsed[name]):
            raise ValueError(f"KIN-011 complete raw data shape changed: {name}")
    t_total = tuple({
        "average_radius_angstrom_external_inscription": row[0],
        "average_total_reaction_time_ps_external_inscription": row[1],
        "uncertainty_higher_ps_external_inscription": row[2],
        "uncertainty_lower_ps_external_inscription": row[3],
    } for row in parsed[selected_members[6]])
    video_rows = tuple(row for row in target_rows if row["source_record_class"] == "complete-supplementary-video")
    archive_rows = tuple(row for row in target_rows if row["source_record_class"] == "complete-source-data-archive-member")
    if sum(row["target_payload"]["frame_count"] for row in video_rows) != 1350 or len(archive_rows) != 204:
        raise ValueError("KIN-011 complete movie/archive target surface changed")

    document = {
        "schema": "sft-v3-diffusion-limited-reaction-primary-records/1",
        "claim_id": "SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-011",
        "source_identity": {
            "article_doi": "10.1038/s41467-025-68008-5",
            "figshare_repository_doi": "10.6084/m9.figshare.30344179",
            "system": "Li-plus-benzene-dimer-helium-droplet-complete-transport-reaction-surface",
        },
        "sealed_boundaries": {
            "prefetch_specification": SPEC_HASH, "source_inventory": INVENTORY_HASH,
            "value_free_identity_registry": IDENTITY_HASH, "withheld_complete_target_registry": TARGET_HASH,
        },
        "complete_registered_target_count": 251, "complete_source_class_census": source_class_census,
        "complete_pdf_page_count": 43, "complete_supplementary_video_count": 2,
        "complete_supplementary_video_frame_count": 1350, "complete_archive_count": 2,
        "complete_archive_member_count": 204, "complete_source_file_count": inventory["complete_source_file_count"],
        "complete_source_file_byte_count": sum(row["byte_count"] for row in inventory["complete_source_files"]),
        "independently_hosted_nature_and_figshare_archive_bytes_identical": sha_file(SNAPSHOT_ROOT / NATURE_ARCHIVE) == sha_file(SNAPSHOT_ROOT / FIGSHARE_ARCHIVE),
        "structural_transport_reaction_path": {
            "ordered_states": (
                {"state": "separated-reactants", "status": "initial-boundary"},
                {"state": "initiated-solvation", "status": "retained-transport-entry"},
                {"state": "transport-occurrence-word", "status": "finite-retained-path"},
                {"state": "encounter-boundary", "status": "transport-exit-equals-reaction-entry"},
                {"state": "product-complex", "status": "reaction-terminal"},
            ),
            "transport_exit_equals_reaction_entry": True,
            "complete_transport_word_required_before_reaction_occurrence": True,
            "no_continuum_field_or_differential_law_used": True,
        },
        "source_reported_stage_vector": (
            {"stage": "solvation", "external_time_inscription": "approximately first 10 ps"},
            {"stage": "diffusion", "external_time_inscription": "approximately 10-45 ps"},
            {"stage": "bond formation", "external_time_inscription": "approximately 45-52 ps"},
        ),
        "complete_fifteen_row_radius_total_reaction_time_vector": t_total,
        "complete_key_raw_data_shapes": tuple({
            "member": name, "row_count": len(parsed[name]), "column_count": len(parsed[name][0]),
            "member_hash": sha_bytes(raw[name]),
        } for name in selected_members),
        "complete_key_raw_data_row_count": sum(len(parsed[name]) for name in selected_members),
        "complete_23_by_15_reaction_yield_matrix_retained": True,
        "complete_150_by_23_coincidence_filtered_distribution_retained": True,
        "source_reported_experimental_diffusion_velocity_external_inscription": "43 m/s",
        "source_reported_one_sigma_velocity_uncertainty_external_inscription": "±5 m/s",
        "source_reported_simulation_diffusion_velocity_external_inscription": "14 m/s",
        "experiment_and_simulation_velocity_discrepancy_retained_without_reconciliation": True,
        "source_reported_rate_constant_estimate_external_inscription": "5×10^12 M^-1 s^-1",
        "source_reported_large_droplet_deviation_from_linear_fit_retained": True,
        "source_reported_time_resolution_insufficient_for_bond_formation_detail_retained": True,
        "peer_review_nonencounter_and_not_all_systems_reactive_adverse_question_retained": True,
        "source_reported_CDF_log_normal_linear_fit_rate_constant_RPMD_and_other_models_retained_as_postseal_provenance_only": True,
        "source_reported_distance_time_velocity_yield_rate_fit_distribution_simulation_uncertainty_and_condition_values_used_as_fold_proof_parameters": False,
        "imported_Fick_Smoluchowski_diffusion_equation_continuum_concentration_field_stochastic_collision_weight_fitted_diffusion_coefficient_selection_average_interpolation_or_target_correction_used_in_law": False,
        "native_numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
        "external_zero_negative_decimal_and_continuum_inscriptions_preserved_only_as_source_provenance": True,
        "complete_decisive_pdf_page_identities": tuple(f"{document}:page-{page}" for document, page in required_page_fragments),
    }
    OUTPUT_PATH.write_text(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output_path": str(OUTPUT_PATH.relative_to(ROOT)), "output_hash": sha_file(OUTPUT_PATH),
        "complete_target_count": 251, "complete_archive_member_count": 204,
        "complete_key_raw_data_row_count": document["complete_key_raw_data_row_count"],
        "complete_reaction_time_value_rows": len(t_total),
    }, indent=2))


if __name__ == "__main__":
    main()

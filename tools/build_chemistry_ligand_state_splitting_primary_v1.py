#!/usr/bin/env python3
"""Build the complete post-seal INORG-006 identity and empirical vectors."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


LAW = ROOT / "sft/chemistry/ligand_state_splitting_law_v1.py"
LAW_HASH = "sha256:b1d1350aff301a5cb2e58471e00021897dedc3a771660f574dbbe54ef8038079"
FAMILY_REGISTRY = ROOT / "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
ADDENDUMS = (
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v1.json", "sha256:7c3e63016b4f52a0cf2a84b8076ac954ba61649580d2459ed826e40a5aff0693"),
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v2.json", "sha256:fa25c3d9d170254de760bc3778af9dd89793b902729ca0314bc0ececa08ff7e8"),
    ("experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v3.json", "sha256:eeca900246f02c7b8d32fa77e5060adbc1033f99dbe2df103c4d8f4d2cb0c17b"),
)
INVENTORIES = (
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v1/source-inventory-v1.json", "sha256:d76d5b6a898ce98a45c97ea936a5fe7902356701474f54ca6443b752f124d1f2", "development-observed"),
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v2/source-inventory-v1.json", "sha256:d9d0e0255439404dcb82a4b585de24d4b6fafbc51d3ae64f2c893985a30fc752", "law-sealed-adverse-absence"),
    ("experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v3/source-inventory-v1.json", "sha256:fe95562bfb5e930c37b17a9fd9ee25d17031c36c7ee9b7949441a533f17acc7b", "law-sealed-blind"),
)
IUPAC_FILES = (
    ("IUPAC-LT06764", "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-lt06764.json", "sha256:dad6da4049a23236e040e7219d1d81d8730e732a72ac63e05da91d3bad410155"),
    ("IUPAC-L03517", "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-l03517.json", "sha256:9ad080420481e49ee9e66b397b7eddc83398087877f9016eae0d9a287ae6aab8"),
)
IDENTITY = ROOT / "experiments/external_sources/chemistry/ligand_state_splitting_target_identities_v1.json"
TARGET = ROOT / "experiments/external_sources/chemistry/ligand_state_splitting_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v3/ligand-state-splitting-primary-records-v1.json"


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _parse_jcamp(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    metadata: dict[str, str] = {}
    points: list[tuple[Fraction, Fraction]] = []
    active = False
    for line in lines:
        if line.startswith("##XYPOINTS"):
            active = True
            continue
        if active and line.startswith("##"):
            active = False
        if active and "," in line:
            x, y = line.split(",", 1)
            points.append((Fraction(x.strip()), Fraction(y.strip())))
        elif line.startswith("##") and "=" in line:
            key, value = line[2:].split("=", 1)
            metadata[key.strip()] = value.strip()
    if metadata.get("DATA TYPE") != "UV/VIS SPECTRUM" or not points:
        return {"payload_class": "captured-non-spectrum-ancillary", "exact_point_count": "EmptyOne"}

    plateaus: list[tuple[Fraction, Fraction, Fraction]] = []
    for x, y in points:
        if plateaus and plateaus[-1][2] == y:
            plateaus[-1] = (plateaus[-1][0], x, y)
        else:
            plateaus.append((x, x, y))
    interior_maxima: list[dict[str, str]] = []
    boundary_maxima: list[dict[str, str]] = []
    interior_minima: list[dict[str, str]] = []
    for index, (first_x, last_x, y) in enumerate(plateaus):
        row = {"x": _fraction_text((first_x + last_x) / 2), "y": _fraction_text(y), "plateau_first_x": _fraction_text(first_x), "plateau_last_x": _fraction_text(last_x)}
        if index == 0:
            if len(plateaus) > 1 and y > plateaus[1][2]:
                boundary_maxima.append(row)
        elif index == len(plateaus) - 1:
            if y > plateaus[index - 1][2]:
                boundary_maxima.append(row)
        else:
            if y > plateaus[index - 1][2] and y > plateaus[index + 1][2]:
                interior_maxima.append(row)
            if y < plateaus[index - 1][2] and y < plateaus[index + 1][2]:
                interior_minima.append(row)
    separations = tuple(
        _fraction_text(Fraction(right["x"]) - Fraction(left["x"]))
        for left, right in zip(interior_maxima, interior_maxima[1:])
    )
    return {
        "payload_class": "complete-uv-visible-spectrum",
        "title": metadata.get("TITLE", ""),
        "cas_registry_number": metadata.get("CAS REGISTRY NO", ""),
        "x_units": metadata.get("XUNITS", ""),
        "y_units": metadata.get("YUNITS", ""),
        "declared_point_count": metadata.get("NPOINTS", ""),
        "exact_point_count": len(points),
        "complete_interior_local_maxima": interior_maxima,
        "boundary_truncated_maxima": boundary_maxima,
        "complete_interior_local_minima": interior_minima,
        "adjacent_interior_maximum_separations": separations,
        "no_smoothing_no_threshold_equal_height_plateau_rule": True,
    }


def _surface_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    identities: list[dict[str, object]] = []
    outcomes: list[dict[str, object]] = []

    def add(source_id: str, authority: str, role: str, path: str, digest: str, custody: str, outcome: dict[str, object]) -> None:
        ordinal = len(identities) + 1
        identity = {
            "target_id": f"SFT-CHEM-INORG006-SPLIT-{ordinal:03d}",
            "source_record_ordinal": ordinal,
            "source_id": source_id,
            "authority": authority,
            "source_record_role": role,
            "snapshot_path": path,
            "snapshot_sha256": digest,
            "custody_class": custody,
        }
        identities.append(identity)
        outcomes.append({**identity, "source_outcome": outcome, "target_payload_hash": sha256_identity((identity["target_id"], role, outcome))})

    for source_id, path, digest in IUPAC_FILES:
        document = json.loads((ROOT / path).read_text(encoding="utf-8"))
        term = document["term"]
        definition = " ".join(row.get("text", "") for row in term.get("definitions", ()))
        for role, outcome in (
            ("complete-source-file", {"term_code": term.get("code"), "title": term.get("title"), "status": term.get("status")}),
            ("complete-definition-surface", {"definition": definition}),
            ("source-citation-surface", {"citation": term.get("citation"), "sources": tuple(source for row in term.get("definitions", ()) for source in row.get("sources", ()))}),
            ("license-disclaimer-surface", {"license": term.get("license"), "disclaimer": term.get("disclaimer")}),
        ):
            add(source_id, "IUPAC", role, path, digest, "family-captured-before-claim", outcome)

    for inventory_path, inventory_hash, custody in INVENTORIES:
        inventory = json.loads((ROOT / inventory_path).read_text(encoding="utf-8"))
        page_by_source = {
            row["source_id"]: row
            for row in inventory["rows"]
            if row["surface_kind"] == "complete-source-page" and row.get("snapshot_sha256")
        }
        for row in inventory["rows"]:
            bound = row if row.get("snapshot_sha256") else page_by_source[row["source_id"]]
            path = str(bound["snapshot_path"])
            digest = str(bound["snapshot_sha256"])
            if row["surface_kind"] == "complete-source-page":
                outcome = {"capture_status": row["capture_status"], "http_status": row.get("http_status"), "content_type": row.get("response_content_type"), "surface_class": "complete-source-page"}
            elif row.get("snapshot_sha256"):
                outcome = {"capture_status": row["capture_status"], "surface_class": "discovered-linked-payload", **_parse_jcamp(ROOT / path)}
            else:
                outcome = {"capture_status": row["capture_status"], "surface_class": "linked-spectrum-absence", "native_absence": "EmptyOne"}
            add(str(row["source_id"]), str(row["authority"]), str(row["surface_kind"]), path, digest, custody, outcome)
    return identities, outcomes


def main() -> None:
    for path, digest in ((LAW, LAW_HASH), (FAMILY_REGISTRY, FAMILY_REGISTRY_HASH), (FAMILY_INVENTORY, FAMILY_INVENTORY_HASH)):
        if hash_file(path) != digest:
            raise SystemExit(f"VOID_INVALID_HALTED: INORG-006 authority changed: {path}")
    registered_files = (*ADDENDUMS, *((path, digest) for path, digest, _ in INVENTORIES), *((path, digest) for _, path, digest in IUPAC_FILES))
    for path, digest in registered_files:
        resolved = ROOT / path if isinstance(path, str) else path
        if hash_file(resolved) != digest:
            raise SystemExit(f"VOID_INVALID_HALTED: INORG-006 source changed: {resolved}")
    identities, outcomes = _surface_rows()
    if len(identities) != 32 or len(outcomes) != 32:
        raise SystemExit("VOID_INVALID_HALTED: INORG-006 complete surface is not 32 rows")
    identity_document = {
        "schema": "sft-v3-ligand-state-splitting-target-identities/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-006",
        "claim_id": "SFT-CHEM-LIGAND-STATE-SPLITTING-006",
        "sealed_fold_law_sha256": LAW_HASH,
        "complete_registered_target_count": len(identities),
        "target_values_peak_positions_intensities_band_counts_definitions_and_outcomes_present": False,
        "all_family_development_adverse_absent_blind_and_ancillary_rows_registered": True,
        "rows": identities,
    }
    IDENTITY.write_text(json.dumps(identity_document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    blind_rows = [row for row in outcomes if row["custody_class"] == "law-sealed-blind"]
    blind_spectrum_rows = [row for row in blind_rows if row["source_outcome"].get("payload_class") == "complete-uv-visible-spectrum"]
    blind_favorable = bool(blind_spectrum_rows) and all(len(row["source_outcome"]["complete_interior_local_maxima"]) >= 2 for row in blind_spectrum_rows)
    adverse_absences = [row for row in outcomes if row["source_outcome"].get("surface_class") == "linked-spectrum-absence"]
    ancillary = [row for row in outcomes if row["source_outcome"].get("payload_class") == "captured-non-spectrum-ancillary"]
    target_document = {
        "schema": "sft-v3-ligand-state-splitting-withheld-targets/1",
        "identity_document_sha256": hash_file(IDENTITY),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(outcomes),
        "rows": outcomes,
    }
    TARGET.write_text(json.dumps(target_document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    primary = {
        "schema": "sft-v3-chemistry-ligand-state-splitting-primary-records/1",
        "sealed_fold_law_sha256": LAW_HASH,
        "identity_document_sha256": hash_file(IDENTITY),
        "withheld_target_document_sha256": hash_file(TARGET),
        "complete_registered_target_count": len(outcomes),
        "exact_postseal_analysis": {
            "forced_generated_support_count": 5,
            "six_direct_axis_positive_multiplicity_vector": [3, 2],
            "six_direct_axis_exact_normalized_structural_separation": "2/3",
            "six_direct_axis_positive_balance_distance_vector": ["2/5", "3/5"],
            "four_complete_axis_positive_multiplicity_vector": [2, 3],
            "four_complete_axis_exact_normalized_structural_separation": "1",
            "four_complete_axis_positive_balance_distance_vector": ["3/5", "2/5"],
            "blind_spectrum_payload_count": len(blind_spectrum_rows),
            "blind_no_smoothing_at_least_two_complete_interior_maxima": blind_favorable,
            "law_sealed_adverse_absent_spectrum_rows": len(adverse_absences),
            "development_capture_ancillary_rows_preserved": len(ancillary),
            "all_32_rows_preserved": len(outcomes) == 32,
            "no_dimensional_wavelength_fitted_or_claimed": True,
        },
        "rows": outcomes,
    }
    PRIMARY.write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "identities": len(identities),
        "identity_sha256": hash_file(IDENTITY),
        "target_sha256": hash_file(TARGET),
        "primary_sha256": hash_file(PRIMARY),
        "blind_spectrum_payload_count": len(blind_spectrum_rows),
        "blind_favorable": blind_favorable,
        "adverse_absences": len(adverse_absences),
        "ancillary_rows": len(ancillary),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

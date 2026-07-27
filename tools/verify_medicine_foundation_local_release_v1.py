#!/usr/bin/env python3
"""Fail closed on any defect in the Medicine local prepublication release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output/release/medicine-1.0.0"
NAMES = (
    "00_From-Fold-to-Medicine_Medicine-and-Health-Sciences-Foundation-Paper-001-v1.0.pdf",
    "01_Ernos-Labs-SFT-Medicine-Foundation-Evidence-and-Source-v1.0.0.zip",
    "02_From-Fold-to-Medicine_Medicine-and-Health-Sciences-Foundation-Paper-001-v1.0.md",
    "99_SHA256SUMS.txt",
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    metadata = json.loads((ROOT / "publication/medicine_foundation_zenodo_metadata.json").read_text())
    release = json.loads((ROOT / "publication/medicine_foundation_release.json").read_text())
    assert metadata["publication_authorized"] is False
    assert metadata["zenodo_draft_id"] is None and metadata["doi"] == ""
    assert release["schema"] == "sft-v3-local-prepublication-branch-release/1"
    assert release["publication_authorized"] is False
    assert release["github_push_authorized"] is False
    assert release["zenodo_publish_authorized"] is False
    assert release["zenodo_record"] is None and release["doi"] == ""
    for name in NAMES:
        assert (RELEASE / name).is_file(), name
    expected = {}
    for line in (RELEASE / NAMES[-1]).read_text(encoding="utf-8").splitlines():
        value, name = line.split("  ", 1)
        expected[name] = value
    assert expected == {name: digest(RELEASE / name) for name in NAMES[:-1]}
    with ZipFile(RELEASE / NAMES[1]) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert len([name for name in names if name.startswith("claims/SFT-MED-") and name.endswith("/certificate.json")]) == 72
        assert len([name for name in names if name.startswith("receipts/engine/model_admitted/SFT-MED-")]) == 72
        assert not any(name.startswith("sft/engine/") for name in names)
        evidence_map = json.loads(archive.read("medicine_foundation_evidence_map.json"))
        assert evidence_map["claim_count"] == 72
        assert evidence_map["candidate_count"] == 18_432
        assert evidence_map["unique_survivor_count"] == 72
        assert evidence_map["control_count"] == 288
        assert evidence_map["prior_atom_count"] == 5
        assert evidence_map["captured_external_source_count"] == 11
        assert evidence_map["failed_external_source_transport_count"] == 2
        for row in evidence_map["files"]:
            assert "sha256:" + digest_bytes(archive.read(row["path"])) == row["sha256"]
    assert (RELEASE / NAMES[0]).read_bytes() == (
        ROOT / "output/pdf/from-fold-to-medicine-health-sciences-foundation-paper-001-v1.0.pdf"
    ).read_bytes()
    assert (RELEASE / NAMES[2]).read_bytes() == (
        ROOT / "publications/current/medicine/FROM_FOLD_TO_MEDICINE.md"
    ).read_bytes()
    print("Medicine local-release gate v1: PASS files=4 claims=72 receipts=72 publication_authorized=false")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fail closed on any defect in the Earth local release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output/release/earth-environment-1.0.0"
NAMES = (
    "00_From-One-World-to-Earth_Earth-and-Environmental-Sciences-Foundation-Paper-001-v1.0.pdf",
    "01_Ernos-Labs-SFT-Earth-and-Environmental-Sciences-Foundation-Evidence-and-Source-v1.0.0.zip",
    "02_From-One-World-to-Earth_Earth-and-Environmental-Sciences-Foundation-Paper-001-v1.0.md",
    "99_SHA256SUMS.txt",
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    metadata = json.loads((ROOT / "publication/earth_environment_foundation_zenodo_metadata.json").read_text())
    github = json.loads((ROOT / "publication/earth_environment_foundation_github_metadata.json").read_text())
    release = json.loads((ROOT / "publication/earth_environment_foundation_release.json").read_text())
    assert metadata["publication_authorized"] is False and metadata["zenodo_draft_id"] is None and metadata["doi"] == ""
    assert github["publication_authorized"] is False and github["release_url"] == "" and github["doi"] == ""
    assert release["schema"] == "sft-v3-local-prepublication-branch-release/1"
    assert release["publication_authorized"] is False and release["github_push_authorized"] is False and release["zenodo_publish_authorized"] is False
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
        assert len([name for name in names if name.startswith("claims/SFT-EARTH-") and name.endswith("/certificate.json")]) == 74
        assert len([name for name in names if name.startswith("receipts/engine/model_admitted/SFT-EARTH-")]) == 74
        assert not any(name.startswith("sft/engine/") for name in names)
        evidence = json.loads(archive.read("earth_environment_foundation_evidence_map.json"))
        assert evidence["claim_count"] == 74 and evidence["candidate_count"] == 18_944 and evidence["control_count"] == 296
        assert evidence["mixed_earthquake_result_adverse_preserved"] is True
        assert evidence["homogeneous_earthquake_holdout_compatible"] is True
        for row in evidence["files"]:
            assert "sha256:" + digest_bytes(archive.read(row["path"])) == row["sha256"]
    assert (RELEASE / NAMES[0]).read_bytes() == (ROOT / "output/pdf/from-one-world-to-earth-environment-foundation-paper-001-v1.0.pdf").read_bytes()
    assert (RELEASE / NAMES[2]).read_bytes() == (ROOT / "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md").read_bytes()
    print("Earth local-release gate v1: PASS files=4 claims=74 receipts=74 publication_authorized=false")


if __name__ == "__main__":
    main()

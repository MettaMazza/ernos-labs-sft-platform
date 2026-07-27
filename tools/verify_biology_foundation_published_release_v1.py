#!/usr/bin/env python3
"""Fail-closed publication verifier frozen before the Biology release is finalized."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output" / "release" / "biology-1.0.0"
NAMES = (
    "00_From-Fold-to-Life_Biology-and-Life-Sciences-Foundation-Paper-001-v1.0.pdf",
    "01_Ernos-Labs-SFT-Biology-Foundation-Evidence-and-Source-v1.0.0.zip",
    "02_From-Fold-to-Life_Biology-and-Life-Sciences-Foundation-Paper-001-v1.0.md",
    "99_SHA256SUMS.txt",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    metadata = read_json(ROOT / "publication" / "biology_foundation_zenodo_metadata.json")
    github = read_json(ROOT / "publication" / "biology_foundation_github_metadata.json")
    release = read_json(ROOT / "publication" / "biology_foundation_release.json")
    paper = ROOT / "publications" / "current" / "biology" / "FROM_FOLD_TO_LIFE.md"
    readme = ROOT / "README.md"
    doi = metadata["doi"]
    match = re.fullmatch(r"10\.5281/zenodo\.(\d+)", doi)
    assert match, "invalid Biology DOI"
    record_id = int(match.group(1))
    assert metadata["publication_authorized"] is True
    assert metadata["zenodo_draft_id"] == record_id
    assert metadata["metadata"]["version"] == "1.0.0"
    assert metadata["metadata"]["access_right"] == "open"
    assert github["publication_authorized"] is True
    assert github["target_branch"] == "main"
    assert github["release_tag"] == "biology-v1.0.0"
    assert github["doi"] == doi
    assert release["schema"] == "sft-v3-published-branch-release/1"
    assert release["publication_authorized"] is True
    assert release["zenodo_publish_authorized"] is True
    assert release["zenodo_record"] == record_id
    assert release["doi"] == doi
    assert paper.read_bytes() == readme.read_bytes(), "GitHub landing page is not the exact paper"
    paper_text = paper.read_text(encoding="utf-8")
    assert "PUBLISHED OPEN-ACCESS BRANCH PAPER" in paper_text
    assert doi in paper_text
    assert "LOCAL PREPUBLICATION" not in paper_text
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
        assert len([name for name in names if name.startswith("claims/SFT-BIO-") and name.endswith("/certificate.json")]) == 75
        assert len([name for name in names if name.startswith("receipts/engine/model_admitted/SFT-BIO-")]) == 75
    print(f"Biology published-release gate v1: PASS doi={doi} files=4")


if __name__ == "__main__":
    main()

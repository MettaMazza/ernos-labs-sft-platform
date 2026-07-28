#!/usr/bin/env python3
"""Fail closed on any defect in the Consciousness local release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output/release/consciousness-cognitive-science-1.0.0"
NAMES = (
    "00_From-Fold-to-Consciousness_Consciousness-and-Cognitive-Science-Foundation-Paper-001-v1.0.pdf",
    "01_Ernos-Labs-SFT-Consciousness-and-Cognitive-Science-Foundation-Evidence-and-Source-v1.0.0.zip",
    "02_From-Fold-to-Consciousness_Consciousness-and-Cognitive-Science-Foundation-Paper-001-v1.0.md",
    "99_SHA256SUMS.txt",
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    metadata = json.loads((ROOT / "publication/consciousness_foundation_zenodo_metadata.json").read_text())
    github = json.loads((ROOT / "publication/consciousness_foundation_github_metadata.json").read_text())
    release = json.loads((ROOT / "publication/consciousness_foundation_release.json").read_text())
    assert metadata["publication_authorized"] is False
    assert metadata["zenodo_draft_id"] is None and metadata["doi"] == ""
    assert github["publication_authorized"] is False
    assert github["release_url"] == "" and github["doi"] == ""
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
        assert len([name for name in names if name.startswith("claims/SFT-CONSC-") and name.endswith("/certificate.json")]) == 72
        assert len([name for name in names if name.startswith("receipts/engine/model_admitted/SFT-CONSC-")]) == 72
        assert not any(name.startswith("sft/engine/") for name in names)
        evidence_map = json.loads(archive.read("consciousness_foundation_evidence_map.json"))
        assert evidence_map["claim_count"] == 72
        assert evidence_map["candidate_count"] == 18_432
        assert evidence_map["unique_survivor_count"] == 72
        assert evidence_map["control_count"] == 288
        assert evidence_map["prior_atom_count"] == 46
        assert evidence_map["external_source_count"] == 15
        assert evidence_map["registered_external_feature_count"] == 61
        assert evidence_map["present_external_feature_count"] == 58
        assert evidence_map["absent_external_feature_count_preserved"] == 3
        assert evidence_map["transport_or_content_failure_rows_preserved"] == 18
        for row in evidence_map["files"]:
            assert "sha256:" + digest_bytes(archive.read(row["path"])) == row["sha256"]
    assert (RELEASE / NAMES[0]).read_bytes() == (
        ROOT / "output/pdf/from-fold-to-consciousness-and-cognitive-science-foundation-paper-001-v1.0.pdf"
    ).read_bytes()
    assert (RELEASE / NAMES[2]).read_bytes() == (
        ROOT / "publications/current/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md"
    ).read_bytes()
    print("Consciousness local-release gate v1: PASS files=4 claims=72 receipts=72 publication_authorized=false")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Preserve obsolete GO rows and capture current replacement routes."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/biology/molx_001_014_v1"
SNAPSHOTS = BASE / "snapshots_addendum_v2"
OUT = BASE / "source_custody_addendum_v2.json"
BASE_ID = "sha256:e0f2a91e9dadc4783e243a05ee5d8e3978af092a17e83cd31d7b8ad73b239d11"
ADDENDUM_V1_ID = "sha256:8774c01ee0b41e7c72a78ae001e780bd7a9337b6190c6bf7d376793c70dbec74"
FORMAL_SEAL = "sha256:662421bd75301c6511aa0889c27a5b254967528392b3f82e12607bf8e36953ee"

SOURCES = (
    ("QUICKGO-NITROGEN-CYCLE-CURRENT", "quickgo_go_0071941.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0071941"),
    ("QUICKGO-MOLYBDOPTERIN-COFACTOR-CURRENT", "quickgo_go_0043545.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0043545"),
)


def canonical(value: object) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing to overwrite MOLX source addendum v2")
    base = json.loads((BASE / "source_custody_manifest.json").read_text())
    addendum = json.loads((BASE / "source_custody_addendum_v1.json").read_text())
    formal = json.loads((ROOT / "census/biology_molx_001_014_formal_prediction_seal_v1.json").read_text())
    if base["manifest_identity"] != BASE_ID or addendum["addendum_identity"] != ADDENDUM_V1_ID or formal["formal_prediction_seal_identity"] != FORMAL_SEAL:
        raise SystemExit("MOLX prior custody changed")
    SNAPSHOTS.mkdir(parents=True, exist_ok=False)
    documents = []
    for source_id, filename, url in SOURCES:
        request = Request(url, headers={"User-Agent": "ErnosLabs-SFT/3.0 (Maria.Smith.Sftoe@gmail.com)", "Accept": "application/json"})
        with urlopen(request, timeout=45) as response:
            data = response.read()
            status = response.status
        path = SNAPSHOTS / filename
        path.write_bytes(data)
        documents.append({"source_id": source_id, "requested_url": url, "status": f"http_{status}", "snapshot_path": str(path.relative_to(ROOT)), "snapshot_hash": file_hash(path), "byte_count": len(data)})
    payload = {
        "schema": "sft-v3-biology-molx-source-custody-addendum/2",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "reason": "The pre-registered GO:0006807 and GO:0051186 rows were returned as obsolete. They remain preserved; these current non-obsolete terms are a distinct lawful evidence retry.",
        "base_source_manifest_identity": BASE_ID,
        "source_addendum_v1_identity": ADDENDUM_V1_ID,
        "formal_prediction_seal_identity": FORMAL_SEAL,
        "document_count": len(documents),
        "documents": documents,
        "obsolete_rows_preserved": True,
        "failed_route_retired_claim": False,
    }
    payload["addendum_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "addendum_identity": payload["addendum_identity"]}, indent=2))


if __name__ == "__main__":
    main()

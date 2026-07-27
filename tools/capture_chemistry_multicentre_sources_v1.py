#!/usr/bin/env python3
"""Capture and register the complete ELEC-008 multicentre structural surface."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/multicentre-v1"
IUPAC_PATH = "experiments/external_sources/chemistry/snapshots/goldbook-terms/08789.json"
DIBORANE_PATH = "experiments/external_sources/chemistry/snapshots/multicentre-v1/nist-cccbdb-diborane-experimental-geometry.html"
BENZENE_PATH = "experiments/external_sources/chemistry/snapshots/multicentre-v1/nist-cccbdb-benzene-experimental-geometry.html"
DIBORANE_URL = "https://cccbdb.nist.gov/expgeom2x.asp?casno=19287457"
BENZENE_URL = "https://cccbdb.nist.gov/expgeom2x.asp?casno=71432"
IUPAC_HASH = "sha256:570755940f01bfa32741b03b6b2f22b02742101605a2263e57369966ea433abd"
DIBORANE_HASH = "sha256:99e1c36da1bf8aa2b559ba9ef84b43b4965982c3ee1cab13abb933c8fba22527"
BENZENE_HASH = "sha256:6e158d7639b301cfa6a18bfab4461988c9ffc6190f99fb9a5c0df7baf6f3ec0f"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/multicentre_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/multicentre_withheld_targets_v1.json"


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def fetch(url: str, path: Path) -> None:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-custody/1"})
    with urlopen(request, timeout=30) as response:
        content = response.read()
    if len(content) < 1000:
        raise RuntimeError("ELEC-008 source response is incomplete: " + url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def plain(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"ELEC-008 {source} fragment absent: {fragment}")


def main() -> None:
    diborane_file = ROOT / DIBORANE_PATH
    benzene_file = ROOT / BENZENE_PATH
    if not diborane_file.is_file():
        fetch(DIBORANE_URL, diborane_file)
    if not benzene_file.is_file():
        fetch(BENZENE_URL, benzene_file)
    iupac_file = ROOT / IUPAC_PATH
    for path, expected in ((iupac_file, IUPAC_HASH), (diborane_file, DIBORANE_HASH), (benzene_file, BENZENE_HASH)):
        if file_hash(path) != expected:
            raise RuntimeError("ELEC-008 byte-sealed source changed: " + str(path))
    iupac = json.loads(iupac_file.read_text(encoding="utf-8"))
    definition = iupac["term"]["definitions"][0]
    notes = definition["notes"]
    require(definition["text"], ("electron density", "localized bonds"), "IUPAC definition")
    require(notes["1"], ("ribbon", "surface", "volume", "benzene", "carboranes"), "IUPAC topology note")
    require(notes["2"], ("not associated with a particular atom", "extended orbital", "several to many atoms"), "IUPAC support note")

    diborane_text = plain(diborane_file.read_text(encoding="utf-8", errors="strict"))
    benzene_text = plain(benzene_file.read_text(encoding="utf-8", errors="strict"))
    require(diborane_text, ("Listing of experimental geometry data for B 2 H 6", "Point Group D 2h", "rBB 1.763", "rBH 1.200", "outer H", "rBH 1.320", "bridging", "aBHB 83.8"), "NIST diborane")
    require(benzene_text, ("Listing of experimental geometry data for C 6 H 6", "Point Group D 6h", "rCC 1.397", "rCH 1.084", "aCCC 120", "C:C 6", "H-C 6"), "NIST benzene")

    source_rows = (
        ("IUPAC-DELOCALIZATION-DEFINITION", "IUPAC-GOLD-BOOK-08789-2026", IUPAC_PATH, file_hash(iupac_file), "definition", definition["text"]),
        ("IUPAC-DELOCALIZATION-RIBBON", "IUPAC-GOLD-BOOK-08789-2026", IUPAC_PATH, file_hash(iupac_file), "ribbon-topology", notes["1"]),
        ("IUPAC-DELOCALIZATION-SURFACE", "IUPAC-GOLD-BOOK-08789-2026", IUPAC_PATH, file_hash(iupac_file), "surface-topology", notes["1"]),
        ("IUPAC-DELOCALIZATION-VOLUME", "IUPAC-GOLD-BOOK-08789-2026", IUPAC_PATH, file_hash(iupac_file), "volume-topology", notes["1"]),
    )
    identities = []
    targets = []
    for target_id, source_id, path, source_hash, role, inscription in source_rows:
        identities.append({"target_id": target_id, "source_id": source_id, "source_url": "https://goldbook.iupac.org/terms/view/08789", "snapshot_path": path, "snapshot_hash": source_hash, "record_role": role})
        targets.append({"target_id": target_id, "source_id": source_id, "record_kind": "authoritative-delocalization-topology", "record_role": role, "inscription": inscription, "snapshot_path": path, "snapshot_hash": source_hash})

    nist_rows = (
        ("NIST-DIBORANE-POINT-GROUP", "diborane", "point-group", "D2h", "absence", "absence"),
        ("NIST-DIBORANE-rBB", "diborane", "rBB", "1.763", 1763, 1000),
        ("NIST-DIBORANE-rBH-OUTER", "diborane", "rBH-outer", "1.200", 1200, 1000),
        ("NIST-DIBORANE-rBH-BRIDGING", "diborane", "rBH-bridging", "1.320", 1320, 1000),
        ("NIST-DIBORANE-aHBH-OUTER", "diborane", "aHBH-outer", "121", 121, 1),
        ("NIST-DIBORANE-aHBH-BRIDGING", "diborane", "aHBH-bridging", "96.2", 962, 10),
        ("NIST-DIBORANE-aBHB", "diborane", "aBHB", "83.8", 838, 10),
        ("NIST-DIBORANE-aHBH-SYMMETRY", "diborane", "aHBH-symmetry", "109.2", 1092, 10),
        ("NIST-DIBORANE-HB-LINK-COUNT", "diborane", "H-B-count", "8", 8, 1),
        ("NIST-BENZENE-POINT-GROUP", "benzene", "point-group", "D6h", "absence", "absence"),
        ("NIST-BENZENE-rCC", "benzene", "rCC", "1.397", 1397, 1000),
        ("NIST-BENZENE-rCH", "benzene", "rCH", "1.084", 1084, 1000),
        ("NIST-BENZENE-aCCC", "benzene", "aCCC", "120", 120, 1),
        ("NIST-BENZENE-aHCC", "benzene", "aHCC", "120", 120, 1),
        ("NIST-BENZENE-AROMATIC-LINK-COUNT", "benzene", "C:C-count", "6", 6, 1),
        ("NIST-BENZENE-HC-LINK-COUNT", "benzene", "H-C-count", "6", 6, 1),
    )
    for target_id, species, role, inscription, numerator, denominator in nist_rows:
        path = DIBORANE_PATH if species == "diborane" else BENZENE_PATH
        url = DIBORANE_URL if species == "diborane" else BENZENE_URL
        source_hash = file_hash(ROOT / path)
        source_id = "NIST-CCCBDB-SRD101-DIBORANE" if species == "diborane" else "NIST-CCCBDB-SRD101-BENZENE"
        identities.append({"target_id": target_id, "source_id": source_id, "source_url": url, "snapshot_path": path, "snapshot_hash": source_hash, "record_role": role})
        targets.append({"target_id": target_id, "source_id": source_id, "record_kind": "experimental-geometry", "species": species, "record_role": role, "inscription": inscription, "positive_value_numerator": numerator, "positive_value_denominator": denominator, "snapshot_path": path, "snapshot_hash": source_hash})
    source = {"bodies": ["International Union of Pure and Applied Chemistry", "National Institute of Standards and Technology"], "retrieval_date": "2026-07-26", "record_count": len(targets)}
    IDENTITIES.write_text(json.dumps({"schema": "sft-v3-multicentre-identities/1", "source": source, "rows": identities}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGETS.write_text(json.dumps({"schema": "sft-v3-multicentre-withheld-targets/1", "source": source, "rows": targets}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("records:", len(targets))
    print("IUPAC records:", len(source_rows))
    print("NIST diborane records:", sum(row[1] == "diborane" for row in nist_rows))
    print("NIST benzene records:", sum(row[1] == "benzene" for row in nist_rows))
    print("IUPAC snapshot:", file_hash(iupac_file))
    print("diborane snapshot:", file_hash(diborane_file))
    print("benzene snapshot:", file_hash(benzene_file))
    print("identity registry:", file_hash(IDENTITIES))
    print("target registry:", file_hash(TARGETS))


if __name__ == "__main__":
    main()

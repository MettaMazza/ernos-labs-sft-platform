#!/usr/bin/env python3
"""Verify the E04 2.0.0 review release and publication boundary."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
BOOK = ROOT / "edu/books/E04-look-again-how-we-check"
SOURCE = BOOK / "source/book-v2.0.0.json"
MANIFEST = BOOK / "book-manifest.json"
CLAIMS = BOOK / "claim-map-v2.0.0.json"
HTML = BOOK / "accessible/student-book-v2.0.0.html"
STUDENT = ROOT / "output/pdf/edu/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK/2.0.0/SFT-E04-Look-Again-How-We-Check-v2.0.0.pdf"
ADULT = ROOT / "output/pdf/edu/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK/2.0.0/SFT-E04-Adult-Guide-v2.0.0.pdf"
CHECKSUMS = BOOK / "editions/2.0.0/CHECKSUMS.sha256"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL E04 2.0.0: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if book["version"] != "2.0.0" or len(pages) != 32:
        fail("source version or page count")
    if [p["page"] for p in pages] != list(range(1, 33)):
        fail("page sequence")
    if sum(1 for p in pages if p.get("activity")) != 11:
        fail("expected eleven paper activities")
    if book["permanent_cast"] != ["Mia", "Sol", "Tavi"] or book["guest"] != "Ivo":
        fail("cast continuity")
    if "OpenMoji" not in book["stable_item_rule"]:
        fail("stable emoji rule")
    if any("Mira" in json.dumps(p) for p in pages):
        fail("legacy name Mira remains")
    if pages[2]["scene"] != "gate" or pages[30]["scene"] != "look":
        fail("closed-to-open gate continuity")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["version"] != "2.0.0" or manifest["medium"] != "paper_native_picture_book":
        fail("manifest version or medium")
    if manifest["final_publication"]["approved"]:
        fail("publication approval incorrectly set")

    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    expected = {"SFT-FOUNDATION-DERIVATION-TRACE-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001", "SFT-ENG-INDEPENDENT-CHECK-001"}
    if {c["claim_id"] for c in claims["scientific_claims"]} != expected:
        fail("claim set")
    for claim in claims["scientific_claims"]:
        receipt_path = ROOT / claim["receipt_path"]
        if not receipt_path.exists():
            fail(f"missing receipt {receipt_path}")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("claim_id") != claim["claim_id"] or receipt.get("receipt_hash") != claim["receipt_hash"]:
            fail(f"receipt identity {claim['claim_id']}")

    html_text = HTML.read_text(encoding="utf-8")
    if len(re.findall(r"<section ", html_text)) != 32:
        fail("accessible HTML page count")
    if html_text.count("This page is a paper activity") != 11:
        fail("accessible activity labels")

    for pdf_path, count in ((STUDENT, 32), (ADULT, 4)):
        if not pdf_path.exists():
            fail(f"missing PDF {pdf_path}")
        reader = PdfReader(str(pdf_path))
        if len(reader.pages) != count:
            fail(f"page count for {pdf_path.name}")
        if (reader.metadata.author or "") != "Maria Smith":
            fail(f"author metadata for {pdf_path.name}")
        if len("".join(page.extract_text() or "" for page in reader.pages)) < 1000:
            fail(f"extractable text for {pdf_path.name}")

    if not CHECKSUMS.exists():
        fail("versioned checksum file is missing")
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        target = ROOT / rel
        if not target.exists() or sha(target) != digest:
            fail(f"checksum mismatch: {rel}")

    publication = ROOT / "publications/education/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK"
    if publication.exists():
        fail("review edition leaked into publications/education")
    print("PASS E04 2.0.0: source, receipts, stable emoji, accessible edition, PDFs and publication boundary")


if __name__ == "__main__":
    main()

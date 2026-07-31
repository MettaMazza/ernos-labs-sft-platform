#!/usr/bin/env python3
"""Verify the complete E03 review-book package."""

from __future__ import annotations

import json
import hashlib
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
BOOK = Path(__file__).resolve().parents[1]
SOURCE = BOOK / "source" / "book-v1.0.0.json"
CLAIM_MAP = BOOK / "claim-map.json"
MANIFEST = BOOK / "book-manifest.json"
CHECKSUMS = BOOK / "CHECKSUMS.sha256"
HTML = BOOK / "accessible" / "student-book-v1.0.0.html"
RELEASE = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN" / "1.0.0"
STUDENT = RELEASE / "SFT-E03-The-Fold-Makes-A-Pattern-v1.0.0.pdf"
ADULT = RELEASE / "SFT-E03-Adult-Guide-v1.0.0.pdf"
ART = ROOT / "edu" / "games" / "companion-adventures" / "public" / "art" / "stages" / "e03-source"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class SectionCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.pages = 0
        self.figures = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "section" and "page" in (values.get("class") or "").split():
            self.pages += 1
        if tag == "figure" and values.get("role") == "img" and values.get("aria-label"):
            self.figures += 1


def main() -> None:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    claims = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(book["version"] == "1.0.0" and book["status"] == "review", "source is not review 1.0.0")
    require(claims["version"] == "1.0.0", "claim map must match the 1.0.0 review")
    require(manifest["version"] == "1.0.0" and manifest["status"] == "review", "manifest is not review 1.0.0")
    require(manifest["final_publication"]["approved"] is False, "review build must not be marked approved")
    require(all(manifest["release_checks"].values()), "one or more manifest release checks are not recorded as passed")
    for artifact in manifest["artifacts"]:
        require((ROOT / artifact["path"]).is_file(), f"missing manifest artifact: {artifact['path']}")
    require(len(book["pages"]) == 32, "student source must contain 32 pages")
    require([p["page"] for p in book["pages"]] == list(range(1, 33)), "student page order is broken")
    require(all(p.get("alt", "").strip() for p in book["pages"]), "every student page needs a picture description")
    require(len(book["reading_codes"]) == 8, "E03 must contain eight optional picture codes")
    require(len({entry["code"] for entry in book["reading_codes"]}) == 8, "E03 picture codes must be unique")
    child_copy = " ".join(str(p.get(field, "")) for p in book["pages"] for field in ("text", "subtext", "alt"))
    require("Mira" not in child_copy, "retired character name appears in current child copy")
    require("lights the garden gate" not in child_copy, "unclear arch wording remains in child copy")
    require(len(claims["scientific_claims"]) == 2, "E03 must cite exactly two direct SFT claims")
    for claim in claims["scientific_claims"]:
        receipt = ROOT / claim["receipt_path"]
        require(receipt.is_file(), f"missing receipt: {receipt}")
        receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
        require(receipt_data["claim_id"] == claim["claim_id"], f"receipt claim mismatch: {claim['claim_id']}")
        require(receipt_data["receipt_hash"] == claim["receipt_hash"], f"receipt hash mismatch: {claim['claim_id']}")

    student = PdfReader(str(STUDENT))
    adult = PdfReader(str(ADULT))
    require(len(student.pages) == 32, "student PDF must contain 32 pages")
    require(len(adult.pages) >= 4, "adult guide PDF is unexpectedly short")
    for index, page in enumerate(student.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        require(abs(width - height) < 1, f"student page {index} is not square")
        require((page.extract_text() or "").strip(), f"student page {index} has no extractable text")
    key_text = " ".join((page.extract_text() or "") for page in student.pages).lower()
    for phrase in ("the turning-light trail", "return means", "a pattern is a rule", "route c follows", "leaf comes next"):
        require(phrase in key_text, f"student PDF is missing text: {phrase}")

    parser = SectionCounter()
    parser.feed(HTML.read_text(encoding="utf-8"))
    require(parser.pages == 32, "accessible HTML must contain 32 page sections")
    require(parser.figures == 32, "accessible HTML must contain 32 labelled picture descriptions")

    art_files = sorted(ART.glob("e03-stage-*.png"))
    require(len(art_files) == 4, "E03 must retain four generated source scenes")
    for art in art_files:
        with Image.open(art) as image:
            require(image.width >= 1500 and image.height >= 1000, f"source art is too small: {art.name}")

    challenge_pages = [p["page"] for p in book["pages"] if p["kind"] == "challenge"]
    require(challenge_pages == [7, 10, 12, 16, 19, 23, 26, 28, 30], "challenge sequence changed")
    require(claims["challenge_reveal_pairs"] == [[7, 8], [10, 11], [12, 13], [16, 17], [19, 20], [23, 24], [26, 27], [28, 29], [30, 31]], "challenge/reveal pacing changed")
    require(set(book["pages"][25]["choices"]) == {"route-short", "route-broken", "route-lawful"}, "route choices changed")

    required_checksums = {
        "edu/books/E03-the-fold-makes-a-pattern/README.md",
        "edu/books/E03-the-fold-makes-a-pattern/NARRATIVE_AND_LEARNING_DESIGN.md",
        "edu/books/E03-the-fold-makes-a-pattern/adult-guide.md",
        "edu/books/E03-the-fold-makes-a-pattern/book-manifest.json",
        "edu/books/E03-the-fold-makes-a-pattern/claim-map.json",
        "edu/books/E03-the-fold-makes-a-pattern/editions/1.0.0/RELEASE_RECORD.md",
        "edu/books/E03-the-fold-makes-a-pattern/source/book-v1.0.0.json",
        "edu/books/E03-the-fold-makes-a-pattern/source/render_e03_v1_0.py",
        "edu/books/E03-the-fold-makes-a-pattern/source/verify_e03_v1_0.py",
        "edu/books/E03-the-fold-makes-a-pattern/accessible/student-book-v1.0.0.html",
        "output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/1.0.0/SFT-E03-The-Fold-Makes-A-Pattern-v1.0.0.pdf",
        "output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/1.0.0/SFT-E03-Adult-Guide-v1.0.0.pdf",
    }
    recorded_checksums: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split(maxsplit=1)
        recorded_checksums[relative_path] = digest
    require(set(recorded_checksums) == required_checksums, "E03 checksum boundary is incomplete or contains an unexpected file")
    for relative_path, expected_digest in recorded_checksums.items():
        data = (ROOT / relative_path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected_digest, f"checksum mismatch: {relative_path}")
    print("E03 review book verified")


if __name__ == "__main__":
    main()

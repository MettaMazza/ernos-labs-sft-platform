#!/usr/bin/env python3
"""Verify the complete E03 review-book package."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
BOOK = Path(__file__).resolve().parents[1]
SOURCE = BOOK / "source" / "book-v1.0.0.json"
CLAIM_MAP = BOOK / "claim-map.json"
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
    require(book["version"] == "1.0.0" and book["status"] == "review", "source is not review 1.0.0")
    require(len(book["pages"]) == 32, "student source must contain 32 pages")
    require([p["page"] for p in book["pages"]] == list(range(1, 33)), "student page order is broken")
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
    require(set(book["pages"][25]["choices"]) == {"route-short", "route-broken", "route-lawful"}, "route choices changed")
    print("E03 review book verified")


if __name__ == "__main__":
    main()

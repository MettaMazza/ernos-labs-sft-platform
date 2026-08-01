#!/usr/bin/env python3
"""Release checks for the paper-native E02 review edition 2.0.0."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
BOOK = ROOT / "edu/books/E02-one-whole-many-parts"
SOURCE = BOOK / "source/book-v2.0.0.json"
MANIFEST = BOOK / "book-manifest.json"
CLAIM_MAP = BOOK / "claim-map-v2.0.0.json"
HTML = BOOK / "accessible/student-book-v2.0.0.html"
ADULT = BOOK / "adult-guide-v2.0.0.md"
STUDENT_PDF = ROOT / "output/pdf/edu/SFT-EDU-E02-ONE-WHOLE-MANY-PARTS/2.0.0/SFT-E02-One-Whole-Many-Parts-v2.0.0.pdf"
ADULT_PDF = ROOT / "output/pdf/edu/SFT-EDU-E02-ONE-WHOLE-MANY-PARTS/2.0.0/SFT-E02-Adult-Guide-v2.0.0.pdf"
RECEIPTS = {
    "SFT-FOUNDATION-ONE-001": ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-ONE-001-68332624c276dc5d.json",
    "SFT-FOUNDATION-COUNT-001": ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-COUNT-001-4b2411716cbef2fb.json",
    "SFT-FOUNDATION-PART-001": ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-PART-001-87b40affae50458b.json",
    "SFT-MATH-EXACT-ARITHMETIC-001": ROOT / "receipts/engine/model_admitted/SFT-MATH-EXACT-ARITHMETIC-001-28252bae62373d86.json",
    "SFT-MATH-ARITH-JUNCTION-ADDITION-002": ROOT / "receipts/engine/model_admitted/SFT-MATH-ARITH-JUNCTION-ADDITION-002-ecbb32a37fb10022.json",
}


class SemanticBookParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.main = 0
        self.pages = 0
        self.figures = 0
        self.figure_labels = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "main":
            self.main += 1
        if tag == "section" and "page" in (values.get("class") or "").split():
            self.pages += 1
        if tag == "figure" and values.get("role") == "img":
            self.figures += 1
            if values.get("aria-label"):
                self.figure_labels += 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def all_child_text(book: dict) -> str:
    return "\n".join("\n".join(str(page.get(field, "")) for field in ("heading", "text", "subtext", "alt")) for page in book["pages"])


def page_text(book: dict, number: int) -> str:
    page = book["pages"][number - 1]
    return " ".join(str(page.get(field, "")) for field in ("heading", "text", "subtext", "alt"))


def verify_source() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    require(book["version"] == "2.0.0" and book["status"] == "review", "source release identity is wrong")
    require(book["medium_contract"] == "Connected picture book that works without the companion game", "medium contract drifted")
    pages = book["pages"]
    require(len(pages) == 32 and [p["page"] for p in pages] == list(range(1, 33)), "student book must contain 32 contiguous pages")
    require(all(p.get("alt", "").strip() for p in pages), "every student page needs a picture description")

    expected_activities = {"lantern-detective", "seam-hunt", "count-keeper", "doorway-parade", "same-size-pairs", "missing-place", "add-together", "lantern-builder"}
    activities = [p["activity"] for p in pages if p.get("activity")]
    require(len(activities) == 8 and set(activities) == expected_activities, "E02 must contain eight distinct paper-native activities")

    lower = all_child_text(book).lower()
    for banned in ("candidate grammar", "parameter-free", "equal-fibred", "junction addition", "tap the screen", "drag", "press the button", "submit", "dashboard", "level select"):
        require(banned not in lower, f"child-facing source contains banned term: {banned}")
    for page in pages:
        prose = "\n".join(str(page.get(field, "")) for field in ("heading", "text", "subtext"))
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", prose):
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
            require(len(words) <= 22, f"page {page['page']} has an overlong child sentence ({len(words)} words): {sentence}")

    require(all(name in page_text(book, 3) for name in ("Mia", "Sol", "Tavi")), "permanent trio must open the story")
    require("parcel" in page_text(book, 3).lower() and "tower slide" in page_text(book, 3).lower(), "E01 parcel continuity is not explicit")
    require("opened the parcel" in page_text(book, 4).lower() and "one red moon lantern" in page_text(book, 4).lower(), "the whole lantern must be visibly introduced before separation")
    require("too wide to fit" in page_text(book, 6).lower(), "the little-door problem must be explicit")
    require("Pax" in page_text(book, 7) and "helper" in page_text(book, 7).lower(), "Pax must be the sole plainly introduced E02 guest")
    require("these are seams" in page_text(book, 10).lower(), "seam must be defined in context before the activity")
    require("four parts" in page_text(book, 12).lower() and "one part" in page_text(book, 13).lower(), "four parts must be experienced before the term is reinforced")
    require("did not skip" in page_text(book, 15).lower() and "twice" in page_text(book, 15).lower(), "clear count must state skip and repeat boundaries")
    require("no part stayed behind" in page_text(book, 18).lower(), "the carrying result must keep all four parts")
    require("same size" in page_text(book, 20).lower() and "pair a" in page_text(book, 21).lower(), "size comparison and answer are missing")
    require("empty place" in page_text(book, 22).lower() and "no gap" in page_text(book, 23).lower(), "missing-place challenge and reveal are incomplete")
    require("2 parts + 2 parts = 4 parts" in page_text(book, 26), "exact two-plus-two equation is missing")
    require("1 part + 1 part + 1 part + 1 part = 4 parts" in page_text(book, 29), "exact one-part junction equation is missing")
    require("Four parts make 1 whole lantern" in page_text(book, 29), "reassembly statement is missing")
    require("equals sign" in page_text(book, 30).lower() and "same four parts" in page_text(book, 30).lower(), "final lesson must explain the equality correspondence")
    require("kept every part" in page_text(book, 31).lower() and "rebuilt the same whole" in page_text(book, 31).lower(), "ending must close the actual action")
    require("fourth space stayed blank" in page_text(book, 32).lower(), "E03 teaser must show an unanswered place")

    emoji_dir = ROOT / "edu/assets/openmoji/16.0.0/color/png-512"
    for filename in ("1F4E6.png", "1F3EE.png", "1F319.png", "2600.png", "1F6AA.png", "2B50.png", "2B1C.png"):
        require((emoji_dir / filename).is_file(), f"missing stable OpenMoji asset: {filename}")
    part_dir = ROOT / "edu/assets/openmoji/16.0.0/derived/lantern-parts"
    for name in ("top-left", "top-right", "bottom-left", "bottom-right"):
        require(part_dir.joinpath(f"lantern-{name}-tile.png").is_file(), f"missing stable lantern part: {name}")
    require(all(spec["id"].startswith("part-") for n in (12,13,15,16,18,19,24,25,26) for spec in pages[n-1].get("emoji", [])), "a repeated quarter was replaced by a non-part asset")
    return book


def verify_records() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    claim_map = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    require(manifest["version"] == "2.0.0" and manifest["status"] == "review", "manifest release identity is wrong")
    require(manifest["series_continuity"]["permanent_team"] == ["Mia", "Sol", "Tavi"], "permanent team drifted")
    require(manifest["series_continuity"]["book_guest"] == "Pax", "E02 guest drifted")
    require(manifest["final_publication"]["approved"] is False, "review edition must not claim publication approval")
    require(claim_map["version"] == "2.0.0" and claim_map["external_models_in_derivation"] is False, "claim-map identity or authority boundary is wrong")
    require({c["claim_id"] for c in claim_map["scientific_claims"]} == set(RECEIPTS), "claim-map receipt set drifted")
    for receipt in RECEIPTS.values():
        require(receipt.is_file(), f"admitted receipt is missing: {receipt.name}")
    require(BOOK.joinpath("book-manifest-v1.0.0.json").is_file(), "historical manifest was not preserved")
    require(BOOK.joinpath("claim-map-v1.0.0.json").is_file(), "historical claim map was not preserved")


def verify_accessible_html() -> None:
    parser = SemanticBookParser()
    parser.feed(HTML.read_text(encoding="utf-8"))
    require(parser.main == 1, "accessible edition needs one main landmark")
    require(parser.pages == 32, "accessible edition needs 32 semantic page sections")
    require(parser.figures == 32 and parser.figure_labels == 32, "every accessible page needs a labelled image role")


def verify_pdfs() -> None:
    student = PdfReader(str(STUDENT_PDF))
    adult = PdfReader(str(ADULT_PDF))
    require(len(student.pages) == 32, "student PDF page count is wrong")
    require(len(adult.pages) == 5, "adult guide PDF must be five complete pages")
    require(student.metadata.get("/Author") == "Maria Smith", "student PDF author metadata is wrong")
    require(adult.metadata.get("/Author") == "Maria Smith", "adult PDF author metadata is wrong")
    student_text = " ".join(("\n".join(page.extract_text() or "" for page in student.pages)).split())
    adult_text = " ".join(("\n".join(page.extract_text() or "" for page in adult.pages)).split())
    for phrase in ("One Whole, Many Parts", "Doorway Parade", "2 parts + 2 parts = 4 parts", "The equals sign showed"):
        require(phrase in student_text, f"student PDF is missing extractable text: {phrase}")
    for phrase in ("SFT-FOUNDATION-ONE-001", "SFT-FOUNDATION-COUNT-001", "SFT-FOUNDATION-PART-001", "awaiting Maria Smith"):
        require(phrase.lower() in adult_text.lower(), f"adult PDF is missing source or boundary text: {phrase}")
    require(STUDENT_PDF.stat().st_size > 1_000_000, "student PDF appears to be missing illustrations")
    require(ADULT_PDF.stat().st_size > 8_000, "adult PDF appears incomplete")


def verify_no_publication_copy() -> None:
    publications = ROOT / "publications/education"
    if publications.exists():
        candidates = [p for p in publications.rglob("*") if p.is_file() and ("E02" in p.name or "One-Whole-Many-Parts-v2.0.0" in p.name)]
        require(not candidates, "unapproved E02 2.0.0 appears in publications/education")


def verify_checksums() -> None:
    checksum_file = BOOK / "editions/2.0.0/CHECKSUMS.sha256"
    require(checksum_file.is_file(), "versioned checksum file is missing")
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.is_file(), f"checksummed artifact is missing: {relative}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"checksum mismatch: {relative}")


def main() -> None:
    verify_source()
    verify_records()
    verify_accessible_html()
    verify_pdfs()
    verify_no_publication_copy()
    verify_checksums()
    require(ADULT.is_file(), "versioned adult guide source is missing")
    print("PASS E02 2.0.0: source, records, stable emoji, accessible edition, PDFs and publication boundary")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL E02 2.0.0: {exc}", file=sys.stderr)
        raise

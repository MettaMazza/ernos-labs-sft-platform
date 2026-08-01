#!/usr/bin/env python3
"""Release checks for the rebuilt paper-native E01 review edition 2.0.0."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
BOOK = ROOT / "edu/books/E01-something-is-here"
SOURCE = BOOK / "source/book-v2.0.0.json"
MANIFEST = BOOK / "book-manifest.json"
CLAIM_MAP = BOOK / "claim-map-v2.0.0.json"
HTML = BOOK / "accessible/student-book-v2.0.0.html"
ADULT = BOOK / "adult-guide-v2.0.0.md"
STUDENT_PDF = ROOT / "output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/2.0.0/SFT-E01-Something-Is-Here-v2.0.0.pdf"
ADULT_PDF = ROOT / "output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/2.0.0/SFT-E01-Adult-Guide-v2.0.0.pdf"
RECEIPT = ROOT / "receipts/engine/model_admitted/SFT-ROOT-THERE-IS-NO-NOTHING-711864171e4d3a2f.json"


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


def fail(message: str) -> None:
    raise AssertionError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def all_child_text(book: dict) -> str:
    return "\n".join("\n".join(str(page.get(field, "")) for field in ("heading", "text", "subtext", "alt")) for page in book["pages"])


def page_text(book: dict, number: int) -> str:
    page = book["pages"][number - 1]
    return " ".join(str(page.get(field, "")) for field in ("heading", "text", "subtext", "alt"))


def verify_source() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    require(book["version"] == "2.0.0", "student source version must be 2.0.0")
    require(book["status"] == "review", "edition must remain a review")
    require(book["medium_contract"] == "Connected picture book that works without the companion game", "medium contract drifted")
    pages = book["pages"]
    require(len(pages) == 32, "student book must contain exactly 32 pages")
    require([p["page"] for p in pages] == list(range(1, 33)), "page numbers must be contiguous")
    require(all(p.get("alt", "").strip() for p in pages), "every page needs a picture description")

    activities = [p for p in pages if p.get("activity")]
    require(len(activities) == 8, "E01 must contain eight paper-native activities")
    require({p["activity"] for p in activities} == {"spot-note", "teddy-trail", "listen", "blank-or-mark", "nothing-word", "curtain-memory", "two-shelves", "final-match"}, "activity identifiers drifted")

    text = all_child_text(book)
    lower = text.lower()
    for banned in ("candidate grammar", "counterexample", "operational boundary", "direct forcing", "derivational object", "tap the screen", "drag", "press the button", "submit", "dashboard", "level select"):
        require(banned not in lower, f"child-facing source contains banned term: {banned}")

    for page in pages:
        prose = "\n".join(str(page.get(field, "")) for field in ("heading", "text", "subtext"))
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", prose):
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
            require(len(words) <= 22, f"page {page['page']} has an overlong child sentence ({len(words)} words): {sentence}")

    require(all(name in " ".join(page_text(book, n) for n in range(3, 5)) for name in ("Mia", "Sol", "Tavi")), "permanent team must be introduced before the note")
    require("slid through its slot" in page_text(book, 6) and "landed" in page_text(book, 6), "note arrival must be visible and explicit")
    require("picked it up" in page_text(book, 8), "Mia must pick up the note before reading it")
    require("inside" in page_text(book, 10).lower(), "the teddy must be visibly inside before the empty result")
    require("not inside" in page_text(book, 12).lower(), "empty must be explained after the teddy moves")
    require("Nori" in " ".join(page_text(book, n) for n in range(13, 17)), "Nori must be the E01 guest")
    require("rang" in page_text(book, 15).lower() and "waited" in page_text(book, 15).lower(), "sound must happen before quiet is checked")
    require("no marks" in page_text(book, 17).lower() and "blank" in page_text(book, 19).lower(), "blank must be experienced before it is named")
    require("could not see" in page_text(book, 22).lower() and "there was the teddy" in page_text(book, 24).lower(), "hidden setup and reveal must both be explicit")
    require("shelf with a card" in page_text(book, 26).lower() and "shelf with no card" in page_text(book, 26).lower(), "both shelf results must be inspected")
    require("secret thing called nothing" in page_text(book, 30).lower(), "final lesson must state what the team did not find")
    require("clear words" in page_text(book, 30).lower() and "what really happened" in page_text(book, 30).lower(), "final lesson must explain why the distinction matters")
    require("slide" in page_text(book, 31).lower() and "parcel" in page_text(book, 31).lower(), "E02 preview must have a visible causal route")

    expected_emoji = {
        "note": "1F4DD.png", "box": "1F4E6.png", "teddy": "1F9F8.png", "bell": "1F514.png",
        "blank": "2B1C.png", "pencil": "270F.png", "door": "1F6AA.png", "star": "2B50.png",
    }
    emoji_dir = ROOT / "edu/assets/openmoji/16.0.0/color/png-512"
    for object_name, filename in expected_emoji.items():
        require((emoji_dir / filename).is_file(), f"missing stable {object_name} emoji asset")
    return book


def verify_records() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    claim_map = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    require(manifest["version"] == "2.0.0" and manifest["status"] == "review", "manifest release identity is wrong")
    require(manifest["series_continuity"]["permanent_team"] == ["Mia", "Sol", "Tavi"], "manifest permanent team drifted")
    require(manifest["series_continuity"]["book_guest"] == "Nori", "manifest guest drifted")
    require(manifest["final_publication"]["approved"] is False, "review edition must not claim publication approval")
    require(claim_map["version"] == "2.0.0", "claim map version is wrong")
    require(claim_map["external_models_in_derivation"] is False, "external model entered derivation")
    require(RECEIPT.is_file(), "admitted claim receipt is missing")
    require(BOOK.joinpath("book-manifest-v1.6.0.json").is_file(), "historical manifest was not preserved")
    require(BOOK.joinpath("claim-map-v1.5.0.json").is_file(), "historical claim map was not preserved")


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
    require(len(adult.pages) == 4, "adult guide PDF must be four complete pages")
    require(student.metadata.get("/Author") == "Maria Smith", "student PDF author metadata is wrong")
    require(adult.metadata.get("/Author") == "Maria Smith", "adult PDF author metadata is wrong")
    student_text = " ".join(("\n".join(page.extract_text() or "" for page in student.pages)).split())
    adult_text = " ".join(("\n".join(page.extract_text() or "" for page in adult.pages)).split())
    for phrase in ("Something Is Here", "FIND NOTHING", "Hidden is not gone", "Clear words help people understand what really happened"):
        require(phrase in student_text, f"student PDF is missing extractable text: {phrase}")
    for phrase in ("SFT-ROOT-THERE-IS-NO-NOTHING", "No admissible operational statement", "unexpressed metaphysical domain", "awaiting Maria Smith"):
        require(phrase.lower() in adult_text.lower(), f"adult PDF is missing source or boundary text: {phrase}")
    require(STUDENT_PDF.stat().st_size > 1_000_000, "student PDF appears to be missing its illustrations")
    require(ADULT_PDF.stat().st_size > 8_000, "adult PDF appears incomplete")


def verify_no_publication_copy() -> None:
    publications = ROOT / "publications/education"
    if publications.exists():
        candidates = [p for p in publications.rglob("*") if p.is_file() and ("E01" in p.name or "Something-Is-Here-v2.0.0" in p.name)]
        require(not candidates, "unapproved E01 2.0.0 appears in publications/education")


def verify_checksums() -> None:
    checksum_file = BOOK / "editions/2.0.0/CHECKSUMS.sha256"
    require(checksum_file.is_file(), "versioned checksum file is missing")
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.is_file(), f"checksummed artifact is missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, f"checksum mismatch: {relative}")


def main() -> None:
    verify_source()
    verify_records()
    verify_accessible_html()
    verify_pdfs()
    verify_no_publication_copy()
    verify_checksums()
    print("PASS E01 2.0.0: source, records, accessible edition, PDFs and publication boundary")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL E01 2.0.0: {exc}", file=sys.stderr)
        raise

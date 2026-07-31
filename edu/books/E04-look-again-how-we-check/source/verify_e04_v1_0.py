#!/usr/bin/env python3
"""Fail-closed source, accessibility, receipt and PDF checks for E04 1.0.0."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.0.json"
CLAIM_MAP = BOOK_DIR / "claim-map.json"
MANIFEST = BOOK_DIR / "book-manifest.json"
HTML = BOOK_DIR / "accessible" / "student-book-v1.0.0.html"
STUDENT_PDF = BOOK_DIR / "editions" / "1.0.0" / "SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf"
ADULT_PDF = BOOK_DIR / "editions" / "1.0.0" / "SFT-E04-Adult-Guide-v1.0.0.pdf"
CHECKSUMS = BOOK_DIR / "CHECKSUMS.sha256"

EXPECTED_PAIRS = [(7, 8), (10, 11), (13, 14), (15, 16), (18, 19), (21, 22), (24, 25), (26, 27), (29, 30)]
EXPECTED_CODES = ["LOOKCLOSE", "SIGNMAKER", "KEEPFIRST", "SPOTCHANGE", "FOLLOWSTEPS", "WIDTHONLY", "FRIENDCHECK", "MOREWORK", "ALLCHECKED"]
EXPECTED_CLAIMS = {
    "SFT-FOUNDATION-DERIVATION-TRACE-001": "sha256:457414dd7e3a14e44b200b1ac329cdc9e2bb3527abe901c3255d7fb6f9233c5e",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001": "sha256:a4e409f6bb8b203de746bd0c21d3f2566e8052003219490c657249e11f6f2086",
    "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001": "sha256:0e21ffcb217271ddfab4000901691761c2b7fd423b93d27f81ab757f0300c58c",
    "SFT-ENG-INDEPENDENT-CHECK-001": "sha256:927d1b0f871cb92e06ae180a9c1fbcf6b2fe0a024135fb487fbf41a9b082b364",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class AccessibleAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.in_main = False
        self.sections = 0
        self.figures = 0
        self.page_ids: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "main":
            self.in_main = True
        elif tag == "section" and self.in_main and "page" in (values.get("class") or "").split():
            self.sections += 1
            self.page_ids.append(values.get("id") or "")
        elif tag == "figure" and values.get("role") == "img" and values.get("aria-label"):
            self.figures += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self.in_main = False

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def verify_sources() -> tuple[dict, dict, dict]:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    claim_map = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pages = book["pages"]

    require(book["book_id"] == "SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK", "book ID drift")
    require(book["title"] == "Look Again: How We Check", "title drift")
    require(book["subtitle"] == "The Garden Welcome Sign", "subtitle drift")
    require(book["version"] == "1.0.0" and book["status"] == "review", "review version drift")
    require(len(pages) == 32, "E04 must contain 32 pages")
    require([page["page"] for page in pages] == list(range(1, 33)), "page sequence is not contiguous")
    require(all(page.get("text", "").strip() for page in pages), "a page has no child text")
    require(all(page.get("subtext", "").strip() for page in pages), "a page has no child prompt")
    require(all(page.get("alt", "").strip() for page in pages), "a page has no picture description")
    require(len({page["alt"] for page in pages}) == 32, "picture descriptions are not page-specific")

    require(book["permanent_trio"] == ["mia", "sol", "tavi"], "permanent trio drift")
    require(book["new_guest"]["name"] == "Ivo" and book["new_guest"]["count"] == 1, "E04 must introduce exactly one guest, Ivo")
    cast_names = {name for page in pages for name in page.get("cast", [])}
    require(cast_names <= {"mia", "sol", "tavi", "ivo"}, f"unexpected E04 cast member: {sorted(cast_names)}")
    require("ivo" in cast_names and {"mia", "sol", "tavi"} <= cast_names, "main cast or Ivo missing")

    require(book["sign_plan"] == {
        "sun_corner": "SUNFLOWER", "moon_corner": "BEE",
        "leaf_corner": "WATERING CAN", "star_corner": "BOOT",
    }, "source sign mapping drift")
    require("garden gate" in normalized(pages[2]["text"]) and "how can we check our work" in normalized(pages[2]["text"]), "E03 garden-gate continuity missing")
    require("before the morning visitors arrive" in normalized(book["mission"]), "single mission is not time-bound")

    challenge_pages = [page for page in pages if page["kind"] == "challenge"]
    require([(page["page"], page.get("stage")) for page in challenge_pages] == [(left, index) for index, (left, _) in enumerate(EXPECTED_PAIRS, 1)], "nine challenge stages drift")
    for stage, (challenge_number, reveal_number) in enumerate(EXPECTED_PAIRS, 1):
        challenge = pages[challenge_number - 1]
        reveal = pages[reveal_number - 1]
        require(challenge["kind"] == "challenge" and challenge.get("stage") == stage, f"stage {stage} challenge missing")
        require(reveal["kind"] in {"reveal", "result"} and reveal.get("stage") == stage, f"stage {stage} reveal missing")
        require("code" not in challenge, f"stage {stage} challenge leaks an optional code")

    codes = book["reading_codes"]
    require([entry["code"] for entry in codes] == EXPECTED_CODES, "reading-code set drift")
    require([entry["page"] for entry in codes] == [right for _, right in EXPECTED_PAIRS], "codes do not follow reveal pages")
    require(all(entry["required_for_progress"] is False for entry in codes), "a picture code gates progress")
    require([page.get("code") for page in pages if page.get("code")] == EXPECTED_CODES, "page codes differ from code manifest")

    child_text = normalized(" ".join(page["badge"] + " " + page["text"] + " " + page["subtext"] for page in pages))
    for phrase in (
        "observation tells what we can see",
        "guess chooses without that check",
        "keep the first rebuild",
        "a trace is a kept record",
        "the ribbon answered its width question",
        "an independent check uses its own clear path",
        "a check can confirm, disagree, or show that more work is needed",
        "every check has a record",
    ):
        require(phrase in child_text, f"required child explanation missing: {phrase}")
    for adult_term in (
        "deterministic replay", "implementation carrier", "target opening",
        "disposition receipt", "constitutional relation", "candidate grammar",
    ):
        require(adult_term not in child_text, f"unexplained adult term in child text: {adult_term}")

    require(claim_map["challenge_reveal_pairs"] == [list(pair) for pair in EXPECTED_PAIRS], "claim-map challenge pairs drift")
    require(claim_map["external_models_in_derivation"] is False, "external model entered derivation")
    require(claim_map["empirical_claim_added"] is False and claim_map["open_claim_added"] is False, "book added scientific authority")
    mapped_claims = {entry["claim_id"]: entry["receipt_hash"] for entry in claim_map["scientific_claims"]}
    manifest_claims = {entry["claim_id"]: entry["receipt_hash"] for entry in manifest["scientific_sources"]}
    require(mapped_claims == EXPECTED_CLAIMS, "claim-map receipt boundary drift")
    require(manifest_claims == EXPECTED_CLAIMS, "manifest receipt boundary drift")
    for source in manifest["scientific_sources"]:
        receipt_path = REPO / source["receipt_path"]
        require(receipt_path.is_file(), f"missing receipt: {source['receipt_path']}")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(receipt.get("claim_id") == source["claim_id"], f"receipt claim mismatch: {source['claim_id']}")
        require(receipt.get("receipt_hash") == source["receipt_hash"], f"receipt hash mismatch: {source['claim_id']}")
        require(receipt.get("model_admitted") is True, f"source is not model admitted: {source['claim_id']}")

    require(manifest["status"] == "review", "manifest is not review status")
    require(manifest["final_publication"]["approved"] is False, "unapproved E04 entered final-publication state")
    for release_check in (
        "level_four_complete",
        "desktop_end_to_end_passed",
        "phone_end_to_end_passed",
        "tablet_end_to_end_passed",
        "offline_narration_generated",
    ):
        require(manifest["release_checks"][release_check] is True, f"release check not complete: {release_check}")
    for artifact in manifest["artifacts"]:
        require((REPO / artifact["path"]).exists(), f"manifest artifact missing: {artifact['path']}")
    return book, claim_map, manifest


def verify_accessible(book: dict) -> None:
    audit = AccessibleAudit()
    audit.feed(HTML.read_text(encoding="utf-8"))
    require(audit.lang == "en", "accessible HTML language missing")
    require(audit.sections == 32, "accessible HTML page count mismatch")
    require(audit.figures == 32, "accessible HTML picture descriptions missing")
    require(audit.page_ids == [f"page-{number}" for number in range(1, 33)], "accessible page order drift")
    text = normalized(" ".join(audit.text))
    for page in book["pages"]:
        require(normalized(page["alt"]) in text, f"accessible edition missing page {page['page']} description")
        first_sentence = normalized(page["text"].split("\n", 1)[0])
        require(first_sentence in text, f"accessible edition missing page {page['page']} text")
    require("this code is not needed to learn or continue" in text, "accessible code boundary missing")


def verify_pdfs(book: dict) -> None:
    student = PdfReader(str(STUDENT_PDF))
    adult = PdfReader(str(ADULT_PDF))
    require(len(student.pages) == 32, "student PDF page count mismatch")
    require(len(adult.pages) >= 8, "adult guide PDF is unexpectedly short")
    require(student.metadata and student.metadata.title.startswith(book["title"]), "student PDF title metadata missing")
    require(student.metadata and student.metadata.author == "Maria Smith", "student PDF author metadata missing")
    student_text = normalized(" ".join((page.extract_text() or "") for page in student.pages))
    adult_text = normalized(" ".join((page.extract_text() or "") for page in adult.pages))
    for phrase in (
        "look again: how we check", "the garden welcome sign",
        "the bee is in the moon corner", "step 3 is the first change",
        "the width fits", "ivo's check confirms the pictures",
        "the disagreement needed more work", "every check has a record",
        "you learned how to check", "the garden gate opens",
    ):
        require(phrase in student_text, f"student PDF missing key page text: {phrase}")
    for phrase in (
        "complete replayable derivation trace",
        "one-way derivation-to-measurement boundary",
        "single fail-closed sft admission law",
        "implementation-distinct check",
        "a measuring tool answers only the question we chose and declared",
        "checking matters because it helps us say what we observed",
        "not an approved final publication",
    ):
        require(phrase in adult_text, f"adult PDF missing required boundary: {phrase}")


def verify_checksums() -> None:
    records: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        records[relative] = digest
    required = [
        "source/book-v1.0.0.json",
        "accessible/student-book-v1.0.0.html",
        "editions/1.0.0/SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf",
        "editions/1.0.0/SFT-E04-Adult-Guide-v1.0.0.pdf",
        "adult-guide.md",
        "claim-map.json",
        "book-manifest.json",
    ]
    require(set(required) <= set(records), "checksum record is incomplete")
    for relative in required:
        require(sha256(BOOK_DIR / relative) == records[relative], f"checksum mismatch: {relative}")


def main() -> None:
    book, _, _ = verify_sources()
    verify_accessible(book)
    verify_pdfs(book)
    verify_checksums()
    print("PASS E04 source: 32 ordered pages, nine setup/reveal stages, one new guest")
    print("PASS E04 boundary: trace, preserved rejection, named measurement questions, fresh friend check")
    print("PASS E04 accessible edition: 32 described pages")
    print(f"PASS E04 student PDF: 32 pages, sha256:{sha256(STUDENT_PDF)}")
    print(f"PASS E04 adult PDF: sha256:{sha256(ADULT_PDF)}")


if __name__ == "__main__":
    main()

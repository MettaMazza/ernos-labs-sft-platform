#!/usr/bin/env python3
"""Fail-closed source, accessibility, receipt and PDF checks for E04 1.0.1."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.1.json"
CLAIM_MAP = BOOK_DIR / "claim-map.json"
MANIFEST = BOOK_DIR / "book-manifest.json"
HTML = BOOK_DIR / "accessible" / "student-book-v1.0.1.html"
STUDENT_PDF = BOOK_DIR / "editions" / "1.0.1" / "SFT-E04-Look-Again-How-We-Check-v1.0.1.pdf"
ADULT_PDF = BOOK_DIR / "editions" / "1.0.1" / "SFT-E04-Adult-Guide-v1.0.1.pdf"
RELEASE_RECORD = BOOK_DIR / "editions" / "1.0.1" / "RELEASE_RECORD.md"
CHECKSUMS = BOOK_DIR / "CHECKSUMS.sha256"

EXPECTED_PAIRS = [(7, 8), (10, 11), (13, 14), (15, 16), (18, 19), (21, 22), (24, 25), (26, 27), (29, 30)]
EXPECTED_CODES = ["LOOKCLOSE", "SIGNMAKER", "KEEPFIRST", "SPOTCHANGE", "FOLLOWSTEPS", "WIDTHONLY", "FRIENDCHECK", "MOREWORK", "ALLCHECKED"]
EXPECTED_CLAIMS = {
    "SFT-FOUNDATION-DERIVATION-TRACE-001": "sha256:457414dd7e3a14e44b200b1ac329cdc9e2bb3527abe901c3255d7fb6f9233c5e",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001": "sha256:a4e409f6bb8b203de746bd0c21d3f2566e8052003219490c657249e11f6f2086",
    "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001": "sha256:0e21ffcb217271ddfab4000901691761c2b7fd423b93d27f81ab757f0300c58c",
    "SFT-ENG-INDEPENDENT-CHECK-001": "sha256:927d1b0f871cb92e06ae180a9c1fbcf6b2fe0a024135fb487fbf41a9b082b364",
}
HISTORICAL_HASHES = {
    "source/book-v1.0.0.json": "befe1309f111975f3ef79cbdce51c8c7d74eff895de03cf29c3c77c75a8605e7",
    "source/generate_accessible_e04.py": "8c8c30c0b87c80c400d7e6766b35bf42e836668b56e183902c6e5b1ae8b417f2",
    "source/render_e04_v1_0.py": "5536a594b8de09d09a0ec11da746dd3a505a651936a899ff2bfc73bda915e9f3",
    "source/verify_e04_v1_0.py": "57c6b946a58432c12a870c15ab49be786653f76232da3e869ae80f2c831e5011",
    "accessible/student-book-v1.0.0.html": "a35112718ce676c0313e7e17e3c8fd6f1ef048a8302ff04db06c8a759e863974",
    "editions/1.0.0/RELEASE_RECORD.md": "38562cc0339a1171becf333316a749f25eca084a32fe8a21a4b72fbe629ff122",
    "editions/1.0.0/SFT-E04-Adult-Guide-v1.0.0.pdf": "8208d63843a8767cd83035c30a795676452620d58b8d13a4b9200bcd8a6cfb3c",
    "editions/1.0.0/SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf": "4ca6a8c079cc60594abfdb48a97061b1ad5c42165480787727bab5c8814dce0a",
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


def child_text(pages: list[dict], through: int | None = None) -> str:
    selected = pages if through is None else pages[:through]
    fields: list[str] = []
    for page in selected:
        fields.extend([page.get("badge", ""), page.get("text", ""), page.get("subtext", "")])
        fields.extend(page.get("labels", []))
    return normalized(" ".join(fields))


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
    require(book["version"] == "1.0.1" and book["status"] == "review", "review version drift")
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
    }, "picture-plan mapping drift")
    require("light shone through the sunrise arch" in normalized(pages[2]["text"]), "E03 light-trail continuity missing")
    require("found a closed garden gate" in normalized(pages[2]["text"]), "garden-gate arrival is missing")
    require("where does the trail lead next" in normalized(pages[2]["text"]), "page 3 asks the wrong opening question")
    require("blank welcome sign" in normalized(pages[3]["text"]) and "picture plan" in normalized(pages[3]["text"]), "page 4 does not reveal the concrete sign problem")
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

    require(pages[12]["choices"] == ["match", "does-not-match", "not-sure"], "page 13 must offer all three honest memory answers")
    require(pages[13]["badge"] == "4 - KEEP SOL'S FIRST TRY", "page 14 does not visibly introduce Stage 4")
    require("ivo kept one card showing each move" in normalized(pages[12]["text"]), "page 13 does not establish step-card capture")
    require("while sol rebuilt" in normalized(pages[16]["text"]) and "one card for each picture" in normalized(pages[16]["text"]), "page 17 step-card continuity is missing")
    require(pages[23]["choices"] == ["same", "different"], "page 24 must ask same or different before confirm")
    require(pages[25]["choices"] == ["guess", "vote", "measure-bottom-to-top"], "page 26 missing-check choices drift")
    require(pages[25]["badge"] == "8 - WHAT HAVE WE NOT CHECKED?", "page 26 does not visibly introduce Stage 8")
    require("bottom to top" in normalized(pages[25]["text"]) and "height" not in normalized(pages[25]["text"]), "page 26 must show the experience before naming height")
    require("that distance is called height" in normalized(pages[26]["text"]), "page 27 does not name height after measuring")
    require("picture plan" in normalized(pages[22]["text"] + " " + pages[22]["alt"]), "Ivo's visible picture plan is missing")
    require("four illustrated cards" in normalized(pages[27]["alt"]), "four recognisable final answer cards are not specified")
    require("five labelled mini-scenes" in normalized(pages[30]["alt"]), "literal page-31 recap scenes are not specified")

    all_child_text = child_text(pages)
    for term, first_page in (("observation", 8), ("width", 20), ("confirm", 25), ("independent", 25), ("height", 27)):
        require(term not in child_text(pages, first_page - 1), f"{term} appears before the child experiences it")
        require(term in child_text(pages, first_page), f"{term} is not named on page {first_page}")
    require("trace" not in all_child_text, "formal trace terminology entered child-facing copy")
    require("first, next and last" in normalized(pages[16]["subtext"]), "page 17 does not explain the step-card order plainly")
    for adult_term in (
        "deterministic replay", "implementation carrier", "target opening",
        "disposition receipt", "constitutional relation", "candidate grammar",
        "source plan", "failed attempt", "fresh path", "declared checkpoint",
        "supported record", "evidence card",
    ):
        require(adult_term not in all_child_text, f"adult jargon remains in child-facing copy: {adult_term}")

    require(claim_map["challenge_reveal_pairs"] == [list(pair) for pair in EXPECTED_PAIRS], "claim-map challenge pairs drift")
    require(claim_map["version"] == "1.0.1", "claim-map version drift")
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

    require(manifest["version"] == "1.0.1" and manifest["status"] == "review", "manifest version or status drift")
    require(manifest["final_publication"]["approved"] is False, "unapproved E04 entered final-publication state")
    release_checks = manifest["release_checks"]
    require(release_checks["phone_end_to_end_passed"] is True, "corrected phone play-through status missing")
    require(release_checks["phone_390x844_full_end_to_end_passed"] is True, "390x844 phone play-through not recorded")
    require(release_checks["desktop_end_to_end_passed"] is False, "desktop is overstated as a full play-through")
    require(release_checks["tablet_end_to_end_passed"] is False, "tablet is overstated as a full play-through")
    require(release_checks["desktop_selector_and_ending_visual_inspected"] is True, "desktop visual inspection missing")
    require(release_checks["tablet_selector_and_ending_visual_inspected"] is True, "tablet visual inspection missing")
    for artifact in manifest["artifacts"]:
        require((REPO / artifact["path"]).exists(), f"manifest artifact missing: {artifact['path']}")

    for relative, expected in HISTORICAL_HASHES.items():
        require(sha256(BOOK_DIR / relative) == expected, f"historical 1.0.0 artifact changed: {relative}")
    return book, claim_map, manifest


def verify_accessible(book: dict) -> None:
    audit = AccessibleAudit()
    audit.feed(HTML.read_text(encoding="utf-8"))
    require(audit.lang == "en", "accessible HTML language missing")
    require(audit.sections == 32, "accessible HTML page count mismatch")
    require(audit.figures == 32, "accessible HTML picture descriptions missing")
    require(audit.page_ids == [f"page-{number}" for number in range(1, 33)], "accessible page order drift")
    text = normalized(" ".join(audit.text))
    require("accessible review 1.0.1" in normalized(HTML.read_text(encoding="utf-8")), "accessible title version drift")
    for page in book["pages"]:
        require(normalized(page["alt"]) in text, f"accessible edition missing page {page['page']} description")
        require(normalized(page["text"]) in text, f"accessible edition missing page {page['page']} text")
    require("does not match" in text and "measure bottom to top" in text, "accessible choice labels are incomplete")
    require("this code is not needed to learn or continue" in text, "accessible code boundary missing")


def verify_pdfs(book: dict) -> None:
    student = PdfReader(str(STUDENT_PDF))
    adult = PdfReader(str(ADULT_PDF))
    require(len(student.pages) == 32, "student PDF page count mismatch")
    require(len(adult.pages) >= 8, "adult guide PDF is unexpectedly short")
    require(student.metadata and student.metadata.title.startswith(book["title"]), "student PDF title metadata missing")
    require(student.metadata and student.metadata.author == "Maria Smith", "student PDF author metadata missing")
    require(student.metadata and "review 1.0.1" in normalized(student.metadata.subject or ""), "student PDF version metadata missing")
    require(adult.metadata and "1.0.1" in (adult.metadata.title or ""), "adult PDF version metadata missing")
    student_text = normalized(" ".join((page.extract_text() or "") for page in student.pages))
    adult_text = normalized(" ".join((page.extract_text() or "") for page in adult.pages))
    for page in book["pages"]:
        require(normalized(page["text"]) in student_text, f"student PDF missing page {page['page']} text")
    for phrase in (
        "does not match", "sol's four step cards", "picture plan covered",
        "bottom to top: not checked yet", "ivo's picture plan", "same", "different",
        "picture-plan comparison", "side-to-side ribbon", "bottom-to-top ribbon",
    ):
        require(phrase in student_text, f"rendered artifact missing required 1.0.1 phrase: {phrase}")
    for phrase in (
        "experience before vocabulary",
        "complete replayable derivation trace",
        "one-way derivation-to-measurement boundary",
        "single fail-closed sft admission law",
        "implementation-distinct check",
        "you checked what was really shown",
        "not an approved final publication",
    ):
        require(phrase in adult_text, f"adult PDF missing required boundary: {phrase}")


def verify_release_record() -> None:
    text = normalized(RELEASE_RECORD.read_text(encoding="utf-8"))
    for phrase in (
        "e04 review 1.0.1", "32 student pages", "9 adult-guide pages",
        "41 rendered page images", "visually inspected", "not finally approved",
    ):
        require(phrase in text, f"release record missing QA statement: {phrase}")


def verify_checksums() -> None:
    records: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        records[relative] = digest
    required = {
        "LICENSE.md", "NARRATIVE_AND_LEARNING_DESIGN.md", "README.md",
        "adult-guide.md", "book-manifest.json", "claim-map.json",
        "source/book-v1.0.0.json", "source/book-v1.0.1.json",
        "source/generate_accessible_e04.py", "source/generate_accessible_e04_v1_0_1.py",
        "source/render_e04_v1_0.py", "source/render_e04_v1_0_1.py",
        "source/verify_e04_v1_0.py", "source/verify_e04_v1_0_1.py",
        "accessible/student-book-v1.0.0.html", "accessible/student-book-v1.0.1.html",
        "editions/1.0.0/RELEASE_RECORD.md", "editions/1.0.1/RELEASE_RECORD.md",
        "editions/1.0.0/SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf",
        "editions/1.0.0/SFT-E04-Adult-Guide-v1.0.0.pdf",
        "editions/1.0.1/SFT-E04-Look-Again-How-We-Check-v1.0.1.pdf",
        "editions/1.0.1/SFT-E04-Adult-Guide-v1.0.1.pdf",
    }
    require(required <= set(records), "checksum record is incomplete")
    for relative in sorted(required):
        require(sha256(BOOK_DIR / relative) == records[relative], f"checksum mismatch: {relative}")


def main() -> None:
    book, _, _ = verify_sources()
    verify_accessible(book)
    verify_pdfs(book)
    verify_release_record()
    verify_checksums()
    print("PASS E04 1.0.1 source: 32 ordered pages, nine challenge/reveal stages, one new guest")
    print("PASS E04 1.0.1 pedagogy: experience before vocabulary, three honest memory choices, retained step cards")
    print("PASS E04 1.0.1 visuals: picture plan, separate measurement directions, Ivo plan, four illustrated cards, literal recap")
    print("PASS E04 1.0.1 accessible edition: 32 described pages")
    print("PASS E04 historical preservation: all locked 1.0.0 artifacts unchanged")
    print(f"PASS E04 student PDF: 32 pages, sha256:{sha256(STUDENT_PDF)}")
    print(f"PASS E04 adult PDF: {len(PdfReader(str(ADULT_PDF)).pages)} pages, sha256:{sha256(ADULT_PDF)}")


if __name__ == "__main__":
    main()

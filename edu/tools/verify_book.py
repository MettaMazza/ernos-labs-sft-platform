#!/usr/bin/env python3
"""Fail-closed checks for an SFT educational book package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "edu" / "templates" / "book_manifest.schema.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class AccessibleHTMLAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = None
        self.in_main = False
        self.page_sections = 0
        self.described_figures = 0
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.html_lang = attributes.get("lang")
        elif tag == "main":
            self.in_main = True
        elif tag == "section" and self.in_main and "page" in (attributes.get("class") or "").split():
            self.page_sections += 1
        elif tag == "figure" and attributes.get("role") == "img" and attributes.get("aria-label"):
            self.described_figures += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self.in_main = False

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def verify_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    for field in schema["required"]:
        require(field in manifest, f"manifest required field missing: {field}")
    require(manifest["schema"] == "sft-education-book-manifest/1", "manifest schema mismatch")
    require(re.fullmatch(r"SFT-EDU-[A-Z0-9-]+", manifest["book_id"]) is not None, "book ID is invalid")
    require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", manifest["version"]) is not None, "version is invalid")
    require(manifest["status"] in {"planning", "draft", "review", "live", "superseded", "withdrawn"}, "status is invalid")
    require(manifest["author"] == "Maria Smith", "scientific authorship changed")
    require(manifest["license"] == "CC-BY-4.0", "documentation licence changed")
    require(manifest["knowledge_boundary"]["census_claim_count"] >= 1, "invalid census count")
    for source in manifest["scientific_sources"]:
        receipt = REPO / source["receipt_path"]
        require(receipt.is_file(), f"missing receipt: {receipt}")
        receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
        require(receipt_data.get("claim_id") == source["claim_id"], "receipt claim mismatch")
        require(receipt_data.get("receipt_hash") == source["receipt_hash"], "receipt hash mismatch")
        require(receipt_data.get("model_admitted") is True, "source claim is not model-admitted")
    for artifact in manifest["artifacts"]:
        require((REPO / artifact["path"]).exists(), f"missing artifact: {artifact['path']}")
    return manifest


def verify_e01(manifest_path: Path, manifest: dict) -> None:
    book_dir = manifest_path.parent
    book = json.loads((book_dir / "source" / "book.json").read_text(encoding="utf-8"))
    claim_map = json.loads((book_dir / "claim-map.json").read_text(encoding="utf-8"))
    pages = book["pages"]
    require(len(pages) == 24, "E01 must have 24 pages")
    require([p["page"] for p in pages] == list(range(1, 25)), "page sequence is not continuous")
    require(all(p.get("text", "").strip() for p in pages), "a page has no text")
    require(all(p.get("alt", "").strip() for p in pages), "a page has no illustration description")
    require(len({p["alt"] for p in pages}) == 24, "illustration descriptions are not page-specific")
    require(claim_map["external_models_in_derivation"] is False, "external model entered derivation")
    require(claim_map["empirical_claim_added"] is False, "picture book added an empirical claim")
    require(claim_map["open_claim_added"] is False, "picture book added an open claim as content")
    mapped = claim_map["scientific_claims"][0]
    source = manifest["scientific_sources"][0]
    require(mapped["claim_id"] == source["claim_id"], "claim map differs from manifest")
    require(mapped["receipt_hash"] == source["receipt_hash"], "claim map receipt differs from manifest")

    html_path = book_dir / "accessible" / "student-book.html"
    html_audit = AccessibleHTMLAudit()
    html_audit.feed(html_path.read_text(encoding="utf-8"))
    require(html_audit.html_lang == "en", "accessible HTML language missing")
    require(html_audit.page_sections == 24, "accessible HTML page count mismatch")
    require(html_audit.described_figures == 24, "accessible image descriptions missing")
    html_text = normalized(" ".join(html_audit.text))
    for page in pages:
        require(normalized(page["text"]) in html_text, f"HTML missing page {page['page']} text")
        require(normalized(page["alt"]) in html_text, f"HTML missing page {page['page']} description")

    student_pdf = REPO / manifest["artifacts"][3]["path"]
    adult_pdf = REPO / manifest["artifacts"][4]["path"]
    student = PdfReader(str(student_pdf))
    adult = PdfReader(str(adult_pdf))
    require(len(student.pages) == 24, "student PDF page count mismatch")
    require(len(adult.pages) >= 4, "adult guide PDF is unexpectedly short")
    require(student.metadata and student.metadata.title == book["title"], "student PDF title missing")
    require(student.metadata and student.metadata.author == "Maria Smith", "student PDF author missing")
    student_text = normalized(" ".join((page.extract_text() or "") for page in student.pages))
    adult_text = normalized(" ".join((page.extract_text() or "") for page in adult.pages))
    for page in pages:
        require(normalized(page["text"]) in student_text, f"student PDF missing page {page['page']} text")
    require("no admissible operational statement" in adult_text, "adult guide missing exact theorem")
    require("unexpressed metaphysical domain" in adult_text, "adult guide missing scope boundary")
    require("curriculum" in adult_text and "not scientific dependencies" in adult_text, "external-reference boundary missing")

    print(f"PASS manifest: {manifest_path.relative_to(REPO)}")
    print(f"PASS pages: {len(pages)} canonical, {len(student.pages)} PDF, 24 semantic HTML")
    print(f"PASS illustration descriptions: {html_audit.described_figures}")
    print(f"PASS scientific source: {source['claim_id']} {source['receipt_hash']}")
    print(f"PASS student PDF sha256:{sha256(student_pdf)}")
    print(f"PASS adult PDF sha256:{sha256(adult_pdf)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    require(manifest_path.is_file(), "manifest does not exist")
    manifest = verify_manifest(manifest_path)
    if manifest["book_id"] == "SFT-EDU-E01-SOMETHING-IS-HERE":
        verify_e01(manifest_path, manifest)
    else:
        print(f"PASS manifest: {manifest_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()

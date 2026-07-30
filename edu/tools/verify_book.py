#!/usr/bin/env python3
"""Fail-closed checks for an SFT educational book package."""

from __future__ import annotations

import argparse
import copy
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
    artifacts_by_role = {artifact["role"]: artifact["path"] for artifact in manifest["artifacts"]}
    source_path = REPO / artifacts_by_role["canonical_student_source"]
    book = json.loads(source_path.read_text(encoding="utf-8"))
    overlay = None
    if book.get("schema") == "sft-education-picture-book-overlay/1":
        overlay = book
        base_path = REPO / overlay["base_source"]
        require(base_path.is_file(), f"overlay base source missing: {base_path}")
        book = copy.deepcopy(json.loads(base_path.read_text(encoding="utf-8")))
        book["version"] = overlay["version"]
        book["status"] = overlay["status"]
        book["subtitle"] = overlay["subtitle"]
        for page_number, update in overlay["page_updates"].items():
            page_index = int(page_number) - 1
            require(book["pages"][page_index]["page"] == int(page_number), f"overlay page mismatch: {page_number}")
            book["pages"][page_index].update(update)
    claim_map = json.loads((book_dir / "claim-map.json").read_text(encoding="utf-8"))
    pages = book["pages"]
    expected_pages = 32 if manifest["version"] in {"1.1.0", "1.2.0", "1.3.0", "1.4.0"} else 24
    require(len(pages) == expected_pages, f"E01 {manifest['version']} must have {expected_pages} pages")
    require([p["page"] for p in pages] == list(range(1, expected_pages + 1)), "page sequence is not continuous")
    require(all(p.get("text", "").strip() for p in pages), "a page has no text")
    require(all(p.get("alt", "").strip() for p in pages), "a page has no illustration description")
    require(len({p["alt"] for p in pages}) == expected_pages, "illustration descriptions are not page-specific")
    require(claim_map["external_models_in_derivation"] is False, "external model entered derivation")
    require(claim_map["empirical_claim_added"] is False, "picture book added an empirical claim")
    require(claim_map["open_claim_added"] is False, "picture book added an open claim as content")
    mapped = claim_map["scientific_claims"][0]
    source = manifest["scientific_sources"][0]
    require(mapped["claim_id"] == source["claim_id"], "claim map differs from manifest")
    require(mapped["receipt_hash"] == source["receipt_hash"], "claim map receipt differs from manifest")

    html_path = REPO / artifacts_by_role["semantic_accessible_edition"]
    html_audit = AccessibleHTMLAudit()
    html_audit.feed(html_path.read_text(encoding="utf-8"))
    require(html_audit.html_lang == "en", "accessible HTML language missing")
    require(html_audit.page_sections == expected_pages, "accessible HTML page count mismatch")
    require(html_audit.described_figures == expected_pages, "accessible image descriptions missing")
    html_text = normalized(" ".join(html_audit.text))
    for page in pages:
        require(normalized(page["text"]) in html_text, f"HTML missing page {page['page']} text")
        require(normalized(page["alt"]) in html_text, f"HTML missing page {page['page']} description")

    student_pdf = REPO / artifacts_by_role["student_pdf"]
    adult_pdf = REPO / artifacts_by_role["adult_guide_pdf"]
    student = PdfReader(str(student_pdf))
    adult = PdfReader(str(adult_pdf))
    require(len(student.pages) == expected_pages, "student PDF page count mismatch")
    require(len(adult.pages) >= 4, "adult guide PDF is unexpectedly short")
    require(student.metadata and student.metadata.title.startswith(book["title"]), "student PDF title missing")
    require(student.metadata and student.metadata.author == "Maria Smith", "student PDF author missing")
    student_text = normalized(" ".join((page.extract_text() or "") for page in student.pages))
    adult_text = normalized(" ".join((page.extract_text() or "") for page in adult.pages))
    for page in pages:
        require(normalized(page["text"]) in student_text, f"student PDF missing page {page['page']} text")
    require("no admissible operational statement" in adult_text, "adult guide missing exact theorem")
    require("unexpressed metaphysical domain" in adult_text, "adult guide missing scope boundary")
    require("curriculum" in adult_text and "not scientific dependencies" in adult_text, "external-reference boundary missing")

    if manifest["version"] in {"1.1.0", "1.2.0", "1.3.0", "1.4.0"}:
        require(book["status"] == "review", f"E01 {manifest['version']} canonical source must remain review")
        require(manifest.get("final_publication", {}).get("approved") is False, "unapproved E01 entered final-publication state")
        require(claim_map["educational_sequence"].startswith("experience_then_"), "discovery sequence missing")
        minimum_pairs = 8 if manifest["version"] == "1.4.0" else 10
        require(len(claim_map["challenge_reveal_pairs"]) >= minimum_pairs, "too few challenge/reveal pairs")
        challenge_pages = [page for page in pages if page["kind"] == "challenge"]
        reveal_pages = [page for page in pages if page["kind"] == "reveal"]
        minimum_reveals = 6 if manifest["version"] == "1.4.0" else 8
        require(len(challenge_pages) >= 8 and len(reveal_pages) >= minimum_reveals, "game challenge/reveal structure is incomplete")
        child_text = normalized(" ".join(page["text"] + " " + page["subtext"] for page in pages))
        for adult_term in ("candidate grammar", "direct forcing", "operational boundary", "provenance", "counterexample"):
            require(adult_term not in child_text, f"unexplained adult term remains in child text: {adult_term}")
        require("challenge/reveal" in adult_text, "adult guide does not explain the revised pedagogy")
        if manifest["version"] == "1.4.0":
            require("returning-character guardrail" in adult_text, "adult guide lacks callback guardrail")
            require("must never identify the new answer" in adult_text, "adult guide permits an answer-giving callback")
        else:
            require("page 19 is the setup" in adult_text, "adult guide lacks paired-page answer guidance")
        require("not approved" in adult_text or "awaiting maria smith's approval" in adult_text, "approval boundary missing")

    if manifest["version"] in {"1.2.0", "1.3.0"}:
        require(overlay is not None, f"E01 {manifest['version']} must use its preserved-source overlay")
        require(overlay["visual_contract"]["recognisable_objects"] is True, "recognisable-object contract missing")
        require(overlay["visual_contract"]["challenge_pages_unlabelled"] is True, "challenge label boundary missing")
        if manifest["version"] == "1.2.0":
            require(overlay["visual_contract"]["reveal_pages_explicitly_labelled"] is True, "reveal label contract missing")
        else:
            require(overlay["visual_contract"]["story_words_above_illustrations"] is True, "words-above-art contract missing")
            require(overlay["visual_contract"]["reveal_labels_above_objects"] is True, "labels-above-objects contract missing")
            require(overlay["visual_contract"]["reading_codes_hidden_as_scene_easter_eggs"] is True, "hidden-code contract missing")
        expected_codes = ["ROOMSTAR", "BOXCLUE", "QUIETWINGS", "BLANKEDGE", "CURTAINMAP", "TWODOORS"]
        require([entry["code"] for entry in overlay["reading_codes"]] == expected_codes, "reading code set mismatch")
        require(all(entry["required_for_progress"] is False for entry in overlay["reading_codes"]), "a reading code blocks progress")
        require("something shown for us to look at is called an example" in child_text, "example is not defined at first use")
        if manifest["version"] == "1.2.0":
            require("we have not seen an object from door b yet" in child_text, "no-example experience is not explicit")
        else:
            require("there was no new object from door b for mira to look at" in child_text, "no-example experience is not explicit")
            for poor_phrase in (
                "looking was happening",
                "no ring happened",
                "the container and the looking",
                "declared mark",
                "which happening",
            ):
                require(poor_phrase not in child_text, f"awkward phrase remains in child text: {poor_phrase}")
        require("no example was given" in child_text, "plain experience is not linked to the short term")
        require("a clue is something" in child_text, "clue is not defined")
        require(
            "a container is something" in child_text or "a container holds things" in child_text,
            "container is not defined",
        )
        require("a view is what we can see" in child_text, "view is not defined")

        game_manifest_path = REPO / artifacts_by_role["companion_game_manifest"]
        game_manifest = json.loads(game_manifest_path.read_text(encoding="utf-8"))
        require(game_manifest["book_id"] == manifest["book_id"], "companion game book mismatch")
        require(game_manifest["book_version"] == manifest["version"], "companion game version mismatch")
        require(game_manifest["scientific_source"]["claim_id"] == source["claim_id"], "companion game claim mismatch")
        require(game_manifest["scientific_source"]["receipt_hash"] == source["receipt_hash"], "companion game receipt mismatch")
        require(game_manifest["reading_codes"] == expected_codes, "companion game code set mismatch")
        if manifest["version"] == "1.3.0":
            require(game_manifest["codes_hidden_in_book_scenes"] is True, "companion hidden-code contract missing")
        require(game_manifest["codes_required_for_progress"] is False, "companion code blocks progress")
        require(game_manifest["scientific_content_locked_behind_codes"] is False, "scientific content is code-locked")
        require(game_manifest["personal_data_collected"] is False, "companion game collects personal data")
        require(game_manifest["analytics_enabled"] is False, "companion game enables analytics")
        require(game_manifest["dependency_audit_reviewed"] is True, "companion dependency audit was not reviewed")
        require(game_manifest["remote_hosting_ready"] is False, "companion incorrectly marked hosting-ready")
        require(game_manifest["final_publication"]["approved"] is False, "unapproved companion entered final state")
        require(game_manifest["final_publication"]["hosted"] is False, "companion was marked hosted without authority")

        game_source = (REPO / artifacts_by_role["companion_game_source"]).read_text(encoding="utf-8")
        require(
            "Word helper" in game_source or "word-definition" in game_source,
            "companion word helper missing",
        )
        require("no object has been shown for us to look at yet" in game_source, "companion no-example definition missing")
        require(re.search(r"\bfetch\s*\(", game_source) is None, "companion application makes a network fetch")
        require("localStorage.removeItem" in game_source, "companion local reset missing")
        if manifest["version"] == "1.3.0":
            game_text = normalized(game_source)
            require("five checked clues will light five stars" in game_text, "five-star premise is not established")
            require("no star lights because" in game_text, "practice scene incorrectly implies a star")
            require("all five stars shine. the star door opens" in game_text, "final door lacks its five-star cause")
            require(game_manifest["level_model"].startswith("one continuous story-puzzle level"), "companion remains fragmented")
            for poor_phrase in (
                "looking was happening",
                "no ring happened",
                "the container and the looking",
                "declared mark",
                "which happening",
                "printed on its reveal page",
            ):
                require(poor_phrase not in game_text, f"awkward phrase remains in companion: {poor_phrase}")

        attribution = (REPO / artifacts_by_role["third_party_asset_attribution"]).read_text(encoding="utf-8")
        require("OpenMoji" in attribution and "CC BY-SA 4.0" in attribution, "OpenMoji attribution incomplete")

    if manifest["version"] == "1.4.0":
        require(overlay is None, "E01 1.4.0 must use its complete canonical source")
        require(book["visual_contract"]["words_above_illustrations"] is True, "words-above-art contract missing")
        require(book["visual_contract"]["recognisable_3d_scenes"] is True, "recognisable 3D scene contract missing")
        require(book["visual_contract"]["challenge_before_reveal"] is True, "challenge-first contract missing")
        require(book["visual_contract"]["codes_optional"] is True, "optional-code contract missing")
        require(book["visual_contract"]["answers_locked_by_codes"] is False, "an answer is locked by a code")
        expected_codes = ["ROOMSTAR", "BOXCLUE", "QUIETWINGS", "BLANKEDGE", "CURTAINMAP", "TWODOORS"]
        require([entry["code"] for entry in book["reading_codes"]] == expected_codes, "reading code set mismatch")
        require(all(entry["required_for_progress"] is False for entry in book["reading_codes"]), "a reading code blocks progress")
        require("empty means the toy is not inside" in child_text, "empty is not defined after its experience")
        require("no ring means the bell did not ring during this short listen" in child_text, "bounded no-ring explanation missing")
        require("a blank card is still a card" in child_text, "blank-card distinction missing")
        require("hidden is not gone" in child_text, "hidden distinction missing")
        require("remember means to bring an earlier clue back to mind" in child_text, "remember is not defined")
        for poor_phrase in (
            "looking was happening",
            "no ring happened",
            "the container and the looking",
            "declared mark",
            "which happening",
            "a returning friend asks",
        ):
            require(poor_phrase not in child_text, f"awkward or editorial phrase remains in child text: {poor_phrase}")

        game_manifest_path = REPO / artifacts_by_role["companion_game_manifest"]
        game_manifest = json.loads(game_manifest_path.read_text(encoding="utf-8"))
        require(game_manifest["book_id"] == manifest["book_id"], "companion game book mismatch")
        require(game_manifest["book_version"] == manifest["version"], "companion game version mismatch")
        require(game_manifest["reading_codes"] == expected_codes, "companion game code set mismatch")
        require(game_manifest["codes_required_for_progress"] is False, "companion code blocks progress")
        require(game_manifest["scientific_content_locked_behind_codes"] is False, "scientific content is code-locked")
        require(game_manifest["personal_data_collected"] is False, "companion game collects personal data")
        require(game_manifest["analytics_enabled"] is False, "companion game enables analytics")
        require(game_manifest["network_required_after_install"] is False, "companion game requires a network after installation")
        require(game_manifest["final_publication"]["approved"] is False, "unapproved companion entered final state")
        require(game_manifest["final_publication"]["hosted"] is False, "companion was marked hosted without authority")

        game_source = (REPO / artifacts_by_role["companion_game_source"]).read_text(encoding="utf-8")
        require(re.search(r"\bfetch\s*\(", game_source) is None, "companion application makes a network fetch")
        require("localStorage.removeItem" in game_source, "companion local reset missing")
        continuity = json.loads((REPO / game_manifest["character_continuity"]).read_text(encoding="utf-8"))
        require("natural story encounter" in continuity["policy"], "natural callback rule missing")
        require("never state or expose the new answer" in continuity["policy"], "callback answer guardrail missing")
        require(any("after an attempt" in rule for rule in continuity["callback_guardrails"]), "post-attempt hint rule missing")
        narration = json.loads((REPO / game_manifest["tts_manifest"]).read_text(encoding="utf-8"))
        require(len(narration["lines"]) == 28, "offline narration line count mismatch")
        audio_dir = REPO / "edu/games/companion-adventures/public/audio/e01"
        require(all((audio_dir / f"{line[0]}.mp3").is_file() for line in narration["lines"]), "offline narration file missing")
        art_provenance = (REPO / artifacts_by_role["companion_generated_art_provenance"]).read_text(encoding="utf-8")
        require("six 1.4.0 stage backgrounds" in art_provenance, "generated stage provenance incomplete")

    print(f"PASS manifest: {manifest_path.relative_to(REPO)}")
    print(f"PASS pages: {len(pages)} canonical, {len(student.pages)} PDF, {html_audit.page_sections} semantic HTML")
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

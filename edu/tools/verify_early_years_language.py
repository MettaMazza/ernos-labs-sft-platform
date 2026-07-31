#!/usr/bin/env python3
"""Fail when an Early Years student manuscript slips back into adult prose."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BANNED_CHILD_PHRASES = (
    "brass",
    "rectangular slot",
    "brass slot",
    "folded paper note",
    "registered",
    "generated item",
    "generated row",
    "partition",
    "non-overlapping",
    "fitted tray",
    "positive count",
    "parameter-free",
    "coordinate",
    "multiplicity",
    "provenance",
    "operational boundary",
    "metaphysical",
    "decimal",
    "equivalence",
    "candidate grammar",
    "destination",
    "safely filed",
    "piece-keeper",
    "parcel chute",
    "cream card",
    "rebuild the trace",
    "woke with a clunk",
    "great brass door",
    "magical door",
    "gold seal",
    "passes all three checks",
    "split along the same lines",
)


def sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:[’'][A-Za-z]+)?", text)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(path: Path) -> None:
    book = json.loads(path.read_text(encoding="utf-8"))
    pages = book["pages"]
    require(len(pages) == 32, f"{path}: expected 32 pages")
    require([page["page"] for page in pages] == list(range(1, 33)), f"{path}: page order is broken")

    for page in pages:
        if page["page"] == 2:  # Legal and provenance language is for the adult reader.
            continue
        child_text = " ".join(str(page.get(field, "")) for field in ("badge", "text", "subtext", "alt"))
        lower = child_text.lower()
        for phrase in BANNED_CHILD_PHRASES:
            require(phrase not in lower, f"{path}: page {page['page']} contains adult phrase: {phrase}")
        for sentence in sentences(page.get("text", "")):
            require(
                len(words(sentence)) <= 22,
                f"{path}: page {page['page']} sentence is too long ({len(words(sentence))} words): {sentence}",
            )

    joined = " ".join(page.get("text", "") + " " + page.get("subtext", "") for page in pages).lower()
    if "E01" in book.get("book_id", ""):
        for phrase in (
            "the star door was shut",
            "a note came through the letter box",
            "mira picked up the note and opened it",
            "his brown teddy was inside",
            "empty means there is no toy inside this box",
        ):
            require(phrase in joined, f"{path}: missing clear E01 cause or definition: {phrase}")
        require(joined.index("his brown teddy was inside") < joined.index("the box is empty"), f"{path}: empty answer appears before the teddy is seen")

    if "E02" in book.get("book_id", ""):
        by_page = {page["page"]: (page.get("text", "") + " " + page.get("subtext", "")).lower() for page in pages}
        require("touched the third tile twice" not in by_page[12], f"{path}: page 12 gives away its answer")
        require("pair a was" not in by_page[21], f"{path}: page 21 gives away its answer")
        require("pax held two" not in by_page[26], f"{path}: page 26 gives away its answer")
        require("four-piece" not in by_page[26], f"{path}: page 26 states the whole count before asking")
        require("one space is open" not in by_page[23], f"{path}: page 23 heading gives away its answer")
        require("they are equal in size" in by_page[22], f"{path}: equal in size is not plainly defined after the activity")
        require("whole means every part is here" in by_page[8], f"{path}: whole is not plainly defined after the activity")
        require("parcel from the last adventure rolled down the library ramp" in by_page[3], f"{path}: page 3 does not clearly continue the parcel story")
        require("opened the parcel" in by_page[4], f"{path}: page 4 does not show how the lantern appeared")
        require("too wide to go through the door" in by_page[5], f"{path}: page 5 does not explain the first obstacle")
        require("how can the whole lantern get through the small door" in by_page[5], f"{path}: page 5 does not state the child-facing story question")
        require("take the lantern apart" in by_page[6] and "put the whole lantern together again" in by_page[6], f"{path}: page 6 does not state the learning plan")

    print(f"Early Years language verified: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("books", nargs="+", type=Path)
    args = parser.parse_args()
    for book in args.books:
        verify(book.resolve())


if __name__ == "__main__":
    main()

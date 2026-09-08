# E01 v3: manuscript and first visual sequence

Status: development, not review-ready and not an approved final edition.

## Implemented

- New `source/book-v3.0.0.json`: complete 32-page child manuscript, picture descriptions, activity answers, reading support and object-state requirements. Existing v2 user corrections and historical editions are untouched.
- Revised route: box, bell, card, curtain, shelves; each visible discovery earns one star. The same map is introduced with the note, guides the route and is filed in the library.
- Simple, sentence-case prose; question/reveal page turns; deliberate hiding rather than an unexplained falling toy; explicit library ramp before the sequel parcel.
- Six optional code locations aligned to existing Level 1 code strings, but game unlock behavior and the revised five-star order are not yet synchronised or tested.
- A functioning four-page PDF renderer for manuscript pages 9–12, plus an accessible text/description excerpt. This is a layout proof, not the complete book.
- Stable teddy emoji and a single open-box diagram with explicit inside/outside layers. The interior is visible after removal. No sealed parcel is used to illustrate empty.
- New generated character-reaction vignette, saved in the project with its prompt and asset record.

## Visual checks actually performed

Rendered all four proof pages with Poppler and inspected each. First pass caught a crop cutting Tavi's head and a teddy size change. Increased picture height to preserve all heads, and aligned teddy scale between question and reveal. Re-rendered and inspected all four updated pages. The final pass also includes the visible author credit and development status.

1. Page 9: all three characters visible; open box and inside teddy readable; text above picture; five hollow stars.
2. Page 10: large uncluttered prediction picture; no solved answer; teddy inside; sentence case.
3. Page 11: matching empty interior and teddy outside; labels above objects; no overlap or clipped flaps.
4. Page 12: changed character reaction; empty box remains; teddy outside; exactly the first star gold.

## Build

From repository root, using a Python environment with the book's ReportLab dependency:

```sh
python3 edu/books/E01-something-is-here/source/render_e01_v3_box_proof.py --reveal-art edu/books/E01-something-is-here/art/v3.0.0/story/e01-box-discovery-v3.0.0.png
```

Output directory: `output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/3.0.0-development/`.

## Remaining

Complete and inspect all other page artwork/layouts, add the proper full-edition imprint, produce the matching adult and accessible books, and adapt the game narrative/audio to the changed source. The proof footer map is a progress excerpt; the full map and its five destinations still need their page-7/8 rendering. Hidden codes are specified but not drawn in this proof. Do not promote a book manifest, claim full v3 QA, or move anything into publications/education yet.

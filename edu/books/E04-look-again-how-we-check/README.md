# E04 - Look Again: How We Check

**Shelf:** Early Years / Foundation

**SFT branch:** Foundation, with one bounded Engineering Translation check

**Current working edition:** 1.0.1 review

**Final-publication approval:** pending Maria Smith's decision

*Look Again: How We Check: The Garden Welcome Sign* follows Book Three's
repaired light through the Sunrise Arch to a closed garden gate. Mia, Sol and
Tavi meet one new friend, Ivo, and rebuild a four-picture welcome sign before
the morning visitors arrive.

The child looks at a picture plan before answering, builds and rebuilds the
sign, keeps Sol's first try, follows his four step cards, checks side to side
and bottom to top separately, and compares Ivo's own sign without copying. The
story ends after four recognisable cards answer four clear questions.

## Read and review

- Student PDF: `editions/1.0.1/SFT-E04-Look-Again-How-We-Check-v1.0.1.pdf`
- Adult guide PDF: `editions/1.0.1/SFT-E04-Adult-Guide-v1.0.1.pdf`
- Scalable text edition: `accessible/student-book-v1.0.1.html`
- Canonical student source: `source/book-v1.0.1.json`
- Adult guide source: `adult-guide.md`
- Companion level: `edu/games/companion-adventures/`

The complete 1.0.0 review remains preserved under `source/`, `accessible/` and
`editions/1.0.0/` as historical material. Its renderer and verifier remain
available and are not used to rebuild 1.0.1.

## Rebuild and verify

```bash
python3 edu/books/E04-look-again-how-we-check/source/generate_accessible_e04_v1_0_1.py
python3 edu/books/E04-look-again-how-we-check/source/render_e04_v1_0_1.py
python3 edu/books/E04-look-again-how-we-check/source/verify_e04_v1_0_1.py
python3 edu/tools/verify_book.py edu/books/E04-look-again-how-we-check/book-manifest.json
```

The renderer creates a 32-page square student book and a portrait adult guide.
The verifier checks page order, challenge/reveal boundaries, single-guest canon,
receipt identities, reading-code safety, experience-before-vocabulary order,
the three page-13 choices, step-card continuity, the missing bottom-to-top
check, accessible structure, PDF page counts and required child-facing
language.

## Scientific boundary

The book is bounded to the registered receipt-backed limits recorded in
`claim-map.json`. The Garden Welcome Sign is an educational translation: it is
not a proof object, measuring a wooden board does not select an SFT law, and a
successful classroom activity does not create scientific authority. Outside
curricula, publishing styles, generated art and narration are comparison or
production support only.

## Approval boundary

Version 1.0.1 is a complete working review build. It must not enter
`publications/education/` until Maria Smith explicitly approves this exact
book-and-game version.

Copyright 2026 Maria Smith. Educational text and documentation: CC BY 4.0.
Repository code: Apache-2.0. See `LICENSE.md` for the package boundary.

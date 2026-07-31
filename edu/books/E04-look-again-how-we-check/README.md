# E04 - Look Again: How We Check

**Shelf:** Early Years / Foundation

**SFT branch:** Foundation, with one bounded Engineering Translation check

**Current working edition:** 1.0.0 review

**Final-publication approval:** pending Maria Smith's decision

*Look Again: How We Check: The Garden Welcome Sign* begins at the garden gate
where Book Three ends. Mia, Sol and Tavi meet one new friend, Ivo, and rebuild a
four-picture welcome sign before the morning visitors arrive.

The child looks before guessing, builds from a visible source, covers and
rebuilds it, keeps a failed attempt, follows its step trace, measures one named
question at a time and compares a fresh check made by a friend. The story ends
only after the rebuilt sign has a visible record for every declared check.

## Read and review

- Student PDF: `editions/1.0.0/SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf`
- Adult guide PDF: `editions/1.0.0/SFT-E04-Adult-Guide-v1.0.0.pdf`
- Scalable text edition: `accessible/student-book-v1.0.0.html`
- Canonical student source: `source/book-v1.0.0.json`
- Adult guide source: `adult-guide.md`
- Companion level: `edu/games/companion-adventures/`

## Rebuild and verify

```bash
python3 edu/books/E04-look-again-how-we-check/source/generate_accessible_e04.py
python3 edu/books/E04-look-again-how-we-check/source/render_e04_v1_0.py
python3 edu/books/E04-look-again-how-we-check/source/verify_e04_v1_0.py
python3 edu/tools/verify_book.py edu/books/E04-look-again-how-we-check/book-manifest.json
```

The renderer creates a 32-page square student book and a portrait adult guide.
The verifier checks page order, challenge/reveal boundaries, single-guest canon,
source-receipt identities, reading-code safety, accessible structure, PDF page
counts and required child-facing language.

## Scientific boundary

The book is bounded to the registered receipt-backed limits recorded in
`claim-map.json`. The Garden Welcome Sign is an educational translation: it is
not a proof object, measuring a wooden board does not select an SFT law, and a
successful classroom activity does not create scientific authority. Outside
curricula, publishing styles, generated art and narration are comparison or
production support only.

## Approval boundary

Version 1.0.0 is a complete working review build. It must not enter
`publications/education/` until Maria Smith explicitly approves this exact
book-and-game version.

Copyright 2026 Maria Smith. Educational text and documentation: CC BY 4.0.
Repository code: Apache-2.0. See `LICENSE.md` for the package boundary.

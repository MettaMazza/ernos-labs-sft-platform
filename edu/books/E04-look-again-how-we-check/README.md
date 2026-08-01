# E04 - Look Again: How We Check

**Shelf:** Early Years / Foundation

**SFT branch:** Foundation, with one bounded Engineering Translation check

**Current working edition:** 2.0.0 review

**Final-publication approval:** pending Maria Smith's decision

*Look Again: How We Check: The Garden Welcome Sign* follows Book Three's
repaired light through the Sunrise Arch to a closed garden gate. Mia, Sol and
Tavi meet one new friend, Ivo, and rebuild a four-picture welcome sign before
the morning visitors arrive.

The child looks at a picture plan before answering, keeps Sol's first try,
follows four clear step cards, checks side to side and bottom to top separately,
and compares Ivo's own sign without copying. Repeated teaching objects use
stable OpenMoji emoji; generated art is reserved for settings and characters.

## Read and review

- Student PDF: `output/pdf/edu/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK/2.0.0/SFT-E04-Look-Again-How-We-Check-v2.0.0.pdf`
- Adult guide PDF: `output/pdf/edu/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK/2.0.0/SFT-E04-Adult-Guide-v2.0.0.pdf`
- Scalable text edition: `accessible/student-book-v2.0.0.html`
- Canonical student source: `source/book-v2.0.0.json`
- Adult guide source: `adult-guide-v2.0.0.md`
- Companion level: `edu/games/companion-adventures/`

Earlier 1.0.0 and 1.0.1 reviews remain preserved as historical material. Their
renderers and verifiers are not used to rebuild 2.0.0.

## Rebuild and verify

```bash
python3 edu/books/E04-look-again-how-we-check/source/render_e04_v2_0.py
python3 edu/books/E04-look-again-how-we-check/source/render_e04_adult_v2_0.py
python3 edu/books/E04-look-again-how-we-check/source/verify_e04_v2_0.py
```

The renderers create a 32-page square student book and a four-page portrait
adult guide. The verifier checks page order, eleven paper activities,
single-guest canon, receipt identities, stable emoji use, accessible structure,
PDF page counts and the publication boundary.

## Scientific boundary

The book is bounded to the registered receipt-backed limits recorded in
`claim-map.json`. The Garden Welcome Sign is an educational translation: it is
not a proof object, measuring a wooden board does not select an SFT law, and a
successful classroom activity does not create scientific authority. Outside
curricula, publishing styles, generated art and narration are comparison or
production support only.

## Approval boundary

Version 2.0.0 is a complete working review build. It must not enter
`publications/education/` until Maria Smith explicitly approves this exact
book-and-game version.

Copyright 2026 Maria Smith. Educational text and documentation: CC BY 4.0.
Repository code: Apache-2.0. See `LICENSE.md` for the package boundary.

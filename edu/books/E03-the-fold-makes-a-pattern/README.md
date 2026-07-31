# E03 — The Fold Makes a Pattern

**Shelf:** Early Years / Foundation
**SFT branch:** Foundation
**Current working edition:** 1.0.0 review
**Final-publication approval:** pending Maria Smith's decision

*The Fold Makes a Pattern: The Turning-Light Trail* continues directly from
Book Two. The rebuilt Moon Lantern lights a path that stops before the Sunrise
Arch. Mia, Sol and Tavi meet one new friend, Vee, and the child restores the
path through visible turn, return, recurrence, repair and new-role activities.

The child experiences every distinction before its short name appears. Each
question has a separate reveal page, every role is identified by picture and
name as well as colour, and wrong attempts remain visible long enough to check.

## Read and review

- Student PDF: `output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/1.0.0/SFT-E03-The-Fold-Makes-A-Pattern-v1.0.0.pdf`
- Adult guide PDF: `output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/1.0.0/SFT-E03-Adult-Guide-v1.0.0.pdf`
- Scalable text edition: `accessible/student-book-v1.0.0.html`
- Canonical student source: `source/book-v1.0.0.json`
- Companion level: `edu/games/companion-adventures/`

## Rebuild and verify

```bash
python3 edu/books/E03-the-fold-makes-a-pattern/source/render_e03_v1_0.py
python3 edu/books/E03-the-fold-makes-a-pattern/source/verify_e03_v1_0.py
python3 edu/tools/verify_book.py edu/books/E03-the-fold-makes-a-pattern/book-manifest.json
cd edu/games/companion-adventures
npm test
npm run lint
```

## Scientific boundary

The book is bounded to `SFT-FOUNDATION-FOLD-001` and
`SFT-FOUNDATION-FOLD-DYNAMICS-001` at their registered receipt-backed limits.
The tile, lights, bridge and role games are educational translations, not proof
objects. External curricula, generated art and local voices provide calibration
or production support only and have no authority in SFT derivation.

## Approval boundary

Version 1.0.0 is a complete working review build. It must not enter
`publications/education/` until Maria Smith explicitly approves this exact
book-and-game version.

Copyright 2026 Maria Smith. Educational text and documentation: CC BY 4.0.
Repository code: Apache-2.0. Art and narration provenance are recorded with the
companion game.

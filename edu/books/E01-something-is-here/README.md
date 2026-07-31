# E01 - Something Is Here

**Shelf:** Early Years / Foundation
**SFT branch:** Foundation
**Scientific source:** `SFT-ROOT-THERE-IS-NO-NOTHING`
**Current working edition:** 1.6.0 review
**Final-publication approval:** pending Maria Smith's decision

*Something Is Here: The Star Door Mystery* begins the SFT Open Education
Library. The child follows permanent friends Mira, Sol and Tavi through one
continuous 32-page journey. A note comes through the shut Star Door's letter
box and starts five clues. Each checked clue lights one star, five stars open
the door, two small doors answer the question, and a library scene recalls an
earlier clue. Nori is the one new friend introduced in this adventure.

The child looks, listens, moves, draws, reads and remembers before the story
gives a short meaning. All story words and answer labels sit above the main
illustration. Six optional picture codes are hidden inside scenes, but no code
gates a clue, explanation, route, star or answer.

## Current package

- `source/book-v1.6.0.json` — complete canonical 32-page source and picture
  descriptions.
- `source/render_e01_v1_5.py` — reproducible student PDF, adult PDF and semantic
  HTML renderer.
- `adult-guide.md` — exact SFT source, facilitation, answers, safeguarding,
  accessibility and returning-character rules.
- `claim-map.json` — page-to-claim, vocabulary, code and companion mapping.
- `book-manifest.json` — version, boundary, artifacts and completed checks.
- `accessible/student-book-v1.6.0.html` — scalable semantic edition with a
  visible description and accessible image role for every page.
- `edu/games/companion-adventures/` — the matching offline-first animated game.

Rendered review PDFs are in
`output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/1.6.0/`.

## Rebuild and verify

```bash
python3 -m pip install -r edu/books/E01-something-is-here/source/requirements.txt
python3 edu/books/E01-something-is-here/source/render_e01_v1_5.py
python3 edu/tools/verify_early_years_language.py \
  edu/books/E01-something-is-here/source/book-v1.6.0.json \
  edu/books/E02-one-whole-many-parts/source/book-v0.1.0.json
python3 edu/tools/verify_book.py edu/books/E01-something-is-here/book-manifest.json
cd edu/games/companion-adventures
npm install
npm test
npm run build
```

## Scientific boundary

The book teaches only the independently replicated operational root claim. An
unpresented absence supplies no counterexample, while every presented
counterexample is an occurrence and is not nothing. The scenes do not claim
knowledge of an unexpressed metaphysical domain, add an empirical result or
use an external model as scientific authority.

## Approval boundary

Version 1.6.0 is a complete working review build. It must not enter
`publications/education/current/` until Maria Smith explicitly approves this
exact book-and-game version. Local-network testing is available; public hosting
requires a separate decision and a cleared dependency review.

Copyright 2026 Maria Smith. Educational text and documentation: CC BY 4.0.
Repository code: Apache-2.0. Generated-art and narration provenance are recorded
with the companion game.

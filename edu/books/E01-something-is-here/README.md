# E01 - Something Is Here

**Shelf:** Early Years / Foundation
**SFT branch:** Foundation
**Scientific source:** `SFT-ROOT-THERE-IS-NO-NOTHING`
**Current working edition:** 1.2.0 review
**Final-publication approval:** pending Maria Smith's decision

`Something Is Here` begins the SFT Open Education Library. Version 1.2.0 is a
32-page discovery-led game story in which children help Mira and Pip complete
the Nothing Hunt. Familiar emoji replace abstract shapes. A challenge first
shows recognisable objects without answer labels; the following reveal repeats
the scene and names each object clearly.

Important learning words are experienced and explained in plain language at
first use. For example, the child sees that Door B has not shown an object
before the phrase *no example was given* is introduced.

## Current package

- `source/book-v1.2.0.json` - canonical 1.2.0 overlay, reading codes and image
  descriptions; it keeps the complete 1.1.0 source as an immutable dependency.
- `source/render_e01_v1_2.py` - reproducible OpenMoji PDF and semantic HTML
  generator.
- `adult-guide.md` - exact source, facilitation, vocabulary, complete page
  answers, misconceptions, accessibility and safeguarding.
- `claim-map.json` - page-to-claim, provenance, vocabulary and game mapping.
- `book-manifest.json` - version, boundary, licence, artifacts and checks.
- `accessible/student-book-v1.2.0.html` - generated semantic edition.
- `edu/games/companion-adventures/` - the reading-first text adventure.
- `editions/1.1.0/RELEASE_RECORD.md` - immutable identity of the previous
  working edition.

Rendered review PDFs are written to
`output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/1.2.0/`.

## Rebuild

Install the Python packages in `source/requirements.txt`, then install the game
dependencies so the renderer can read OpenMoji 16 assets:

```bash
python3 -m pip install -r edu/books/E01-something-is-here/source/requirements.txt
cd edu/games/companion-adventures && npm install
python3 edu/books/E01-something-is-here/source/render_e01_v1_2.py
```

Run the companion locally with `npm run dev`; verify it with `npm test`.

## Scientific boundary

The book teaches only the independently replicated operational root claim. An
unpresented absence supplies no counterexample, while every presented example
is an occurrence and therefore is not nothing. The story does not claim
knowledge of an unexpressed metaphysical domain, add a numerical zero or create
an empirical result.

## Approval and hosting boundary

The book and game may be reviewed from `edu/` and GitHub. They must not enter
`publications/education/current/` until Maria Smith explicitly approves this
exact version. The game has not been remotely deployed; hosting needs a
separate explicit decision.

## Licences

Copyright 2026 Maria Smith. Original educational text and documentation are
licensed under CC BY 4.0. Rendering and game code are Apache-2.0 repository
code. OpenMoji-derived book illustrations are CC BY-SA 4.0; full attribution is
recorded in `edu/games/companion-adventures/OPENMOJI_ATTRIBUTION.md`.

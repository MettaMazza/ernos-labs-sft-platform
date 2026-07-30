# E01 illustration and accessibility audit

Edition: 1.3.0 review
Audit date: 30 July 2026
Final-publication approval: pending

## Visual design intent

The 32-page student edition is a continuous visual game story. The parcel on
page 3 introduces the mystery, the map begins with five empty spaces, practice
earns no star, five checked clues light those spaces in order, and the complete
map causes the Star Door to open. Mira and Pip recur throughout, and every
challenge page is followed by a reveal or check. Challenge pages use familiar,
recognisable emoji without answer names. Reveal pages repeat the scene and
attach a written label above every intended answer object. All story words and
instructions also appear above the illustration so the page reads from words
to picture. Optional codes are small details hidden within six reveal scenes.

Printable emoji are OpenMoji 16 colour SVGs rendered as vector artwork. They
are used under CC BY-SA 4.0 with attribution recorded in
`edu/games/companion-adventures/OPENMOJI_ATTRIBUTION.md`. No publisher
illustration or copied character is used. The browser game uses original
generated 3D bitmap artwork recorded in
`edu/games/companion-adventures/ART_PROVENANCE.md`; the generation model is an
illustration tool and has no scientific-authority role.

## Scientific visual accuracy

- Empty-box scenes distinguish the present container from the named toy that is
  not inside.
- Still-bell scenes bound “no ring” to the illustrated listening check and do
  not depict silence as a substance.
- Blank-card scenes retain the card, edge and observers while declaring only
  that no mark is on the card.
- Curtain scenes depict one blocked view, not nonexistence.
- Door A visibly presents a card. Door B uses an empty dashed frame and first
  says that no card has been shown yet. Only afterward does the text introduce
  the short phrase “no example was given.” No hidden counterexample is placed
  in the frame.
- The fair-play boundary contains only show, say, draw and record tokens and
  adds no invented object beyond the declared checking region.

The pictures are educational demonstrations of the operational distinction.
They are not empirical measurements or substitutes for the exact two-class
claim census.

## Description audit

The canonical source contains 32 nonempty, page-specific illustration
descriptions. The semantic HTML attaches each description to its page figure
through `role="img"`, an `aria-label` and a visible figcaption. The automated
verifier checks that every description appears in the semantic edition.

Descriptions name:

- all intended spotting targets;
- the location and relation that matter to the answer;
- extra visual clues where their presence affects fair play;
- text and shape labels that duplicate colour distinctions; and
- whether a frame is deliberately unfilled rather than holding a hidden item.

Descriptions were cross-checked against the exact visible emoji and labels.
They do not claim an arrow, lid, gesture or object absent from the page.

## Perceivability and interaction

- Colour is never the only carrier: targets use numbers, outlines, words,
  distinct object shapes or dashed frames.
- Student text is large, high contrast and set against stable backgrounds.
- Challenges accept pointing, gaze, sign, sound, speech, drawing or a partner
  record.
- Reveals are separated onto later pages so screen-reader and print users both
  receive the challenge before the answer.
- Code hiding is visual play only. The accessible HTML states each code and
  its scene location, and no code is required for learning or progress.
- Important learning words are defined in plain language at first child-facing
  use. The companion game repeats those meanings in a visible definition after
  the relevant experience.
- The adult guide advises reducing scene density, using tactile equivalents and
  allowing extra processing time.
- The certificate records participation rather than ability or attainment.

## Format boundary

The semantic HTML is the primary screen-reader edition and supports browser
text scaling. The PDF contains selectable text and metadata but is not claimed
as a fully tagged PDF. This limitation is stated rather than hidden.

## Render review record

All 32 student pages and all 8 adult-guide pages were rendered from the latest
1.3.0 PDFs to PNG and inspected on 30 July 2026. The review found and corrected:

- words or prompts sitting below illustrations rather than before them;
- reveal labels sitting below the pictures they named;
- oversized code banners, replaced by small scene Easter eggs;
- awkward abstractions, replaced with direct character actions; and
- code positions or object spacing that made labels collide or float apart;
- stars and doors appearing without a narrative cause; and
- a final-door illustration that did not visibly show the offered card.

The corrected full contact sheets show no clipped text, overlapping text,
broken glyph, missing answer label, unreadable contrast or page-number defect.
Challenge and reveal pages remain visually distinct. The eight-page adult guide
has consistent headings, margins, page numbers and footers with no split or
overlap defect.

The rebuilt digital Level One was also played manually from landing page to
ending on desktop, including a wrong first try, recovery, all multi-select
routes, all five star changes, invalid and valid book-code entry, the two-door
result and the delayed recall. The landing page and interactive scene layout
were separately inspected at 390 × 844 mobile and 768 × 1024 tablet viewports.
The review corrected stray sprite-sheet fragments, replaced ambiguous map and
curtain choices, made Door A visibly present its card and confirmed that all
choice names sit above their illustrations.

Visual rendering and accessibility review therefore pass for the 1.3.0 review
edition. This pass does not constitute Maria Smith's final-publication
approval.

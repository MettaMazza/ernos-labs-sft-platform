# E01 illustration and accessibility audit

Edition: 1.2.0 review
Audit date: 30 July 2026
Final-publication approval: pending

## Visual design intent

The 32-page student edition is a continuous visual game story. Mira and Pip
recur throughout, a treasure map retains the five-clue progression, and every
challenge page is followed by a reveal or check. Challenge pages use familiar,
recognisable emoji without answer names. Reveal pages repeat the scene and
attach a written label to every intended answer object.

Printable emoji are OpenMoji 16 colour SVGs rendered as vector artwork. They
are used under CC BY-SA 4.0 with attribution recorded in
`edu/games/companion-adventures/OPENMOJI_ATTRIBUTION.md`. No publisher
illustration, copied character or generated bitmap is used. The browser game
uses the reader's native emoji glyphs as text symbols and redistributes no
platform emoji font.

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
- Important learning words are defined in plain language at first child-facing
  use. The companion game repeats those meanings in a visible word helper.
- The adult guide advises reducing scene density, using tactile equivalents and
  allowing extra processing time.
- The certificate records participation rather than ability or attainment.

## Format boundary

The semantic HTML is the primary screen-reader edition and supports browser
text scaling. The PDF contains selectable text and metadata but is not claimed
as a fully tagged PDF. This limitation is stated rather than hidden.

## Render review record

All 32 student pages and all 7 adult-guide pages were rendered from the latest
1.2.0 PDFs to PNG and inspected on 30 July 2026. The review found and corrected:

- labels and descriptions that referred to a lid or arrow not shown;
- the two-door vocabulary, which used *no example* before explaining it;
- a visible stop-sign symbol that contradicted “nothing shown yet,” replaced by
  an empty dashed frame;
- the map-opening scene, which needed separate MAP and FIVE CLUE STARS labels;
  and
- the final sorting picture sizes and answer-basket connections.

The corrected full contact sheets show no clipped text, overlapping text,
broken glyph, missing answer label, unreadable contrast or page-number defect.
Challenge and reveal pages remain visually distinct. The seven-page adult guide
has consistent headings, margins, page numbers and footers with no split or
overlap defect.

Visual rendering and accessibility review therefore pass for the 1.2.0 review
edition. This pass does not constitute Maria Smith's final-publication
approval.

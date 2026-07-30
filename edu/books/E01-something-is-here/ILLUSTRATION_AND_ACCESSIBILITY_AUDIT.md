# E01 illustration and accessibility audit

Edition: 1.1.0 review
Audit date: 30 July 2026
Final-publication approval: pending

## Visual design intent

The 32-page student edition is a continuous visual game story. Mira and Pip
recur throughout, a treasure map retains the five-clue progression, and every
challenge page is followed by a reveal or check. Busy scenes contain harmless
extra details so a child's unprompted observation can be correct even when it
is not the printed target.

All scenes are original vector drawings produced by the checked-in renderer.
No stock image, publisher illustration, copied character or generated bitmap is
used.

## Scientific visual accuracy

- Empty-box scenes distinguish the present container from the named toy that is
  not inside.
- Still-bell scenes bound “no ring” to the illustrated listening check and do
  not depict silence as a substance.
- Blank-card scenes retain the card, edge and observers while declaring only
  that no mark is on the card.
- Curtain scenes depict one blocked view, not nonexistence.
- Door A visibly presents an example; Door B visibly records that no example
  was supplied and does not place a hidden counterexample in the frame.
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

## Perceivability and interaction

- Colour is never the only carrier: targets use numbers, outlines, words,
  distinct object shapes or dashed frames.
- Student text is large, high contrast and set against stable backgrounds.
- Challenges accept pointing, gaze, sign, sound, speech, drawing or a partner
  record.
- Reveals are separated onto later pages so screen-reader and print users both
  receive the challenge before the answer.
- The adult guide advises reducing scene density, using tactile equivalents and
  allowing extra processing time.
- The certificate records participation rather than ability or attainment.

## Format boundary

The semantic HTML is the primary screen-reader edition and supports browser
text scaling. The PDF contains selectable text and metadata but is not claimed
as a fully tagged PDF. This limitation is stated rather than hidden.

## Render review record

All 32 student pages and all 6 adult-guide pages were rendered from the latest
PDFs to PNG and inspected on 30 July 2026. The review found and corrected:

- descriptions that implied gestures or background objects absent from the
  vector scenes;
- Door A's first static card, which did not visibly demonstrate a handover;
- sorting cards that relied on written labels without picture symbols; and
- answer-basket labels that needed repainting above their connecting lines.

The corrected full contact sheets show no clipped text, overlapping text,
broken glyph, missing answer label, unreadable contrast or page-number defect.
Challenge and reveal pages remain visually distinct. The six-page adult guide
has consistent headings, margins, page numbers and footers with no split or
overlap defect.

Visual rendering and accessibility review therefore pass for the 1.1.0 review
edition. This pass does not constitute Maria Smith's final-publication
approval.

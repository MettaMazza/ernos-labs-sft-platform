# E01 illustration and accessibility audit

Edition: 1.4.0 review
Audit date: 30 July 2026
Final-publication approval: pending

## Visual system and accuracy

The 32-page student edition uses six original, warm 3D environments generated
for this project and original transparent traveller/prop assets. No publisher
illustration, third-party game character, world or interface is reproduced.
Prompts, source paths and the non-authority boundary are recorded in
`edu/games/companion-adventures/ART_PROVENANCE.md`.

Each room is recognisable and causally connected. The box remains when the toy
moves outside; the still bell remains during a bounded listening check; a blank
card remains a card; a curtain blocks one view rather than erasing the toy;
Door A visibly supplies a card while Door B supplies no object. These are
educational demonstrations, not empirical measurements or substitutes for the
formal SFT claim.

## Description and reading-order audit

- All 32 canonical pages have unique, nonempty illustration descriptions.
- The semantic HTML exposes every description through a `figure` with
  `role="img"`, an `aria-label` and a visible `figcaption`.
- Every page is a separately linked semantic section inside the main content.
- Story text, prompts, definitions and reveal labels appear above the main
  illustration in the PDF.
- Optional hidden codes are stated in the semantic edition and never gate
  progress.
- Colour is never the only clue; targets also use shape, position, number or
  text.
- The PDF contains selectable text and metadata but is not claimed as a fully
  tagged PDF; the semantic HTML is the primary screen-reader edition.

## Interaction and callback accessibility

The book and game accept pointing, gaze, sign, speech, touch, drawing or adult
support. No timed response or forced silence is required. A wrong recall choice
receives a process hint and another attempt, not a penalty. Returning characters
must enter naturally or as optional post-attempt support and must never identify
the new answer.

## Manual render record

All 32 final student pages and all 5 adult-guide pages were rendered to PNG and
inspected at readable resolution. Corrections removed duplicate props, kept the
box from covering Sol, removed a redundant card, preserved character faces and
replaced a child-facing editorial callback sentence with an in-story clue.
Final pages show no clipped text, overlap, broken glyph, missing label, unreadable
contrast or page-number defect.

The matching game was played from opening to ending at 1280 × 720 and 390 × 844,
including every mini-game, an incorrect recall and the earned process hint. The
1024 × 768 stage was separately inspected. Body scrolling was absent; captions,
touch targets and the two-door scene remained visible. Browser console errors
and warnings were absent.

Visual and accessibility review passes for review 1.4.0. This does not constitute
Maria Smith's final-publication approval.

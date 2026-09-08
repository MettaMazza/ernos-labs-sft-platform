# E01: complete current-edition visual review

Reviewed: 8 September 2026. Edition: 2.0.0, including the existing uncommitted credit and page-8 sentence-case corrections. Saved after write access was restored. This is a review of the actual PDFs, not approval or a claim of corrections completed.

Student PDF: `output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/2.0.0/SFT-E01-Something-Is-Here-v2.0.0.pdf`.
Adult PDF: same directory, `SFT-E01-Adult-Guide-v2.0.0.pdf`.

## Scope actually completed

Read the complete book source and adult guide. Visually inspected all 32 student pages and all four adult-guide pages by rendering the PDFs in memory during read-only access. Inspected relevant renderer code. No game play test was performed in this pass. No original edition was modified by this review.

## Decision

Not publication-ready. The central discoveries must be shown, not merely asserted. The most serious issues are a sealed parcel used to demonstrate an open/empty box, hidden objects drawn in front of their hiding place, a five-star progression never visually earned, and repeated unchanged illustrations that do not show the narrated actions.

## Every student page

| Page | Observation and required response |
|---|---|
| 1 | Warm cover and corrected joint credit; retain these strengths. |
| 2 | Clear imprint. Eventually describe “1 of 4” as the opening sequence, not the full all-age library. |
| 3 | Mia's reason for visiting is missing. Establish a simple child-understandable motivation. |
| 4 | Friendly character introductions and useful gestures; retain. |
| 5 | The door opens when an adventure is ready, but that rule is vague. Connect the door to the discoveries and star sequence. |
| 6 | Recognisable note, but it floats near the hand rather than clearly arriving on the floor. Use “letter box” and show arrival. |
| 7 | Usable spotting activity. Description calls the book blue while the picture is red. Object labels appear before the identification reveal. |
| 8 | Sentence case is corrected. Identical pose to page 6 does not show picking up or reading the note. |
| 9 | All five stars already shine; no earned-star rule or clearly pointing star is shown. Establish empty spaces and a first destination. |
| 10 | Critical: the supposedly open box is a sealed parcel emoji, with a teddy placed over its lid. It does not depict inside. |
| 11 | The tracing path starts beside the box rather than at the teddy; both objects are already on the rug. Show a clear inside-to-outside action. |
| 12 | “Empty” labels a sealed box whose interior cannot be seen. The promised earned star is absent. |
| 13 | The blue doorway/star-guided transition is asserted but not shown. |
| 14 | Nori's introduction is friendly. Establish the bell and its physical interaction clearly. |
| 15 | Same poses, enlarged bell; ringing is not depicted. |
| 16 | Real listening play is useful. Clarify the child's response signal and distinguish ringing from quiet visually. |
| 17 | The card is useful, but the next star and Nori joining the journey lack setup. |
| 18 | Optional mark-or-leave activity never shows both resulting states. Provide a visible comparison without assuming the chosen branch. |
| 19 | “Blank” is explained clearly, but the marked-card branch has no resolution. |
| 20 | Seven letters assume reading knowledge. Adult reads while child notices marks; fourth clue needs story setup. PDF-only explanatory text is missing from canonical text/HTML. |
| 21 | Teddy falls from a bag it was never put into. Story says behind the curtain; art places it in front. Rolling teddy's pawprints have no clear cause. |
| 22 | Curtain was already closed before Tavi closes it. Reused art does not show the change. |
| 23 | Trail idea could work, but its cause is unclear and its endpoint is in front of the curtain. |
| 24 | Expressive reveal; visible teddy labelled “hidden teddy” risks confusing state with object name. Earned stars still absent. |
| 25 | All five stars flash and a way opens in text only. Show the original Star Door's payoff. |
| 26 | Shelf comparison is useful, but a card appears between pages without explanation. Preserve object setup. |
| 27 | Simple explanation, but “this shelf” needs an unmistakable point or label. |
| 28 | Repeats starting-door art with the door shut; Nori vanishes. “Found empty, quiet…” becomes abstract. |
| 29 | Matching is already solved. Sealed parcel depicts empty and visible teddy depicts hidden: conditions are mapped to object names instead of visible states. |
| 30 | Map appears unestablished. Narrator benefit is useful, but connect what/how/why to specific actions rather than “secret thing called nothing.” |
| 31 | Slide establishes sequel, but map has not been introduced and reused pose does not show filing it. |
| 32 | Capitals remain; Nori still waves after goodbye; no one attends to the parcel. Next-book subtitle in source is absent from PDF. |

## Cross-page and renderer findings

- `draw_magic_stars` is defined but never called. Source `stars` values do not produce earned-star pictures. Descriptions therefore promise visual evidence absent from the PDF.
- Hidden book codes requested by the user were not found in the rendered book or inspected source/renderer.
- Reusing the same art for arrival, discovery, action and reveal causes narrative state changes to disappear.
- Do not simply swap one box icon for another: inside, movement, empty interior and still-existing box must each be unambiguous.
- Preserve the SFT source distinction. A story demonstration is not empirical proof of an unrestricted metaphysical claim.

## All four adult-guide pages

The complete guide was inspected. It describes some actions and visuals not actually rendered, attributes the empty-box explanation to Mia rather than Tavi, and lists seven activities while omitting the shelf activity. It needs pre-reader support, useful instructions for the companion game and optional codes, and a narrower explanation of empty: absence of one named item alone does not establish that a container contains no other objects.

Page 1 flattens metadata into running prose. Page 4 crowds the quotation border against the following paragraph. Retain the useful adult participation, signing/opt-out options and source-boundary explanation.

## Required next production work

Rewrite the continuous story and visual state sequence before generating replacement pictures. Keep repeated teaching objects stable emojis, but choose/construct their states deliberately. Give the child genuine choices before reveals. Make the star holder, map and sequel delivery causally visible. Produce a new review edition rather than overwriting historical releases. Reinspect every changed page and the complete resulting story.

Status: review complete; revisions and game audit pending; exact-edition user approval pending.

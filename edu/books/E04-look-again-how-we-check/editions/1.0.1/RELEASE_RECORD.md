# E04 review 1.0.1

Prepared: 31 July 2026

Status: working review; not finally approved

This review contains the revised 32-page student book *Look Again: How We
Check*, its adult guide, semantic HTML, exact claim-and-receipt map, licence
record and reproducible versioned render sources. It preserves the complete
1.0.0 review as historical material.

## Child-first revision

Version 1.0.1 lets the child experience each action before meeting its short
name. The visible starting board is called the **picture plan**. The child looks
before learning *observation*, follows Sol's already-prepared step cards using
the plain sequence *first, next and last*, checks side to side before learning
*width*, sees Ivo make his own sign before learning *independent check*, and
measures bottom to top before learning *height*. The formal word *trace* remains
adult/reviewer language only.

Page 13 now offers MATCH, DOES NOT MATCH and NOT SURE while the picture plan is
covered. Pages 13 and 17 make it clear that Ivo kept one step card after every
move. The final sequence uses four recognisable illustrated cards, and page 31
uses literal mini-scenes rather than unrelated recap objects.

## Generated artifacts

- `SFT-E04-Look-Again-How-We-Check-v1.0.1.pdf`: 32 square student pages.
- `SFT-E04-Adult-Guide-v1.0.1.pdf`: 9 A4 adult-guide pages.
- `../../accessible/student-book-v1.0.1.html`: 32 semantic page sections with
  visible choices, labels and page-specific picture descriptions.

## Visual QA evidence

All 32 student pages and all 9 adult-guide pages were rendered with Poppler,
producing 41 rendered page images. Every image was visually inspected in page
order. The final 160-pixel-per-inch pass used eight student contact sheets,
four full pages per sheet, and three adult-guide contact sheets, three full
pages per sheet. Pages 17, 19, 22, 23, 26, 27 and 32 also received individual
full-resolution inspection.

The first proof exposed crowded repeated labels on page 23 and page 31, plus a
duplicate label over page 19's picture plan. A later full-size object audit
also found illustrations entering their word-label areas. The renderer was
corrected to reserve a separate opaque label band in every sign cell and to
scale each picture inside its remaining space. Covered signs are now fully
opaque. Page 19's FIRST CHANGE marker, page 22's bottom-to-top marker and page
26's answer layout were repositioned so they do not obscure the teaching
picture. The exact page 3 opening and the numbered page 14 and page 26 badges
were confirmed in the final render.

All affected pages were rerendered before the final 41-image inspection. The
final proof showed no clipped page text, hidden choices, overlapping child
controls, unreadable card labels or content outside the page boundary. Page
13's three choices, page 23's visible Ivo picture plan, pages 28-30's four
illustrated check cards and page 31's five literal recap scenes are all clear.

## Verification boundary

The 1.0.1 verifier checks canonical ordering, nine challenge/reveal pairs,
single-guest canon, experience-before-vocabulary order, step-card continuity,
separate measurement directions, receipt identities, semantic HTML, PDF text
and metadata, release checksums and locked hashes for every preserved 1.0.0
artifact. The shared education manifest verifier is also part of the release
check.

Companion Level Four remains a separate review surface. No game file is part
of this book-artifact revision, and game status must not be inferred from this
record.

This GitHub review version remains under `edu`. It must not be copied into
`publications/education` until Maria Smith explicitly approves this exact book
after reviewing it alongside the companion level.

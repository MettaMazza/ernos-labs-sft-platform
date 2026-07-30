# Level One manual end-to-end QA

Version: 1.4.0 review
Date: 30 July 2026
Final-publication approval: pending Maria Smith's review

## Complete journey tested

The local game was manually played from opening to ending on desktop and phone:

1. Star Door wakes, supplies the note and establishes five clues.
2. Note hotspot opens the route.
3. Toy is moved out and the box is inspected.
4. Bell is pressed and held for the bounded listening check.
5. Card accepts pointer/touch drawing or may remain blank.
6. Seven tiles accept `N O T H I N G` in order.
7. Curtain drag reveals the toy and completes the fifth star.
8. Both final doors are inspected in either order before the result.
9. Delayed recall was deliberately answered incorrectly first; Tavi supplied
   only the process hint “The toy was outside. What was empty?” and the child
   still had to choose the answer.
10. The completed map was filed before the E02 parcel appeared.

Optional code entry, local resume and Start Over were also checked. Codes did
not change the scientific route or reveal an answer.

## Visual/device checks

- Desktop: 1280 × 720, complete play-through.
- Phone: 390 × 844, complete play-through using touch interactions.
- Tablet: 1024 × 768, opening and moving-stage layout inspection.
- Body scroll: absent at all three sizes.
- Browser errors and warnings: none.

Corrections made during QA moved the cast clear of the dialogue overlay, aligned
the box hotspot and visible parcel, stopped props covering faces, made curtain
drag reliable for touch, kept recall objects separate and adjusted the phone
door-room crop so both small doors remain visible.

## Automated checks

- six application/content tests: pass;
- lint: pass, with five non-blocking image-optimisation warnings;
- production build: pass;
- no application fetch or analytics call: pass;
- scientific claim and receipt identity: pass;
- all 28 narration files present: pass.

This QA makes review 1.4.0 ready for Maria Smith's play test. It does not approve
the version, authorise public hosting or move it into `publications/education/`.

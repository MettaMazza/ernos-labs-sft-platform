# Level One manual end-to-end QA

Version: 1.5.0 review
Date: 30 July 2026
Final-publication approval: pending Maria Smith's review

## Complete journey tested

The complete 1.4.3 game structure was manually played from opening to ending on
desktop and phone. Review 1.5.0 keeps those activities and adds the plain-language
dialogue and exact mobile restoration checks recorded below:

1. A note comes through the shut Star Door's letter box and establishes five clues.
2. A three-object spotting game asks the child to identify the written note.
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

The automatic narration boundary was also exercised between dialogue and every
activity. The final story line did not replay when the activity prompt appeared;
each automatic line is keyed to play once, and only the replay control can
deliberately repeat it.

Optional code entry, local resume and Start Over were also checked. Codes did
not change the scientific route or reveal an answer.

The new level selector was checked before and after Level One play. Level One
starts or resumes without a page reload, the in-level home control returns to
the selector, and Level Two remains visibly unavailable while in development.

Each success panel offers `Play again`; it resets only that stage's interactive
state, preserves earned progress and returns directly to the activity prompt.

## Visual/device checks

- Desktop: 1280 × 720, complete play-through.
- Phone: 390 × 844, complete play-through using touch interactions; 390 × 724,
  short-browser title and first-dialogue regression inspection.
- Tablet: 1024 × 768, opening and moving-stage layout inspection.
- Body scroll: absent at all three sizes.
- Root and body overscroll: `none` at all three sizes.
- Browser errors and warnings: none.

Corrections made during QA kept Mira visibly identifiable as a permanent member
of the trio, replaced ambiguous or clipped props with labelled emoji objects,
kept the mobile cast clear of activities, made the five-star holder and each
earned star animate clearly, held the curtain reveal long enough to inspect,
kept recall objects separate and adjusted the phone door room so both small
doors remain visible. Mira's tall portrait sprite is now bottom-anchored so her
feet share the trio's ground line, and the opening cast has a separate safe area
above the level title and cards at phone, tablet and desktop sizes. At the short
phone size the measured cast-to-title gap is 70 pixels, and Mira's speech
indicator is anchored to her visible portrait box beside her head.

## Automated checks

- nine application/content tests: pass;
- lint: pass, with two non-blocking image-optimisation warnings;
- production build: pass;
- no application fetch or analytics call: pass;
- scientific claim and receipt identity: pass;
- all 35 narration files present: pass.

## 1.5.0 mobile restoration and wording regression

- At 390 pixels wide, reloading during Sol's first parcel line returned to that
  exact sentence instead of the level selector.
- After moving the teddy but before opening the box, reloading kept the activity
  unfinished and kept the box ready to inspect.
- The empty-box definition appeared only after the child inspected the box.
- The opening used only Star Door, letter box and note; no decorative material,
  geometric slot description or unexplained door action remained.
- The generated Kokoro files were rebuilt from the exact 35 revised captions.

This QA makes review 1.5.0 ready for Maria Smith's next play test. It does not approve
the version, authorise public hosting or move it into `publications/education/`.

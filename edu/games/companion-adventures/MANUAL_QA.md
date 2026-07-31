# Level One and Level Two manual end-to-end QA

Version: unified game 2.0.0 review
Date: 31 July 2026
Final-publication approval: pending Maria Smith's review

## Level Two story-clarity replay

Level Two was replayed from the parcel to the final lantern at 390 x 844. Every
dialogue turn, prompt, correct interaction, success line and transition was
checked. The child sees and hears the same mission before Pax teaches the plan;
the carrying and recall controls consistently say `spot`, not `tile`; the ending
answers the opening question; and no console errors occurred.

The persistent mission banner and layout bounds were also checked at 1024 x 768
and 1280 x 720. Returning to the page restored the exact Level Two scene after
the brief loading state.

## Complete journey tested

The complete 1.4.3 game structure was manually played from opening to ending on
desktop and phone. Review 1.6.0 keeps those activities and adds the plain-language
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

The level selector was checked before and after Level One play. Level One starts
or resumes without a page reload, and the in-level home control returns to the
selector. Level Two is now available beside it with separate saved progress.

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

## Level One automated checks

- nine application/content tests: pass;
- lint: pass, with two non-blocking image-optimisation warnings;
- production build: pass;
- no application fetch or analytics call: pass;
- scientific claim and receipt identity: pass;
- all 35 narration files present: pass.

## 1.6.0 mobile restoration and wording regression

- At 390 pixels wide, reloading during Sol's first parcel line returned to that
  exact sentence instead of the level selector.
- After moving the teddy but before opening the box, reloading kept the activity
  unfinished and kept the box ready to inspect.
- The empty-box definition appeared only after the child inspected the box.
- The opening used only Star Door, letter box and note; no decorative material,
  geometric slot description or unexplained door action remained.
- The generated Kokoro files were rebuilt from the exact 35 revised captions.
- At 390 by 724 pixels, the labelled note lands beside Mira on the matching
  caption and moves to her hand on “Mira picked up the note and opened it.”
- Leaving for another browser tab and returning preserved that exact line and
  the picked-up note. Reloading preserved the same state too.

## Level Two complete journey

Level Two was manually played from the first parcel to the lit Moon Lantern:

1. The parcel was opened before its card became available.
2. Pax was introduced as the only new guest, after the trio reached the narrow
   workshop door.
3. Whole-lantern choices showed a gap, every part and an extra part clearly.
4. Each of four bridge tiles accepted one touch; touching one twice produced a
   short correction without completing the game.
5. The part choices clearly showed a gap, an overlap and four same-size parts.
6. Four separate lantern parts moved into the circle one time each.
7. The same-size comparison kept both pairs visible until the child chose.
8. A recognisable lantern part filled the gap; the triangle remained outside.
9. The held count and whole count were asked on separate turns, before answers
   were spoken.
10. Four separate footprint tiles supported delayed recall without a character
    giving the answer; the child then placed the whole lantern on its stand.

Every stage's wrong path, success path and `Play again` control was exercised.
All room changes had a visible or spoken cause. Object names appeared above the
new activity pictures. Reload during Level Two restored the exact unfinished
activity. Leaving for another browser tab and returning preserved Mira's exact
parcel sentence. The landing page stayed on the chosen level until the child
used the Levels control.

## Level Two visual/device checks

- Desktop: 1280 × 720, all nine stages and ending inspected.
- Phone: 390 × 844, all nine stages and ending inspected; 390 × 724 selector,
  cast/title spacing and whole-lantern choices inspected.
- Tablet: 1024 × 768, all nine stages, selector and ending inspected.
- No activity was covered by the phone navigation buttons after the final
  right-side safe-area adjustment.
- The selector kept Mira, Tavi and Sol above and clear of the title and cards at
  phone, tablet and desktop sizes.
- Pax, Mira, Sol and Tavi shared a visible ground line in all Level Two rooms.

## Unified automated checks

- fourteen application/content tests: pass;
- plain-language gate for E01 and E02: pass;
- lint: no errors; four expected image-optimisation warnings for local character
  sprites;
- production build: pass;
- all 62 caption-matched narration files present: pass;
- no application fetch, analytics, sign-in or child-data collection: pass.

## Short-phone ending escape regression

- Level Two was completed through the real interface at a 360 × 640 viewport.
- The complete ending card, replay button and level-select button all remained
  visible inside the phone viewport.
- The ending itself can scroll when a still shorter browser needs more room.
- A fixed `Levels` control remained in the phone safe area throughout the
  ending and returned directly to the adventure selector.
- Opening the game in a new tab after completion returned to the selector
  instead of restoring an inescapable ending screen.
- The selector retained the completed progress and offered `Play Level 2
  again`; choosing replay starts a fresh Level Two journey.

This QA makes E01 review 1.6.0, E02 review 1.0.0 and unified game review 2.0.0
ready for Maria Smith's next play test. It does not approve
the version, authorise public hosting or move it into `publications/education/`.

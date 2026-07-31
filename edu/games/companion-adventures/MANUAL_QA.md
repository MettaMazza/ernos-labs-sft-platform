# Levels One, Two and Three manual end-to-end QA

Version: unified game 2.0.0 review
Date: 31 July 2026
Final-publication approval: pending Maria Smith's review

## Level Three complete journey

Level Three was played from its opening Moon Lantern line to the lit Sunrise
Arch at both the compact 390 × 844 phone viewport and the supplied 579 × 1280
phone viewport. Every one of the nine puzzles was completed through the visible
interface. A plausible wrong path was deliberately taken in every puzzle before
the successful path:

1. `Moon-and-Sun Catch`: moved the catcher between three lanes, missed a light,
   then caught blue moon, gold sun, blue moon and gold sun in order.
2. `Two-Side Camera`: recorded one face twice to use a try light, then turned
   the tile and recorded both named faces.
3. `Gate Crank`: released early, then used the gold-mark touch alternative and
   released the fully turned tile.
4. `Return Run`: launched the tile through a path that missed the required
   one-turn return, then chose the path that brought the blue moon back.
5. `Path Builder`: placed the wrong moving light, then completed the next three
   lawful lights from the belt.
6. `Rule Repair`: replaced the wrong place first, then found and repaired the
   first broken move while Sol's original row remained visible.
7. `Bridge Hop`: chose a closed lane, then guided Vee through all five labelled
   arches while changing between over and under.
8. `Trail Mapper`: tested the broken route before choosing the route that both
   reached the arch and changed picture at every move.
9. `New-Role Relay`: broke the star-and-leaf rule, then continued it from the
   fixed first star; the delayed first-gate recall was also answered wrongly
   once before the gold sun was chosen.

All three-try round-loss and one-touch recovery controls remained available.
Every board retained its goal, current state and relevant objects together.
No puzzle could be completed by clicking every object, and no correct answer
pulsed before a genuine attempt.

## Level Three visual, restoration and ending checks

- Phone 390 × 844 and 579 × 1280: complete play-through, all wrong paths,
  successes, replays, final lesson and all ending controls.
- Tablet 768 × 1024: complete nine-stage play-through with a full lost round,
  recovery, deliberate wrong paths, all successes and the completed ending.
- Desktop 1440 × 900: complete nine-stage play-through through the visible
  interface; the narrator lesson and all three controls fit without scrolling.
- The opening cast remained entirely above the title and level cards at phone,
  tablet and desktop sizes.
- The rebuilt bridge showed five numbered arches with explicit open and closed
  over/under lanes; all three route maps fit inside the phone board.
- Rapidly pressing catch a second time failed after the light moved to a new
  lane; `Path Builder` kept both moon and sun visible without a timer race.
- `Rule Repair` used a readable 3-by-2 phone board, `Bridge Hop` kept Vee inside
  a fixed-height arch board, and `Trail Mapper` used three full-width route
  rows with recognisable symbols.
- Reload during a dialogue restored the exact scene and dialogue turn.
- Reload during a retained wrong `Rule Repair` attempt restored the same scene,
  used try light and unfinished board; leaving for another tab and returning
  preserved it too.
- Leaving for another tab and returning preserved the current state and stopped
  narration while hidden.
- A completed Level Three run reloaded to its exact ending. The selector offers
  `Review Level 3 ending` without erasing completion.
- The ending narrator speaks directly to the child, defines a pattern, names
  the evidence used in the level and explains why prediction and locating a
  mistake matter.
- The `TRAILLIGHT` book code displayed its animated music-and-lantern surprise
  without exposing an answer or skipping a lesson.
- The turning tile has an explicit Enter/Space keyboard handler in addition to
  swipe and pointer activation. Every drag activity retains a labelled click or
  tap alternative, and live feedback uses status or alert semantics.

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

Corrections made during QA kept Mia visibly identifiable as a permanent member
of the trio, replaced ambiguous or clipped props with labelled emoji objects,
kept the mobile cast clear of activities, made the five-star holder and each
earned star animate clearly, held the curtain reveal long enough to inspect,
kept recall objects separate and adjusted the phone door room so both small
doors remain visible. Mia's tall portrait sprite is now bottom-anchored so her
feet share the trio's ground line, and the opening cast has a separate safe area
above the level title and cards at phone, tablet and desktop sizes. At the short
phone size the measured cast-to-title gap is 70 pixels, and Mia's speech
indicator is anchored to her visible portrait box beside her head.

## Level One automated checks

- nine application/content tests: pass;
- lint: pass, with two non-blocking image-optimisation warnings;
- production build: pass;
- no application fetch or analytics call: pass;
- scientific claim and receipt identity: pass;
- all 36 narration files present: pass.

## 1.6.0 mobile restoration and wording regression

- At 390 pixels wide, reloading during Sol's first parcel line returned to that
  exact sentence instead of the level selector.
- After moving the teddy but before opening the box, reloading kept the activity
  unfinished and kept the box ready to inspect.
- The empty-box definition appeared only after the child inspected the box.
- The opening used only Star Door, letter box and note; no decorative material,
  geometric slot description or unexplained door action remained.
- The generated Kokoro files were rebuilt from the exact 35 revised captions.
- At 390 by 724 pixels, the labelled note lands beside Mia on the matching
  caption and moves to her hand on “Mia picked up the note and opened it.”
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
activity. Leaving for another browser tab and returning preserved Mia's exact
parcel sentence. The landing page stayed on the chosen level until the child
used the Levels control.

## Level Two visual/device checks

- Desktop: 1280 × 720, all nine stages and ending inspected.
- Phone: 390 × 844, all nine stages and ending inspected; 390 × 724 selector,
  cast/title spacing and whole-lantern choices inspected.
- Tablet: 1024 × 768, all nine stages, selector and ending inspected.
- No activity was covered by the phone navigation buttons after the final
  right-side safe-area adjustment.
- The selector kept Mia, Tavi and Sol above and clear of the title and cards at
  phone, tablet and desktop sizes.
- Pax, Mia, Sol and Tavi shared a visible ground line in all Level Two rooms.

## Unified automated checks

- nineteen application/content tests: pass;
- plain-language gate for E01 and E02: pass;
- lint: no errors; seven expected image-optimisation warnings for local character
  sprites;
- production build: pass;
- all 92 caption-matched narration files present: pass;
- no application fetch, analytics, sign-in or child-data collection: pass.

## Short-phone ending escape regression

- Level Two was completed through the real interface at a 360 × 640 viewport.
- The complete ending card, replay button and level-select button all remained
  visible inside the phone viewport.
- The ending itself can scroll when a still shorter browser needs more room.
- A fixed `Levels` control remained in the phone safe area throughout the
  ending and returned directly to the adventure selector.
- Opening the game in a new tab after completion restored the exact ending; its
  fixed Levels control returned to the selector without trapping the player.
- The selector retained the completed progress and offered `Play Level 2
  again`; choosing replay starts a fresh Level Two journey.

## Level Two nine-mini-game play-through

Level Two was replayed from its first line through all nine revised mini-games
at 579 × 1280:

1. `Parcel Dash`: steered the parcel along the glowing floor path to the yellow
   reading mat without crossing a book-cart square.
2. `Lantern Detective`: uncovered one visible lantern quarter per tap, then
   chose the supported whole/missing/extra conclusion.
3. `Fit-the-Circle Lab`: matched four exact numbered quadrants to one round
   plan, with every curve meeting at the same centre.
4. `Twin-Part Test`: compared both visible pairs on the balance and selected
   the same-size pair.
5. `Doorway Delivery`: selected each lantern part and carried it through the
   small door once, with already-carried parts retained visibly.
6. `Count-and-Collect`: tapped each of the two parts in Pax's hands and the two
   parts on the labelled tray, then answered the held count and whole count on
   separate turns.
7. `Gap Repair`: used a labelled flat practice frame, rejected the triangle,
   turned and fitted the missing lantern picture, then returned the real parts
   to the carrying tray.
8. `Lantern Sum Builder`: placed four visible one-part groups, chose the total
   and read the exact addition statement while all four parts stayed separate.
9. `Lantern Builder`: used those same four counted parts in the one final
   whole-lantern jigsaw.

Each mini-game displayed its own title and live progress. Success led back into
the story and `Play again` restarted the complete mini-game. A wrong answer
produced a gentle clue without changing completed progress. The activity and
prompt regions did not overlap at 1280 × 720.

The current automated suite contains nineteen application/content tests; all
nineteen pass together with lint and the production build.

## Level Two exact-addition revision — 31 July 2026

- Played Level Two from the opening parcel through the revised ending at a
  579 × 1280 phone viewport, matching the supplied phone screenshots.
- Inspected the empty and completed `Fit-the-Circle Lab`: all four pieces are
  exact quadrants of the same code-drawn lantern, meet at one centre, and touch
  the same circular rim.
- Replaced and removed `Memory Moonwalk`; no passive picture-order task remains
  in Level Two.
- In `Lantern Sum Builder`, placed all four visible parts, deliberately chose
  the wrong total `3`, retained the recoverable clue and one used try light,
  then chose `4`.
- Verified the revealed equation `1 part + 1 part + 1 part + 1 part = 4 parts`
  and the separate explanations of plus and equals while the four parts stayed
  visibly separate. Verified that the following and final `Lantern Builder`
  alone performs the `4 counted parts → 1 whole lantern` reassembly.
- Confirmed the completion dialogue and direct-to-child lesson fit the phone
  screen and that `Next level`, `Play Level 2 again` and `Choose a level` remain
  reachable.
- Rendered and visually inspected revised student pages 14–17 and 23–32 plus
  all six adult-guide pages. The practice-frame, held/tray count, addition and
  final rebuild images remain recognisable and in the same causal order as the
  text.
- Regenerated all 28 E02 voice files from the caption manifest using Maria
  Smith's local Kokoro model and voice weights.
- Passed all nineteen application/content tests, the production build and lint
  with no errors.

This QA makes E01 review 1.6.0, E02 review 1.0.0, E03 review 1.0.0 and unified game review 2.0.0
ready for Maria Smith's next play test. It does not approve
the version, authorise public hosting or move it into `publications/education/`.

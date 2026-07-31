# SFT Learning Adventures - review 2.0.0

Prepared: 31 July 2026
Author: Maria Smith  
Status: working review; not finally approved or publicly hosted

## Story-clarity revision

- Rebuilt Level Two around one visible mission: get the whole Moon Lantern
  through the small door and take it to the balcony.
- Turned every activity into one step of a four-part plan: check the whole,
  choose and count every part, carry every part, and rebuild the same whole.
- Removed unexplained door and room changes from the Level Two dialogue.
- Renamed the counting interaction from abstract bridge tiles to carrying spots
  that track the actual lantern pieces.
- Kept the mission banner visible while the first obstacle is explained.
- Regenerated all 27 Level Two Kokoro lines from the revised captions.

## Mobile ending escape fix

- Reworked both level endings to fit short phones and to scroll internally when
  the available browser height is smaller than the ending card.
- Added a fixed, always-reachable `Levels` escape control to both endings.
- Completed Level Two sessions now reopen at the adventure selector while
  retaining their completion record.
- Added a clear `Play Level 2 again` path that resets the saved Level Two run.
- Reproduced and cleared the reported trap at 360 × 640 through a complete
  Level Two play-through, then verified the new-tab recovery path.
- Added an automated regression check for ending scrolling, fixed navigation
  and completed-session restoration.

## Nine-stage mini-game rebuild

- Replaced Level Two’s short tap prompts with nine named, distinct mini-games.
- Added multi-step play to every stage: catching, unwrapping, inspecting,
  fitting, measuring, delivering, collecting, repairing, building, lighting
  and crossing a memory path.
- Added an always-visible mini-game title and live progress counter so a child
  knows what they are playing and what remains.
- Kept every mini-game replayable, with sound feedback, gentle wrong-answer
  guidance and no penalty for trying again.
- Kept each mechanic inside the Moon Lantern journey rather than interrupting
  the story with unrelated quizzes.
- Completed all nine revised mini-games at 360 × 640 and inspected the desktop
  layout at 1280 × 720.

- Added the complete nine-stage companion to E02 *One Whole, Many Parts*.
- Added Pax as the only new Level Two guest while keeping Mira, Sol and Tavi as
  the permanent team.
- Added a short replayable game to every Level Two story stage.
- Made every move in the lantern plan explicit in simple child language.
- Used clear labelled pictures for whole, gap, extra, overlap, four parts,
  same-size parts, held counts and four separate carrying spots.
- Put object words above their pictures in the new activities.
- Added 27 exact-caption Kokoro lines from the local model and voice weights.
- Added separate device-local Level Two progress and active-level restoration.
- Enabled Level Two on the landing screen without disturbing Level One.
- Completed full visual play-throughs at 1280 × 720, 390 × 844, 390 × 724 and
  1024 × 768, including wrong answers, replay, reload and tab return.
- Passed the production build and all fourteen application/content tests.

This source review may be tested on the local network and pushed to GitHub
`main`. It is not a deployed child service or an approved final educational
publication.

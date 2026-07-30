# E01 companion adventure - review 1.4.2

Prepared: 30 July 2026  
Author: Maria Smith  
Status: complete working review; not finally approved or publicly hosted

- Established Sol, Tavi and Mira as the permanent adventure trio and Nori as
  the single new E01 guest character.
- Added Mira's generated, independently animated full-body sprite to the
  opening, every story stage and her speech portrait.
- Rewrote every room transition to explain what the friends found, why it was
  not nothing and why they travel to the next room.
- Made all eight stages playable: note spotting, toy/box movement, held bell
  listening, finger drawing, ordered letter stepping, curtain dragging,
  two-door inspection and delayed recall.
- Recorded the permanent rule that every future stage in every level or book
  must include a short replayable learning mini-game with direct input, visible
  feedback and a clear learning purpose.
- Added a stage-level `Play again` control so each mini-game can be repeated
  immediately without replaying its preceding dialogue.
- Added the unified landing-page level selector: Level One is playable with
  device-local resume, and Level Two is visibly reserved as the next
  book-and-game milestone.
- Bottom-anchored Mira's taller sprite and moved the permanent trio into a
  dedicated responsive cast area so no character floats or overlaps the level
  title and cards.
- Added an in-level home control and an ending-screen route back to level
  selection without reloading the page.
- Contained root and stage overscroll so an accidental mobile edge swipe or
  pull does not refresh or scroll the game page.
- Replaced ambiguous interaction art with recognisable labelled emoji objects,
  strengthened the five-star holder and earned-star animations, fixed the
  clipped box and kept the curtain reveal visible for inspection.
- Expanded local Kokoro narration to 34 caption-matched lines, removed
  speech-unfriendly wording and added clear journey narration.
- Prevented automatic narration from repeating a story line when the activity
  screen appears; deliberate replay remains available.
- Completed the mobile end-to-end play-through, responsive phone/tablet/desktop
  visual checks, production build, lint and eight application/content tests.

This source review may be tested on the local network and pushed on GitHub
`main`. It is not a deployed child service or approved final educational
publication. Dependency advisories remain recorded in `SECURITY_REVIEW.md`.

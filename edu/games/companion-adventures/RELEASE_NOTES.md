# E01 companion adventure - review 1.4.0

Prepared: 30 July 2026  
Author: Maria Smith  
Status: complete working review; not finally approved or publicly hosted

- Replaced the 1.3 read-and-scroll/card interface with a fixed `100dvh` animated
  stage and no gameplay body scrolling.
- Added six original generated 3D room backgrounds and independent original
  character sprites with walk-in, idle, speaking and celebration motion.
- Added eight direct environmental activities: note search, toy/box movement,
  held listening, finger drawing, letter stepping, curtain dragging, two-door
  inspection and delayed object recall.
- Added 28 caption-matched local Kokoro narration files and offline Web Audio
  effects for taps, steps, clunks, stars, rustles and listening.
- Kept all captions visible and all progress device-local.
- Introduced Tavi as E01's careful spotter and recorded the series rule that a
  callback must be a natural encounter or earned process hint, never an answer.
- Added a wrong-recall route that first reminds the child what was outside and
  then asks what was empty; the answer remains for the child to choose.
- Preserved all six optional book codes without locking knowledge or progress.
- Completed desktop and phone end-to-end play-throughs, tablet layout review,
  production build, lint and six application/content tests.

This source review may be tested on the local network and pushed on GitHub
`main`. It is not a deployed child service or approved final educational
publication. Dependency advisories remain recorded in `SECURITY_REVIEW.md`.

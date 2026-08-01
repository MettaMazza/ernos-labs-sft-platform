# E01 review release 2.0.0

Date: 2026-08-01  
Status: review  
Author: Maria Smith  
Final-publication approval: not yet granted

## Release purpose

Edition 2.0.0 is a complete rebuild of *Something Is Here* as a professional
paper-native picture book for ages three to five. It remains connected to the
Star Rooms series and companion game, but it tells and teaches its whole story
without requiring the game.

## What changed

- rebuilt all 32 pages around one clear arrival, mystery, five-clue journey,
  resolution and connected ending;
- introduced Mia, Sol and Tavi before the note and kept Nori as the single guest;
- replaced generated versions of recurring clues with stable, recognisable
  OpenMoji note, box, teddy, bell, card, pencil, door and star assets;
- reserved generated illustration for character, setting, emotion and story
  action;
- required children to see or perform each distinction before the word empty,
  quiet, blank or hidden is explained;
- added eight paper-native activities using pointing, tracing, listening,
  speaking, a page turn or safe separate paper;
- removed game menus, dashboards, buttons, progress bars and simulated digital
  interaction from the book medium;
- rewrote the narrator ending to say what the child learned, how the clues
  showed it and why clear language matters;
- created a versioned semantic HTML edition, adult guide, narrative design,
  claim map, visual audit and reproducible render sources; and
- preserved the 1.6.0 manifest, 1.5.0 claim map and all earlier edition records.

## Review artifacts

- Student PDF: `output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/2.0.0/SFT-E01-Something-Is-Here-v2.0.0.pdf`
- Adult guide PDF: `output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/2.0.0/SFT-E01-Adult-Guide-v2.0.0.pdf`
- Accessible edition: `edu/books/E01-something-is-here/accessible/student-book-v2.0.0.html`
- Student source: `edu/books/E01-something-is-here/source/book-v2.0.0.json`
- Adult source: `edu/books/E01-something-is-here/adult-guide-v2.0.0.md`
- Visual audit: `edu/books/E01-something-is-here/ILLUSTRATION_AND_ACCESSIBILITY_AUDIT-v2.0.0.md`

## Checks

`python3 edu/books/E01-something-is-here/source/verify_e01_v2_0.py`

Result: pass for source structure, child language boundaries, narrative order,
emoji assets, scientific records, accessible HTML, PDF topology, extractable
text and unpublished status.

## Approval gate

This release is ready for Maria Smith's review. It must remain outside
`publications/education` until she explicitly approves this exact 2.0.0 student
book and adult guide.

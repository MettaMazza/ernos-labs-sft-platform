# SFT Learning Adventures gameplay standard

Status: mandatory from Level Two onward

The companion is a puzzle adventure, not an illustrated quiz and not a chain of
buttons. Story captions explain why the team has entered a puzzle. Once play
begins, the board itself must carry the rule and the player must manipulate the
world.

## Every stage must pass all gates

1. **One visible board.** The important objects, goal and current state remain
   visible together. Completing one button must not merely reveal the next
   button.
2. **A distinct mechanic.** No two stages may be reskins of the same input loop.
   The level must mix dragging, routing, timing, ordering, spatial fitting,
   comparison, construction and memory.
3. **A decision with consequences.** At least one plausible action must be
   wrong. A wrong move changes the board, spends one of three visible try
   lights, or blocks the route until the player repairs or resets it.
4. **A round can be lost.** Three wrong moves end the round with a clear,
   friendly explanation and a one-touch retry. Story progress is never erased.
5. **The player can recover.** Undo, reset or replay is always visible. The game
   never traps a child after a mistake.
6. **Replay changes something meaningful.** A new round changes layout, route,
   distractors, order or timing while preserving the same lesson and answer
   boundary.
7. **The lesson lives in the mechanic.** Winning requires using the book's
   distinction. A child cannot win by clicking every object or following a
   pulsing answer.
8. **No answer beacon.** Correct answers do not pulse before a genuine attempt.
   Hints explain a method after a mistake; they never identify the answer.
9. **Movement and feedback.** Characters and puzzle pieces visibly move. Correct
   and wrong actions use different animation and sound. Captions describe the
   result in plain language.
10. **Touch-first access.** Targets are at least 44 CSS pixels, dragging also has
    an accessible tap-select/tap-place equivalent, and keyboard play reaches the
    same result.

## Level Two rebuild map

| Stage | Puzzle mechanic | Loss condition | Replay change |
| --- | --- | --- | --- |
| Parcel discovery | steer a rolling parcel through a small library obstacle course | three obstacle hits | obstacle positions |
| Whole detector | tap one covered lantern to uncover its four visible parts | three false whole/missing/extra conclusions after uncovering | cover order |
| Four-part plan | match four lantern-picture cards to their places in a circular frame | three rejected placements | picture-card tray order |
| Same-size test | place parts on a balance track and compare their reach | three mismatched pairs | pair positions and distractor size |
| Doorway delivery | choose each lantern part and carry it through the small door exactly once | repeat a carried part three times | part tray order |
| Held-and-whole count | count the four visible lantern parts, then answer how many Pax holds and how many make the whole | three repeated counts or wrong answers | visible part order |
| Gap repair | choose, rotate and fit one piece while rejecting distractors | three non-fitting pieces | distractor set and rotation |
| Lantern Sum Builder | place four visible one-part groups, choose the exact total and read `1 + 1 + 1 + 1 = 4 parts` while every part stays separate | three wrong totals | part-tray order |
| Lantern builder | after the equation has checked all four parts, assemble those same parts as the one final spatial jigsaw | three wrong slots | starting rotation and tray order |

## Level Three rebuild map

| Stage | Puzzle mechanic | Loss condition | Replay change |
| --- | --- | --- | --- |
| Moon-and-Sun Catch | move a catcher across three lanes to collect four ordered lights; each attempt moves the next light to a new lane | three missed lights | starting lane |
| Two-Side Camera | turn one tile and photograph both named faces | three repeated face records | starting face |
| Gate Crank | pull a gate handle to its gold mark, or use the equivalent tap target, and release it | three early releases | handle direction |
| Return Run | compare three complete paths and send the tile through the one-turn path that restores its first face | three wrong paths | the one-turn path changes letter and position |
| Path Builder | choose between two visibly moving lights and place three lawful lights from left to right | three rule breaks | choice order |
| Rule Repair | find and replace the first broken move in a retained row | three incorrect replacements | break position |
| Bridge Hop | guide Vee through five physical arches, changing between over and under after every crossing | three wrong lane moves | starting role |
| Trail Mapper | inspect three complete route maps and find the one whose lights keep the rule to the arch | three wrong routes | map order |
| New-Role Relay | continue star-and-leaf roles from one fixed star clue, then recall the first gate | three sequence or recall errors | fresh two-part relay |

## Completion-screen rule

Every completed level shows three equally reachable actions:

- play this level again;
- choose a level;
- continue to the next level in order.

If the next level is not yet built, the third action remains visible and clearly
says that the next level is in development; it must not pretend to launch an
unavailable level.

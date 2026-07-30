# Level One manual end-to-end QA

Version: 1.3.0 review

Date: 30 July 2026

Final-publication approval: pending Maria Smith’s review

## Tested journey

The local game was manually played in the in-app browser from the landing page
through all nine story scenes and the ending:

1. **Arrival** — verified that the parcel, five empty map spaces and locked door
   are explained before any star appears. Tested an incorrect “door already
   open” choice, neutral recovery and the correct route.
2. **Practice search** — selected the labelled box, bell, blank card and map;
   confirmed that the persistent map remains at zero stars.
3. **Clue One: box** — verified the toy-outside/box-empty distinction and Star
   One.
4. **Clue Two: bell** — selected both the still bell and listener, rejected the
   ringing event and verified Star Two.
5. **Clue Three: card** — verified card-here/no-mark, the plain definition of
   *blank* and Star Three.
6. **Clue Four: word** — verified visible NOTHING letter tiles, the record
   explanation and Star Four.
7. **Clue Five: curtain** — selected the curtain, visible toy parts and Luma;
   verified the view boundary, Star Five and the explicit cause of the door
   opening.
8. **Two doors** — verified that Door A visibly presents both a door and card,
   Door B presents no object, the plain definition of *no example given* and the
   non-invention rule.
9. **Delayed recall** — returned to the earlier box clue, earned a memory spark
   without adding a sixth map star and filed the completed case.

The ending was checked for the five-star state, plain child-facing result,
separately labelled grown-up boundary and E02 parcel preview.

## Optional and failure routes

- Invalid book code retained as a first try with a helpful search prompt.
- `ROOMSTAR` accepted case-insensitively and unlocked only optional story.
- Code counter updated locally; no scientific content or next scene was gated.
- Local progress survived reload and resumed at the stored scene.
- Start-over removed local progress.
- Replay moved some choices while preserving their labels and meanings.

## Visual and responsive checks

- Desktop: 1280 × 720, every scene and result state.
- Tablet: 768 × 1024 landing and story layout.
- Mobile: 390 × 844 landing, story, two-door choice cards and controls.

All choice names appear above their illustrations. Visual review corrected
sprite-sheet edge fragments, added recognisable word and curtain art, showed
the offered card with Door A and retained high-contrast, large touch targets.

## Automated checks accompanying this record

- lint: pass;
- production build: pass;
- five application/content tests: pass;
- no application fetch, WebSocket, beacon or analytics call: pass;
- book/game claim and receipt identity: pass;
- production dependency audit: three inherited high advisories remain recorded
  in `SECURITY_REVIEW.md`; remote hosting readiness remains false.

This QA pass makes the version ready for Maria Smith’s review and play test. It
does not constitute her approval or move the version into
`publications/education/`.

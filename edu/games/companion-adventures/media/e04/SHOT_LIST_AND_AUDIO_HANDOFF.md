# E04 media shot list and audio handoff

Status: live-review production plan; no asset in this plan is an approved-final publication

Scope: Book/Game E04, *Look Again: How We Check*

Scientific-authority status: none. Generated illustration pixels, synthesized music and Kokoro voices may present the checked story, but they do not supply or validate any educational or SFT claim. The game captions and the E04 claim map remain authoritative.

## Continuity lock

- Permanent team: Mia, Sol and Tavi.
- One new E04 guest only: **Ivo**, a friendly moss-green garden checker with a round magnifying lens and a checkerboard satchel.
- World connection: the turning-light trail reaches a garden gate and a welcome-sign checking workshop.
- Visual language: original warm 3D children's puzzle-adventure, rounded sculpted forms, tactile wood/cloth/painted metal, expressive but uncluttered silhouettes, soft morning garden light and no resemblance to a third-party game property.
- Every stage background is scenery only. Characters, movable props, measurements, differences, ordered placement records, answers, labels and failed attempts must be deterministic overlays so replay variations remain exact and readable.

## Master image constraints

Apply these constraints to every generation below:

> Original child-friendly 3D puzzle-adventure environment, warm rounded sculpted materials, polished animated-film lighting, landscape composition, child-height three-quarter camera, crisp recognisable objects, broad unobstructed foreground play lane, strong depth separation, gentle moss green, sunflower gold and sky blue palette. No character, person, creature, writing, letters, numbers, labels, answer, interface, button, logo, watermark, signature, photorealism, copied design or recognisable third-party property. Keep the upper 18 percent quiet for the game header and the lower 28 percent visually calm for characters and captions. Do not crop the principal set piece.

Source generations should be preserved under `public/art/stages/e04-source/`. Approved playable crops should be 1536 by 864 PNG files in `public/art/stages/`. Keep the source prompt and the final crop hash in the eventual E04 section of `ART_PROVENANCE.md`.

## Character shot: Ivo

Generated-review source export: `public/art/characters/individual/ivo-v1.png`

Playable filename: `public/art/characters/individual/ivo.png`

The delivered source export is already transparent; no separate chroma-source file is present in the review package. The source export and playable alias are byte-identical. Their exact dimensions and hashes are recorded in `media/e04/ART_PROVENANCE.md`.

Exact prompt:

> Create one entirely original, friendly full-body 3D children's adventure character named Ivo, front-facing in a relaxed helpful pose. Ivo is a small rounded moss-green garden checker with a lighter leaf-green face and belly, two short leaf-shaped head tufts, large warm brown eyes, sturdy little amber boots, a round brass-rimmed magnifying lens held clearly in one hand, and a cream-and-dark-green checkerboard satchel worn across the body. The lens, hand and satchel must have separate readable silhouettes. Ivo should look patient, curious and delighted to check a friend's work, never stern. Match a warm sculpted animated-film game style while remaining wholly original. One character only, centred, complete from head tufts to boot soles, generous clear space on every side, flat #ff00ff removable chroma background, even warm key light, no floor shadow, no text, no logo, no watermark, no crop, no extra prop and no copied or recognisably similar character.

Acceptance checks:

- One character and exactly one handheld round magnifying lens.
- Checkerboard pattern is confined to the satchel and reads at phone size.
- Both feet and both head tufts are present; nothing touches the frame.
- Chroma removal leaves no magenta fringe or missing green body pixels.
- At 96 CSS pixels tall, Ivo remains distinct from Nori, Pax, Vee, Mia, Sol and Tavi.

## Nine stage backgrounds

### 1. Look-and-Point

Canonical source: `public/art/stages/e04-source/e04-stage-01-look-and-point-v2.png`

Canonical playable: `public/art/stages/e04-stage-01-look-and-point-v2.png`

Superseded open-gate review output retained for provenance only: `public/art/stages/e04-source/e04-stage-01-look-and-point-v1.png` and `public/art/stages/e04-stage-01-look-and-point-v1.png`.

Add to the master constraints:

> Show the outside of a welcoming magical garden gate at early morning. The gate stands closed at centre-right so opening it remains a later story result. Beside it is one child-height wooden welcome-sign frame with a completely blank cream signboard, a low stone ledge and three empty brass pointing markers. Leave a wide clear lawn-and-path area at centre-left for exact observation props and touch targets. The trail from the previous adventure glows faintly as alternating moon-blue and sunrise-gold stones leading to the gate. Do not include any readable mark on the sign and do not place clues or differences in the scenery.

Overlay purpose: the child points only to what is visibly present; a deterministic sign/prop overlay carries the observation choices.

### 2. Build-the-Board

Source: `public/art/stages/e04-source/e04-stage-02-build-the-board-v1.png`

Playable: `public/art/stages/e04-stage-02-build-the-board-v1.png`

Add to the master constraints:

> Inside a bright garden checking workshop, show one large empty rectangular sign frame on a sturdy child-height workbench. Place four clearly separate but empty shallow parts trays along the back edge, plus a second slim display rail where a failed first arrangement can remain visible. Keep the sign frame and trays blank and front-facing. Leave the centre of the bench unobstructed for draggable board pieces. Rounded shelves hold only soft-focus garden tools in the distance.

Overlay purpose: build, test and rebuild the same welcome board while the first failed arrangement stays visible.

### 3. Curtain Memory

Source: `public/art/stages/e04-source/e04-stage-03-curtain-memory-v1.png`

Playable: `public/art/stages/e04-stage-03-curtain-memory-v1.png`

Add to the master constraints:

> Show a small garden-show room connected to the workshop. A wide brass rail holds two fully open sunflower-yellow curtains, revealing one empty, evenly lit four-space Welcome Sign frame. Include a second empty four-space recall frame beside it. Leave generous space for a curtain overlay to close across the complete sign and for four separate picture-card overlays. No picture may already occupy a sign space.

Overlay purpose: observe the canonical four-picture sign order, close the curtain, rebuild that order from memory, then reveal and compare without deleting the attempt.

### 4. Difference Finder

Source: `public/art/stages/e04-source/e04-stage-04-difference-finder-v1.png`

Playable: `public/art/stages/e04-stage-04-difference-finder-v1.png`

Add to the master constraints:

> Show a leafy inspection courtyard with two identical empty cream display panels mounted side by side at the same height, same size and same camera angle. Put a small neutral comparison rail exactly between them and leave both panels completely blank. Keep lighting symmetrical across the two panels and reserve clear space around every edge for tappable difference overlays.

Overlay purpose: two deterministic welcome-sign pictures differ in controlled places; scenery must not introduce accidental asymmetry.

### 5. Ordered Placement Record

Canonical source: `public/art/stages/e04-source/e04-stage-05-placement-record-v2.png`

Canonical playable: `public/art/stages/e04-stage-05-placement-record-v2.png`

Superseded route-scene review output retained for provenance only: `public/art/stages/e04-source/e04-stage-05-footprint-trace-v1.png` and `public/art/stages/e04-stage-05-footprint-trace-v1.png`.

Add to the master constraints:

> Show an inviting garden checking terrace beside the same closed gate. Put one long child-height workbench across the middle distance. On it place exactly four clearly separated, identical, blank upright card holders in one straight left-to-right row, plus one large blank square source-plan frame divided into exactly four equal corner spaces. Keep every holder and source space blank. Include no printed arrow, number, letter, word, icon, picture, footprint, route or highlighted answer.

Overlay purpose: show Sol's four placement cards as an ordered record, compare them with the source in order and retain Step 3 as the first changed placement.

### 6. Measuring Ribbon

Source: `public/art/stages/e04-source/e04-stage-06-measuring-ribbon-v1.png`

Playable: `public/art/stages/e04-stage-06-measuring-ribbon-v1.png`

Add to the master constraints:

> Show an airy potting-and-measuring nook with one long perfectly straight child-height worktable viewed nearly front-on. The table has a blank inset measuring channel across its full width, a fixed brass start stop at the left and three empty object stands above it. Keep the channel free of tick marks, numbers, ribbons and objects. Leave clear horizontal space for a draggable measuring-ribbon overlay to start at the brass stop.

Overlay purpose: align the same zero/start boundary, measure a board piece and check rather than judge length by appearance.

### 7. Friend Check

Source: `public/art/stages/e04-source/e04-stage-07-friend-check-v1.png`

Playable: `public/art/stages/e04-stage-07-friend-check-v1.png`

Add to the master constraints:

> Show a cosy greenhouse checking bay with two separate, identical child-height inspection desks facing one central blank sign stand. Each desk has one empty four-space checklist holder, and a low divider prevents one checker from seeing the other's choices too soon. Leave standing space for Tavi at one desk and Mia, Sol and Ivo at the other. Keep every holder, stand and board blank.

Overlay purpose: Tavi checks all four spaces independently before the team compares results; nobody supplies Tavi with Mia's answer first.

### 8. Height Question

Canonical source: `public/art/stages/e04-source/e04-stage-08-height-check-v2.png`

Canonical playable: `public/art/stages/e04-stage-08-height-check-v2.png`

Superseded claim-board review output retained for provenance only: `public/art/stages/e04-source/e04-stage-08-disagreement-detective-v1.png` and `public/art/stages/e04-stage-08-disagreement-detective-v1.png`.

Add to the master constraints:

> Show a clear height-check workshop beside the same closed garden gate. Include exactly one upright blank Welcome Sign in a tall simple frame with its top and bottom edges fully visible. Beside it leave one broad clean vertical measuring lane running from the bottom edge to the top edge. Add one small neutral worktable at the side. Include no claim boards, voting props, width ribbon, tick, ruler, answer or pass state.

Overlay purpose: expose that width alone did not answer height, choose the missing height question instead of guessing or voting, and move a height tool from the bottom edge to the top edge.

### 9. Four-Record Checkpoint

Canonical source: `public/art/stages/e04-source/e04-stage-09-record-checkpoint-v2.png`

Canonical playable: `public/art/stages/e04-stage-09-record-checkpoint-v2.png`

Superseded open-gate/lamp review output retained for provenance only: `public/art/stages/e04-source/e04-stage-09-final-checkpoint-v1.png` and `public/art/stages/e04-stage-09-final-checkpoint-v1.png`.

Add to the master constraints:

> Return to the magical garden gate in warm early-morning light. Keep the gate visibly closed and latched before the final decision. Beside it place one blank Welcome Sign. Build exactly four identical blank record plinths in one clean left-to-right row and exactly four identical blank gate-question frames in a second paired row. Keep all eight spaces blank. Include no open onward path, lamp, label, answer or success state.

Overlay purpose: match the four visible picture, width, height and friend-check records to their four gate questions; retain wrong matches and open the gate only after every question has support.

## Image-generation rejection gate

Reject and regenerate any asset that:

- bakes in a correct answer, failed attempt, measurement, difference or ordered-record result;
- contains accidental text, pseudo-writing, UI or a watermark;
- changes the number or geometry of required blank frames, desks, trays, card holders, record plinths or question rails;
- places a character in a stage background;
- hides a playable surface behind scenery or creates low-contrast touch targets;
- clips the main set piece in a 16:9 centre crop; or
- is not immediately recognisable on a 360 CSS-pixel-wide phone.

## Level Four music

`scripts/generate_background_music.py` contains an original 78 BPM garden score. Paired wooden notes form a soft look-and-check call-and-answer, with one quiet bell closing each phrase. It uses only programmed NumPy tones and local FFmpeg encoding; it contains no stock, streamed or model-generated recording.

From `edu/games/companion-adventures/`, render only this score without rewriting checked Level 1–3 files:

```bash
python3 scripts/generate_background_music.py --score level-four
```

Expected output: `public/audio/music/level-four.mp3`, 24 kHz stereo MP3 at 112 kbit/s nominal. The eventual game must loop it quietly, duck it under narration, stop it on exit, pause it while hidden and never auto-play before a child or grown-up starts Level 4.

## Kokoro narration handoff

The copy-locked source is the exported `LEVEL_FOUR_NARRATION` array in `app/level-four-state.mjs`. `narration-manifest-e04.json` contains its 32 stable IDs, speakers and captions without editorial changes. The manifest must be regenerated whenever that authoritative array changes; stale audio must never be retained beneath revised visible text.

Voice continuity for the eventual manifest:

```json
{
  "Narrator": "bf_emma",
  "Mia": "bf_alice",
  "Sol": "bm_fable",
  "Tavi": "bm_daniel",
  "Ivo": "bm_lewis"
}
```

`bm_lewis` is installed in the local Kokoro voice bundle and is unused by E01–E03, so Ivo remains distinct while the permanent trio and narrator retain their established voices.

Exact render command, from `edu/games/companion-adventures/`, after the caption-to-manifest equality check passes:

```bash
python3 scripts/generate_kokoro_narration.py \
  --model /Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx \
  --voices /Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin \
  --manifest narration-manifest-e04.json \
  --output public/audio/e04-v1.0.0
```

The generator renders British English at speed 0.94, encodes mono MP3 at 24 kHz/80 kbit/s and writes `generation-receipt.json` with the exact model, voice bundle, manifest and output SHA-256 hashes. The weights remain local and must never be copied into the repository or sent to a child's device.

Before rendering, the E04 manifest must satisfy all of these gates:

1. Every audible caption has one stable line ID, speaker and exact text.
2. Every manifest line appears verbatim in the game; no stale name, stage or lesson remains.
3. Every game narration lookup resolves to a manifest ID, including intro, retry-independent result explanation, transition and ending.
4. Ivo is the only new speaker and uses `bm_lewis` consistently.
5. Punctuation is written for natural TTS; no shorthand such as `shh`, symbols read unexpectedly or stage directions are spoken.
6. App-switch/resume testing proves that hidden or superseded lines stop and do not replay over the current caption.

After rendering, record `narration-manifest-e04.json`, `public/audio/e04-v1.0.0/generation-receipt.json`, every E04 MP3, `level-four.mp3`, the final generated art, this handoff and the changed generator in the release checksum set.

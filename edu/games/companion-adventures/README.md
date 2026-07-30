# SFT E01 companion adventure

*The Star Door Mystery* is the animated companion to review edition 1.4.0 of
E01 *Something Is Here*. It is a fixed, full-screen moving stage: not a menu,
quiz-card stack or read-and-scroll page.

## What the child does

Mira, Sol and Tavi walk into six original generated 3D rooms, idle, speak and
celebrate. The child spots the written note, moves Sol's toy, inspects the box,
listens at Nori's bell, draws on a card, steps the mystery-word letters, drags a
curtain, checks both small doors and retrieves an earlier clue. Every one of the
eight story stages contains a short playable learning activity. The written
caption remains visible whenever a local voice line plays.

The door supplies the note, the note establishes five clues, every checked clue
lights one star and five stars open the final chamber. A new parcel appears only
after the completed map is filed. Six book codes unlock optional jokes, visits
or previews; they never gate an explanation, star, route or answer.

## Characters and future callbacks

Sol, Tavi and Mira are the permanent adventure trio. Each level or book
introduces no more than one memorable lesson character; E01 introduces Nori. A
guest character may return
later through a natural story encounter or as an optional hint earned after a
genuine attempt. Returning characters can recall how to look or check, but must
never state the new answer. The formal continuity record is
`character-continuity.json`.

## Offline narration and privacy

Thirty-four lines were pre-rendered from Maria Smith's local Kokoro ONNX model
and voice weights. Audio is bundled under `public/audio/e01/`; after installation
the game does not need the model or an internet connection. Sound effects are
made locally in the browser. Captions are always available.

The game collects no name, age, email, location, voice, image or analytics. It
saves only progress on the device. Start Over removes that record.

## Run and verify

Requires Node.js 22.13 or later.

```bash
npm install
npm run dev -- --hostname 0.0.0.0
npm test
npm run lint
npm run build
```

Devices on the same local network can open the computer's displayed LAN URL.
Public hosting is not authorised and remains blocked by the dependency review.

The only scientific source is `SFT-ROOT-THERE-IS-NO-NOTHING`, receipt
`sha256:711864171e4d3a2f2734f0c2890965bcd81a0228349538751a3c80699c27d669`.
Art and voice systems have no scientific-authority role. This is a review build,
not an approved final publication.

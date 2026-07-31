# SFT Learning Adventures

This offline game now contains two complete book companions: E01 *The Star Door
Mystery* and E02 *The Moon Lantern Workshop*. The level selector opens either
fixed, animated adventure. Neither level is a quiz-card stack or a
read-and-scroll page.

## What the child does

Mira, Sol and Tavi walk through original generated 3D rooms, idle, speak and
celebrate. In Level One the child spots the written note, moves Sol's toy, inspects the box,
listens at Nori's bell, draws on a card, steps the mystery-word letters, drags a
curtain, checks both small doors and retrieves an earlier clue. Every one of the
eight story stages contains a short playable learning activity. The written
caption remains visible whenever a local voice line plays.

In Level Two the child opens the new parcel, meets Pax, finds a whole lantern,
touches four bridge tiles once each, chooses four fitting parts, rebuilds the
lantern, compares same-size parts, fills a gap, keeps an extra part outside,
answers two different count questions and remembers Sol's repeated bridge tile.
Every one of its nine connected story stages contains a replayable game.

The note comes through the Star Door's letter box, establishes five clues, and every checked clue
lights one star and five stars open the final chamber. A new parcel appears only
after the completed map is filed. Six book codes unlock optional jokes, visits
or previews; they never gate an explanation, star, route or answer.

## Characters and future callbacks

Sol, Tavi and Mira are the permanent adventure trio. Each level or book
introduces no more than one memorable lesson character; E01 introduces Nori and
E02 introduces Pax. A
guest character may return
later through a natural story encounter or as an optional hint earned after a
genuine attempt. Returning characters can recall how to look or check, but must
never state the new answer. The formal continuity record is
`character-continuity.json`.

## Level selection and mobile play

The landing page shows both available adventure levels. Each can start or resume
from device-local progress. The
in-level home control and the ending screen return to level selection without a
page reload. The app root and every moving stage are locked to the visible
viewport, with page overflow and pull-to-refresh overscroll contained for phone
and tablet play.

## Offline narration and privacy

Sixty-two lines were pre-rendered from Maria Smith's local Kokoro ONNX model
and voice weights. Audio is bundled under `public/audio/e01-v1.6.0/` and
`public/audio/e02-v1.0.0/`; after installation
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

The scientific sources and exact receipt hashes for both levels are recorded in
`game-manifest.json` and `claim-map.json`.
Art and voice systems have no scientific-authority role. This is a review build,
not an approved final publication.

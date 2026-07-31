# SFT Learning Adventures

This offline game now contains four complete book companions: E01 *The Star
Door Mystery*, E02 *The Moon Lantern Workshop*, E03 *The Turning-Light Trail*
and E04 *The Garden Gate Check*. The level selector opens any of the four fixed,
animated adventures.
None is a quiz-card stack or a
read-and-scroll page.

## What the child does

Mia, Sol and Tavi walk through original generated 3D rooms, idle, speak and
celebrate. In Level One the child spots the written note, moves Sol's toy, inspects the box,
listens at Nori's bell, draws on a card, steps the mystery-word letters, drags a
curtain, checks both small doors and retrieves an earlier clue. Every one of the
eight story stages contains a short playable learning activity. The written
caption remains visible whenever a local voice line plays.

In Level Two the child holds one problem throughout: the whole Moon Lantern is
too wide for a small door on the way to the balcony. The child checks the whole,
chooses a four-part plan, compares sizes, carries each part through once, checks
the held and whole counts, keeps an unrelated extra outside and rebuilds the
same whole lantern. At the balcony the child makes
`1 + 1 + 1 + 1 = 4 parts`, learns that equals names the same total, and then
joins those four counted parts into one whole lantern. Every one of its nine
connected story stages contains a replayable game and visibly advances that
plan.

In Level Three the rebuilt lantern lights a path that stops before the Sunrise
Arch. The child catches the moon-and-sun lights, records both sides of one
tile, operates a turning gate, chooses a return path, continues the lights,
repairs the first broken move, guides Vee over and under five arches, compares
three complete route maps and reuses the same rule with star and leaf. Each
stage has a recoverable wrong path, three visible try lights and replay.

In Level Four the turning light reaches the Sunrise Arch and reveals a closed
garden gate. Morning visitors are waiting, but the Welcome Sign is not ready.
The child looks at its four-picture plan, builds the sign, keeps a wrong sign
visible and finds the two pictures that changed. The child follows Sol's four
move cards, watches Mia repair the sign, checks its width side to side and its
height bottom to top, and helps Ivo make another sign without peeking. Four
answer cards are then matched to four questions so the gate can open. Width
and height allow as many practice lengths as the child needs; the other games
keep visible attempts and offer a recoverable new puzzle after three mistakes.

The note comes through the Star Door's letter box, establishes five clues, and every checked clue
lights one star and five stars open the final chamber. A new parcel appears only
after the completed map is filed. Six book codes unlock optional jokes, visits
or previews; they never gate an explanation, star, route or answer.

## Characters and future callbacks

Sol, Tavi and Mia are the permanent adventure trio. Each level or book
introduces no more than one memorable lesson character; E01 introduces Nori,
E02 introduces Pax, E03 introduces Vee and E04 introduces Ivo. A
guest character may return
later through a natural story encounter or as an optional hint earned after a
genuine attempt. Returning characters can recall how to look or check, but must
never state the new answer. The formal continuity record is
`character-continuity.json`.

## Level selection and mobile play

The landing page shows all four available adventure levels. Each can start or resume
from device-local progress. The
in-level home control and the ending screen return to level selection without a
page reload. The app root and every moving stage are locked to the visible
viewport, with page overflow and pull-to-refresh overscroll contained for phone
and tablet play.

## Offline narration, music and privacy

One hundred and thirty-six lines were pre-rendered from Maria Smith's local
Kokoro ONNX model and voice weights: 40 for Level One and 32 each for Levels
Two, Three and Four. Audio is bundled under `public/audio/e01-v1.6.0/`,
`public/audio/e02-v1.0.0/`, `public/audio/e03-v1.0.0/` and
`public/audio/e04-v1.0.1/`; after installation the game does not need the model
or an internet connection. Captions are always available.

Each level also has its own original instrumental background score:
`public/audio/music/level-one.mp3`, `level-two.mp3`, `level-three.mp3` and
`level-four.mp3`. These four distinct loops were composed and synthesized locally by
`scripts/generate_background_music.py` from programmed notes and tones; no
streamed or stock recording is used. Music begins only after the child starts
the narrated introduction, loops quietly and ducks while someone speaks. It
can be turned on or off from the introduction, gameplay controls and ending
screen, with that preference kept only on the device. Music pauses when the
page is hidden or left, resumes when appropriate, and stops and resets when a
level is exited or changed. Movement and interaction effects are made locally
in the browser with Web Audio.

The game collects no name, age, email, location, voice, image or analytics. It
saves only progress on the device. Start a fresh game removes all four progress
records after confirmation.

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

The scientific sources and exact receipt hashes for all four levels are recorded in
`game-manifest.json` and `claim-map.json`.
Art and voice systems have no scientific-authority role. This is a review build,
not an approved final publication.

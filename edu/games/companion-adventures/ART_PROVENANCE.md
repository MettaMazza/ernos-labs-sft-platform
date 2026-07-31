# Level One art provenance

Version: E01 companion review 1.4.1

Prepared: 30 July 2026

Scientific-authority status: none

The 3D artwork in *The Star Door Mystery* was generated specifically for this
project with the repository’s image-generation tool, then used locally. The
tool supplied illustration pixels only. It supplied no premise, theorem,
derivation, educational claim or curriculum authority.

## Originality boundary

The direction requested the sense of a warm, collectible 3D educational
adventure while explicitly requiring entirely original characters, props and
architecture. It prohibited copied or recognisably similar third-party game
characters, assets, logos, interface elements and world designs.

## Generated source assets

- `public/art/world/e01-observatory-keyart-v1.png` — full observatory scene with
  Mia, Pip, six original rounded travellers, parcel, bell, blank card, map and
  Star Door.
- `public/art/characters/e01-six-character-sheet-v3.png` — transparent six-
  character sheet used to derive the local character images in
  `public/art/characters/individual/`.
- `public/art/world/e01-prop-sheet-v1.png` — transparent prop sheet used to
  derive the local images in `public/art/props/`.
- `public/art/stages/e01-stage-01-observatory-v1.png` — empty playable
  observatory with the Star Door, parcel, bell, card and route map.
- `public/art/stages/e01-stage-02-bell-gallery-v1.png` — playable bell gallery.
- `public/art/stages/e01-stage-03-paper-room-v1.png` — playable blank-card and
  seven-tile room.
- `public/art/stages/e01-stage-04-curtain-passage-v1.png` — playable curtain
  passage.
- `public/art/stages/e01-stage-05-star-door-v1.png` — final two-door chamber.
- `public/art/stages/e01-stage-06-library-v1.png` — library and next-parcel
  ending.
- `public/art/characters/individual/mira-v1.png` — transparent, independently
  animated Mia sprite used on the opening and every playable stage.

Earlier chroma-removal trials `e01-six-character-sheet-v1.png` and
`e01-six-character-sheet-v2.png` remain as provenance records but are not used
by the interface.

## Prompt records

### Observatory key art

Create a cinematic, warm, child-friendly 3D educational puzzle-adventure scene
inside an original round observatory workshop. Show a curious child guide, a
small blue bird companion and six entirely original rounded collectible
travellers gathered around an open parcel, a hand bell, a blank card, a
five-space clue map and a star-marked door. Use soft sculpted materials,
expressive faces, golden evening light, clear silhouettes and no text. The
characters, architecture and props must be original and must not copy or be
recognisably similar to any existing game property.

### Six-character sheet

Create a clean 3-by-2 character sheet on a removable solid chroma background.
Show six different original, friendly, rounded 3D travellers: turquoise with
antennae and scarf; golden with flame-shaped hair and satchel; purple with
goggles; green with soft spikes and belt; blue with cap and trainers; coral
with long floppy ear-like arms. Full body, front-facing, consistent lighting,
no text, no overlap and no copied or recognisably similar third-party
characters.

### Prop sheet

Create a clean 4-by-2 3D prop sheet on a removable solid chroma background:
open cardboard box, teddy, brass hand bell, blank cream card, magnifying glass,
rolled clue map, wooden star door and empty violet dotted frame. Use clear,
recognisable silhouettes, consistent warm lighting, no labels, no overlap and
entirely original asset design.

### Playable stage set (1.4.0)

Built-in image generation mode was used with the observatory key art as a
style-and-world reference only. Each prompt requested a wide, empty, original
3D animated-film game environment with a broad lower-third walking lane, no
characters, no words, no interface, no logo or watermark, and no copied or
recognisably similar third-party imagery.

The six primary requests were:

1. An observatory stage with the brass-and-blue Star Door at right and an open
   parcel, five-star map, hand bell and blank card on the centre table.
2. A connected bell gallery with three brass bells, a large still central bell
   and a glowing star-map pedestal.
3. A connected paper-and-letter room with a low table, blank cream card,
   chunky pencil and seven separate unlettered colourful tiles.
4. A connected curtain passage with a freestanding brass rail, coral velvet
   sliding curtain, empty toy plinth and star-map pedestal.
5. A final chamber with two small matching doors, a visible card at Door A, an
   empty matching shelf at Door B, and the five-socket Star Door behind them.
6. A welcoming observatory library with curved low shelves, a child-height
   route-map stand, reading rug, sunrise window and newly delivered parcel.

### Mia sprite (1.4.1)

Built-in image generation mode was used to create a stylized-concept,
full-body game sprite preserving Mia's established identity, outfit and warm
3D adventure style. The final prompt requested a front-facing, friendly Mia
with one hand raised as if speaking; a flat `#ff00ff` removable chroma
background; and no crop, shadow, text, logo, watermark or other character.
The generated source was saved under `tmp/imagegen/e01-mira-chroma-v1.png` and
processed with the repository's chroma-removal helper into
`public/art/characters/individual/mira-v1.png`.

## Processing mode

Mode: built-in image generation for the key art, character/prop sources, Mia
sprite and all six 1.4.0 stage backgrounds, followed by local chroma removal and lossless
cropping only for the earlier character and prop sheets. Stage images are used
directly. Character and prop crops are transparent PNG files that the game
moves independently over the stages; CSS supplies movement, touch targets,
letter reveals and the draggable curtain without changing scientific content.

## Level Two source art — review 1.0.0

Prepared: 31 July 2026
Scientific-authority status: none

The same original warm 3D world was extended for *The Moon Lantern Workshop*.
Image generation supplied illustration pixels only and did not supply or judge
any SFT claim. Source generations are preserved under
`public/art/stages/e02-source/`; the matching playable 16:9 crops are stored one
directory above them.

The generated stages are:

1. `e02-stage-02-whole-room-v1.png` — one Moon Lantern, one narrow workshop
   door and three blank choice spaces.
2. `e02-stage-03-count-bridge-v1.png` — exactly four large glowing floor tiles.
3. `e02-stage-04-part-gate-v1.png` — exactly three blank circular choices and
   exactly four tray spaces.
4. `e02-stage-05-rebuild-room-v1.png` — one empty round outline and exactly
   four tray spaces. An earlier five-space generation was rejected and is not
   used.
5. `e02-stage-06-match-table-v1.png` — exactly two blank comparison mats.
6. `e02-stage-07-checking-room-v1.png` — one circle divided into exactly four
   spaces and one route onward.
7. `e02-stage-08-balcony-v1.png` — one empty lantern stand, open doors and the
   first evening star.

Each prompt requested an original, child-friendly, wide 3D game environment
with an open lower walking lane, clear countable spaces, no characters, no
words, no interface, no logo or watermark, and no copied or recognisably
similar third-party imagery. The generated backgrounds do not carry answers:
the renderer and eventual game add the exact countable diagrams separately.

## Level Three source art — review 1.0.0

Prepared: 31 July 2026
Scientific-authority status: none

Built-in image generation extended the same original 3D world for *The
Turning-Light Trail*. The four landscape source scenes are stored under
`public/art/stages/e03-source/`:

1. `e03-stage-01-trail-station-v1.png` - the Moon Lantern, the first alternating
   blue-moon and gold-sun lights, and the distant Sunrise Arch.
2. `e03-stage-02-turn-gate-v1.png` - a child-safe one-turn gate with an empty
   round mechanism for an exact interactive tile overlay.
3. `e03-stage-03-over-under-bridge-v1.png` - one clearly visible route over a
   rounded bridge and one clearly visible route under it.
4. `e03-stage-04-sunrise-arch-v1.png` - the pre-dawn final arch and three empty
   route lanes for exact interactive choices.

Each prompt requested a polished, child-friendly 3D scene with open foreground
space, no characters, no words, no interface, no logo and no watermark. The
blue-moon and gold-sun symbols in the first scene are decorative continuity
props. All question state, order, labels and correct answers are added by the
deterministic book renderer and game interface. Generated pixels supply no SFT
premise, theorem, derivation or curriculum authority.

## Level Four generated art — live review

Version: E04 companion review 1.0.1 (*The Garden Gate Check*)

Prepared: 31 July 2026
Scientific-authority status: none
Approval status: generated review assets; not approved-final publication art

Built-in image generation extended the same original 3D world into the garden
checking workshop for *Look Again: How We Check*. Generated pixels establish
setting and empty play surfaces only. They supply no SFT claim, lesson, answer,
measurement or checking result. The exact prompt plan and the full per-scene
custody record are preserved in `media/e04/SHOT_LIST_AND_AUDIO_HANDOFF.md` and
`media/e04/ART_PROVENANCE.md`.

The character export `public/art/characters/individual/ivo-v1.png` and runtime
alias `public/art/characters/individual/ivo.png` are byte-identical 1254×1254
RGBA PNG files, each with SHA-256
`ea3382945c0285a12fa3649972827a1c0245b5a0ff610b441367ad06cd11c599`.
Ivo is the one new E04 guest and carries a magnifying lens and checkerboard
satchel; the sprite contains no puzzle answer.

Each generated source scene is a 1672×941 opaque PNG. Each matching playable
file is a distinct 1536×864 opaque PNG export:

1. Find It With the Lens — canonical closed-gate source
   `public/art/stages/e04-source/e04-stage-01-look-and-point-v2.png`
   (`010868b27f7b58e77ea496071c081f03d1a5bc25c23b3b51a58bfbe650c93503`),
   canonical playable `public/art/stages/e04-stage-01-look-and-point-v2.png`
   (`aba8b8450d7e9e0fecec168b3c0e8669b6c7a1fae631272ca6e189322b5f2cd0`).
   The open-gate v1 source
   `public/art/stages/e04-source/e04-stage-01-look-and-point-v1.png`
   (`3abce9429b1a14153af8722c2ec0e442fa478b2c46159956ac042f4fe816071c`)
   and playable `public/art/stages/e04-stage-01-look-and-point-v1.png`
   (`a56e6acb85a39b871c083d4c2f57c2aa64307c15bdf2aa1439aec5c3bceb8c03`)
   are superseded review outputs retained only for provenance.
2. Welcome Sign Builder — source
   `public/art/stages/e04-source/e04-stage-02-build-the-board-v1.png`
   (`266274074483ba04b5c88ad585bc698be201c082b7d1ee6af332fff43c6d06ae`),
   playable `public/art/stages/e04-stage-02-build-the-board-v1.png`
   (`ee1681b225b77d4316763fc371d74c2d2c999628141305e41071c3d7f639fb3a`).
3. Curtain Copy — source
   `public/art/stages/e04-source/e04-stage-03-curtain-memory-v1.png`
   (`3b303a66ed682e706598b7a4cd74cf57c0e218095d55d5a31f1423de56bf675b`),
   playable `public/art/stages/e04-stage-03-curtain-memory-v1.png`
   (`4cd6d9b732ba776f6f52c6b18faa1642632175f1d499ac426a0fcae6db12cb8a`).
4. Difference Finder — source
   `public/art/stages/e04-source/e04-stage-04-difference-finder-v1.png`
   (`15d84cf27a12af212fce7e839453265d9f47ddd709f6afd732b89f57c6a52c14`),
   playable `public/art/stages/e04-stage-04-difference-finder-v1.png`
   (`8c998afe9e22ac2f7b7ff673e1a19481f040d698497725e1af05bd7e98de5a14`).
5. Sol's Step Cards — canonical source
   `public/art/stages/e04-source/e04-stage-05-placement-record-v2.png`
   (`c9b0785de78e6e3ebe522f98e1248ebc568c716f21b4b17732a97170f7e05def`),
   canonical playable `public/art/stages/e04-stage-05-placement-record-v2.png`
   (`4d4f2792347b241197b128d04e6131d17dddcf2560eb72f93b61a42d5038cfaa`).
   The v1 route-scene source
   `public/art/stages/e04-source/e04-stage-05-footprint-trace-v1.png`
   (`2d8720eee949e7d41dd77dacdbb03336f66ef9e6d8bf2bb0368e0ad550878924`)
   and playable `public/art/stages/e04-stage-05-footprint-trace-v1.png`
   (`78e1ed34267e600df0322be5cb70e9e0c12fc41167b5fafbc985e35489d5e1b1`)
   are superseded review outputs retained only for provenance.
6. Measuring Ribbon — source
   `public/art/stages/e04-source/e04-stage-06-measuring-ribbon-v1.png`
   (`0a6cb30c5edacc12fbc21c8a9715bafdf7ab7175777c6330d8a5c6d390a28e36`),
   playable `public/art/stages/e04-stage-06-measuring-ribbon-v1.png`
   (`a0c1e55676f83853382b734392853eee421c7e1ed209b54945cc8b0420be323d`).
7. Ivo Makes His Own Sign — source
   `public/art/stages/e04-source/e04-stage-07-friend-check-v1.png`
   (`9cee25cdd9f8d28630e98329faf76d7486a68f205042223a592a89dd4f4fd7a4`),
   playable `public/art/stages/e04-stage-07-friend-check-v1.png`
   (`dfe43399138a8209f59f1234cec16a63e307a05e78d2ed3e91cb4d412321ffb0`).
8. Does It Fit Bottom to Top? — canonical source
   `public/art/stages/e04-source/e04-stage-08-height-check-v2.png`
   (`1be2596e866b097ddafd5a0f1f4e21c5977e40da8c4f6f93dd5cc84bb53e08a8`),
   canonical playable `public/art/stages/e04-stage-08-height-check-v2.png`
   (`08ab5c1495bfc7f77b70725f62bc8a3e20a3e7794b88b895b8252c674e879c3c`).
   The v1 claim-board source
   `public/art/stages/e04-source/e04-stage-08-disagreement-detective-v1.png`
   (`2492bc1e4423cbc76b832fff1a4d98bf1f3427890f618923bbb5064d6547f336`)
   and playable `public/art/stages/e04-stage-08-disagreement-detective-v1.png`
   (`26c11b54f2a9be15f54e5f714b9e3519f7aa695ada75ecb4e9479a46f11b3fe2`)
   are superseded review outputs retained only for provenance.
9. Match the Answer Cards — canonical source
   `public/art/stages/e04-source/e04-stage-09-record-checkpoint-v2.png`
   (`2b2d8fb94f33cd26b53ff1b3634251da276d0e2b86b003e41a579d0f53b34719`),
   canonical playable `public/art/stages/e04-stage-09-record-checkpoint-v2.png`
   (`129d7301b8133c36db71422ea7354ce6cc03cb5b25d5ec754b462d11d50317e4`).
   The v1 open-gate/lamp source
   `public/art/stages/e04-source/e04-stage-09-final-checkpoint-v1.png`
   (`6f5173598fb3a2821391f1b961b225434107757af4a4a37efb7d75368b58b708`)
   and playable `public/art/stages/e04-stage-09-final-checkpoint-v1.png`
   (`854be055f291a8c6485e058bcbecb67912a6dbebe42ffc6db1d080cdae63b4f4`)
   are superseded review outputs retained only for provenance.

All nine backgrounds are blank of story answers. The picture plan, Sol's wrong
sign and move cards, measuring tools, earlier attempts, Ivo's second sign and
the four answer cards remain deterministic game overlays. The Ivo scene's
three decorative desk slots are not counters; the game displays the exact four
picture places separately. Exact visual and music custody is verified by
`media/e04/CHECKSUMS.sha256`.

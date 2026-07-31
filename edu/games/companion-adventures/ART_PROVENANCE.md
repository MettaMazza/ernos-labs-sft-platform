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

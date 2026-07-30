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
  Mira, Pip, six original rounded travellers, parcel, bell, blank card, map and
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
  animated Mira sprite used on the opening and every playable stage.

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

### Mira sprite (1.4.1)

Built-in image generation mode was used to create a stylized-concept,
full-body game sprite preserving Mira's established identity, outfit and warm
3D adventure style. The final prompt requested a front-facing, friendly Mira
with one hand raised as if speaking; a flat `#ff00ff` removable chroma
background; and no crop, shadow, text, logo, watermark or other character.
The generated source was saved under `tmp/imagegen/e01-mira-chroma-v1.png` and
processed with the repository's chroma-removal helper into
`public/art/characters/individual/mira-v1.png`.

## Processing mode

Mode: built-in image generation for the key art, character/prop sources, Mira
sprite and all six 1.4.0 stage backgrounds, followed by local chroma removal and lossless
cropping only for the earlier character and prop sheets. Stage images are used
directly. Character and prop crops are transparent PNG files that the game
moves independently over the stages; CSS supplies movement, touch targets,
letter reveals and the draggable curtain without changing scientific content.

# Book 1 v3 development artwork

Status: development, not an approved or complete edition. Credit: Maria & Matthew Smith.

## Box discovery vignette

File: `story/e01-box-discovery-v3.0.0.png`.
Generated with the built-in image-generation tool on 8 September 2026. The first request failed at the service; a second request succeeded. No CLI/API fallback was used.

Character/style reference: `art/v2.0.0/story/e01-box-rug-v2.0.0.png`. The reference was visually inspected before the request. The generated output was inspected and copied into this versioned project directory; no earlier artwork was overwritten.

Successful prompt, verbatim:

> Use case: illustration-story. Generate a new landscape 3:2 book illustration using this image only as character and style reference. Keep Mia (teal coat, brown hair) on far left, Tavi (blue round antenna friend) at back centre, Sol (golden flame-shaped friend) far right. They sit around a rug, looking delighted towards the EMPTY foreground centre, with new poses: Mia points down, Tavi leans forward, Sol spreads his hands. Leave ample empty rug in centre/front for teaching emojis to be added afterwards. Do not draw boxes, teddy bears, toys, labels, letters or UI. Warm magical tower room, soft daylight, quiet uncluttered background, high-quality dimensional children's picture-book illustration for ages 3–5. Keep all bodies within the image, hands clear. No dark text reserve at top.

The scene is used for page 12's discovery reaction. Teaching objects are not baked into the generated image. The deterministic PDF renderer places the same teddy emoji outside the same open-box diagram.

## Teaching objects

- Teddy and filled star: existing local OpenMoji 16.0.0 assets, CC BY-SA 4.0; see `edu/assets/openmoji` attribution. No regenerated teddy variants.
- Open box: new code-native diagram in `source/render_e01_v3_box_proof.py`, with separated interior, front walls and open flaps. It is a diagram, not a claim that a standard open-box Unicode emoji exists. Its warm carton palette and strong outline sit alongside the emoji artwork. The ordinary sealed parcel icon is reserved for the later delivery.
- Hollow stars: code-native outlines. Only the first fills at the discovery on page 12.

The first layout proof reuses the old room illustration on page 9 with an adjusted crop; page 12 uses the new reaction scene. All other v3 page artwork remains pending. Do not represent this one generated vignette as a fully illustrated 32-page book.

## Opening illustrations, 12 September 2026

Two new built-in image-generation requests succeeded. No CLI fallback was used. Both used the visually inspected `art/v2.0.0/story/e01-opening-meet-v2.0.0.png` solely for character identity and style. Outputs were inspected, then copied into this project without replacing old assets.

- `story/e01-enter-v3.0.0.png`: Mia remains outside the open entrance and peeks in; Tavi and Sol notice her. Used on page 3.
- `story/e01-note-held-v3.0.0.png`: the trio lean towards Mia's supporting palms. The renderer places the stable note emoji in her hands. Used on page 7.

Entry-scene prompt, verbatim:

> Use case: illustration-story. New landscape 3:2 children's picture-book scene for ages 3–5. Reference image supplies exact Mia, Sol and Tavi identities and the warm dimensional magical tower style. Show the moment BEFORE that greeting: view from inside the tower towards its small OPEN blue entrance on the left. Mia, brown hair in bun, teal headband and teal coat, is still on the sunny outside step, leaning her head around the open door and looking in curiously. Show her complete face and feet with door clear of her body. On the right inside, blue round antenna friend Tavi and golden flame-shaped Sol turn to notice her. Friendly anticipation. Make the open blue door and threshold immediately understandable, all three bodies comfortably within the image. Simple warm stone tower entry with blue and gold accents, uncluttered floor. No written words, labels, UI, diagrams or teaching objects. No blank dark reserve. Keep identities and size relationship, but create new poses and new camera angle.

Note-reading-scene prompt, verbatim:

> Use case: illustration-story. New landscape 3:2 children's picture-book scene. Use reference solely for exact character identities and warm dimensional book style. Medium close view of Mia in the centre, brown hair bun, teal headband and coat, with blue antenna friend Tavi left and golden flame-shaped Sol right. They have found a small note and gathered to read it together. Mia smiles down and holds both hands forward palms-up beside one another, horizontally at lower centre, offering clear support for a paper emoji that the renderer will add. Leave the small area directly above her palms clear of clothing detail; do NOT draw the paper itself or any other learning object. Tavi and Sol lean in and look towards her palms, interested rather than shocked. Behind them a softly focused closed blue Star Door with large gold star and letter box; no legible writing. Keep all heads fully visible, no body clipping at sides, fingers coherent, warm soft daylight. No text, UI or borders.

Opening pages 1, 4, 5 and 6 reuse existing book-specific character art where the scene fits, with new layout and explicit object states. Page 5 adds a code-drawn letter box so it exists before the note arrives. Page 6 places unlabelled stable note/book/map emojis on the rug; page 7 reveals the labelled note above Mia's palms. Page 8 draws a five-place route with one hollow star per stop, including the same open-box diagram. These are not game screenshots.

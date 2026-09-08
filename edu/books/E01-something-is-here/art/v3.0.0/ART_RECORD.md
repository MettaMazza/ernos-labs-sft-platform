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

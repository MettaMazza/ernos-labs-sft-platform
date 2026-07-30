# Level One narration provenance

Version: E01 companion review 1.4.1
Prepared: 30 July 2026
Scientific-authority status: none

All spoken story lines were generated locally from the checked captions in
`narration-manifest.json`. Kokoro supplies voices only; it supplies no premise,
lesson, educational conclusion, SFT claim or scientific authority. The written
caption is always visible and is the authoritative accessibility transcript.

## Local render

- engine: Kokoro ONNX 1.0 through the installed `kokoro_onnx` package
- model used: `/Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx`
- voices used: `/Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin`
- generator: `scripts/generate_kokoro_narration.py`
- output: 34 MP3 files at 24 kHz in `public/audio/e01/`
- playback: bundled files only; no network or runtime model access
- detailed model, voice, manifest and output hashes:
  `public/audio/e01/generation-receipt.json`

The large local model weights are deliberately not copied into the repository
or sent to a child's device. A device receives only the pre-rendered narrated
lines, so Level One remains offline-capable and practical on phones and tablets.

## Voice continuity

Narrator uses `bf_emma`; Mira uses `bf_alice`; Sol uses `bm_fable`; Tavi uses
`bm_daniel`; and E01 guest Nori uses `bf_isabella`. This mapping is versioned
in the manifest so returning characters retain recognisable voices.

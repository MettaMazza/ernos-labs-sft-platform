# Levels One through Four audio provenance

Version: unified game review 2.1.0
Prepared: 31 July 2026
Scientific-authority status: none

All 136 spoken story lines were generated locally from the checked captions in
`narration-manifest.json`, `narration-manifest-e02.json`,
`narration-manifest-e03.json` and `narration-manifest-e04.json`. Kokoro supplies
voices only; it supplies no premise,
lesson, educational conclusion, SFT claim or scientific authority. The written
caption is always visible and is the authoritative accessibility transcript.

## Local render

- engine: Kokoro ONNX 1.0 through the installed `kokoro_onnx` package
- model used: `/Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx`
- voices used: `/Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin`
- generator: `scripts/generate_kokoro_narration.py`
- output: 40 E01 MP3 files at 24 kHz in `public/audio/e01-v1.6.0/`
- output: 32 E02 MP3 files at 24 kHz in `public/audio/e02-v1.0.0/`
- output: 32 E03 MP3 files at 24 kHz in `public/audio/e03-v1.0.0/`
- output: 32 E04 MP3 files at 24 kHz in `public/audio/e04-v1.0.0/`
- playback: bundled files only; no network or runtime model access
- detailed model, voice, manifest and output hashes:
  `public/audio/e01-v1.6.0/generation-receipt.json`,
  `public/audio/e02-v1.0.0/generation-receipt.json`,
  `public/audio/e03-v1.0.0/generation-receipt.json` and
  `public/audio/e04-v1.0.0/generation-receipt.json`

The large local model weights are deliberately not copied into the repository
or sent to a child's device. A device receives only the pre-rendered narrated
lines, so all four levels remain offline-capable and practical on phones and tablets.

## Original offline background music

The four levels use four distinct original instrumental loops. They were
composed as programmed note, chord and rhythm sequences and synthesized locally
by `scripts/generate_background_music.py`; they do not contain streamed, stock
or model-generated recordings. The script uses NumPy to construct the tones and
local FFmpeg to encode 24 kHz stereo MP3 files at 112 kbit/s.

- Level One: `public/audio/music/level-one.mp3`, a gentle 72 BPM star-room bell score
- Level Two: `public/audio/music/level-two.mp3`, a warm 84 BPM workshop pluck score
- Level Three: `public/audio/music/level-three.mp3`, a moving 96 BPM turning-trail score
- Level Four: `public/audio/music/level-four.mp3`, a gentle 78 BPM garden-check call-and-answer score

The score starts only after the child begins a level's narrated introduction.
It loops at low volume, ducks beneath narration and can be turned on or off in
the introduction, gameplay HUD and ending screen. That preference is stored
only on the device. Playback pauses when the page is hidden or left, resumes
when appropriate, and stops and resets when the child exits or changes levels.
The files are bundled with the game and require no network access.

## Voice continuity

Narrator uses `bf_emma`; Mia uses `bf_alice`; Sol uses `bm_fable`; Tavi uses
`bm_daniel`; E01 guest Nori uses `bf_isabella`; E02 guest Pax uses
`bm_george`; E03 guest Vee uses `af_heart`; and E04 guest Ivo uses `bm_lewis`.
This mapping is versioned in the manifest so returning characters retain
recognisable voices.

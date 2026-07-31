# E04 Kokoro narration provenance

Status: live-review media; not an approved-final publication

Prepared: 31 July 2026

Scientific-authority status: none

All 32 spoken Level Four lines were generated locally from the copy-locked captions exported as `LEVEL_FOUR_NARRATION` in `app/level-four-state.mjs` and recorded exactly in `narration-manifest-e04.json`. Kokoro supplies voices only. It supplies no story premise, lesson, educational conclusion, SFT claim or scientific authority. The visible caption remains the authoritative accessibility transcript.

## Local render

- engine: Kokoro ONNX 1.0 through the installed `kokoro_onnx` package
- model used: `/Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx`
- model SHA-256: `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5`
- voices used: `/Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin`
- voice-bundle SHA-256: `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`
- manifest: `narration-manifest-e04.json`
- manifest SHA-256: `6efbdf6656c72e4386f15ed1562a9baa604dcb4fd843e5bb5ea8a75b3c652a07`
- generator: `scripts/generate_kokoro_narration.py`
- output: 32 mono MP3 files at 24 kHz/80 kbit/s in `public/audio/e04-v1.0.0/`
- output receipt: `public/audio/e04-v1.0.0/generation-receipt.json`
- receipt SHA-256: `73deb2bb034b02bacdabc9d8b69d4008bb9a8d754a1de696ba0b698e2afc74aa`
- combined spoken duration: 315.477 seconds
- playback boundary: bundled files only; no network or runtime model access

The local model weights are deliberately excluded from the repository and from children's devices. Only the pre-rendered MP3 files are bundled with the offline game.

## Voice continuity

- Narrator: `bf_emma`
- Mia: `bf_alice`
- Sol: `bm_fable`
- Tavi: `bm_daniel`
- Ivo: `bm_lewis`

The permanent trio and narrator retain their established voices. `bm_lewis` was present in the checked local voice bundle and had not been assigned to an earlier level, giving Ivo a distinct recurring voice.

## Render command

From `edu/games/companion-adventures/`:

```bash
python3 scripts/generate_kokoro_narration.py \
  --model /Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx \
  --voices /Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin \
  --manifest narration-manifest-e04.json \
  --output public/audio/e04-v1.0.0
```

## Quality checks

- The manifest was compared structurally against `LEVEL_FOUR_NARRATION`: all 32 IDs, speakers and caption strings matched exactly.
- All 32 IDs are unique and every used speaker resolves to the declared voice map.
- The receipt manifest hash and all 32 receipt file hashes were recomputed and matched.
- The output directory contains exactly the expected 32 MP3 files and the receipt; there are no stale narration stems.
- Every MP3 decodes successfully as 24 kHz mono audio. Durations range from 6.144 to 31.787 seconds, with no empty or truncated file.
- Decoded peaks range from 0.552 to 0.959, so no file clips at full scale.
- A secondary offline Faster Whisper Base transcription pass preserved the full meaning of every line. Its word-sequence similarity ranged from 0.923 to 1.000 (mean 0.984). The lowest score was a word-boundary transcription of “four-corner rebuild” as “four corner a build”; expected proper-name and possessive homophones such as Sol's/soles also occurred. No word or name was silently changed in the manifest or captions.

The transcription pass is a pronunciation/truncation diagnostic only. It is not an authority and does not replace direct listening during the required phone, tablet and desktop play-through.

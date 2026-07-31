# E04 Kokoro narration provenance

Status: corrected live-review 2.1.1 media; not an approved-final publication

Prepared: 31 July 2026

Scientific-authority status: none

Kokoro supplies voices only. It supplies no story premise, lesson, educational
conclusion, SFT claim or scientific authority. The visible caption remains the
authoritative accessibility transcript.

## Current corrected render - `e04-v1.0.1`

All 32 spoken Level Four lines were generated locally from the copy-locked
captions exported as `LEVEL_FOUR_NARRATION` in `app/level-four-state.mjs` and
recorded exactly in `narration-manifest-e04.json`.

- engine: Kokoro ONNX 1.0 through the installed `kokoro_onnx` package
- model used: `/Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx`
- model SHA-256: `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5`
- voices used: `/Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin`
- voice-bundle SHA-256: `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`
- manifest: `narration-manifest-e04.json`
- manifest SHA-256: `6b0be35215932124b224c27d6775ba00c6831657d7429fd043e0153fbc343c3a`
- generator: `scripts/generate_kokoro_narration.py`
- output: 32 mono MP3 files at 24 kHz/80 kbit/s in `public/audio/e04-v1.0.1/`
- output receipt: `public/audio/e04-v1.0.1/generation-receipt.json`
- receipt SHA-256: `5d8d360c7f3835a63f2be29b69543abecd7ba9e03e2afbe5cbdbe64dc81b2ef3`
- combined spoken duration: 284.736 seconds
- shortest file: `02a-narrator-ivo-arrives.mp3`, 5.205 seconds
- longest file: `10-narrator-to-you.mp3`, 30.635 seconds
- playback boundary: bundled files only; no network or runtime model access

### Corrected-set validation

- The manifest was compared structurally against `LEVEL_FOUR_NARRATION`: all
  32 IDs, speakers and caption strings matched exactly and remained in the
  same stable order.
- All 32 expected stems are unique. The output directory contains exactly
  those 32 MP3 files plus the receipt, with no missing or extra MP3.
- The receipt contains exactly the same 32 filenames, with no missing, extra
  or duplicate receipt entry.
- The current manifest hash exactly matches the receipt's
  `manifest_sha256` value.
- Every receipt MP3 SHA-256 was recomputed from disk and matched.
- Every MP3 decoded without error as MP3, 24 kHz, one-channel mono audio.
- All files are non-empty and their durations range from 5.205 to 30.635
  seconds. No zero-length, implausibly short or truncated file was found.

This validation checks identity, completeness, format and successful decoding.
It does not replace a human listening check. The approval play test should
listen to the full level on each intended device before publication.

## Voice continuity

- Narrator: `bf_emma`
- Mia: `bf_alice`
- Sol: `bm_fable`
- Tavi: `bm_daniel`
- Ivo: `bm_lewis`

The permanent trio and narrator retain their established voices. `bm_lewis`
was present in the checked local voice bundle and had not been assigned to an
earlier level, giving Ivo a distinct recurring voice.

## Corrected render command

From `edu/games/companion-adventures/`:

```bash
python3 scripts/generate_kokoro_narration.py \
  --model /Users/mettamazza/Desktop/HIVENET/models/kokoro-v1.0.onnx \
  --voices /Users/mettamazza/Desktop/HIVENET/models/voices-v1.0.bin \
  --manifest narration-manifest-e04.json \
  --output public/audio/e04-v1.0.1
```

The local model weights are deliberately excluded from the repository and
from children's devices. Only the pre-rendered MP3 files are bundled with the
offline game.

## Superseded render record - `e04-v1.0.0`

The earlier 1.0.0 narration remains in the repository for provenance only. It
belongs to the superseded Level Four copy and must not play beneath the
corrected review 2.1.1 captions.

- output: `public/audio/e04-v1.0.0/`
- old manifest SHA-256: `6efbdf6656c72e4386f15ed1562a9baa604dcb4fd843e5bb5ea8a75b3c652a07`
- receipt: `public/audio/e04-v1.0.0/generation-receipt.json`
- receipt SHA-256: `73deb2bb034b02bacdabc9d8b69d4008bb9a8d754a1de696ba0b698e2afc74aa`
- file count and format: 32 mono MP3 files at 24 kHz/80 kbit/s
- combined spoken duration: 315.477 seconds
- duration range: 6.144 to 31.787 seconds
- decoded peak range: 0.552 to 0.959, with no full-scale clipping

The superseded set's receipt manifest hash and all 32 receipt file hashes were
recomputed and matched during its original review. Its output directory held
exactly the expected 32 MP3 files and receipt, with no stale narration stems.

A secondary offline Faster Whisper Base transcription pass on the superseded
set preserved the full meaning of every line. Word-sequence similarity ranged
from 0.923 to 1.000, with a mean of 0.984. The lowest score was a word-boundary
rendering of “four-corner rebuild” as “four corner a build”; expected proper-
name and possessive homophones such as Sol's/soles also occurred. That
transcription pass was a pronunciation and truncation diagnostic only, not an
authority or replacement for direct listening.

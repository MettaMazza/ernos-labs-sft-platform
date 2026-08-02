# OpenAI ten advances capture — 2026-08-01

This directory is a local source-custody capture of OpenAI's publication
**Ten Advances in Mathematics and Theoretical Computer Science**, published on
2026-08-01 and retrieved from official OpenAI sources on 2026-08-02.

## Scientific boundary

These are external, answer-bearing comparison artifacts. They are not SFT
derivations, do not select or repair an SFT law, and have no claim-admission
authority. The capture itself establishes no mathematical agreement,
disproof, or incoherence. Any SFT comparison must preserve the repository's
WHY / DERIVATION / CHECK separation and may enter correspondence only after
the applicable SFT derivation is independently sealed.

## Captured material

- `snapshots/ten-proofs-oai.pdf` — the 249-page collection of ten manuscripts.
- `snapshots/reasoning-walkthroughs.pdf` — the 62-page mathematical discovery
  notes released with the manuscripts.
- `snapshots/ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6.zip`
  — an immutable archive of the official `openai/ten-proofs` Lean repository.
- `upstream_tree/ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6/`
  — the extracted archive for local inspection.
- `source_custody_manifest.json` — URLs, upstream identity, rights status,
  byte counts, hashes, and verification results.
- `SHA256SUMS` — hashes for the three exact downloaded artifacts.

The Lean source targets Lean 4.32.0 and contains one formalization for each of
the ten announced results. The archive integrity and PDF structure were
checked at capture time. The Lean project has **not** yet been built or
independently proof-checked in this repository.

## Rights

The Lean repository declares Apache-2.0 and its upstream `LICENSE` is retained
in the extracted tree. The release page does not state a separate license for
the two PDFs. They are retained here for local research and source criticism;
no redistribution right is asserted. Do not package, publish, or upload this
capture without a rights review and Maria Smith's explicit authorization.

Upstream changes must be captured in a new versioned directory. Never
overwrite these snapshots.

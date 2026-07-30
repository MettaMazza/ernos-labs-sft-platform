# SFT E01 companion adventure

`Mira & Pip's Nothing Hunt` is the reading-first companion game for review
edition 1.2.0 of E01 *Something Is Here*. It is a source-controlled local web
application, not a separately authorised publication or hosted service.

## Learning loop

Each of the six short levels asks the learner to look and choose before labels
appear. Every attempt points back to named book pages. The reveal-page code
unlocks an optional character moment or badge; it never unlocks scientific
content or blocks progress.

The game collects no personal information and makes no network request. It
saves only level progress and optional bonuses in the browser's local storage.
The reset button removes that record.

## Run and verify

Requires Node.js 22.13 or later.

```bash
npm install
npm run dev
npm test
```

The verified production build is generated locally in `dist/` and is ignored
by Git. Hosting requires a separate explicit decision by Maria Smith.

The current upstream dependency advisories and hosting block are recorded in
`SECURITY_REVIEW.md`; do not deploy this review version as a production child
service.

## Scientific and publication boundaries

The only scientific source is
`SFT-ROOT-THERE-IS-NO-NOTHING`, receipt
`sha256:711864171e4d3a2f2734f0c2890965bcd81a0228349538751a3c80699c27d669`.
The game does not add an empirical or open claim. It remains a review artifact
until the exact book and companion version receive Maria Smith's approval.

## Illustration licence

The browser interface uses operating-system emoji as familiar text symbols.
The printable book renderer uses OpenMoji 16 artwork. See
`OPENMOJI_ATTRIBUTION.md` for the required attribution and licence boundary.

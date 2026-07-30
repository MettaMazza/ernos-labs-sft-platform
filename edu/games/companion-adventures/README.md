# SFT E01 companion adventure

`The Star Door Mystery` is the first complete story-puzzle level in the unified
SFT learning game, paired with review edition 1.3.0 of E01 *Something Is Here*.
It is a source-controlled local web
application, not a separately authorised publication or hosted service.

## Learning loop

Level One is one continuous mystery rather than six disconnected quizzes. A
parcel establishes five empty star spaces; practice teaches the interaction
without awarding a star; five checked investigations light Stars One to Five;
and only the completed map opens the two-door ending. Every scene is fully
readable and defines its learning word. Each successful check then points back
to exact book pages. A code hidden inside a matching book reveal unlocks an
optional character moment; it never unlocks scientific content or blocks
progress.

After the two-door result, a delayed recall asks the player to explain an
earlier star before the completed map is filed. It earns a memory spark rather
than changing the five-star scientific route.

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

## Illustration and asset provenance

The game uses original generated 3D world, character and prop artwork created
for this project, with CSS-drawn supporting objects. It does not copy a
third-party game’s characters, world or assets. Generation prompts, source
files, crops and the non-authority boundary are recorded in
`ART_PROVENANCE.md`. The printable book renderer still uses OpenMoji 16 artwork;
see `OPENMOJI_ATTRIBUTION.md` for that attribution and licence boundary.

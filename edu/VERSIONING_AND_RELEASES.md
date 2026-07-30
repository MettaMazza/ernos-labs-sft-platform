# Educational Versioning and Release Policy

## Version identity

Every book uses semantic versioning:

- **Major** — the learner contract, stage, branch scope or scientific boundary
  changes incompatibly.
- **Minor** — new admitted material, chapters, activities or substantial
  accessibility improvements are added without changing the book identity.
- **Patch** — corrections to wording, layout, metadata, links, answers or
  accessibility that do not change the scientific scope.

The first public-ready edition is `1.0.0`. Drafts use `0.x.y`.

## Live-work status

Every edition displays one status:

- `planning` — catalogue entry only;
- `draft` — incomplete and not suitable for teaching release;
- `review` — complete draft undergoing scientific, educational, accessibility
  or safety review;
- `live` — current verified edition;
- `superseded` — preserved published edition replaced by a newer version;
- `withdrawn` — preserved for custody but unsafe or materially incorrect, with
  the reason and replacement stated.

“Live” means the current educational edition. It does not mean the underlying
scientific branch is permanently complete.

## Release layout

Editable source remains under `edu/books/<book-id>/`. Rendered PDFs are written
under `output/pdf/edu/<book-id>/<version>/`. Each release includes:

- the student work;
- adult or teacher guidance;
- accessible HTML or equivalent semantic edition;
- the exact book manifest;
- the claim-and-receipt map;
- the changelog entry;
- a release checksum file; and
- release notes that state the scientific and educational boundaries.

## Maria Smith approval and final-publication layout

GitHub availability from the working `edu/` tree is not the same as approval
as a final educational publication. A book enters the final education
collection only after Maria Smith explicitly approves that exact book version.

Before approval:

- the editable book remains in `edu/books/<book-id>/`;
- rendered review copies remain in `output/pdf/edu/<book-id>/<version>/`;
- new manifests record `final_publication.approved: false`; and
- no copy of that version is placed in `publications/education/`.

After explicit approval:

1. finish any changes requested during approval and increment the version if
   those changes alter the already-recorded edition;
2. rerun the complete scientific, educational, accessibility, PDF and checksum
   gates on the updated final copy;
3. record the approved version, approval date and Maria Smith as approver in
   the manifest and release notes;
4. preserve the editable source under `edu/` for future live-work updates;
5. place the complete approved, checksum-bound publication copy under
   `publications/education/current/<book-id>/<version>/`; and
6. commit and push that exact approved copy to `main`.

When a later approved edition replaces it, move the earlier approved package
to `publications/education/superseded/<book-id>/<version>/`. Never overwrite or
silently alter an approved publication package.

## Superseding an edition

When an edition becomes outdated:

1. do not overwrite its source tag or rendered release;
2. record what changed and why;
3. state whether the cause was scientific extension, scientific correction,
   educational correction, safety, accessibility or presentation;
4. mark the old edition `superseded` or `withdrawn`;
5. link old and new versions in both directions; and
6. preserve the exact claim and repository boundary used by each edition.

## GitHub publication

Each verified working version is committed intentionally with only its scoped
files, then pushed to the existing project repository. Placement in
`publications/education/` additionally requires Maria Smith's explicit final
approval for the exact version. Tags and GitHub Releases are separate remote
actions and are not implied by an ordinary push. DOI, Zenodo and other services
always require separate explicit authorization.

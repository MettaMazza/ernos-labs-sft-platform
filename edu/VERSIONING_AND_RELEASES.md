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

Each verified version is committed intentionally with only its scoped files,
then pushed to the existing project repository. Tags and GitHub Releases are
separate remote actions and are not implied by an ordinary push. DOI, Zenodo
and other services always require separate explicit authorization.

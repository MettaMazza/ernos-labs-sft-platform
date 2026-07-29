# Final publication proofreading review

Date: 29 July 2026

Scope: the seven controlled complete-field successor manuscripts listed in
`audits/FINAL_PUBLICATION_PASS_CONTROL_2026-07-29.md`.

This is an editorial review record. It does not supersede a claim package,
receipt, source capture, chronology record, evidence classification or
scientific reconciliation.

## Applied editorial corrections

- Standardised the active manuscripts on British English in ordinary prose.
  The literal-aware v1 pass applied 1,829 safe changes. The v2 extension
  applied 156 additional safe changes, including `authorise`, `catalogue`,
  `centre`, `optimisation` and `rigour` where those words are not protected
  scientific or machine text.
- Replaced the alphabetic copyright approximation in the seven active front
  matters with `©`. Historical publication versions were not edited.
- Corrected the stale reference to “Mathematics 1.3” in the version 1.5
  limitations section.
- Updated stale platform-count prose in the Mathematics and Chemistry
  conclusions to the current lightweight status of 2,751 admitted claims.
- Removed the premature assertion that the Physics candidate was already
  publication-ready. It remains subject to the publication gates and Maria
  Smith's approval.
- Rewrote the abbreviated Information Science, Chemistry and Materials
  conclusions and extended the Classical Computation, Quantum Computation and
  Physics conclusions so that current evidence, historical corrections,
  adverse/unresolved custody, open extension and downstream ownership are
  explicit.
- Corrected generated-prose duplications such as `finite finite`, `generated
  generated`, `canonical canonical` and `comparison comparison` without
  changing candidate labels, counts, statements, decisions or receipts.

## Scientific-text protection

British spelling and general-purpose prose-lint suggestions are not applied
inside identifiers, code, filenames, paths, hashes, machine output, source
titles, quotations, exact current statements or retained claim records.
American spellings that remain in those fields are literal historical or
machine evidence, not unresolved house-style defects.

The first v2 British-prose application exposed a protection gap in additive
`Current exact statement:` fields. The scientific-preservation gate halted
three papers. Forty-five reconciliation statements were then restored directly
from `census/claims.json`, two additional Physics theorem displays were restored
to their exact current `catalog` wording, and the spelling tool's protected
markers were extended. The current preservation gate passes all seven papers.
The halted report remains preserved; it was not relabelled as a pass.

## Codespell review

The complete corpus scan returned 378 findings. Every finding belongs to a
domain term, formula, identifier, source title or exact claim phrase:

| Finding | Count | Disposition |
|---|---:|---|
| `Te` | 306 | Tellurium symbol; preserve. |
| `Mesures` | 13 | Literal source-title spelling; preserve. |
| `AlO`, `AlS` | 12 | Chemical formula fragments; preserve. |
| `Ans` / `ans` | 7 | Calculator notation or literal field; preserve. |
| `FO` | 6 | Literal abbreviation/identifier field; preserve. |
| `parm` | 6 | Machine/data token; preserve. |
| `CaCl`, `CaF` | 10 | Chemical formula fragments; preserve. |
| `GeS`, `LiK`, `SiSe`, `TeH` | 14 | Chemical formula fragments; preserve. |
| `disjointness` | 2 | Correct mathematical term; preserve. |
| `SLAC`, `aaS`, `regio` | 3 | Proper name, identifier or domain term; preserve. |
| `unsucceeded` | 1 | Exact authoritative Physics statement; preserve. |

Codespell therefore identified no safe remaining spelling correction.

## Proselint review

The baseline scan returned 4,591 suggestions. Of these, 4,160 were requests to
replace straight quotation marks. Those occurrences are overwhelmingly JSON,
machine strings, source material and literal records; converting them would
damage exactness. The remaining categories were reviewed as follows:

| Category | Baseline count | Disposition |
|---|---:|---|
| `-ly` phrasal-adjective warnings | 131 | Generated terms and compound technical labels; preserve unless a human-prose instance is independently proven. |
| period-spacing warnings | 112 | Exact theorem/source strings and retained double spacing; preserve. |
| spelling-consistency warnings | 42 | British prose corrected; literal exact/source forms retained. |
| lexical-illusion warnings | 33 | Genuine generated-prose duplications corrected; mathematical `log log`, numeric rows, headings and machine observations retained. |
| redundancy suggestions | 22 | `same exact`, `exact opposite` and similar phrases retained where exactness is substantive or the phrase belongs to a protected statement. |
| ellipsis/trademark suggestions | 36 | Formulae, source names, literal products and machine text; preserve. |
| “uncomparable” suggestions | 16 | `least complete` is a defined ordering phrase in the scientific grammar; preserve. |
| preferred-form/diacritic suggestions | 17 | Names, source text and scientific notation; preserve. |
| date/month/time suggestions | 11 | Source-bound dates, identifiers and chemical notation; preserve. |
| other style warnings | 9 | Contextually reviewed; no unambiguous safe correction remains. |

The linter's `(c)` warning within the Physics body refers to the mathematical
expression `C(v)`, not copyright. Its multiplication warning refers to the
literal current claim statement `-3 x 10^-15`; that exact statement is
preserved.

## Mechanical Markdown review

The current structural audit reports:

- seven of seven manuscripts pass;
- all live branch claim IDs are displayed;
- all required publication surfaces are present;
- all headline claim, candidate, survivor and control totals are present;
- no unbalanced fenced-code delimiter;
- no broken relative Markdown link; and
- no inconsistent Markdown table shape.

Two-space line endings in the Information Science and Materials manuscripts
are intentional Markdown hard breaks, not stray whitespace.

## Current gate position

`tools/verify_publication_scientific_preservation_v2.py` passes 7/7 after the
latest editorial corrections. `tools/audit_publication_guidance_v4.py` passes
7/7 for all 23 manuscript guidance surfaces. The final PDF mechanical, raster,
manual visual and release gates also pass 7/7. These passes do not replace
Maria Smith's final approval, which remains required before any Zenodo action.

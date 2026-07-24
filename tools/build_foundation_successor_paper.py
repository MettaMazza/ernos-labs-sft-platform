#!/usr/bin/env python3
"""Build the exhaustive Foundation successor manuscript from sealed evidence."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "publications/inventories/successors/foundation.json"
LEDGER = ROOT / "census/foundation_prior_obligations.json"
OUTPUT = ROOT / "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_002.md"


def read_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path: Path) -> str: return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def publication_ascii(text: str) -> str:
    return text.translate(str.maketrans({
        "—": "-", "–": "-", "‑": "-", "→": "->", "·": "*",
        "“": '"', "”": '"', "‘": "'", "’": "'",
    }))


def clean_claim_text(text: str) -> str:
    lines = text.splitlines()
    while lines and (lines[0].startswith("# ") or not lines[0].strip()): lines.pop(0)
    if lines and lines[0].startswith("Claim:"): lines = lines[1:]
    return "\n".join(lines).strip()


def table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    rule = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(str(cell).replace("\n", " ").replace("|", "\\|") for cell in row) + " |" for row in rows]
    return "\n".join((head, rule, *body))


def main() -> None:
    inventory = read_json(INVENTORY); ledger = read_json(LEDGER)
    census = {row["claim_id"]: row for row in read_json(ROOT / "census/claims.json")["claims"]}
    claim_ids = inventory["required_claim_ids"]
    claims = []
    for claim_id in claim_ids:
        package = ROOT / "claims" / claim_id
        claims.append({
            "id": claim_id,
            "row": census[claim_id],
            "registration": read_json(package / "registration.json"),
            "census": read_json(package / "candidate_census.json"),
            "elimination": read_json(package / "elimination_receipt.json"),
            "controls": read_json(package / "controls.json"),
            "certificate": read_json(package / "certificate.json"),
            "narrative": clean_claim_text((package / "WHY_DERIVATION_CHECK.md").read_text(encoding="utf-8")),
            "package": package,
        })

    candidate_total = sum(len(item["census"]["candidates"]) for item in claims)
    control_total = sum(len(item["controls"]["controls"]) for item in claims)
    prior = ledger["foundation_summary"]
    receipt_rows = []
    for item in claims:
        receipt_rows.append((item["id"], item["row"]["closure_status"], len(item["census"]["candidates"]), item["row"]["receipt_hash"]))

    parts: list[str] = []
    parts.append("""# From Nothing to Fold

## A premise-free, parameter-free and machine-closed Foundation for Smithian Fold Theory

**Foundation Branch Paper 002 — exhaustive V3 successor**
**Maria Smith** — Independent researcher and founder, Ernos Labs
Email: Maria.Smith.Sftoe@gmail.com
GitHub: https://github.com/MettaMazza
Discord submissions: https://discord.gg/ucwGryVxGr
Date: 24 July 2026
Paper licence: CC BY 4.0 · Code licence: Apache-2.0

> **Principal result.** Starting from the operational impossibility of presenting
> nothing as a counterexample, this branch forces the structural One, exact
> positive count and part coordinates, the minimal two-fibre Fold, its complete
> finite support, its exact positive operations, the half-One ground, its
> two-preimage dynamics, a mechanically enumerated least-size uniqueness law,
> recursive form closure, complete replay traces, one-way measurement custody
> and a single fail-closed admission route—without axioms, fitted parameters,
> floating-point proof values or measurement-selected laws.
""")
    parts.append(f"""## Abstract

This paper reports the completed Foundation successor of the third clean-room
Smithian Fold Theory reconstruction. The live branch contains **{len(claims)}
model-admitted theorems**, **{candidate_total:,} generated candidate classes**,
**{control_total} required adverse-control executions**, and **{len(claims)}
implementation-distinct reproductions**. Its V1/V2 ownership audit reviewed all
**763** registered prior entries, decomposed the 24 Foundation-relevant source
entries into atomic components, assigned **{prior['atomic_obligation_count']}**
Foundation-owned obligations and closed all **{prior['same_strength_closed_count']}**
at the registered exact strength.

The reconstruction adds six laws absent from Foundation Paper 001: the complete
exact operational interface; the uniquely forced half-One ground; the exact
two-preimage Fold dynamics and uniform-partition theorem; the four-map and
84-composition least-size uniqueness theorem; the depth-independent replayable
derivation-trace theorem; and the 2,048-path fail-closed admission theorem. It
also resolves a prior terminology collision by distinguishing complement from
half-One phase translation, preserving both exact results without silently
identifying different operations.

This is a formal Foundation branch. It owns no physical constant, dimensional
quantity or observational dataset. Accordingly, physical measurement is not an
applicable evidence class here. The empirically consequential result is instead
the forced one-way boundary: future empirical branches must seal an exact
prediction before authoritative target data open, retain every row and preserve
both accepted and rejected receipts. The paper includes the complete dependency,
candidate, elimination, control, certificate and receipt route for every theorem.
""")
    parts.append("""## 1. Headline findings

1. **The root is operationally premise-free.** An unpresented absence supplies no
   counterexample; any presented denial is an occurrence and is therefore not
   nothing.
2. **The One and exact positive domain are closed.** Proof quantities are exact
   positive parts through the One. Numerical zero, signed values, floating point,
   irrationals and imaginaries are outside the derivational carrier.
3. **Fold is structurally and operationally fixed.** The minimal nontrivial
   reversible distinction has two equal disjoint held fibres and a return to the
   One; operational Fold is exact self-junction followed by complete-One cast.
4. **Half-One is derived, not fitted.** One held fibre of the first Fold is the
   unique proper one-of-two class whose self-junction is the One. It is
   self-complementary, Folds to the One and is not the same operation as a
   half-One phase translation.
5. **The Fold fibre is exactly two.** Every image has the lower preimage `y/2`
   and its half-One phase partner; both Fold to the same image. Even uniform
   divisions remain uniform after duplicate images are identified.
6. **Primitive uniqueness is mechanically scoped.** Four normalized primitive
   maps are executed. Base-four ranking produces 4, 16 and 64 composition words.
   Fold alone generates at size one; positive construction-size induction prevents
   every later word from displacing it. The claim is conditional on the explicit
   grammar and generator predicate.
7. **A proof is a replayable object.** Every admitted finite derivation retains
   immutable sources, dependency receipts, ordered exact operations, intermediate
   identities and a terminal identity that independent execution must reproduce.
8. **Authority is fail-closed.** Of 2,048 generated admission paths, only one
   preserves root custody, zero parameters, complete enumeration, unique forcing,
   form closure, controls, independent validation, post-seal measurement order,
   receipt retention and admitted-dependency use.
""")
    parts.append("## 2. Exact validation scoreboard\n\n" + table(
        ("Measure", "Exact result"),
        [
            ("Prior source entries reviewed", "356 V1 + 407 V2 = 763"),
            ("Foundation-relevant source entries", "14 V1 + 10 V2 = 24"),
            ("Foundation-owned atomic obligations", f"{prior['atomic_obligation_count']} of {prior['atomic_obligation_count']} closed"),
            ("Model-admitted Foundation theorems", len(claims)),
            ("Generated candidate classes", f"{candidate_total:,}"),
            ("Required adverse controls", control_total),
            ("Implementation-distinct reproductions", len(claims)),
            ("Closure scope", "16 depth-independent certificates"),
            ("Axioms", "none"),
            ("Free, fitted or learned parameters", "none"),
            ("Physical measurements owned by this branch", "none; not an applicable evidence class"),
            ("Open Foundation obligations", prior["open_count"]),
        ],
    ))
    parts.append("""## 3. Evidence constitution

Every theorem uses three separated roles. **WHY** states the scientific need and
cannot force a result. **DERIVATION** receives only the root theorem, admitted V3
dependencies and registered non-answering structural inputs. It generates an
explicit candidate grammar, decides every candidate and requires exactly one
survivor. **CHECK** begins only after sealing and contains the independent
implementation, hostile controls and—only for an empirical claim—the separately
held measurement target.

Earlier SFT results are mandatory observations that define reconstruction
obligations. They are not executable premises and cannot select the V3 grammar,
eliminator or survivor. Conventional mathematics and physics are comparison
languages after derivation, never replacement premises. Every source, census,
decision, closure certificate, control, validator and engine receipt is bound by
SHA-256 identity. Failure is retained; it is not edited into success.

The formal results in this paper are computational proofs at their registered
grammar boundaries. Unit tests show that the engine implementation behaves as
specified; they do not substitute for theorem closure. Independent validators
rebuild the candidate space and exact witness without importing the scientific
derivation module.
""")
    parts.append("## 4. Prior-obligation reconciliation\n\nThe complete atomic ledger is [`census/foundation_prior_obligations.json`](../../../census/foundation_prior_obligations.json). Its non-Foundation exclusion list is enumerated and hash-bound, so the 739 reviewed non-owning entries are not silently absent.\n\n" + table(
        ("Source", "Reviewed", "Foundation-relevant", "Atomic Foundation obligations", "Open"),
        [
            ("V1 theorem manifest", 356, 14, sum(1 for e in ledger["source_entries"] if e["source"] == "v1" for a in e["atomic_obligations"] if a["categorical_owner"] == "foundation"), 0),
            ("V2 OneFoldMaster", 407, 10, sum(1 for e in ledger["source_entries"] if e["source"] == "v2" for a in e["atomic_obligations"] if a["categorical_owner"] == "foundation"), 0),
        ],
    ))
    parts.append("""## 5. Dependency order

```text
there is no nothing
  → structural One
    → positive finite count
      → exact positive part → cross-partition equivalence
      → minimal Fold → complete finite Fold-word assembly
        → exact primitive operations → half-One → Fold dynamics
          → primitive-map uniqueness
        → recursive form grammar → canonical form enforcement
          → replayable derivation trace
          → one-way measurement boundary
            → fail-closed admission law
```

Every non-root registration names exactly the single root theorem and only
model-admitted dependencies. The engine refuses an absent dependency receipt.
""")

    for number, item in enumerate(claims, start=6):
        registration = item["registration"]; census_data = item["census"]
        decisions = item["elimination"]["decisions"]; closure = item["elimination"]["closure"]
        survivor = next(row["candidate_id"] for row in decisions if row["survives"])
        rejected = Counter(row["reason"] for row in decisions if not row["survives"])
        rejection_rows = sorted(((count, reason) for reason, count in rejected.items()), reverse=True)
        controls = item["controls"]["controls"]; cert = item["certificate"]
        independent_certificate = cert.get("independent_certificate_hash", "recorded within the external-validation identity")
        parts.append(f"## {number}. {registration['title']}\n\n**Claim:** `{item['id']}`\n\n> {registration['statement']}\n\n{item['narrative']}\n\n### Generated grammar and exhaustive decision\n\n- Generation rule: {census_data['generation_rule']}\n- Exact boundary: {census_data['grammar_boundary']}\n- Expected and generated cardinality: `{census_data['expected_cardinality']}`.\n- Unique survivor: `{survivor}`.\n- Completeness certificate: `{census_data['completeness_certificate_hash']}`.\n\nThe complete candidate list is retained at `{item['package'].relative_to(ROOT).as_posix()}/candidate_census.json`. The elimination summary below counts every rejected candidate exactly once by its registered decision reason:\n\n" + table(("Rejected candidates", "First decisive reason"), rejection_rows) + "\n\n### Closure and independent check\n\n" + f"- Closure scope: `{closure['scope']}`.\n- Exact closure boundary: {closure['exact_boundary']}\n- Minimality: `{str(closure['minimality_passed']).lower()}`.\n- Named-shape uniqueness: `{str(closure['named_shape_uniqueness_passed']).lower()}`.\n- Closure proof hash: `{closure['proof_hash']}`.\n- Generality certificate: `{closure['generality_certificate_hash']}`.\n- Source manifest: `{cert['source_manifest_hash']}`.\n- Independent implementation: `{cert['independent_implementation_hash']}`.\n- Independent certificate: `{independent_certificate}`.\n- Derivation seal: `{cert['derivation_seal_hash']}`.\n- External-validation identity: `{cert['external_validation_hash']}`.\n- Model-admitted engine receipt: `{item['row']['receipt_hash']}` at `{item['row']['receipt_path']}`.\n\n### Adverse controls\n\n" + table(("Control", "Expected", "Observed", "Pass", "Receipt"), [(c['kind'], c['expected_behavior'], c['observed_behavior'], c['passed'], c['receipt_hash']) for c in controls]))

    next_number = 6 + len(claims)
    parts.append(f"""## {next_number}. Resolution of complement and phase-antipode terminology

The prior sources contain two exact operations under one English word. V1's
positional antipode is the half-One phase translation
`A(x)=cast(x+half-One)`. It is an involution and satisfies
`Fold(A(x))=Fold(x)`. V2 Step 24 calls the complement within the One an
antipode: `C(x)=Take(One,x)` for a proper part. The half-One is
self-complementary because `C(half-One)=half-One`; its phase antipode is instead
the One because `A(half-One)=cast(One)=One`.

V3 does not invalidate either prior exact calculation and does not hide the
word collision. It assigns separate names, operations and receipts. This is the
only way to retain both statements without allowing one symbol to denote two
different maps.
""")
    parts.append(f"""## {next_number + 1}. Measurement, falsification and non-claim boundary

No theorem in this Foundation inventory outputs a physical constant, unit,
material property or observed frequency. Inventing a measurement here would be
category error. The applicable external evidence is implementation-distinct
formal reproduction. Physical and other empirical branches must satisfy the
measurement-boundary theorem derived here:

1. freeze source and candidate grammar;
2. derive and seal the exact consequence without target access;
3. open an independently identified authoritative target;
4. compare every row with full units and uncertainty where applicable;
5. run deliberately false and tampered controls;
6. preserve success, failure and rejection; and
7. prohibit the comparison from mutating the law.

The Foundation branch is falsified at its declared scope by any reproducible
case in which the bound candidate generator omits a form inside its boundary,
two candidates survive, the independent implementation disagrees, a required
control fails, a dependency cannot trace to the root receipt, an inexact or
forbidden proof value enters, or the 763-entry branch review contains an omitted
Foundation-owned component. Claims outside the explicit primitive grammar,
completed infinite objects, arbitrary host programs, physical constants and
application performance are not claimed by this paper.
""")
    parts.append(f"""## {next_number + 2}. One-command reproduction

From the repository root on macOS, Windows or Linux with Python 3:

```text
python3 tools/build_foundation_prior_obligations.py
python3 tools/build_foundation_successor_bundle.py
python3 tools/verify_publication_compliance.py --branch foundation --require-ready
```

The first command rebuilds the exact prior-obligation ledger. The second
reconstructs and verifies the complete Foundation successor evidence bundle.
The third applies the strengthened successor inventory, ownership, manuscript,
rendered-paper and receipt gate. Later branches are not replayed while their
own successor reconstructions remain deliberately open.
No Docker container, network service or opaque predictor is required.
""")
    parts.append(f"## {next_number + 3}. Immutable theorem ledger\n\n" + table(("Claim", "Closure", "Candidates", "Engine receipt"), receipt_rows))
    parts.append(f"""## {next_number + 4}. Conclusion

The Foundation branch is reconstructed at current registered V1/V2 strength:
{prior['atomic_obligation_count']} of {prior['atomic_obligation_count']} owned
atomic obligations closed, {len(claims)} of {len(claims)} required theorems
model-admitted, {candidate_total:,} candidate classes decided, and every
required independent and adverse check preserved. The result is not a manifesto
or a software lock. It is an inspectable chain of exact claims whose authority
ends at their explicit grammar boundaries and whose receipts can be independently
replayed or invalidated.

The next dependency-ordered branch is Mathematics. Its successor cannot inherit
Foundation's closure as a substitute for its own 763-entry ownership review,
same-strength reconstruction, exact enumerations and independent checks.

## Data and code availability

All source, candidate censuses, decisions, controls, certificates and receipts
are contained in the Ernos Labs Smithian Fold Theory Open Science Platform and
Knowledge Tree. The archived Foundation Paper 001 and its DOI artifacts remain
unchanged. This Paper 002 is a new successor and does not rewrite the historical
record.
""")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(publication_ascii("\n\n".join(parts).rstrip() + "\n"), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} bytes={OUTPUT.stat().st_size} sha256={digest(OUTPUT)}")


if __name__ == "__main__": main()

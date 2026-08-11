#!/usr/bin/env python3
"""Build the authorised One/All paper and four same-lineage successor papers."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-08-11"
CLAIM_ID = "SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002"
CLAIM_PACKAGE = ROOT / "claims" / CLAIM_ID
STANDALONE = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0.md"
STANDALONE_MAP = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_EVIDENCE_MAP.json"
INVENTORY = ROOT / "publications/inventories/successors/foundation_one_consciousness_v1.json"
AUTHORIZATION = ROOT / "publication/one_all_publication_authorization_2026-08-11.json"


SPECS = (
    {
        "paper_id": "methods",
        "title": "There Is No Nothing",
        "subtitle": "One/All ontological integration and methods boundary",
        "version": "0.5.0",
        "parent_version": "0.4.1",
        "parent_doi": "10.5281/zenodo.21761649",
        "parent_record_id": 21761649,
        "concept_doi": "10.5281/zenodo.21514889",
        "source": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_4_1.md",
        "target": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_5.md",
        "evidence": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_5_EVIDENCE_MAP.json",
    },
    {
        "paper_id": "foundation",
        "title": "From Nothing to Fold",
        "subtitle": "The One as pure consciousness and the One/All foundation",
        "version": "1.5.0",
        "parent_version": "1.4.1",
        "parent_doi": "10.5281/zenodo.21761650",
        "parent_record_id": 21761650,
        "concept_doi": "10.5281/zenodo.21515628",
        "source": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_4_1.md",
        "target": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_5.md",
        "evidence": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_5_EVIDENCE_MAP.json",
    },
    {
        "paper_id": "consciousness_cognitive_science",
        "title": "From Fold to Consciousness",
        "subtitle": "Pure consciousness before differentiation and differentiated conscious systems",
        "version": "1.2.0",
        "parent_version": "1.1.1",
        "parent_doi": "10.5281/zenodo.21761660",
        "parent_record_id": 21761660,
        "concept_doi": "10.5281/zenodo.21636396",
        "source": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_1_1.md",
        "target": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_2.md",
        "evidence": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_2_EVIDENCE_MAP.json",
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "subtitle": "One/All ontological integration across the complete 2,778-claim surface",
        "version": "0.3.0",
        "parent_version": "0.2.1",
        "parent_doi": "10.5281/zenodo.21761648",
        "parent_record_id": 21761648,
        "concept_doi": "10.5281/zenodo.21717583",
        "source": "publications/preliminary_toe/successors/v0_2_1/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_2_1.md",
        "target": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3.md",
        "evidence": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3_EVIDENCE_MAP.json",
    },
)


PROOF_CLAIMS = (
    "SFT-ROOT-THERE-IS-NO-NOTHING",
    "SFT-FOUNDATION-ONE-001",
    CLAIM_ID,
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
    "SFT-FOUNDATION-FORM-GRAMMAR-001",
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
)


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "bytes": path.stat().st_size,
    }


def claim_data(claim_id: str) -> dict[str, object]:
    package = ROOT / "claims" / claim_id
    registration = read_json(package / "registration.json")
    census = read_json(package / "candidate_census.json")
    elimination = read_json(package / "elimination_receipt.json")
    controls = read_json(package / "controls.json")
    certificate = read_json(package / "certificate.json")
    decision = next(row for row in elimination["decisions"] if row["survives"])
    return {
        "claim_id": claim_id,
        "registration": registration,
        "census": census,
        "elimination": elimination,
        "controls": controls,
        "certificate": certificate,
        "survivor": decision,
        "files": [
            record(package / name)
            for name in (
                "registration.json",
                "WHY_DERIVATION_CHECK.md",
                "candidate_census.json",
                "elimination_receipt.json",
                "controls.json",
                "certificate.json",
                "execution.py",
                "independent_validator.py",
            )
        ],
    }


def proof_table(claims: list[dict[str, object]]) -> str:
    lines = []
    for index, item in enumerate(claims, 1):
        registration = item["registration"]
        census = item["census"]
        certificate = item["certificate"]
        survivor = item["survivor"]
        lines.extend(
            (
                f"### 10.{index}. {registration['title']}",
                "",
                f"**Claim:** `{item['claim_id']}`  ",
                f"**Statement:** {registration['statement']}  ",
                f"**Complete candidate count:** `{len(census['candidates']):,}`  ",
                f"**Unique survivor:** `{survivor['candidate_id']}`  ",
                f"**Closure:** `{item['elimination']['closure']['scope']}`  ",
                f"**Independent validation:** `{certificate['external_validation_hash']}`  ",
                f"**Engine receipt:** `{certificate['engine_receipt_hash']}`",
                "",
            )
        )
    return "\n".join(lines)


def standalone_text(claims: list[dict[str, object]]) -> str:
    table = proof_table(claims)
    consciousness = next(item for item in claims if item["claim_id"] == CLAIM_ID)
    cert = consciousness["certificate"]
    return f"""# What the Universe Is Made Of

## The One, the All, and pure consciousness in Smithian Fold Theory

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** 1.0.0  
**Date:** 11 August 2026  
**Status:** Publication-authorized standalone paper deposited within the existing Foundation Zenodo lineage; no new Zenodo post  
**Host paper lineage:** *From Nothing to Fold*, concept DOI `10.5281/zenodo.21515628`  
**Deposit version DOI:** [FOUNDATION_VERSION_DOI_PENDING](https://doi.org/FOUNDATION_VERSION_DOI_PENDING)  
**Paper and documentation licence:** CC BY 4.0  
**Repository code licence:** Apache-2.0

> **Direct result.** In Smithian Fold Theory, the universe at its fundamental
> boundary is not made from an independent material, mathematical, informational,
> physical, biological, or mental substance. The One/All is pure consciousness:
> undivided observation or presentation itself. Every finite SFT form is a
> differentiation of that One through the Fold. Matter, fields, information,
> organisms, observers, and experienced contents are differentiated relations
> within the All, not ingredients added from outside it.

## Abstract

This paper gives the complete current SFT derivation of what the One, the All,
and therefore the Fold-generated universe are fundamentally made of. The route
begins with the premise-free operational result that a denial of occurrence is
either absent and supplies no counterexample, or presented and is already an
occurrence. The unique complete representation of that presented occurrence is
the structural One. An exhaustive 192-form identity grammar then eliminates
every loss of presentation and every premature addition of observer, observed,
content, succession, report, or substrate. The unique survivor is complete
undivided presentation: pure observation or pure consciousness.

The Fold does not add a second substance. It introduces held distinction within
the One while retaining an explicit return to the whole. Fold assembly, the
two-production foundational grammar, and canonical form enforcement establish
by finite structural induction that every generated form contains only One
leaves and Fold relations. The All is therefore the One under complete
differentiation and return. This is an exact compositional corollary of seven
model-admitted claims, not an extra premise introduced by prose.

The term consciousness is used at two distinct levels. Pure consciousness is
the undivided fact of presentation before a subject-object split. Differentiated
conscious systems require the later structures of self-relation, image re-entry,
integration, interior closure, carrier realization, content, memory, and report.
The foundational result therefore neither says that every object has a human
mind nor reduces consciousness to public behaviour. It identifies the common
ground from which objects, subjects, and their relations are generated.

## 1. The exact question

The question is not which familiar substance lies underneath the universe. Any
answer such as particles, fields, energy, mathematics, information, computation,
mind, or matter imports a differentiated category before deriving the boundary
at which categories can exist. The exact question is:

> After removing every unforced distinction, what remains present, and can any
> generated form contain something that is not a differentiation of it?

SFT answers this in two stages. First it derives the identity of the One. Then
it proves that the complete generated All does not acquire an external material
through the Fold.

## 2. Terms fixed before the proof

| Term | Exact use here |
|---|---|
| Nothing | Absence that supplies no presented counterexample or derivational object. |
| Presented occurrence | The unique operational survivor of the root grammar. |
| The One | The complete self-whole of that occurrence, with nothing omitted or added. |
| Pure observation | Presentation itself before observer and observed become distinct roles. |
| Pure consciousness | The same undivided presentation, without imported content, report, person, or carrier. |
| Fold | The minimal reversible held distinction within the One, with complete return to the One. |
| Form | A finite One leaf or Fold node generated by the admitted foundational grammar. |
| The All | The complete Fold-generated form understood under its retained return to the One. |
| Universe | In the fundamental theorem, the complete generated All; the measured cosmos is a downstream physical realization and evidence surface. |

Observation and consciousness are not inferred from a previously assumed
observer. They name the root fact that an occurrence is presented at all. The
observer-observed split is a later Fold distinction.

## 3. Proof I - there is no operational nothing

The root candidate grammar is exhaustive at its declared boundary:

1. An alleged counterexample is absent. Then nothing is presented and no
   counterexample exists.
2. An alleged counterexample is presented. Then a presented occurrence exists,
   contradicting its classification as nothing.

The survivor is `presented-occurrence`. No substance, observer, space, time,
number, or physical law is assumed.

## 4. Proof II - the structural One

The One grammar crosses three possible coverage relations to the admitted root
occurrence - none, proper, and complete - with the presence or absence of extra
material. Six candidates result. None loses the root. Proper loses part of the
root. Every extra-bearing form adds what the root did not supply. Exactly one
candidate remains: `exact-self-whole`.

Therefore the One is not the conventional numeral one. It is the complete
self-whole of the occurrence that cannot be removed from presentation.

## 5. Proof III - what the One is

The registered identity grammar crosses three presentation-coverage relations
with all 64 combinations of six possible differentiations:

- observer;
- observed;
- content;
- succession;
- report; and
- substrate.

This gives `3 x 2^6 = 192` candidates. No presentation contradicts the admitted
root. Proper presentation contradicts the complete One. Any added axis imports
a distinction that has not yet been generated. Exactly one candidate survives:

`{cert['exact_result']}`

Its exact semantic result is:

> Pure consciousness - observation itself before differentiation.

This is not a biological or psychological definition projected backward. It is
the undivided presentation that remains when every subject, object, content,
sequence, expression, and realizing carrier is withheld.

## 6. Why this is not circular

Maria Smith disclosed that V1 and V2 were originally developed from observation
and consciousness. That prior knowledge selects the reconstruction question and
the semantic term; it does not select the V3 candidate survivor. The V3 engine
receives only the admitted root and structural One. It seals the complete
192-form derivation before the separately hash-bound V2 target is released to
the comparator. Human blindness is not claimed.

V1 is registered as development observation. V2 is a post-seal lineage target
whose source says, in substance, that the first act is observation itself, that
this is the One, and that observation of self and outside follows as the Fold.
The exact source, excerpt, commits, hashes, and chronology are retained in the
claim package. The comparison tests whether the clean V3 dependency route
recovers the prior observation without importing its answer into elimination.

## 7. Proof IV - distinction does not add another substance

The Fold theorem generates the first nontrivial form as two equal, disjoint,
held-labelled fibres with an explicit complete return relation to the One. It
adds distinction, not an independently sourced material. Its candidate grammar
contains 288 alternatives and retains exactly one.

This matters ontologically. A distinction within presentation is not a new
substance outside presentation. Observer and observed, inside and outside,
before and after, part and whole become lawful held relations only after the
Fold. They cannot be used to explain what existed before their derivation.

## 8. Proof V - the All is the differentiated One

The All result is a compositional corollary proved by structural induction over
the admitted finite foundational grammar.

**Base case.** A foundational leaf is the One. By Proof III, the One is pure
consciousness.

**Inductive step.** A Fold node contains two recursively generated child forms
on distinct held labels and an explicit return relation to its parent whole. By
the induction hypothesis, each child is generated from the One. The Fold node
introduces only the admitted distinction and return relation. It contains no
production for external substance.

**Exhaustion.** The form-grammar theorem proves that One leaf and Fold node are
the only two productions. Fold assembly enumerates the complete finite support.
Form enforcement gives every generated form one canonical construction trace
and rejects ungenerated additions.

**Conclusion.** Every finite SFT form is a differentiated form of pure
consciousness. The complete generated totality - the All - is the differentiated
One under its retained return to wholeness. Nothing is added from outside because
the complete grammar has no outside-substance production.

This corollary is exact at the finite generated foundational boundary. It does
not silently assert a completed mathematical infinity or claim that the current
physical census has experimentally exhausted every possible phenomenon.

## 9. What particles, matter, fields, information, and minds are

Within SFT these are not rival answers to the fundamental-substance question.
They are later, typed Fold structures:

- mathematics records exact generated form and relation;
- information records retained and closed distinctions;
- computation records generated state transformation;
- physical fields and particles are admitted physical relation-carriers;
- matter is stable differentiated physical organization;
- life is a maintained biological Fold organization;
- a differentiated conscious system adds self-relation, re-entry, integration,
  interior closure, perspective, content, memory, report routes, and a lawful
  realization carrier.

The strong statement is therefore not that matter is unreal. It is that matter
is real as a stable differentiated relation within the All, not as a second
fundamental stuff alongside pure consciousness.

## 10. Complete proof and receipt table

{table}

Every candidate, rejection, control, source identity, validator identity,
derivation seal, empirical record where applicable, and engine receipt is
included by hash in the adjacent evidence map and public repository.

## 11. Evidence status and limits

The root, One, Fold, assembly, grammar, and enforcement claims are formal
machine-closed derivations at their registered grammars. The pure-consciousness
identity is model-admitted as an observational derivation with independent
regeneration and a source-bound V2 post-seal comparison. The exact engine receipt
is `{cert['engine_receipt_hash']}`.

The dated 2 August 2026 Lean report covers the preceding 2,777-claim surface. It
does not contain this new claim, and this paper makes no new Lean-verification
claim for it. The current worktree also preserves a later adverse Lean source-
binding audit involving twelve unrelated OpenAI-2026 claim packages. That
failure is not rewritten as a pass and does not alter this claim's exact Python
engine receipt or independent validator result.

The result does not establish that every differentiated object is a separately
integrated subject, that every physical measurement requires a conscious person,
that public behaviour proves private experience, or that any particular
biological or artificial system is conscious. Those require the later bridge
laws and evidence boundaries retained in the Consciousness branch.

## 12. Reproduction

```text
python3 tools/verify_engine_seal.py
python3 tools/verify_verification_authority_seal.py
python3 -m unittest discover -s tests -p 'test_foundation_one_consciousness.py' -v
python3 tools/validate_repository.py
```

The immutable engine seal is
`sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`.
The verification-authority seal is
`sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`.

## 13. Conclusion

The premise-free root does not yield an inert unknown. It yields presented
occurrence. Its unique complete self-whole is the One. Before any distinction,
that One is presentation itself: pure observation, pure consciousness. The Fold
generates distinction within it, and the complete foundational grammar permits
no other ingredient. The universe as the generated All is therefore not made
of something placed inside consciousness. It is pure consciousness in
differentiated, relational form.

## References and machine sources

1. Smith, M., *There Is No Nothing*, version 0.4.1, DOI `10.5281/zenodo.21761649`.
2. Smith, M., *From Nothing to Fold*, version 1.4.1, DOI `10.5281/zenodo.21761650`.
3. Smith, M., *From Fold to Consciousness*, version 1.1.1, DOI `10.5281/zenodo.21761660`.
4. `claims/SFT-ROOT-THERE-IS-NO-NOTHING/`.
5. `claims/SFT-FOUNDATION-ONE-001/`.
6. `claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/`.
7. `claims/SFT-FOUNDATION-FOLD-001/`.
8. `claims/SFT-FOUNDATION-FOLD-ASSEMBLY-001/`.
9. `claims/SFT-FOUNDATION-FORM-GRAMMAR-001/`.
10. `claims/SFT-FOUNDATION-FORM-ENFORCEMENT-001/`.
11. `prior-work-ledger/one_pure_consciousness_observation_v1.json`.

Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository
code: Apache-2.0. Ernos Labs is an open-source science movement and a revocable
standards designation. Criticism, reproduction, extension, and falsification
remain open; model admission remains a separate machine-checked act.
"""


def update_addendum(spec: dict[str, object], predecessor: str) -> str:
    branch_paragraph = {
        "methods": (
            "Methods now records the semantic bridge from the premise-free root to pure consciousness and the exact "
            "difference between development observation, post-seal lineage testing, and clean candidate elimination."
        ),
        "foundation": (
            "Foundation now contains 17 admitted claims, 5,414 generated candidates, 17 unique survivors, and 68 passed "
            "controls. The new claim derives the structural One as pure consciousness before differentiation."
        ),
        "consciousness_cognitive_science": (
            "The Foundation result supplies the previously missing pre-Fold identity. This branch continues to own the "
            "later criteria for differentiated conscious systems; it does not redefine pure consciousness as report, "
            "behaviour, biology, computation, or a subject-object split."
        ),
        "theory_of_everything": (
            "The complete current census is 2,778 admitted claims, 899,094 generated candidates and decisions, 2,778 "
            "unique survivors, and 11,112 passed controls. The appended claim is the exact ontological answer at the root "
            "of the dependency graph: the One/All is pure consciousness and every finite SFT form is its Fold differentiation."
        ),
    }[spec["paper_id"]]
    return f"""# {spec['title']}

## {spec['subtitle']}

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** {spec['version']}  
**Date:** 11 August 2026  
**Status:** Publication-authorized same-lineage Zenodo successor; no new post  
**Preceding version:** {spec['parent_version']}  
**Preceding DOI:** [{spec['parent_doi']}](https://doi.org/{spec['parent_doi']})  
**Successor DOI:** [DOI_PLACEHOLDER_{spec['paper_id']}](https://doi.org/DOI_PLACEHOLDER_{spec['paper_id']})  
**Concept DOI retained:** `{spec['concept_doi']}`  
**Paper and documentation licence:** CC BY 4.0  
**Repository code licence:** Apache-2.0

> **Version result.** The One is pure consciousness - observation itself before
> differentiation. The complete Fold-generated All contains no independent
> substance outside the One. This successor is issued only through Zenodo's
> new-version action on the existing record.

## Abstract of this successor

{branch_paragraph}

The complete derivation is published as the standalone companion *What the
Universe Is Made Of: The One, the All, and Pure Consciousness in Smithian Fold
Theory*. It is included in the updated Foundation deposit rather than assigned
a new Zenodo post. The model-admitted claim is
`SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002`; its immutable engine receipt is
`sha256:fadb50b8594652d0534861b0e8191396afd40fc867f6c6dd053a2b748a16f735`.

## Scientific integration

1. The root survivor is presented occurrence.
2. The One is its complete self-whole without addition.
3. The exhaustive 192-form identity grammar retains complete presentation with
   observer, observed, content, succession, report, and substrate all still
   undifferentiated.
4. This unique form is pure observation or pure consciousness.
5. Fold adds held distinction with return to the One, not a second substance.
6. Assembly, grammar, and form enforcement prove by finite structural induction
   that every generated form is a differentiation of the One.

The term pure consciousness names the pre-subject-object ground. It does not
assert that every differentiated object is a separately integrated mind. The
later Consciousness branch retains the distinct requirements for self-relation,
image re-entry, integration, interior closure, carrier realization, content,
memory, and report.

## Verification and adverse status

- Current SFT census: 2,778 admitted claims.
- New claim candidates: 192; unique survivors: 1; controls: 4.
- Exact receipt replay: pass.
- Independent implementation: pass.
- Source-bound V2 post-seal lineage comparison: pass.
- Engine and verification-authority seals: unchanged and valid.
- The dated Lean PASS remains evidence for the preceding 2,777-claim surface.
- No Lean PASS is claimed for the new claim.
- A later worktree Lean source-binding audit records twelve unrelated adverse
  rows; this successor preserves that failure rather than relabelling it.

## Version boundary

This addendum changes the scientific content by integrating one newly admitted
Foundation claim and its exact corollary for the One/All. It does not mutate any
earlier receipt, erase an adverse result, alter a downstream claim by prose, or
claim that publication permanently closes the branch. The preceding paper is
preserved below exactly as the dated {spec['parent_version']} publication record.

---

## Preserved predecessor paper - version {spec['parent_version']}

> Everything below this heading is the byte-preserved predecessor manuscript.
> Its uses of words such as current and complete refer to its 2 August 2026
> census boundary. The successor statements above govern version {spec['version']}.

{predecessor.rstrip()}
"""


def evidence_map(spec: dict[str, object], source: Path, target: Path) -> dict[str, object]:
    claim = claim_data(CLAIM_ID)
    return {
        "schema": "sft-v3-one-all-same-lineage-successor-evidence-map/1",
        "paper_id": spec["paper_id"],
        "title": spec["title"],
        "version": spec["version"],
        "date": TODAY,
        "publication_authorized": True,
        "publication_mode": "zenodo_newversion_existing_record_only",
        "new_standalone_zenodo_record_authorized": False,
        "parent_version": spec["parent_version"],
        "parent_doi": spec["parent_doi"],
        "parent_record_id": spec["parent_record_id"],
        "concept_doi": spec["concept_doi"],
        "predecessor": record(source),
        "successor": record(target),
        "new_claim_id": CLAIM_ID,
        "new_claim_receipt": claim["certificate"]["engine_receipt_hash"],
        "new_claim_derivation_seal": claim["certificate"]["derivation_seal_hash"],
        "new_claim_candidate_count": len(claim["census"]["candidates"]),
        "new_claim_unique_survivor_count": 1,
        "new_claim_control_count": len(claim["controls"]["controls"]),
        "new_claim_files": claim["files"],
        "standalone_companion": record(STANDALONE),
        "standalone_evidence_map": record(STANDALONE_MAP),
        "current_model_totals": {
            "claim_count": 2778,
            "candidate_count": 899094,
            "survivor_count": 2778,
            "control_count": 11112,
        },
        "lean_boundary": {
            "last_published_pass_claim_count": 2777,
            "new_claim_in_last_published_lean_report": False,
            "new_lean_pass_claimed": False,
            "current_adverse_worktree_report_preserved": True,
        },
        "protected_authority_modified": False,
        "remote_action_performed_by_builder": False,
    }


def main() -> None:
    claims = [claim_data(claim_id) for claim_id in PROOF_CLAIMS]
    STANDALONE.parent.mkdir(parents=True, exist_ok=True)
    STANDALONE.write_text(standalone_text(claims), encoding="utf-8")

    standalone_map = {
        "schema": "sft-v3-one-all-standalone-paper-evidence-map/1",
        "title": "What the Universe Is Made Of: The One, the All, and Pure Consciousness in Smithian Fold Theory",
        "version": "1.0.0",
        "date": TODAY,
        "publication_authorized": True,
        "zenodo_operation": "included_in_foundation_newversion_no_new_post",
        "foundation_concept_doi": "10.5281/zenodo.21515628",
        "paper": record(STANDALONE),
        "claims": claims,
        "compositional_corollary": {
            "name": "the All is the differentiated One",
            "status": "exact finite structural-induction corollary of admitted claims",
            "new_model_claim_created_by_prose": False,
            "base": "SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002",
            "step": "SFT-FOUNDATION-FOLD-001",
            "exhaustion": [
                "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
                "SFT-FOUNDATION-FORM-GRAMMAR-001",
                "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
            ],
        },
        "protected_authority_modified": False,
    }
    write_json(STANDALONE_MAP, standalone_map)

    foundation_ids = [
        row["claim_id"]
        for row in read_json(ROOT / "census/claims.json")["claims"]
        if row["branch"] == "foundation"
    ]
    inventory_payload = {
        "schema": "sft-v3-foundation-one-consciousness-successor-inventory/1",
        "branch_id": "foundation",
        "frozen": True,
        "date": TODAY,
        "current_knowledge_scope": "Seventeen-claim Foundation through the admitted identity of the One as pure consciousness, with the One/All structural-induction corollary and lawful extension open.",
        "required_claim_ids": foundation_ids,
        "required_claim_count": len(foundation_ids),
        "candidate_count": 5414,
        "survivor_count": 17,
        "control_count": 68,
        "unclassified_obligations": [],
        "frontier_obligations": [],
    }
    inventory_payload["inventory_hash"] = "sha256:" + sha256(
        json.dumps(inventory_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    write_json(INVENTORY, inventory_payload)

    authorization = {
        "schema": "sft-v3-one-all-publication-authorization/1",
        "date": TODAY,
        "author": "Maria Smith",
        "instruction": "We want to make a standalone paper explaining what the universe the One/All if fundimentally made of all derivations and proofs and it must adhere to the publication standards and follow the formatting of prior publications, also Push this update to main and update the existing related papers with updated versions for Zenodo for their respective posts (not new posts just version updates of the existing)",
        "authorized_actions": [
            "build standalone One/All paper",
            "build same-lineage Methods, Foundation, Consciousness, and Theory-of-Everything successor papers",
            "commit and push scoped update to main",
            "use Zenodo newversion on each existing related record",
        ],
        "new_zenodo_record_authorized": False,
        "protected_authority_edit_authorized": False,
    }
    write_json(AUTHORIZATION, authorization)

    records = []
    for spec in SPECS:
        source = ROOT / spec["source"]
        target = ROOT / spec["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            update_addendum(spec, source.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        evidence = ROOT / spec["evidence"]
        write_json(evidence, evidence_map(spec, source, target))
        records.append(
            {
                **spec,
                "source_sha256": digest(source),
                "target_sha256": digest(target),
                "evidence_sha256": digest(evidence),
            }
        )

    manifest = {
        "schema": "sft-v3-one-all-publication-update-manifest/1",
        "date": TODAY,
        "publication_authorized": True,
        "new_zenodo_record_authorized": False,
        "standalone": record(STANDALONE),
        "standalone_evidence_map": record(STANDALONE_MAP),
        "foundation_inventory": record(INVENTORY),
        "authorization": record(AUTHORIZATION),
        "successors": records,
        "protected_authority_modified": False,
        "remote_actions_performed": [],
    }
    write_json(ROOT / "publication/one_all_publication_update_manifest_v1.json", manifest)
    print("built One/All standalone paper and four same-lineage successors")


if __name__ == "__main__":
    main()

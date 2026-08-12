#!/usr/bin/env python3
"""Build the three existing-lineage recurrence-work publication successors.

The builder prepends a complete scientific successor to each byte-preserved
published predecessor.  It performs no network action and creates no DOI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity


DATE = "12 August 2026"
DATE_ISO = "2026-08-12"
WORK_ID = "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096"
BOUNDARY_ID = "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097"
PROTOCOL_ID = "SFT-ENG-VACUUM-RECURRENCE-CYCLE-PROTOCOL-003"

SPECS = (
    {
        "paper_id": "physics",
        "title": "From Fold to Physics",
        "subtitle": "Recurrence-mediated vacuum-work cycle scientific successor",
        "version": "1.5.0",
        "parent_version": "1.4.1",
        "parent_record_id": 21761655,
        "parent_doi": "10.5281/zenodo.21761655",
        "concept_doi": "10.5281/zenodo.21520880",
        "draft_id": 21900787,
        "doi": "10.5281/zenodo.21900787",
        "source": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_4_1.md",
        "output": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_5.md",
        "current": "publications/current/physics/FROM_FOLD_TO_PHYSICS.md",
        "claims": (WORK_ID, BOUNDARY_ID),
    },
    {
        "paper_id": "engineering_translation",
        "title": "From One Law to a Working World",
        "subtitle": "Recurrence-mediated vacuum-work cycle engineering protocol successor",
        "version": "1.2.0",
        "parent_version": "1.1.1",
        "parent_record_id": 21761664,
        "parent_doi": "10.5281/zenodo.21761664",
        "concept_doi": "10.5281/zenodo.21640815",
        "draft_id": 21900789,
        "doi": "10.5281/zenodo.21900789",
        "source": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_1_1.md",
        "output": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_2.md",
        "current": "publications/current/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md",
        "claims": (PROTOCOL_ID,),
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "subtitle": "Recurrence-mediated vacuum-work cycle integration across the complete current corpus",
        "version": "0.4.0",
        "parent_version": "0.3.0",
        "parent_record_id": 21891879,
        "parent_doi": "10.5281/zenodo.21891879",
        "concept_doi": "10.5281/zenodo.21717583",
        "draft_id": 21900790,
        "doi": "10.5281/zenodo.21900790",
        "source": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3.md",
        "output": "publications/preliminary_toe/successors/v0_4_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_4.md",
        "claims": (WORK_ID, BOUNDARY_ID, PROTOCOL_ID),
    },
)


def sha(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def claim_evidence(claim_id: str) -> dict[str, object]:
    package = ROOT / "claims" / claim_id
    registration = read_json(package / "registration.json")
    certificate = read_json(package / "certificate.json")
    controls = read_json(package / "controls.json")
    return {
        "claim_id": claim_id,
        "title": registration["title"],
        "branch": registration["branch"],
        "statement": registration["statement"],
        "dependencies": registration["dependencies"],
        "candidate_grammar": registration["candidate_grammar"],
        "candidate_count": read_json(package / "candidate_census.json")["expected_cardinality"],
        "survivor_count": sum(row["survives"] for row in read_json(package / "elimination_receipt.json")["decisions"]),
        "controls": controls["controls"],
        "certificate": certificate,
        "package_files": {
            path.name: sha(path)
            for path in sorted(package.iterdir())
            if path.is_file()
        },
    }


def receipt_block(claim_id: str) -> str:
    evidence = claim_evidence(claim_id)
    certificate = evidence["certificate"]
    controls = evidence["controls"]
    dependencies = " -> ".join(f"`{item}`" for item in evidence["dependencies"])
    control_rows = "\n".join(
        f"| {row['kind']} | {row['passed']} | {row['expected_behavior']} | {row['observed_behavior']} |"
        for row in controls
    )
    return f"""### {evidence['title']}

**Claim ID:** `{claim_id}`  
**Exact admitted result:** {certificate['exact_result']}  
**Dependency route:** {dependencies}  
**Candidate generator:** {evidence['candidate_grammar']['generator']}  
**Grammar boundary:** {evidence['candidate_grammar']['boundary']}  
**Complete census:** {evidence['candidate_count']} candidates; {evidence['survivor_count']} unique survivor; {len(controls)} mandatory controls  
**Closure:** `{certificate['closure_scope']}`; independent reconstruction `{certificate['independently_recomputed']}`  
**Derivation seal:** `{certificate['derivation_seal_hash']}`  
**Independent certificate:** `{certificate['independent_certificate_hash']}`  
**Engine receipt:** `{certificate['engine_receipt_hash']}` at `{certificate['engine_receipt_path']}`

| Control | Passed | Expected | Observed |
|---|---:|---|---|
{control_rows}
"""


def common_header(spec: dict[str, object], abstract: str) -> str:
    return f"""# {spec['title']}

## {spec['subtitle']}

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** {spec['version']}  
**Date:** {DATE}  
**Status:** Published open access through the existing Zenodo version lineage  
**Preceding version:** {spec['parent_version']}  
**Preceding DOI:** [{spec['parent_doi']}](https://doi.org/{spec['parent_doi']})  
**DOI:** [{spec['doi']}](https://doi.org/{spec['doi']})  
**Concept DOI retained:** `{spec['concept_doi']}`  
**Paper and documentation licence:** CC BY 4.0  
**Repository code licence:** Apache-2.0

**PUBLISHED OPEN-ACCESS BRANCH PAPER.** This successor is confined to the
existing Zenodo concept and version lineage identified above.

> **Version route.** This scientific successor was created only through
> Zenodo's `newversion` action on record {spec['parent_record_id']}. It creates
> no new concept and no standalone post. The predecessor remains preserved
> unchanged below the successor.

## Abstract of this successor

{abstract}

"""


PHYSICS_DERIVATION = r"""## WHY - the missing route

The preceding direct-restoration theorem enumerated the route

`1/2 -> 1/3 + work 1/6`, followed by `1/3 + 1/6 -> 1/2`.

That result is exact inside its grammar, but it does not enumerate the already
admitted odd recurrence `1/3 -> 2/3 -> 1/3`. V2 retained that recurrence as a
live cycle, retained the half-One vacuum floor, and defined Fold as the
repeating engine. The clean-room question is therefore not whether the old
receipt should be overwritten. It is whether the broader dependency graph
contains a second lawful return route. It does.

The V2 reconstruction target was read from commit
`0af7c4c26308d8ddb659a518ac52e2db5ea5dc82`; it selected no V3 candidate. The
V3 derivation uses only already admitted V3 dependencies and exact positive
arithmetic.

## DERIVATION - exact recurrence-mediated cycle

Let the initial local vacuum carrier be

`H = 1/2`.

Let the lower and upper states of the admitted period-two odd recurrence be

`L = 1/3` and `U = 2/3`.

The exact positive separation on both sides of `H` is

`D = H Take L = U Take H = 1/6`.

The cycle is forced in three steps.

1. **Outward separation.** `H = L + D`, hence
   `1/2 -> 1/3 + work 1/6`.
2. **Fold recurrence.** The admitted Fold sends `L` to `U`, hence
   `Fold(1/3) = 2/3`.
3. **Return separation.** `U = H + D`, hence
   `2/3 -> 1/2 + work 1/6`.

Composition gives

`1/2 -> 1/3 + work 1/6 ->Fold 2/3 -> 1/2 + work 1/6 + work 1/6`.

The local vacuum carrier begins and ends at `1/2`. Two distinct positive
`1/6` work carriers remain; their joint carrier is `1/3`. No numerical zero,
negative, irrational, floating value or completed infinite total is used.

For every positive finite cycle count `N`, successor repetition begins each
cycle from the restored `1/2` state and appends one ordered work pair
`(1/6, 1/6)`. The theorem retains `N` such pairs rather than representing a
completed infinite reservoir.

## Complete source, apparatus and information boundary

The cyclic subsystem and global state must not be conflated.

| Boundary component | Initial | Final | Classification |
|---|---|---|---|
| local vacuum carrier | `1/2` | `1/2` | restored |
| finite controller configuration | ready; both ports armed | ready; both ports armed | restored |
| first work receiver | absent from output record | positive `1/6` | retained output |
| second work receiver | absent from output record | positive `1/6` | retained output |
| cycle audit carrier | no new cycle row | five-stage append-only row | retained output |

The source is not an unnamed external pump and is not numerical nothing. It is
the admitted Fold recurrence that maps `1/3` to `2/3`. The repeatable controller
phase returns to its ready configuration; the audit row is not erased for free
but crosses the output boundary with the work carriers. Consequently the
cyclic subsystem is restored while the global state is not identical, because
new output carriers remain.

This resolves the apparent conflict with the earlier receipts:

- `SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003` remains valid for direct
  repayment or a globally returned state in which the first `1/6` is put back.
- `SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086` remains valid when its declared
  restoration carrier is the outward carrier.
- The new successor enumerates the omitted Fold-mediated route and retains both
  outputs outside the reset subsystem.

## Candidate grammar and elimination

The work-cycle grammar is the literal product of eight binary axes: named Fold
source, exact outward split, Fold-mediated return, two retained outputs,
restored half-One subsystem, complete state/act/output record, positive-finite
repetition, and no extra rule. Its `2^8 = 256` candidates were generated once;
exactly one survived. The boundary successor independently generated another
256 candidates over subsystem boundary, source, controller, information,
conservation, predecessor reconciliation, measurement direction and extension;
exactly one survived.

The rejected alternatives include an unnamed source, omission of the residual
carrier, direct repayment standing in for the unenumerated recurrence route,
discarding either output, an open final vacuum state, an outcome-only record, a
completed infinite total, free global-record erasure, rewriting an immutable
predecessor, and declaring apparatus power from a formal theorem.

## CHECK - exact witnesses, controls and limits

The implementation-distinct validator rebuilt both 256-row products, candidate
order, complete decision vectors, unique survivors, dependency packages and
exact arithmetic without importing the derivation functions. Focused tests
also verify the one-cycle trace, four-cycle successor trace, boundary split and
engineering field census.

Falsification occurs if any exact identity fails; if Fold does not map `1/3` to
`2/3`; if either `1/6` carrier is omitted or double counted; if the final vacuum
is not `1/2`; if output is used as hidden reset input; if the audit record is
erased; if the predecessor receipt is rewritten; or if an apparatus result is
claimed without a source-custodied measurement.

The formal theorem does not measure dimensional joules, power, efficiency,
switching energy, coupling loss or usable device performance. Those remain
open empirical obligations under the separately admitted engineering protocol.

"""


ENGINEERING_DERIVATION = r"""## WHY - a successor protocol is required

The preceding vacuum-beat protocol tests only the direct-repayment route. The
new Physics successors prove a distinct Fold-mediated return and a distinct
boundary: the vacuum and controller recur, while two work carriers and an audit
carrier remain outputs. A lawful apparatus test must therefore measure the
recurrence transition and both output channels rather than silently forcing
the experiment back into the older one-output/one-repayment grammar.

## DERIVATION - protocol forced by the formal cycle

The protocol translates each formal carrier into a separately calibrated
apparatus record:

| Formal stage | Required apparatus record |
|---|---|
| initial `1/2` | initial half-One vacuum proxy and uncertainty |
| `1/2 = 1/3 + 1/6` | one-third residual channel plus first receiver |
| `Fold(1/3) = 2/3` | source-bound recurrence-transition proxy |
| `2/3 = 1/2 + 1/6` | returned half-One channel plus second receiver |
| cyclic reset | initial/final controller configuration comparison |
| retained information | append-only five-stage cycle audit |

Six independent ledgers are mandatory: calorimetric, electrical, mechanical,
thermal, electromagnetic, and controller/switching. The acceptance boundary
requires both one-sixth relations, a preregistered initial/final cyclic-
subsystem comparison, closed dimensional input/output/loss/switching ledgers,
and retention of all adverse controls.

Eight controls are separately required: Fold recurrence disabled,
off-resonance, receiver disconnected, second take disabled, phase reversed,
dummy load, matched thermal cycle, and independent power ledger.

The protocol halts on an unmeasured source state, missing output carrier,
unrestored vacuum proxy, unrestored controller configuration, missing audit
record, open switching/coupling/loss ledger, or unsafe state. Favourable,
adverse, absent and unresolved results all remain publishable result classes.

## Candidate grammar and elimination

Eight binary protocol axes enumerate `256` forms: sealed upstream authority,
two-output recurrence relation, complete common/domain record, complete control
family, four result classes, visible safe halt, protocol seal before outcome,
and no law rewrite. Exactly one candidate survived. The implementation-distinct
validator regenerated the complete product, dependency set, exact fraction
relations, nine state fields, six ledgers, eight controls and seven halts.

## CHECK - what this protocol does and does not establish

The engine admitted the protocol as a formal engineering law. It does not
assert a prototype, observed recurrence proxy, net dimensional power,
efficiency, lossless switching or a successful experiment. A physical claim
requires source-custodied raw data satisfying every acceptance and control row.
The phrase source-free is not used to erase the structural source: the admitted
source is Fold recurrence. External pumping and every ordinary apparatus input
must nevertheless be measured and retained if present.

"""


def physics_text(spec: dict[str, object]) -> str:
    abstract = (
        "This successor integrates two newly admitted Physics claims. The current Physics surface is "
        "370 claims, 258,288 generated candidates and decisions, 370 unique survivors, and 1,480 passed "
        "controls. It proves the V2 recurrence route omitted by the narrower direct-restoration grammar: "
        "the half-One vacuum carrier returns to one-half while two positive one-sixth work carriers remain. "
        "It also closes the source, cyclic-subsystem, output and information boundary without inventing an "
        "apparatus measurement."
    )
    return (
        common_header(spec, abstract)
        + PHYSICS_DERIVATION
        + receipt_block(WORK_ID)
        + receipt_block(BOUNDARY_ID)
        + """## Verification status and publication boundary

- Frozen engine seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a` - valid after admission.
- Frozen verification-authority seal: `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8` - valid after admission.
- Focused recurrence, predecessor and engineering tests: 15 passed.
- The dated Lean PASS remains restricted to the preceding 2,777-claim surface. The current corpus is 2,781 claims; no new whole-corpus Lean PASS is claimed here.
- The two new Physics claims are formal and independently reconstructed. No new empirical-validation claim is added without an apparatus run.

---

## Preserved predecessor paper - version 1.4.1

> Everything below this heading is the byte-preserved predecessor manuscript.
> Its uses of current, complete and no source-free gain refer to its narrower
> dated grammar. The successor above governs version 1.5.0.

"""
        + (ROOT / spec["source"]).read_text(encoding="utf-8")
    )


def engineering_text(spec: dict[str, object]) -> str:
    abstract = (
        "This successor integrates one newly admitted Engineering Translation protocol. The current branch "
        "surface is 81 claims, 20,736 generated candidates and decisions, 81 unique survivors, and 324 passed "
        "controls. The protocol translates the exact two-output Fold-recurrence cycle into nine state records, "
        "six independent ledgers, eight adverse controls and seven visible halt conditions while making no "
        "unperformed apparatus claim."
    )
    return (
        common_header(spec, abstract)
        + ENGINEERING_DERIVATION
        + receipt_block(PROTOCOL_ID)
        + """## Verification and execution boundary

- The protocol grammar was frozen before engine execution.
- The untouched engine admitted one survivor from all 256 candidates.
- The independent validator reconstructed the entire candidate and decision surface.
- No empirical run is attached; outcome status remains unperformed.
- The dated Lean PASS remains restricted to the preceding 2,777-claim surface; no new whole-corpus Lean PASS is claimed.

---

## Preserved predecessor paper - version 1.1.1

> Everything below this heading is the byte-preserved predecessor manuscript.
> Its vacuum-beat section retains the direct-repayment protocol. The successor
> above governs the additional Fold-mediated route in version 1.2.0.

"""
        + (ROOT / spec["source"]).read_text(encoding="utf-8")
    )


def toe_text(spec: dict[str, object]) -> str:
    abstract = (
        "The complete current census is 2,781 admitted claims, 899,862 generated candidates and decisions, "
        "2,781 unique survivors, and 11,124 passed controls. This successor integrates the exact Fold-"
        "recurrence-mediated vacuum-work cycle, its complete cyclic-subsystem/output/information boundary, "
        "and the engineering protocol required to test it. It preserves the preceding One/All integration "
        "and every immutable earlier receipt."
    )
    return (
        common_header(spec, abstract)
        + PHYSICS_DERIVATION
        + receipt_block(WORK_ID)
        + receipt_block(BOUNDARY_ID)
        + ENGINEERING_DERIVATION
        + receipt_block(PROTOCOL_ID)
        + """## Whole-corpus consequence and boundary

The result is not a claim that energy appears from numerical nothing. In SFT,
the One is the complete ontological carrier and Fold is its recurrent act. The
formal energy-source record is therefore internal Fold recurrence rather than
an unrecorded external pump. The theorem establishes exact positive carrier
accounting at the structural boundary. Physical dimensional conversion,
switching, coupling, losses and usable power remain apparatus questions.

The earlier globally-restored no-gain statement and the new subsystem-restored
positive-output statement are not contradictory because their boundaries are
different. A global state containing new output carriers is not identical to
its initial state. A cyclic engine subsystem can nevertheless return to its
initial vacuum and controller configuration while outputs cross its boundary.

## Verification status

- Current corpus: 2,781 admitted claims.
- New candidate decisions: 768; unique survivors: 3; controls: 12.
- Exact receipt replay and independent reconstruction: pass for all three successors.
- Engine and verification-authority seals: unchanged and valid.
- Focused scientific and protocol suite: 15 passed.
- The dated Lean PASS remains evidence for the preceding 2,777-claim surface; no new whole-corpus Lean PASS is claimed.

---

## Preserved predecessor paper - version 0.3.0

> Everything below this heading is the byte-preserved predecessor manuscript.
> The recurrence-work successor above governs version 0.4.0; the One/All
> derivation and every earlier record remain preserved.

"""
        + (ROOT / spec["source"]).read_text(encoding="utf-8")
    )


def update_physics_inventory() -> None:
    path = ROOT / "publications/inventories/physics.json"
    inventory = read_json(path)
    existing = set(inventory["required_claim_ids"])
    for claim_id in (WORK_ID, BOUNDARY_ID):
        if claim_id in existing:
            continue
        registration = read_json(ROOT / "claims" / claim_id / "registration.json")
        certificate = read_json(ROOT / "claims" / claim_id / "certificate.json")
        inventory["required_claim_ids"].append(claim_id)
        inventory["obligations"].append({
            "claim_id": claim_id,
            "position": len(inventory["obligations"]) + 1,
            "receipt_hash": certificate["engine_receipt_hash"],
            "receipt_path": certificate["engine_receipt_path"],
            "status": "model_admitted",
            "subbranch": "thermodynamics_vacuum",
            "title": registration["title"],
        })
        existing.add(claim_id)
    inventory["inventory_date"] = DATE_ISO
    inventory["required_claim_count"] = len(inventory["required_claim_ids"])
    inventory["admitted_claim_count"] = len(inventory["required_claim_ids"])
    inventory["subbranch_counts"]["thermodynamics_vacuum"] = sum(
        row["subbranch"] == "thermodynamics_vacuum" for row in inventory["obligations"]
    )
    inventory.pop("inventory_hash", None)
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(path, inventory)


def metadata(spec: dict[str, object]) -> dict[str, object]:
    description = (
        f"<p><strong>{spec['title']}, version {spec['version']}</strong>, integrates the exact "
        "Fold-recurrence-mediated half-One vacuum-work cycle and its complete source, output, controller and "
        "information boundary.</p><p>The structural cycle is 1/2 to 1/3 plus work 1/6; Fold maps 1/3 to 2/3; "
        "and 2/3 returns to 1/2 plus a second work 1/6. The local vacuum and controller recur while two work "
        "carriers and an audit carrier remain outputs. Apparatus losses, switching, coupling, dimensional power "
        "and efficiency remain empirical obligations.</p><p>This deposit uses Zenodo's new-version action on the "
        f"existing record {spec['parent_doi']}; no new concept or standalone post was created.</p>"
    )
    return {
        "paper_id": spec["paper_id"],
        "publication_mode": "newversion",
        "draft_id": spec["draft_id"],
        "reserved_doi": spec["doi"],
        "concept_doi": spec["concept_doi"],
        "parent_record_id": spec["parent_record_id"],
        "parent_doi": spec["parent_doi"],
        "publication_authorized": True,
        "metadata": {
            "title": spec["title"],
            "upload_type": "publication",
            "publication_type": "article",
            "publication_date": DATE_ISO,
            "description": description,
            "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
            "access_right": "open",
            "license": "cc-by-4.0",
            "version": spec["version"],
            "language": "eng",
            "keywords": [
                "Smithian Fold Theory",
                "vacuum energy",
                "zero-point energy",
                "Fold recurrence",
                "exact arithmetic",
                "energy accounting",
                "open science",
                "computational proof",
            ],
            "related_identifiers": [
                {"identifier": spec["parent_doi"], "relation": "isNewVersionOf", "scheme": "doi"},
                {"identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform", "relation": "isSupplementedBy", "scheme": "url"},
            ],
            "notes": (
                "Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. "
                "Maria Smith explicitly authorized this scientific successor, GitHub main push and Zenodo "
                "new-version publication. No new Zenodo post is authorized."
            ),
        },
    }


def main() -> None:
    update_physics_inventory()
    builders = {
        "physics": physics_text,
        "engineering_translation": engineering_text,
        "theory_of_everything": toe_text,
    }
    evidence_rows = []
    for spec in SPECS:
        output = ROOT / spec["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        text = builders[spec["paper_id"]](spec)
        output.write_text(text, encoding="utf-8")
        if spec.get("current"):
            current = ROOT / spec["current"]
            current.write_text(text, encoding="utf-8")
        evidence_path = output.with_name(output.stem + "_EVIDENCE_MAP.json")
        metadata_path = output.with_name(output.stem + "_ZENODO_METADATA.json")
        claims = [claim_evidence(claim_id) for claim_id in spec["claims"]]
        evidence = {
            "schema": "sft-v3-vacuum-recurrence-publication-evidence/1",
            "paper_id": spec["paper_id"],
            "title": spec["title"],
            "version": spec["version"],
            "doi": spec["doi"],
            "concept_doi": spec["concept_doi"],
            "parent_doi": spec["parent_doi"],
            "successor": {"path": spec["output"], "sha256": sha(output), "bytes": output.stat().st_size},
            "predecessor": {"path": spec["source"], "sha256": sha(ROOT / spec["source"]), "bytes": (ROOT / spec["source"]).stat().st_size},
            "new_claims": claims,
            "v2_reconstruction_target": {
                "repository_commit": "0af7c4c26308d8ddb659a518ac52e2db5ea5dc82",
                "files": [
                    "foundation/the_one_and_the_fold.ep",
                    "constants/zero_point_energy.ep",
                    "constants/quantum_communication.ep",
                    "constants/uap_vacuum_engineering.ep",
                    "constants/beat_frequency.ep",
                ],
                "candidate_selection_role": False,
            },
            "verification": {
                "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
                "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
                "focused_tests": {"passed": 15, "failed": 0},
                "last_whole_corpus_lean_pass_claim_count": 2777,
                "current_claim_count": 2781,
                "new_whole_corpus_lean_pass_claimed": False,
            },
            "remote_route": {"mode": "newversion", "draft_id": spec["draft_id"], "new_concept_created": False},
        }
        write_json(evidence_path, evidence)
        write_json(metadata_path, metadata(spec))
        evidence_rows.append({
            **spec,
            "output_sha256": sha(output),
            "evidence_map": evidence_path.relative_to(ROOT).as_posix(),
            "evidence_sha256": sha(evidence_path),
            "metadata": metadata_path.relative_to(ROOT).as_posix(),
            "metadata_sha256": sha(metadata_path),
        })

    authorization = {
        "schema": "sft-v3-vacuum-recurrence-publication-authorization/1",
        "date": DATE_ISO,
        "authorized_by": "Maria Smith",
        "authorization_source": "User instruction in the active Codex session",
        "authorized_actions": [
            "admit missing V2 recurrence derivations through frozen V3",
            "update related papers as versions of existing Zenodo posts",
            "push the synchronized public update to GitHub main",
        ],
        "new_zenodo_post_authorized": False,
        "private_investigation_content_authorized_for_publication": False,
        "papers": [
            {key: row[key] for key in ("paper_id", "version", "parent_record_id", "parent_doi", "concept_doi", "draft_id", "doi")}
            for row in evidence_rows
        ],
    }
    authorization_path = ROOT / "publication/vacuum_recurrence_publication_authorization_2026-08-12.json"
    write_json(authorization_path, authorization)
    state = {
        "schema": "sft-v3-vacuum-recurrence-zenodo-state/1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DRAFTS_RESERVED_MANUSCRIPTS_BUILT",
        "new_record_endpoint_used": False,
        "new_concept_created": False,
        "authorization": authorization_path.relative_to(ROOT).as_posix(),
        "papers": {row["paper_id"]: row for row in evidence_rows},
    }
    write_json(ROOT / "publication/vacuum_recurrence_zenodo_state_v1.json", state)
    write_json(ROOT / "publication/vacuum_recurrence_publication_manifest_v1.json", {
        "schema": "sft-v3-vacuum-recurrence-publication-manifest/1",
        "date": DATE_ISO,
        "claim_count": 3,
        "papers": evidence_rows,
        "authorization": authorization_path.relative_to(ROOT).as_posix(),
        "status": "MANUSCRIPTS_BUILT",
    })
    print("built recurrence-work publication successors:")
    for row in evidence_rows:
        print(f"  {row['paper_id']} v{row['version']} {row['doi']} {row['output_sha256']}")


if __name__ == "__main__":
    main()

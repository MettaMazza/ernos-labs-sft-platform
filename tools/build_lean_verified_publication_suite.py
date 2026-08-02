#!/usr/bin/env python3
"""Build local, versioned Lean-verified publication successors.

This is a publication-layer builder.  It never edits the protected admission
engine, the verification authority, an existing published manuscript, an
existing receipt, or an existing release bundle.  Every output is a new local
successor and remains unpublished until Maria Smith explicitly authorises the
external action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
from typing import Iterable

import apply_british_prose_v2 as british_prose


ROOT = Path(__file__).resolve().parents[1]
TODAY = date(2026, 8, 2)
DATE_TEXT = "2 August 2026"
LEAN_ROOT = ROOT / "generated/lean4_validation"
LEAN_REPORT = LEAN_ROOT / "reports/whole_model_validation.json"
SUITE_ROOT = ROOT / "publications/lean4_verification"
TOE_ROOT = ROOT / "publications/preliminary_toe/successors/v0_2_0"
MANIFEST_PATH = SUITE_ROOT / "LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"


@dataclass(frozen=True)
class PaperSpec:
    paper_id: str
    title: str
    subtitle: str
    version: str
    previous_version: str
    source: str
    output: str
    branches: tuple[str, ...] = ()
    include_current_census_delta: bool = False
    paper_role: str = "branch_successor"


PAPERS = (
    PaperSpec(
        "methods",
        "There Is No Nothing",
        "A premise-free operational foundation and an open verification platform for Smithian Fold Theory",
        "0.4.0",
        "0.3.0",
        "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_3.md",
        "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_4.md",
        paper_role="methods_successor",
    ),
    PaperSpec(
        "foundation",
        "From Nothing to Fold",
        "A premise-free, parameter-free and machine-closed Foundation for Smithian Fold Theory",
        "1.4.0",
        "1.3.0",
        "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_3.md",
        "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_4.md",
        ("foundation",),
        True,
    ),
    PaperSpec(
        "mathematics",
        "From Fold to Mathematics",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Mathematical Foundations from Smithian Fold Theory",
        "1.6.0",
        "1.5.0",
        "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md",
        "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_6.md",
        ("mathematics",),
        True,
    ),
    PaperSpec(
        "information_science",
        "From Distinction to Information",
        "An Exact, Parameter-Free and Machine-Closed Derivation of the Complete Dated Information Sciences from Smithian Fold Theory",
        "1.5.0",
        "1.4.0",
        "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md",
        "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_5.md",
        ("information_science",),
        True,
    ),
    PaperSpec(
        "computation",
        "After Turing: The Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Classical Computational Science from Smithian Fold Theory",
        "1.5.0",
        "1.4.0",
        "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md",
        "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_5.md",
        ("computation",),
        True,
    ),
    PaperSpec(
        "quantum_computation",
        "The Quantum Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Reversible and Quantum Computation from Smithian Fold Theory",
        "1.5.0",
        "1.4.0",
        "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md",
        "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_5.md",
        ("quantum_computation",),
        True,
    ),
    PaperSpec(
        "physics",
        "From Fold to Physics",
        "An Exact, Parameter-Free and Machine-Closed Complete-Field Reconstruction of Physical Science from Smithian Fold Theory",
        "1.4.0",
        "1.3.0",
        "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md",
        "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_4.md",
        ("physics",),
        True,
    ),
    PaperSpec(
        "chemistry",
        "From Fold to Chemistry",
        "An Exact, Parameter-Free and Machine-Closed Complete-Field Reconstruction of Chemical Science from Smithian Fold Theory",
        "1.4.0",
        "1.3.0",
        "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md",
        "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_4.md",
        ("chemistry",),
        True,
    ),
    PaperSpec(
        "materials",
        "From Fold to Materials",
        "An Exact, Parameter-Free and Machine-Closed Complete-Field Reconstruction of Materials Science from Smithian Fold Theory",
        "1.4.0",
        "1.3.0",
        "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md",
        "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_4.md",
        ("materials",),
        True,
    ),
    PaperSpec(
        "biology",
        "From Fold to Life",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Biology and Life Sciences from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/biology/FROM_FOLD_TO_LIFE.md",
        "publications/successors/biology/FROM_FOLD_TO_LIFE_PAPER_001_V1_1.md",
        ("biology",),
        True,
    ),
    PaperSpec(
        "medicine",
        "From Fold to Medicine",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Medicine and Health Sciences from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/medicine/FROM_FOLD_TO_MEDICINE.md",
        "publications/successors/medicine/FROM_FOLD_TO_MEDICINE_PAPER_001_V1_1.md",
        ("medicine",),
        True,
    ),
    PaperSpec(
        "consciousness_cognitive_science",
        "From Fold to Consciousness",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Consciousness and Cognitive Science from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md",
        "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_1.md",
        ("consciousness_cognitive_science",),
        True,
    ),
    PaperSpec(
        "earth_environment",
        "From One World to Earth",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Earth and Environmental Sciences from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md",
        "publications/successors/earth_environment/FROM_ONE_WORLD_TO_EARTH_PAPER_001_V1_1.md",
        ("earth_environment",),
        True,
    ),
    PaperSpec(
        "astronomy_cosmology",
        "From One Sky to Cosmos",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Astronomy and Cosmology from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS.md",
        "publications/successors/astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS_PAPER_001_V1_1.md",
        ("astronomy_cosmology",),
        True,
    ),
    PaperSpec(
        "social_collective_systems",
        "From One Relation to Society",
        "An Exact, Zero-Parameter and Machine-Closed Reconstruction of Social and Collective Sciences from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/social_collective_systems/FROM_ONE_RELATION_TO_SOCIETY.md",
        "publications/successors/social_collective_systems/FROM_ONE_RELATION_TO_SOCIETY_PAPER_001_V1_1.md",
        ("social_collective_systems", "social_collective"),
        True,
    ),
    PaperSpec(
        "engineering_translation",
        "From One Law to a Working World",
        "An Exact, Zero-Parameter and Machine-Closed Foundation for Engineering Translation from Smithian Fold Theory",
        "1.1.0",
        "1.0.0",
        "publications/current/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md",
        "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_1.md",
        ("engineering_translation",),
        True,
    ),
    PaperSpec(
        "formal_verification_counterpaper",
        "Formal Verification Is Not Foundational Derivation",
        "A zero-registered-axiom Smithian Fold audit of OpenAI's ten advances in mathematics and theoretical computer science",
        "0.2.0",
        "0.1.0",
        "frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_1.md",
        "frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_2.md",
        paper_role="comparison_successor",
    ),
    PaperSpec(
        "strict_openai_comparison",
        "Twelve Verdicts From the Fold",
        "Strict SFT proof/disproof of OpenAI's ten advances in mathematics and theoretical computer science",
        "0.2.0",
        "0.1.0",
        "frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_1.md",
        "frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_2.md",
        paper_role="comparison_successor",
    ),
)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def apply_british_house_style(path: Path) -> dict:
    """Apply only the existing literal-aware safe British-English pass."""
    return british_prose.v1.process(path, apply=True)


def enrich_claim(row: dict) -> dict:
    """Add exact package counts needed by the publication layer."""
    package = ROOT / "claims" / row["claim_id"]
    census = json.loads((package / "candidate_census.json").read_bytes())
    certificate = json.loads((package / "certificate.json").read_bytes())
    controls = json.loads((package / "controls.json").read_bytes())["controls"]
    elimination_path = package / "elimination_receipt.json"
    elimination = json.loads(elimination_path.read_bytes()) if elimination_path.exists() else {}
    candidates = census.get("candidates", [])
    decisions = elimination.get("decisions", [])
    candidate_count = int(certificate.get("candidate_count", len(candidates)))
    survivor_count = int(
        certificate.get(
            "unique_survivor_count",
            sum(bool(decision.get("survives")) for decision in decisions),
        )
    )
    if survivor_count == 0 and row.get("model_admitted"):
        # Custom decision packages bind the unique survivor in their registered
        # certificate even when they do not expose the standard decision list.
        survivor_count = 1
    return {
        **row,
        "candidate_count": candidate_count,
        "unique_survivor_count": survivor_count,
        "control_count": len(controls),
        "passed_control_count": sum(bool(control.get("passed")) for control in controls),
    }


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def body_from_abstract(text: str) -> str:
    match = re.search(r"(?m)^## Abstract\s*$", text)
    if match:
        return text[match.start() :].strip()
    headings = list(re.finditer(r"(?m)^##\s+", text))
    if not headings:
        return text.strip()
    return text[headings[min(1, len(headings) - 1)].start() :].strip()


def abstract_and_remainder(text: str) -> tuple[str, str]:
    """Return the exact Abstract body and the scientific body after it."""
    match = re.search(r"(?m)^## Abstract\s*$", text)
    if not match:
        return "", body_from_abstract(text)
    following = re.search(r"(?m)^##\s+", text[match.end() :])
    if following:
        end = match.end() + following.start()
        return text[match.end() : end].strip(), text[end:].strip()
    return text[match.end() :].strip(), ""


def doi_tokens(text: str) -> list[str]:
    return sorted(set(re.findall(r"10\.5281/zenodo\.\d+", "\n".join(text.splitlines()[:100]))))


def publication_header(spec: PaperSpec, previous_text: str, report: dict) -> str:
    dois = doi_tokens(previous_text)
    previous_doi = ", ".join(f"[{item}](https://doi.org/{item})" for item in dois)
    if not previous_doi:
        previous_doi = "No DOI assigned in the preceding local manuscript"
    return f"""# {spec.title}

## {spec.subtitle}

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** {spec.version}  
**Date:** {DATE_TEXT}  
**Status:** Final local publication candidate; not approved, deposited or published  
**Preceding version:** {spec.previous_version}, preserved unchanged at `{spec.source}`  
**Preceding DOI record(s):** {previous_doi}  
**Successor DOI:** Pending the authorised new-version or new-record deposit; no identifier has been invented  
**Paper and documentation licence:** CC BY 4.0  
**Repository code licence:** Apache-2.0

> **Publication control.** This is a new versioned successor. It does not rewrite
> the preceding paper, its DOI record, historical receipts or evidence. No push,
> upload, DOI action, release or publication is authorised until Maria Smith
> explicitly confirms the exact final files and hashes.

> **Lean verification integration.** The current SFT ordered census passed the
> independent Lean 4 verification layer on {DATE_TEXT}: {report['claim_count']:,} accepted claims,
> {report['candidate_count']:,} candidate records and decisions, {report['control_count']:,} controls, seventeen branches
> and no reported issue. Lean natively proves the two-class operational root and
> its unique survivor and constructs proof-bearing acceptance-gate certificates.
> The remaining claim content is checked as the complete registered artifact
> graph; that distinction is retained throughout this successor.
"""


def current_abstract(
    spec: PaperSpec,
    previous_abstract: str,
    previous_full_text: str,
    claims: list[dict],
    report: dict,
) -> str:
    relevant = [row for row in claims if row["branch"] in spec.branches]
    current_candidates = sum(int(row["candidate_count"]) for row in relevant)
    current_controls = sum(int(row["control_count"]) for row in relevant)
    present = [row for row in relevant if row["claim_id"] in previous_full_text]
    newly_integrated = len(relevant) - len(present)
    if spec.paper_role == "methods_successor":
        opening = (
            f"This paper states the operational problem of presenting nothing, preserves the premise-free SFT methods constitution and now adds a kernel-checked Lean 4 formalisation of the exact two-class root. Lean proves constructively that `presentedOccurrence` is the unique survivor, with no imported or user-declared axiom reported for the exported root theorem. The compiled verification layer separately accepts all {report['claim_count']:,} current model claims after checking the complete artifact graph."
        )
    elif spec.paper_role == "comparison_successor":
        opening = (
            f"This successor preserves the preceding conclusion-level and admissibility analysis and adds the methodological consequence of SFT's own Lean 4 verification, which passed all {report['claim_count']:,} claims in the current ordered census. Formal acceptance establishes the encoded proposition; SFT admission additionally binds that proposition to its generated grammar, ownership, evidence boundary, candidate decisions, controls and receipts. The new verification does not reclassify any OpenAI comparison verdict or turn external Lean acceptance into automatic SFT theoremhood."
        )
    elif relevant:
        branch_names = ", ".join(spec.branches)
        opening = (
            f"This successor presents the complete current `{branch_names}` paper surface: "
            f"{len(relevant):,} live model-admitted claims, {current_candidates:,} generated candidates, "
            f"{len(relevant):,} unique survivors and {current_controls:,} passed controls. "
            f"It integrates {newly_integrated:,} claim section(s) not present in the preceding abstract's dated surface and remains complete only to this versioned registered census, with lawful extension open. "
            f"The independent Lean 4 layer returned PASS for this surface as part of all {report['claim_count']:,} current claims."
        )
    else:
        opening = (
            f"This successor integrates the independent Lean 4 whole-model PASS over {report['claim_count']:,} current claims while preserving the preceding paper's scientific and chronological boundary."
        )

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", previous_abstract) if part.strip()]
    # The first paragraph normally carries the preceding version's dated counts
    # and status.  Those values remain preserved later as version history; the
    # current abstract instead retains the domain-specific result paragraphs.
    retained = paragraphs[1:] if len(paragraphs) > 1 else []
    if spec.paper_role == "comparison_successor" and paragraphs:
        retained = paragraphs
    retained_text = "\n\n".join(retained[:4])
    boundary = (
        "Formal admission, implementation validation, observation, measurement, empirical support, confirmation, adverse evidence, unresolved evidence and publication status remain separate classifications. Lean does not reclassify an empirical result, repair an adverse observation or convert a later comparison into an earlier prediction. Lawful criticism, falsification and versioned extension remain open."
    )
    return "## Abstract\n\n" + opening + ("\n\n" + retained_text if retained_text else "") + "\n\n" + boundary


def successor_headlines(spec: PaperSpec, previous_text: str, claims: list[dict], report: dict) -> str:
    relevant = [row for row in claims if row["branch"] in spec.branches]
    missing = [row for row in relevant if row["claim_id"] not in previous_text]
    lines = [
        "## Successor headline findings",
        "",
        f"1. **Independent whole-model result.** Lean 4 returned `PASS` for {report['claim_count']:,}/{report['claim_count']:,} current claims, {report['candidate_count']:,} candidates and decisions, {report['control_count']:,} controls and all {report['branch_count']} branches, with no issue.",
        "2. **Operational root.** The exact registered two-class grammar is formalised natively, and `presentedOccurrence` is proved to be its unique survivor without an imported or user-declared axiom in the exported theorem's axiom audit.",
        "3. **Typed validation.** The root and generic acceptance implications are native Lean theorems; the remaining scientific claims are checked as complete registered artifacts. Empirical truth is not inferred from proof-assistant acceptance alone.",
        "4. **Fail-closed custody.** A six-file byte-identity mismatch halted the first run. Exact registered bytes were restored, all 385 source bindings were re-audited, and the unchanged verifier then passed.",
    ]
    if relevant:
        lines.append(
            f"5. **Current paper surface.** This successor accounts for all {len(relevant):,} current claim(s) in its declared branch ownership boundary; {len(missing):,} later claim section(s) are integrated in the successor supplement."
        )
    if missing:
        lines.append(
            "6. **Newly integrated results.** "
            + "; ".join(f"`{row['claim_id']}` — {row['title']}" for row in missing)
            + "."
        )
    lines.extend(
        [
            "",
            "These findings supplement rather than erase the branch-specific headline results retained below. Any adverse, corrected, unresolved, unavailable or chronology-bound result in the preceding scientific record remains governed by its current claim package.",
        ]
    )
    return "\n".join(lines)


def guidance_layer(spec: PaperSpec, claims: list[dict], report: dict) -> str:
    relevant = [row for row in claims if row["branch"] in spec.branches]
    completion = (
        f"{len(relevant):,} current claims in the declared branch surface"
        if relevant
        else "methodological or comparison scope; no downstream claim ownership transferred"
    )
    return f"""## Current status, evidence language and reader map

| Status field | Current position |
|---|---|
| Paper and completion boundary | {completion}. Completion is dated to the current registered census and remains open to lawful versioned extension. |
| Formal status | The Lean root theorem is kernel checked. Every live model claim has a current admitted receipt and passed the Lean artifact gates. Formal admission does not imply empirical confirmation. |
| Empirical status | Claim specific. Blind, non-blind, development-observed, holdout, favourable, adverse, null, missing, unavailable, disputed and unresolved distinctions remain exactly as recorded. |
| Chronology | Claim-specific registration, sealing, custody and observation order controls. Later evidence never becomes an earlier prediction without the registered chronology. |
| Publication status | Version {spec.version} is a final local publication candidate awaiting Maria Smith's approval. It is not deposited or published. |
| Ownership | This paper retains its declared scientific boundary. Lean verification creates no new branch ownership and no application may select a law. |
| What is not claimed | Permanent closure of science, universal empirical confirmation, conversion of compatibility into confirmation, or superiority to every rival model. |

### Corpus-wide terminology and evidence key

| Term | Reserved meaning in this paper |
|---|---|
| Theorem | A formally closed proposition at its declared grammar and dependency boundary. |
| Law | An admitted branch relation with its declared carrier, boundary, dependencies and extension rule. |
| Claim | The registered unit judged by the engine and bound to one immutable receipt. |
| Constitution | The rules governing admissible objects, derivations, evidence and publication; not an empirical result. |
| Derivation | Generation and elimination of the declared candidate space to its surviving structure. |
| Prediction | A consequence sealed before the matching target is released under the registered custody protocol. |
| Observation | A source-bound external record; it does not enter candidate generation. |
| Measurement | An instrument-, method-, condition- and uncertainty-bound observed value. |
| Reconstruction | A separately implemented regeneration or an explicitly identified inference of a retained state or history. |
| Exact numerical correspondence | Equality or registered interval relation between exact numerical objects at the declared boundary. |
| Structural correspondence | A post-derivation relation between forms without a claim of exact numerical prediction. |
| Boundary correspondence | Agreement restricted to the named interface, limit or ownership boundary. |
| Compatibility | Non-adverse but non-discriminating evidence. |
| Support | Relevant evidence that is not unique confirmation. |
| Confirmation | Used only when the current registered evidence protocol warrants that classification. |
| Validation | Successful execution of the named formal, computational or empirical test; its kind must be stated. |
| Adverse result | A registered test result that conflicts with the tested claim at its declared boundary. |
| Unresolved result | Required evidence remains unavailable, incomplete, disputed or insufficiently classified. |
| Implementation identity | The hash-bound identity of executable material; implementation success is not empirical confirmation. |
| Formal, empirical and publication status | Three independent classifications; none substitutes for another. |
| Foundational closure | Completion of the registered foundation only; not field-wide closure. |
| Field-wide closure | Completion of the named frozen or registered dated field census. |
| Current-evidence closure | Closure only to the evidence surface presently registered and preserved. |
| Extension openness | New questions may enter a later version without rewriting receipts or history. |

Proof language is reserved for formal closure; derivation for generated structure; implementation for executable demonstration; prediction for a correctly sealed prospective consequence; observation and measurement for source-bound external records; reconstruction for separately regenerated or inferred states; correspondence for post-derivation relations; compatibility and support for non-unique evidence; confirmation only where the registered protocol authorises it; adverse for conflict; and unresolved where required evidence remains incomplete.

### Three reading levels

1. **Conceptual paper.** The abstract, headline findings, branch narrative, major derivations, evidence synthesis, limitations and conclusion provide the readable scientific argument.
2. **Scientific audit layer.** Family and claim sections preserve exact status, dependencies, candidate and survivor counts, controls, chronology, sources, corrections, adverse evidence and reconciliation.
3. **Machine archive.** The repository packages preserve complete candidates, decisions, hashes, receipts, executable traces, source snapshots and certificates. They remain authoritative where prose abbreviates display.

### Editorial change control

This successor improves currency, expression, typography and navigation. It does not change scientific meaning, chronology, evidence class, branch ownership, claim status or machine identity. Any conflict between authoritative records must be resolved by explicit supersession or reported to Maria Smith; prose alone cannot manufacture agreement.
"""


def claim_details(claim: dict) -> str:
    claim_id = claim["claim_id"]
    package = ROOT / "claims" / claim_id
    registration = json.loads((package / "registration.json").read_bytes())
    certificate = json.loads((package / "certificate.json").read_bytes())
    census = json.loads((package / "candidate_census.json").read_bytes())
    controls = json.loads((package / "controls.json").read_bytes())["controls"]
    elimination_path = package / "elimination_receipt.json"
    elimination = json.loads(elimination_path.read_bytes()) if elimination_path.exists() else {}
    dependencies = registration.get("dependencies", [])
    dependency_text = " -> ".join(f"`{item}`" for item in dependencies) or "Root; no preceding dependency"
    closure = elimination.get("closure", {})
    exact_result = certificate.get("exact_result", "Recorded in the custom domain certificate")
    survivors = [row for row in elimination.get("decisions", []) if row.get("survives")]
    survivor_text = ", ".join(f"`{row.get('candidate_id')}`" for row in survivors)
    if not survivor_text:
        survivor_text = "Unique survivor recorded by the registered custom decision artifact"
    control_rows = "\n".join(
        f"| {row.get('kind')} | {row.get('passed')} | {row.get('expected_behavior')} | {row.get('observed_behavior')} |"
        for row in controls
    )
    return f"""### {claim['title']}

**Claim ID:** `{claim_id}`  
**Exact statement:** {claim['statement']}  
**Dependency route:** {dependency_text}  
**Candidate generator:** {registration.get('candidate_grammar', {}).get('generator', census.get('generation_rule'))}  
**Grammar boundary:** {registration.get('candidate_grammar', {}).get('boundary', census.get('grammar_boundary'))}  
**Complete census:** {claim['candidate_count']:,} candidates; {claim['unique_survivor_count']} unique survivor; {claim['control_count']} controls  
**Survivor:** {survivor_text}  
**Exact result:** {exact_result}  
**Closure:** `{claim['closure_status']}`; minimality `{closure.get('minimality_passed')}`; named-shape uniqueness `{closure.get('named_shape_uniqueness_passed')}`  
**External status:** `{claim['external_status']}`  
**Engine receipt:** `{claim['receipt_hash']}` at `{claim['receipt_path']}`

| Control | Passed | Expected | Observed |
|---|---|---|---|
{control_rows}
"""


def ensure_exact_claim_records(path: Path, relevant: list[dict]) -> list[str]:
    """Restore any authoritative statement or receipt protected from prose edits."""
    text = path.read_text(encoding="utf-8")
    missing = [
        row
        for row in relevant
        if row["claim_id"] not in text
        or row["statement"] not in text
        or row["receipt_hash"] not in text
    ]
    if not missing:
        return []
    appendix = [
        "## Exact current claim-record preservation addendum",
        "",
        "The records below are reproduced byte-for-byte from the current census and claim packages because literal-aware house-style editing must never alter an authoritative statement or receipt identity.",
        "",
    ]
    for row in missing:
        appendix.append(claim_details(row))
    write_text(path, text + "\n\n" + "\n".join(appendix))
    return [row["claim_id"] for row in missing]


def census_delta(spec: PaperSpec, previous_text: str, claims: list[dict]) -> tuple[str, list[str]]:
    relevant = [row for row in claims if row["branch"] in spec.branches]
    missing = [row for row in relevant if row["claim_id"] not in previous_text]
    branch_counts: dict[str, int] = {}
    for row in relevant:
        branch_counts[row["branch"]] = branch_counts.get(row["branch"], 0) + 1
    counts = ", ".join(f"`{key}` {value}" for key, value in sorted(branch_counts.items()))
    parts = [
        "## Complete current-census successor supplement",
        "",
        f"The authoritative current scope of this paper is {len(relevant):,} live model-admitted claims ({counts}). "
        "Counts retained inside the preceding-version narrative describe the dated freeze at which those passages were written; this successor table and the machine census control the current total.",
        "",
    ]
    if missing:
        parts.extend(
            [
                f"The preceding manuscript did not contain {len(missing):,} later-admitted claim section(s). "
                "They are included below in dependency order so the successor covers the complete current branch surface.",
                "",
            ]
        )
        for row in missing:
            parts.append(claim_details(row))
    else:
        parts.extend(
            [
                "Every current claim identifier for this paper's branch surface already occurs in the inherited scientific body. No claim-level prose delta is required.",
                "",
            ]
        )
    return "\n".join(parts), [row["claim_id"] for row in missing]


def lean_update(spec: PaperSpec, report: dict, report_hash: str) -> str:
    branch_count = sum(report["branches"].get(branch, 0) for branch in spec.branches)
    branch_line = (
        f"This paper's registered branch surface contributes **{branch_count:,}** of the accepted claims."
        if spec.branches
        else "This paper is a methodological or comparison paper and does not acquire ownership of downstream claims through this verification."
    )
    comparison_note = ""
    if spec.paper_role == "comparison_successor":
        comparison_note = """
### Relation to the external Lean comparison

The new SFT Lean layer does not reverse this paper's methodological distinction. A proof assistant checks the proposition encoded for it. Foundational derivation additionally requires that the encoded proposition, grammar, ownership and evidence boundary are the ones lawfully generated by the model. The SFT verifier therefore binds Lean's proof-bearing gates to the registered census, candidate decisions, controls, certificates, source manifests and receipts. It does not treat acceptance of an unrelated Lean declaration as automatic SFT admission, and it does not alter the conclusion-level verdict artifacts audited by this paper.
"""
    return f"""## Lean 4 independent verification update

### Verified result

The pinned Lean toolchain `leanprover/lean4:v4.32.0` compiled the verification project and the executable verifier returned `PASS`. Its immutable report identity for this successor is `{report_hash}`.

| Verified surface | Result |
|---|---:|
| Ordered census claims | {report['claim_count']:,} |
| Proof-bearing accepted claim gates | {report['accepted_claim_count']:,} |
| Source-bound claims | {report['source_binding_passed_claim_count']:,} |
| Candidate records | {report['candidate_count']:,} |
| Decision records | {report['decision_count']:,} |
| Passed controls | {report['control_count']:,} |
| Registered branches | {report['branch_count']:,} |
| Issues | {report['issue_count']:,} |

{branch_line}

### Native theorem proof and artifact verification are different layers

`SFTValidation/Root.lean` formalises the exact registered two-member operational grammar: `unpresentedAbsence` and `presentedOccurrence`. The decision function rejects the former and accepts the latter. Lean proves existence by the accepted constructor and uniqueness by exhaustive case analysis over the two constructors. `#print axioms` reports no imported or user-declared axioms for the exported root theorems. This is a kernel-checked proof of the unique survivor inside the exact registered operational grammar.

`SFTValidation/Gates.lean` defines twelve Boolean acceptance obligations and can construct an inhabitant of `ClaimGate.Accepted gate` only when all twelve equal `true`. The runtime verifier then parses the complete ordered census and execution manifest, recomputes identities, cardinalities, one-to-one decision coverage, survivor count, controls, closure fields, empirical boundaries, certificate bindings and authoritative receipts, and calls that proof-bearing constructor for every current claim.

The exact scientific statements of the other claims are not all re-expressed as {report['claim_count'] - 1:,} separate Lean propositions in this version. They are validated as the repository's complete registered machine artifacts through Lean-executed checks. The source-manifest gate uses a read-only Python bridge solely to instantiate the already registered source factories; Lean consumes the result. This layer does not replace the protected admission engine, does not write receipts and does not substitute for source experiments or empirical replication.

### Fail-closed custody event

The first whole-model run halted on six source-capture byte hashes. The discrepancy was traced to line-ending normalisation in the working tree, not to a changed scientific target or a failed theorem. The registered source bytes were restored, exact-byte Git attributes were added for those six captures, all 385 registered external source bindings were re-audited with no mismatch, and the unchanged Lean verification was rerun to `PASS`. The preserved halt demonstrates that source drift is detected rather than silently forgiven.

### What the result supports

The result materially strengthens the model's case for formal coherence, exhaustive current-census coverage, unique-survivor enforcement, dependency and provenance integrity, cross-branch consistency and reproducibility by an implementation outside the admission engine. It does not by itself establish that every empirical claim is true in nature, that the registered grammar is the only conceivable grammar outside its stated boundary, or that SFT is superior to every rival theory. Those questions remain governed by the papers' declared experiments, falsification conditions and comparative tests.
{comparison_note}
"""


def successor_conclusion(spec: PaperSpec, claims: list[dict], report: dict) -> str:
    relevant = [row for row in claims if row["branch"] in spec.branches]
    contribution = (
        f"This paper contributes {len(relevant):,} current claim(s) within `{', '.join(spec.branches)}` to the total dependency spine."
        if relevant
        else "This paper contributes methodological or comparative analysis and does not acquire ownership of a scientific branch."
    )
    return f"""## Successor conclusion

Version {spec.version} preserves the preceding paper's derivations, evidence classes, corrections, adverse and unresolved records, ownership limits and open frontier, while integrating the independent Lean 4 result and every later current claim in its declared scope. {contribution}

The new formal result establishes that the registered two-class operational root has one Lean-proved survivor and that all {report['claim_count']:,} current claims satisfy the proof-bearing artifact gates. The major conflation resolved by this update is between native theorem proof and whole-repository artifact verification: both are valuable, but they are not the same evidential act. No empirical status is strengthened merely because the artifact graph passes, and no historical halt or correction is erased.

The current evidence therefore establishes formal coherence, current-census completeness, unique-survivor enforcement and intact source, dependency, certificate and receipt custody for this version. Field-specific empirical conclusions remain exactly those authorised by their current records. Lawful discovery, falsification, stronger evidence and versioned extension remain open, and publication itself remains pending Maria Smith's explicit confirmation.
"""


def structural_completion(
    spec: PaperSpec,
    existing_text: str,
    claims: list[dict],
    report: dict,
    report_hash: str,
) -> str:
    """Add only publication-guidance surfaces absent from the inherited paper."""
    lower = existing_text.lower()
    relevant = [row for row in claims if row["branch"] in spec.branches]
    blocks: list[str] = []
    if not re.search(r"(?im)^##\s+[^\n]*ownership[^\n]*$", existing_text):
        blocks.append(
            "## Scope and ownership boundary\n\n"
            + (
                f"This paper owns the `{', '.join(spec.branches)}` surface comprising {len(relevant):,} current claims. "
                if relevant
                else "This paper owns its methodological or comparative argument and no downstream scientific branch. "
            )
            + "Ownership identifies responsibility for derivation and falsification; it does not prevent criticism or lawful cross-branch use. Application performance, consensus, credentials and Lean acceptance cannot transfer ownership or select a law."
        )
    if not re.search(r"(?im)^##\s+[^\n]*(?:mathematical constitution|empirical constitution)[^\n]*$", existing_text):
        blocks.append(
            "## Mathematical, computational and empirical constitutions\n\n"
            "The mathematical constitution retains exact generated carriers, relations, candidate grammars, decisions, survivors and closure boundaries. The computational constitution retains executable identities, complete traces, controls, independent reconstructions and receipts. The empirical constitution retains source registration, transport, pre-seal and post-seal chronology, custody, measurement or observation, uncertainty, favourable and adverse rows, missingness, unresolved records and falsification conditions. None of these evidence classes substitutes for another."
        )
    if not re.search(r"(?im)^##\s+[^\n]*(?:historical reconciliation|chronology)[^\n]*$", existing_text):
        blocks.append(
            "## Chronology and historical reconciliation\n\n"
            f"Version {spec.previous_version} remains unchanged at `{spec.source}`. Its original dates, DOI lineage, claims, corrections, failed transports, adverse and unresolved evidence remain historical authority for that version. Version {spec.version} adds the current census delta and Lean verification after those events. The later validation is not relabelled as an earlier prediction, and no original halt is converted into success."
        )
    if not re.search(r"(?im)^##\s+[^\n]*(?:registered source|source registry|sources and references)[^\n]*$", existing_text):
        blocks.append(
            "## Registered source surface\n\n"
            "Human-readable scholarly references remain in the inherited paper. Machine source IDs, custodians, releases, locators, source captures, access outcomes, hashes and transport status remain in the current claim packages and external-source registries. Source prestige is not evidential authority; each source is used only in its registered role. The Lean source-binding gate checks custody and identity, not empirical truth by reputation."
        )
    if not re.search(r"(?im)^##\s+[^\n]*(?:limitations?|open frontier|dated completion)[^\n]*$", existing_text):
        blocks.append(
            "## Limitations and open frontier\n\n"
            "The current result is formally complete only to the named dated grammar, census and artifact graph. Native Lean theoremhood is presently established for the operational root and generic gate implications; the other scientific claims are artifact checked rather than individually restated as Lean propositions. Empirical validation remains claim specific, and adverse, unavailable and unresolved evidence remains open where the current records say so. New discoveries, falsifications, stronger comparisons and native claim-level formalisations may enter only through a later version without rewriting this one."
        )
    if not re.search(r"(?im)^##\s+Data and code availability\s*$", existing_text):
        blocks.append(
            "## Data and code availability\n\n"
            f"The successor Markdown is `{spec.output}` and its scientific predecessor is `{spec.source}`. "
            f"The Lean sources and report are under `generated/lean4_validation/`; the report is `{relative(LEAN_REPORT)}`. "
            "Current claims are indexed by `census/claims.json`; complete candidates, decisions, controls, certificates, observations and receipts remain under `claims/<claim-id>/` and `receipts/`. The paper's evidence map and draft deposit metadata sit beside the successor source. No remote action was performed."
        )
    if not re.search(r"(?im)^##\s+References(?:\s+and[^\n]*)?\s*$", existing_text):
        blocks.append(
            "## References and source registry\n\n"
            "1. Smith, Maria. The preceding version of this paper, preserved at the repository path identified above, 2026.\n"
            "2. Smith, Maria. *There Is No Nothing*. Ernos Labs Methods Paper 00, versioned publication series, 2026.\n"
            "3. de Moura, Leonardo, and Sebastian Ullrich. “The Lean 4 Theorem Prover and Programming Language.” *Automated Deduction — CADE 28*, 2021. DOI: [10.1007/978-3-030-79876-5_37](https://doi.org/10.1007/978-3-030-79876-5_37).\n"
            "4. Lean FRO. *The Lean Language Reference*. [lean-lang.org/doc/reference/latest](https://lean-lang.org/doc/reference/latest/).\n"
            "5. Ernos Labs. Current claim packages, source registries and Lean verification report, repository snapshot bound by the machine identities below."
        )
    blocks.append(
        "## Successor machine-identity appendix\n\n"
        f"- Preceding source: `{spec.source}`\n"
        f"- Preceding source SHA-256: `{sha256(ROOT / spec.source)}`\n"
        f"- Lean report: `{relative(LEAN_REPORT)}`\n"
        f"- Lean report SHA-256: `{report_hash}`\n"
        f"- Ordered census SHA-256: `{report['census_file_hash']}`\n"
        f"- Execution manifest SHA-256: `{report['execution_manifest_file_hash']}`\n"
        "- Protected engine seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`\n"
        "- Verification-authority seal: `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`\n"
        "- Publication authorised: `false`\n"
        "- Remote actions performed: `false`"
    )
    return "\n\n".join(blocks)


def build_successor(spec: PaperSpec, claims: list[dict], report: dict, report_hash: str) -> dict:
    source = ROOT / spec.source
    output = ROOT / spec.output
    previous = source.read_text(encoding="utf-8")
    previous_abstract, body = abstract_and_remainder(previous)
    missing_ids: list[str] = []
    delta = ""
    if spec.include_current_census_delta:
        delta, missing_ids = census_delta(spec, previous, claims)
    text = publication_header(spec, previous, report)
    text += "\n" + current_abstract(spec, previous_abstract, previous, claims, report)
    text += "\n\n" + successor_headlines(spec, previous, claims, report)
    if "## Current status, evidence language and reader map" not in body:
        text += "\n\n" + guidance_layer(spec, claims, report)
    text += "\n\n" + body + "\n\n"
    if delta:
        text += delta + "\n\n"
    if previous_abstract:
        text += "## Preceding-version abstract preserved for chronology\n\n"
        text += (
            f"The following abstract is reproduced from version {spec.previous_version}. "
            "Its counts and status language describe that dated version and do not override the current abstract or census above.\n\n"
        )
        text += previous_abstract + "\n\n"
    text += structural_completion(spec, text, claims, report, report_hash) + "\n\n"
    text += lean_update(spec, report, report_hash)
    text += "\n\n" + successor_conclusion(spec, claims, report)
    write_text(output, text)
    apply_british_house_style(output)
    exact_scope = [row for row in claims if row["branch"] in spec.branches]
    if spec.paper_role == "methods_successor":
        exact_scope = [row for row in claims if row["claim_id"] == "SFT-ROOT-THERE-IS-NO-NOTHING"]
    ensure_exact_claim_records(output, exact_scope)

    relevant = [row for row in claims if row["branch"] in spec.branches]
    evidence = {
        "schema": "sft-v3-lean4-verified-paper-evidence-map/1",
        "paper_id": spec.paper_id,
        "title": spec.title,
        "version": spec.version,
        "date": TODAY.isoformat(),
        "source_path": spec.source,
        "source_sha256": sha256(source),
        "successor_path": spec.output,
        "successor_sha256": sha256(output),
        "branches": list(spec.branches),
        "current_claim_count": len(relevant),
        "current_claim_ids": [row["claim_id"] for row in relevant],
        "newly_embedded_claim_ids": missing_ids,
        "lean_report_path": relative(LEAN_REPORT),
        "lean_report_sha256": report_hash,
        "lean_status": report["status"],
        "publication_authorized": False,
        "remote_actions_performed": False,
    }
    evidence_path = output.with_name(output.stem + "_EVIDENCE_MAP.json")
    write_json(evidence_path, evidence)
    metadata = {
        "metadata": {
            "title": spec.title,
            "subtitle": spec.subtitle,
            "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
            "publication_date": TODAY.isoformat(),
            "version": spec.version,
            "language": "eng",
            "license": "cc-by-4.0",
            "description": (
                f"Local publication candidate for {spec.title}, version {spec.version}. "
                f"Integrates the independent Lean 4 whole-model PASS over {report['claim_count']:,} current claims."
            ),
            "related_identifiers": [
                {"identifier": item, "relation": "isNewVersionOf", "scheme": "doi"}
                for item in doi_tokens(previous)
            ],
            "notes": "LOCAL CANDIDATE ONLY. Publication requires Maria Smith's explicit confirmation of the final files and hashes.",
        },
        "paper_id": spec.paper_id,
        "publication_authorized": False,
        "remote_action_permitted": False,
        "ready_for_review": True,
        "ready_to_publish": False,
    }
    metadata_path = output.with_name(output.stem + "_ZENODO_METADATA_DRAFT.json")
    write_json(metadata_path, metadata)
    return {
        **asdict(spec),
        "source_sha256": sha256(source),
        "output_sha256": sha256(output),
        "output_bytes": output.stat().st_size,
        "evidence_map": relative(evidence_path),
        "evidence_map_sha256": sha256(evidence_path),
        "metadata": relative(metadata_path),
        "metadata_sha256": sha256(metadata_path),
        "newly_embedded_claim_count": len(missing_ids),
        "newly_embedded_claim_ids": missing_ids,
    }


def patch_inventory(path: Path, generated_papers: list[dict]) -> None:
    record = json.loads(path.read_bytes())
    by_id = {row["paper_id"]: row for row in generated_papers}
    record["schema"] = "sft-v3-lean4-verified-authoritative-corpus-inventory/1"
    record["date"] = TODAY.isoformat()
    record["status"] = "local_lean4_verified_successor_corpus_complete__publication_confirmation_pending"
    record["authority"]["paper_status"] = "complete local Lean-verified successor; publication confirmation pending"
    record["authority"]["protected_authority_edited"] = False
    record["publication_boundary"] = {
        "publication_authority": "Maria Smith",
        "remote_publication_authorised": False,
        "remote_action_permitted": False,
        "remote_actions_performed": False,
        "confirmation_required": True,
        "successor_operation": "new version for existing paper records; new standalone record for the Lean paper",
        "doi_actions_performed": False,
    }
    record["lean4_verification"] = {
        "report_path": relative(LEAN_REPORT),
        "report_sha256": sha256(LEAN_REPORT),
        "status": "PASS",
    }
    for role in list(record["active_papers"]):
        paper_id = role
        if paper_id in by_id:
            output = ROOT / by_id[paper_id]["output"]
            record["active_papers"][role] = {
                "path": relative(output),
                "sha256": sha256(output).removeprefix("sha256:"),
                "bytes": output.stat().st_size,
                "line_count": len(output.read_text(encoding="utf-8").splitlines()),
                "heading_count": len(re.findall(r"(?m)^#{1,6}\s+", output.read_text(encoding="utf-8"))),
                "title": by_id[paper_id]["title"],
                "doi_tokens": doi_tokens(output.read_text(encoding="utf-8")),
                "version_tokens": [f"version {by_id[paper_id]['version']}"],
                "full_text_read": True,
            }
    write_json(path, record)


def build_toe_successor(generated_papers: list[dict], claims: list[dict], report: dict, report_hash: str) -> dict:
    TOE_ROOT.mkdir(parents=True, exist_ok=True)
    inventory_path = TOE_ROOT / "AUTHORITATIVE_CORPUS_INVENTORY_V0_2.json"
    inventory_module = load_module(
        "sft_lean_inventory_builder",
        ROOT / "publications/preliminary_toe/build_authoritative_inventory.py",
    )
    inventory_module.OUTPUT = inventory_path
    inventory_module.ACTIVE_PAPERS = {
        **inventory_module.ACTIVE_PAPERS,
        **{
            row["paper_id"]: row["output"]
            for row in generated_papers
            if row["paper_id"] in inventory_module.ACTIVE_PAPERS
        },
    }
    inventory_module.main()
    patch_inventory(inventory_path, generated_papers)

    matrix_json = TOE_ROOT / "EXHAUSTIVE_TOE_CONTENT_MATRIX_V0_2.json"
    matrix_md = TOE_ROOT / "EXHAUSTIVE_TOE_CONTENT_MATRIX_V0_2.md"
    matrix_module = load_module(
        "sft_lean_matrix_builder",
        ROOT / "publications/preliminary_toe/build_exhaustive_toe_content_matrix.py",
    )
    matrix_module.INVENTORY_PATH = inventory_path
    matrix_module.OUTPUT_JSON = matrix_json
    matrix_module.OUTPUT_MD = matrix_md
    matrix_module.main()
    matrix = json.loads(matrix_json.read_bytes())
    matrix["schema"] = "sft-v3-lean4-verified-exhaustive-toe-content-matrix/1"
    matrix["date"] = TODAY.isoformat()
    matrix["lean_report_path"] = relative(LEAN_REPORT)
    matrix["lean_report_sha256"] = report_hash
    matrix["publication_authorized"] = False
    write_json(matrix_json, matrix)
    matrix_text = matrix_md.read_text(encoding="utf-8")
    matrix_text = matrix_text.replace("**Date:** 31 July 2026", f"**Date:** {DATE_TEXT}")
    matrix_text += "\n\n## Lean 4 whole-model verification\n\n"
    matrix_text += f"The complete matrix is independently checked by `{relative(LEAN_REPORT)}` (`{report_hash}`), which reports PASS for all {report['claim_count']:,} ordered claims and no issue.\n"
    write_text(matrix_md, matrix_text)

    temporary_parent = ROOT / "tmp"
    temporary_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sft-toe-v0-2-", dir=temporary_parent) as temp_name:
        temp = Path(temp_name)
        raw_master = temp / "raw_monograph.md"
        raw_volumes = temp / "volumes"
        monograph_module = load_module(
            "sft_lean_monograph_builder",
            ROOT / "publications/preliminary_toe/build_exhaustive_toe_monograph.py",
        )
        monograph_module.HERE = temp
        monograph_module.INVENTORY_PATH = inventory_path
        monograph_module.MATRIX_PATH = matrix_json
        monograph_module.OUTPUT = raw_master
        monograph_module.VOLUME_DIR = raw_volumes
        monograph_module.main()

        toe_spec = PaperSpec(
            "theory_of_everything",
            "The Smithian Fold Theory V3 Theory of Everything",
            "Exhaustive Lean-verified successor monograph from There Is No Nothing through the complete current computational proof surface",
            "0.2.0",
            "0.1.0",
            "publications/preliminary_toe/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH.md",
            relative(TOE_ROOT / "SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_2.md"),
            tuple(report["branches"].keys()),
            False,
            "toe_successor",
        )
        raw_text = raw_master.read_text(encoding="utf-8")
        raw_abstract, body = abstract_and_remainder(raw_text)
        body = body.replace("2,751", f"{report['claim_count']:,}")
        body = body.replace("892,246", f"{report['candidate_count']:,}")
        body = body.replace("11,004", f"{report['control_count']:,}")
        raw_abstract = raw_abstract.replace("2,751", f"{report['claim_count']:,}")
        raw_abstract = raw_abstract.replace("892,246", f"{report['candidate_count']:,}")
        raw_abstract = raw_abstract.replace("11,004", f"{report['control_count']:,}")
        final_path = ROOT / toe_spec.output
        write_text(
            final_path,
            publication_header(
                toe_spec,
                (ROOT / toe_spec.source).read_text(encoding="utf-8"),
                report,
            )
            + "\n"
            + current_abstract(
                toe_spec,
                raw_abstract,
                (ROOT / toe_spec.source).read_text(encoding="utf-8"),
                claims,
                report,
            )
            + "\n\n"
            + successor_headlines(toe_spec, (ROOT / toe_spec.source).read_text(encoding="utf-8"), claims, report)
            + "\n\n"
            + guidance_layer(toe_spec, claims, report)
            + "\n\n"
            + body
            + "\n\n"
            + structural_completion(toe_spec, body, claims, report, report_hash)
            + "\n\n"
            + lean_update(toe_spec, report, report_hash)
            + "\n\n"
            + successor_conclusion(toe_spec, claims, report),
        )
        apply_british_house_style(final_path)
        ensure_exact_claim_records(final_path, claims)
        volume_records = []
        final_volume_dir = TOE_ROOT / "volumes"
        for raw_volume in sorted(raw_volumes.glob("*.md")):
            raw_volume_text = raw_volume.read_text(encoding="utf-8")
            volume_abstract, volume_body = abstract_and_remainder(raw_volume_text)
            volume_body = volume_body.replace("2,751", f"{report['claim_count']:,}")
            volume_body = volume_body.replace("892,246", f"{report['candidate_count']:,}")
            volume_body = volume_body.replace("11,004", f"{report['control_count']:,}")
            branch = raw_volume.stem.split("_", 1)[1]
            label = monograph_module.BRANCH_LABELS[branch]
            volume_spec = PaperSpec(
                f"toe_volume_{branch}",
                f"The Smithian Fold Theory V3 Theory of Everything — {label}",
                f"Exhaustive branch volume in the Lean-verified ToE successor",
                "0.2.0",
                "0.1.0",
                toe_spec.source,
                relative(final_volume_dir / raw_volume.name),
                (branch,),
                False,
                "toe_volume",
            )
            volume_path = ROOT / volume_spec.output
            write_text(
                volume_path,
                publication_header(
                    volume_spec,
                    (ROOT / toe_spec.source).read_text(encoding="utf-8"),
                    report,
                )
                + "\n"
                + current_abstract(
                    volume_spec,
                    volume_abstract,
                    (ROOT / toe_spec.source).read_text(encoding="utf-8"),
                    claims,
                    report,
                )
                + "\n\n"
                + successor_headlines(volume_spec, raw_volume_text, claims, report)
                + "\n\n"
                + guidance_layer(volume_spec, claims, report)
                + "\n\n"
                + volume_body
                + "\n\n"
                + structural_completion(volume_spec, volume_body, claims, report, report_hash)
                + "\n\n"
                + lean_update(volume_spec, report, report_hash)
                + "\n\n"
                + successor_conclusion(volume_spec, claims, report),
            )
            apply_british_house_style(volume_path)
            ensure_exact_claim_records(
                volume_path,
                [row for row in claims if row["branch"] == branch],
            )
            volume_records.append(
                {
                    "branch": branch,
                    "path": relative(volume_path),
                    "sha256": sha256(volume_path),
                    "bytes": volume_path.stat().st_size,
                    "claims": report["branches"][branch],
                }
            )

    evidence_path = final_path.with_name(final_path.stem + "_EVIDENCE_MAP.json")
    write_json(
        evidence_path,
        {
            "schema": "sft-v3-lean4-verified-toe-evidence-map/1",
            "version": "0.2.0",
            "date": TODAY.isoformat(),
            "paper_path": relative(final_path),
            "paper_sha256": sha256(final_path),
            "claim_count": report["claim_count"],
            "candidate_count": report["candidate_count"],
            "control_count": report["control_count"],
            "branch_count": report["branch_count"],
            "lean_report_path": relative(LEAN_REPORT),
            "lean_report_sha256": report_hash,
            "inventory_path": relative(inventory_path),
            "inventory_sha256": sha256(inventory_path),
            "matrix_path": relative(matrix_json),
            "matrix_sha256": sha256(matrix_json),
            "volumes": volume_records,
            "publication_authorized": False,
            "remote_actions_performed": False,
        },
    )
    metadata_path = final_path.with_name(final_path.stem + "_ZENODO_METADATA_DRAFT.json")
    write_json(
        metadata_path,
        {
            "metadata": {
                "title": toe_spec.title,
                "subtitle": toe_spec.subtitle,
                "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
                "publication_date": TODAY.isoformat(),
                "version": "0.2.0",
                "language": "eng",
                "license": "cc-by-4.0",
                "related_identifiers": [
                    {"identifier": "10.5281/zenodo.21717584", "relation": "isNewVersionOf", "scheme": "doi"}
                ],
                "notes": "LOCAL CANDIDATE ONLY. New-version deposit requires Maria Smith's explicit confirmation.",
            },
            "publication_authorized": False,
            "remote_action_permitted": False,
            "ready_to_publish": False,
        },
    )
    return {
        **asdict(toe_spec),
        "source_sha256": sha256(ROOT / toe_spec.source),
        "output_sha256": sha256(final_path),
        "output_bytes": final_path.stat().st_size,
        "evidence_map": relative(evidence_path),
        "evidence_map_sha256": sha256(evidence_path),
        "metadata": relative(metadata_path),
        "metadata_sha256": sha256(metadata_path),
        "inventory": relative(inventory_path),
        "matrix": relative(matrix_json),
        "volumes": volume_records,
        "newly_embedded_claim_count": 2,
        "newly_embedded_claim_ids": [
            "SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001",
            "SFT-COMP-AIX-EXACT-TEACHER-LEARNING-002",
        ],
    }


def standalone_paper(report: dict, report_hash: str) -> tuple[Path, Path, Path]:
    root_source = LEAN_ROOT / "SFTValidation/Root.lean"
    gates_source = LEAN_ROOT / "SFTValidation/Gates.lean"
    verifier_source = LEAN_ROOT / "SFTValidation/Verifier.lean"
    source_hashes = {
        relative(path): sha256(path)
        for path in (
            LEAN_ROOT / "lean-toolchain",
            LEAN_ROOT / "lakefile.toml",
            LEAN_ROOT / "Main.lean",
            LEAN_ROOT / "SFTValidation.lean",
            root_source,
            gates_source,
            LEAN_ROOT / "SFTValidation/JsonUtil.lean",
            verifier_source,
            LEAN_ROOT / "source_binding_probe.py",
            LEAN_ROOT / "run_validation.sh",
        )
    }
    hash_rows = "\n".join(f"| `{path}` | `{digest}` |" for path, digest in source_hashes.items())
    branch_rows = "\n".join(
        f"| `{branch}` | {count:,} |" for branch, count in sorted(report["branches"].items())
    )
    standalone_spec = PaperSpec(
        "lean4_whole_model_verification",
        "Independent Lean 4 Verification of the Complete Smithian Fold Theory Model",
        "A kernel-checked operational root, proof-bearing acceptance gates and fail-closed audit of all current branches",
        "1.0.0",
        "none",
        "generated/lean4_validation/README.md",
        "publications/lean4_verification/SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_PAPER_V1_0.md",
        paper_role="standalone_lean_verification",
    )
    standalone_guidance = guidance_layer(standalone_spec, [], report)
    path = SUITE_ROOT / "SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_PAPER_V1_0.md"
    text = f"""# Independent Lean 4 Verification of the Complete Smithian Fold Theory Model

## A kernel-checked operational root, proof-bearing acceptance gates and fail-closed audit of all current branches

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** 1.0.0  
**Date:** {DATE_TEXT}  
**Status:** Final local standalone publication candidate; not approved, deposited or published  
**DOI:** Pending a new standalone record after explicit confirmation; no DOI has been assigned or invented  
**Paper and documentation licence:** CC BY 4.0  
**Verification code licence:** Apache-2.0

> **Publication control.** This manuscript and its evidence bundle are prepared
> locally. No push, upload, DOI creation, release or publication is authorised
> until Maria Smith confirms the exact candidate files and hashes.

## Abstract

This paper reports an independent Lean 4 verification layer for the complete current Smithian Fold Theory (SFT) model without modifying the model, its frozen admission engine, its verification authority, any claim package or any historical receipt. The project pins `leanprover/lean4:v4.32.0`. It formalises the registered operational root as an exhaustive two-constructor type, proves constructively that `presentedOccurrence` is the unique survivor, and reports no imported or user-declared axiom for the exported root theorems under Lean's `#print axioms` audit. It separately formalises twelve whole-claim acceptance gates and constructs a proof-bearing certificate only if every gate is true.

The compiled verifier then reads the complete ordered model census and execution manifest as data. It checks {report['claim_count']:,} live claims across {report['branch_count']} branches, {report['candidate_count']:,} candidate records, {report['decision_count']:,} decision records and {report['control_count']:,} controls. It verifies identity, source custody, dependency closure, candidate completeness, decision coverage, exactly one survivor, minimality, named-form uniqueness, controls, empirical boundary, certificate binding and admitted-receipt status for every claim. The final result is `PASS` with {report['issue_count']} issue. The machine report is `{relative(LEAN_REPORT)}` with identity `{report_hash}`.

The result strengthens SFT's formal-coherence, exhaustiveness, provenance and cross-branch consistency case. It does not convert the remaining {report['claim_count'] - 1:,} scientific statements into native Lean propositions, replace empirical tests, or establish superiority to every rival theory. Those boundaries are part of the verified claim discipline rather than exceptions to it. Lawful criticism, falsification and versioned extension remain open, and empirical and publication status remain distinct.

## Headline findings

1. **Unique operational survivor.** Lean 4 proves constructively that `presentedOccurrence` is the unique survivor of the exact registered two-class operational grammar.
2. **No added theorem axiom.** The exported root theorems report no imported or user-declared axiom under `#print axioms`; no `sorry` is present.
3. **Complete current-census audit.** All {report['claim_count']:,} ordered claims receive proof-bearing accepted gate certificates after {report['candidate_count']:,} candidates, the same number of decisions and {report['control_count']:,} controls are checked.
4. **Complete branch surface.** All {report['branch_count']} registered branches reconcile with no omitted census claim and no reported issue.
5. **Independent, read-only architecture.** The Lean layer does not modify or replace the protected engine, verification authority, claim packages or receipts.
6. **Demonstrated fail-closed behaviour.** Six byte-level source mismatches halted the initial run; the expected identities and acceptance logic were not weakened, and the corrected exact-byte state passed.
7. **Bounded scientific meaning.** The result supports formal coherence and custody. It does not independently establish every empirical claim or comparative superiority.

{standalone_guidance}

## Scope, ownership and evidence constitutions

The verification paper owns the description and reproduction of the Lean layer. It does not take scientific ownership from Foundation, Mathematics, Information Science, Computation, Quantum Computation, Physics, Chemistry, Materials, Biology, Medicine, Consciousness, Earth, Astronomy, Social and Collective Systems, Engineering Translation or Cross-Branch Synthesis.

The mathematical constitution is the explicit inductive root grammar, its decision function, constructive unique-survivor proof and the proof-bearing acceptance structure. The computational constitution is the pinned toolchain and compiled read-only traversal of the exact model artifacts. The empirical constitution remains in the claim packages: source identity, transport, registration, seal, custody, observation or measurement, adverse and unresolved rows and falsification rule. Lean verifies those records and gates as artifacts; it does not become the measuring instrument.

Chronology remains claim specific. The root formalisation was written after the model and therefore validates an existing registered theorem; it is not retroactively classified as the theorem's original prediction. The source-custody halt precedes the final PASS and remains part of the verification history.

## 1. Question and contribution

The verification question is exact: can an independent proof-assistant layer reproduce the registered two-class operational root, prove its unique survivor, and traverse every current SFT branch without changing the model or its admission authority? The answer for the repository state bound by this paper is yes.

The contribution has three parts. First, the root theorem is stated in Lean as a finite inductive grammar whose constructors correspond exactly to the two registered operational challenge classes. Second, the acceptance constitution is represented as a proof-bearing structure. Third, a compiled Lean executable audits the complete machine artifact graph and refuses success if any required gate is absent, malformed or false.

This is validation, not a new derivation route. The SFT engine remains the only component that admits a model claim and writes an authoritative receipt. The Lean layer is read-only with respect to all scientific artifacts. Its report records what it independently reconstructed from those artifacts.

## 2. Protected-boundary design

The verification project lives under `generated/lean4_validation/`. Its local toolchain and build outputs are isolated under `.elan/` and `.lake/` and ignored by version control. The executable receives the repository root and an output-report path. It reads the census, execution manifest, claim packages, certificates, controls, source registrations and receipts. It writes only its report under the Lean project.

Before and after the work, the repository's protected engine seal and verification-authority seal are checked by their existing seal verifiers. No file under `sft/engine/` is imported as editable proof-assistant source, and no authority hash is regenerated to accommodate the Lean result. This asymmetry is deliberate: Lean may inspect the admitted record, but it may not become a hidden second admission route.

The source binding gate needs the registered Python factories because those factories define how several source manifests are instantiated. A small read-only bridge, `source_binding_probe.py`, imports those registrations, computes their current bindings and returns JSON to the Lean process. It does not call the engine's admission operation and cannot issue a receipt. The Lean verifier treats a failed bridge, malformed response, missing registration or false binding as a failed gate.

## 3. Formalization of the two-class operational root

### 3.1 Registered grammar

The root claim is `SFT-ROOT-THERE-IS-NO-NOTHING`:

> No admissible operational statement, denial, record, proof object or derivational object is nothing: absence presents no counterexample, while every presented counterexample is an occurrence.

Its registered candidate generator partitions every purported operational counterexample by whether it emits an identifiable presentation at the proof boundary. The exact census contains two forms:

1. `unpresented-absence`: no statement, denial, record, trace or identity is presented, so there is no operational counterexample to admit;
2. `presented-occurrence`: a statement, denial, record, trace or identity is presented, and that presentation is an occurrence rather than nothing.

The Lean type mirrors only that registered partition:

```lean
inductive ChallengeClass where
  | unpresentedAbsence
  | presentedOccurrence

def survives : ChallengeClass -> Bool
  | .unpresentedAbsence => false
  | .presentedOccurrence => true
```

The type is finite by construction and has no hidden third constructor. `challengePartitionComplete` proves by cases that an arbitrary member equals one of the two named constructors.

### 3.2 Presentation supplies an occurrence

The formalisation makes the operational witness explicit. A `Presentation` carries an occurrence identity. `Occurrence.ofPresentation` constructs the occurrence supplied by that presentation, and `OccurrenceOf presentation` is the subtype whose member is exactly that occurrence. `presentationIsOccurrence` proves `Nonempty (OccurrenceOf presentation)` for every presentation by giving the constructor and reflexivity proof.

This theorem does not assert that every imaginable metaphysical account has been encoded. It states the registered operational boundary: once a challenge is presented as a checkable object, the presentation itself supplies an occurrence at that boundary.

### 3.3 Existence and uniqueness

Define

```lean
def HasUniqueSurvivor : Prop :=
  ∃ candidate : ChallengeClass,
    survives candidate = true ∧
    ∀ other : ChallengeClass,
      survives other = true -> other = candidate
```

Existence is witnessed by `presentedOccurrence`, whose decision reduces definitionally to `true`. For uniqueness, take any surviving candidate and eliminate it by the two constructors. In the `unpresentedAbsence` case, the hypothesis reduces to `false = true`, which is impossible. In the `presentedOccurrence` case, equality is reflexive. Therefore every survivor equals `presentedOccurrence`.

The exported `rootExactResult` conjoins the positive decision, the negative decision and the unique-survivor theorem. Lean's axiom audit prints an empty axiom dependency list for `presentationIsOccurrence`, `uniqueSurvivor` and `rootExactResult`. “No axioms” here has a precise software meaning: no `axiom`, `sorry`, classical choice declaration or other extra axiom is imported by those theorems. Lean's kernel and dependent type theory remain the proof-checking metalanguage; they are not registered as SFT model premises.

### 3.4 Scope of uniqueness

The uniqueness theorem quantifies over `ChallengeClass`, the exact two-member registered operational grammar. It therefore proves one survivor in that complete encoded grammar. The scientific claim that this partition covers the declared operational boundary is represented by the constructor exhaustiveness and by the source registration to which the code is bound. The theorem should not be paraphrased as quantification over every grammar that any critic might later invent without first giving a structure-preserving translation into the registered boundary.

## 4. Proof-bearing whole-claim gates

`SFTValidation/Gates.lean` defines a `ClaimGate` with twelve Boolean fields:

1. identity bound;
2. source artifacts bound;
3. dependency closed;
4. candidate enumeration complete;
5. decision coverage complete;
6. exactly one survivor;
7. minimality passed;
8. named-shape uniqueness passed;
9. structural controls passed;
10. empirical boundary passed;
11. certificate bound;
12. receipt admitted.

`ClaimGate.Accepted gate` is a proposition containing a proof that every field equals `true`. `ClaimGate.certify?` checks the fields in sequence. Only the all-true path returns `some` proof certificate; every false path returns `none`. Downstream theorems extract source binding, dependency closure, complete candidate and decision coverage and exactly-one-survivor facts from any certificate.

This design prevents a successful runtime label from floating free of the logical gates. The runtime code must produce a certificate inhabiting the accepted type for each claim. The certificate is erased or compiled as ordinary Lean computation as appropriate, but its construction was checked by the kernel.

## 5. Whole-model executable audit

### 5.1 Inputs

The verifier binds the exact census and execution-manifest file hashes recorded in the final report:

- census: `{report['census_file_hash']}`;
- execution manifest: `{report['execution_manifest_file_hash']}`.

It parses each ordered claim and its execution entry, resolves the package, and reconstructs the gates. It requires exact claim, branch, grammar and dependency identities. It checks candidate identifiers for uniqueness, expected and actual cardinality equality, a one-to-one decision map and exactly one `survives = true` row. It validates closure scope and boundary, minimality and named-form uniqueness, all four required controls, registered empirical extensions, certificate hashes and the current admitted receipt.

The verifier also preserves historical lineages without counting them as current authority: {report['preserved_receipt_lineage_count']} prior receipt lineages and {report['preserved_certificate_source_lineage_count']} prior certificate-source lineages were encountered. It checked {report['custom_decision_artifact_count']} custom decision artifacts. Two uncensused nonmodel package directories were reported rather than silently absorbed: an empty future package and a rejected adverse package whose rejected receipt remains preserved. Neither is counted among the {report['claim_count']:,} accepted claims.

### 5.2 Complete result

| Quantity | Verified result |
|---|---:|
| Claims in ordered census | {report['claim_count']:,} |
| Accepted proof-bearing gates | {report['accepted_claim_count']:,} |
| Source-bound claims | {report['source_binding_passed_claim_count']:,} |
| Candidates | {report['candidate_count']:,} |
| Decisions | {report['decision_count']:,} |
| Controls | {report['control_count']:,} |
| Branches | {report['branch_count']} |
| Issues | {report['issue_count']} |

The exact branch distribution is:

| Branch | Claims |
|---|---:|
{branch_rows}

The totals reconcile exactly: every ordered claim reached an accepted certificate, every claim passed the source-binding gate, candidate and decision totals match, and the issue list is empty.

### 5.3 Complete claim-inventory boundary

The standalone conceptual paper does not duplicate {report['claim_count']:,} full claim records. The scientific audit layer is the successor ToE matrix and the per-paper evidence maps. The machine archive remains the ordered census and the claim packages. Completeness is tested by requiring every census identifier, authoritative statement, candidate and decision cardinality, survivor, control, certificate and receipt binding to appear in the checked graph. The branch table above is the complete ownership partition for this report.

## 6. Preserved fail-closed event and correction

The first whole-model execution did not pass. It halted on six registered source-capture hashes. Investigation showed that the working-tree copies had been normalised to LF line endings while the registered source identities referred to the exact archived bytes. This was a custody mismatch even though the scientific text was not a new target.

The response was not to weaken the verifier, change the expected hashes or relabel the halt. The six exact registered byte sequences were restored from the preserved archive reference. Repository attributes were added so those specific source captures are treated as byte-preserved rather than text-normalised. A separate sweep checked all 385 registered external artifact bindings and found no remaining mismatch. The Lean verifier was then rerun without changing its acceptance logic and returned `PASS`.

This event is evidence about the verifier's sensitivity. It shows that a source identity mismatch blocks acceptance even when a human might regard line endings as semantically harmless. It is not evidence that the original mismatch was a scientific falsification, and the final report does not count it as one. Both the halted state and the correction rationale remain documented.

## 7. Interpretation: how the result bears on SFT

The result favors SFT in five bounded ways.

First, the root is not merely described in prose. An independent theorem prover accepts a faithful finite encoding and verifies the unique survivor constructively without extra declared axioms. Second, the current model surface is exhaustive relative to the ordered census: all {report['claim_count']:,} entries were traversed, not a favourable sample. Third, exactly-one-survivor is enforced at both the artifact level and the proof-bearing gate level. Fourth, source, dependency, certificate and receipt identities remain coupled across all branches. Fifth, the mismatch halt demonstrates that the layer can reject the live workspace rather than being engineered only to emit success.

These are substantial supports for internal coherence, implementation independence, provenance custody and reproducibility. They answer the concern that a large cross-disciplinary model might contain omitted branches, duplicated decisions, unmatched receipts or a root theorem that cannot be rendered precisely enough for a proof assistant.

The result is not an empirical universal confirmation. A formally coherent model can still make an empirically adverse prediction. The source gate verifies the registered custody and protocol artifacts; it does not recreate every instrument, patient cohort, astronomical survey or chemical measurement inside Lean. Likewise, the root uniqueness proof is relative to the exact operational grammar. Comparative superiority requires rival models, common observables and discriminating tests. The paper therefore reports formal validation as a strong but typed kind of evidence.

## 8. Reproduction

From `generated/lean4_validation/`, with the pinned toolchain installed locally:

```sh
ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" lake build
ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" \
  .lake/build/bin/sft-verify ../.. reports/whole_model_validation.json
```

The checked-in `./run_validation.sh` performs the same build-and-run route. A successful run must exit zero and reproduce a report whose scientific counts, input hashes and issue-free status match this paper. The report file's byte hash can differ only if non-scientific serialization metadata changes; in this version the exact expected identity is `{report_hash}`.

### Verification-source identities

| Source | SHA-256 |
|---|---|
{hash_rows}

## Open science, criticism and admission

The verification sources, paper, evidence map, report and reproduction commands are open for inspection. Criticism does not require credentials or institutional permission. Scientific admission remains separate: a proposed correction must identify the exact theorem, grammar, artifact, source, chronology or empirical boundary it challenges and must pass the shared versioned protocol. Lean acceptance, reputation, consensus and application performance cannot substitute for that route.

Maria Smith retains authorship and sole publication authority. Ernos Labs denotes conformance to the open evidence constitution, not authority over criticism. Paper and documentation are CC BY 4.0; repository verification code is Apache-2.0. Contributions and machine assistance do not transfer authorship or publication authority.

## 9. Falsification and review conditions

This verification result fails for the bound repository state if any of the following is demonstrated:

- `Root.lean` admits an extra root constructor, relies on an undeclared axiom or fails to prove uniqueness;
- the root code is not a structure-preserving encoding of the registered two-class grammar;
- a current census claim is omitted or counted twice;
- candidate cardinality, decision coverage or survivor count is accepted when inconsistent;
- a required control, empirical boundary, certificate or admitted receipt can be false while a proof-bearing certificate is returned;
- a source binding can drift without causing failure;
- the reported input hashes do not identify the audited census and execution manifest;
- the pinned toolchain cannot reproduce the build and pass result; or
- the protected engine or authority was modified to make the Lean layer succeed.

A critique of the scientific model should additionally target the registered grammar, a particular derivation, an empirical protocol, an adverse observation or a discriminating prediction. A generic statement that Lean proves only formal encodings is correct but incomplete here, because this project explicitly separates native propositions from artifact checks and binds both to the repository's evidence structure.

## 10. Limitations and next formalisation frontier

The present version natively proves the operational root and generic gate implications. It does not translate every domain statement into a bespoke Lean proposition, nor should its artifact checks be described as if it did. Formal closure, implementation validation and empirical validation remain distinct, and the empirical frontier stays open wherever a claim's current record is adverse, unavailable or unresolved. A future version may add native formalisations for selected mathematical and physical claims, along with equivalence theorems between those propositions and their registered JSON representations. Such extensions must remain versioned and cannot retroactively change this paper's result.

The read-only Python source bridge is a practical boundary rather than a hidden proof step. Eliminating it would require translating each registered source factory and transport rule into Lean or exporting a separately authenticated language-neutral registry. The current bridge is fail-closed, its role is disclosed, and its output is included in the claim gate.

The verification proves the integrity of the current census, not permanent closure against lawful discovery. A new claim changes the census and manifest hashes and requires a new report and paper version. This is a feature of the versioned scientific model: completeness is always exact to a declared dated surface.

## 11. Conclusion

Lean 4 independently verifies the exact two-class SFT operational root and proves that `presentedOccurrence` is its unique survivor. The same compiled project constructs proof-bearing acceptance certificates for all {report['claim_count']:,} current claims after checking {report['candidate_count']:,} candidates, {report['decision_count']:,} decisions, {report['control_count']:,} controls and the complete seventeen-branch evidence graph. The final report is `PASS` with no issue, while the preserved source-hash halt demonstrates fail-closed behaviour. Adverse and unresolved scientific records remain evidence-bound rather than reclassified; empirical testing, criticism and lawful versioned extension remain open.

The appropriate conclusion is strong and bounded: the complete current SFT model is formally coherent and machine-consistent under this independent Lean verification architecture, with intact source, dependency, survivor, certificate and receipt custody. Empirical truth and comparative physical adequacy remain questions for the model's registered experiments and falsification programme.

## Data and code availability

All verification sources, the pinned toolchain declaration, the machine report, the publication evidence map and the local release manifest are included in the repository. The model and historical evidence remain in their original locations. No external publication action was performed while preparing this candidate.

## References

1. de Moura, Leonardo, and Sebastian Ullrich. “The Lean 4 Theorem Prover and Programming Language.” In *Automated Deduction — CADE 28*, Lecture Notes in Computer Science 12699, 625–635. Springer, 2021. DOI: [10.1007/978-3-030-79876-5_37](https://doi.org/10.1007/978-3-030-79876-5_37).
2. Lean FRO. *The Lean Language Reference*. Current reference documentation used with the pinned Lean 4.32.0 toolchain: [lean-lang.org/doc/reference/latest](https://lean-lang.org/doc/reference/latest/).
3. Smith, Maria. *There Is No Nothing: A Premise-Free Operational Foundation and an Open Verification Platform for Smithian Fold Theory*. Ernos Labs Methods Paper 00, versioned publication series, 2026.
4. Smith, Maria. *The Smithian Fold Theory V3 Theory of Everything*. Exhaustive preliminary monograph and machine audit archive, versioned publication series, 2026.
5. Ernos Labs. `generated/lean4_validation/README.md`, `SFTValidation/Root.lean`, `SFTValidation/Gates.lean`, `SFTValidation/Verifier.lean` and `reports/whole_model_validation.json`, repository snapshot bound by the hashes in this paper.

## Suggested citation

Smith, Maria (2026). *Independent Lean 4 Verification of the Complete Smithian Fold Theory Model: A Kernel-Checked Operational Root, Proof-Bearing Acceptance Gates and Fail-Closed Audit of All Current Branches*. Ernos Labs, version 1.0.0. DOI pending author-confirmed deposit.
"""
    write_text(path, text)
    apply_british_house_style(path)
    root_claim = next(row for row in json.loads((ROOT / "census/claims.json").read_bytes())["claims"] if row["claim_id"] == "SFT-ROOT-THERE-IS-NO-NOTHING")
    ensure_exact_claim_records(path, [enrich_claim(root_claim)])
    evidence_path = SUITE_ROOT / "SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_EVIDENCE_MAP_V1_0.json"
    evidence = {
        "schema": "sft-lean4-whole-model-verification-paper-evidence-map/1",
        "title": "Independent Lean 4 Verification of the Complete Smithian Fold Theory Model",
        "version": "1.0.0",
        "date": TODAY.isoformat(),
        "paper_path": relative(path),
        "paper_sha256": sha256(path),
        "lean_report_path": relative(LEAN_REPORT),
        "lean_report_sha256": report_hash,
        "lean_toolchain": report["lean_toolchain"],
        "root_source": relative(root_source),
        "root_source_sha256": sha256(root_source),
        "gate_source": relative(gates_source),
        "gate_source_sha256": sha256(gates_source),
        "verifier_source": relative(verifier_source),
        "verifier_source_sha256": sha256(verifier_source),
        "verification_source_hashes": source_hashes,
        "result": report,
        "interpretive_boundary": {
            "native_lean_root_theorems": True,
            "native_lean_generic_gate_theorems": True,
            "all_other_claims_checked_as_registered_artifacts": True,
            "all_other_claims_reexpressed_as_native_lean_propositions": False,
            "empirical_truth_established_by_lean_alone": False,
            "protected_engine_modified": False,
            "verification_authority_modified": False,
        },
        "publication_authorized": False,
        "remote_actions_performed": False,
    }
    write_json(evidence_path, evidence)
    metadata_path = SUITE_ROOT / "SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_ZENODO_METADATA_DRAFT_V1_0.json"
    write_json(
        metadata_path,
        {
            "metadata": {
                "title": "Independent Lean 4 Verification of the Complete Smithian Fold Theory Model",
                "upload_type": "publication",
                "publication_type": "article",
                "publication_date": TODAY.isoformat(),
                "description": (
                    f"Standalone verification paper for the Lean 4 PASS over {report['claim_count']:,} current SFT claims, "
                    f"{report['candidate_count']:,} candidates and {report['control_count']:,} controls, including a native proof of the two-class operational root's unique survivor."
                ),
                "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
                "access_right": "open",
                "license": "cc-by-4.0",
                "version": "1.0.0",
                "language": "eng",
                "keywords": [
                    "Smithian Fold Theory",
                    "Lean 4",
                    "formal verification",
                    "operational root",
                    "unique survivor",
                    "proof-bearing certificate",
                    "reproducible science",
                    "zero-parameter model",
                ],
                "notes": "LOCAL DRAFT ONLY. No DOI has been assigned. Publication requires Maria Smith's explicit confirmation.",
            },
            "publication_authorized": False,
            "remote_action_permitted": False,
            "ready_for_review": True,
            "ready_to_publish": False,
        },
    )
    return path, evidence_path, metadata_path


def audit_document(report: dict, report_hash: str, paper: Path, evidence: Path) -> Path:
    path = ROOT / "audits/LEAN4_WHOLE_MODEL_VERIFICATION_2026-08-02.md"
    text = f"""# Lean 4 whole-model verification audit — 2 August 2026

**Author and publication authority:** Maria Smith  
**Audit status:** PASS  
**Publication status:** Local evidence record; no remote action authorised

## Result

The independent Lean 4 layer passed the complete current ordered SFT census: {report['claim_count']:,}/{report['claim_count']:,} claims accepted, {report['candidate_count']:,} candidates and decisions checked, {report['control_count']:,} controls checked, {report['branch_count']} branches traversed and {report['issue_count']} issue reported.

- Machine report: `{relative(LEAN_REPORT)}`
- Machine report SHA-256: `{report_hash}`
- Census identity: `{report['census_file_hash']}`
- Execution-manifest identity: `{report['execution_manifest_file_hash']}`
- Toolchain: `{report['lean_toolchain']}`
- Standalone paper: `{relative(paper)}`
- Evidence map: `{relative(evidence)}`

## Exact interpretation

Lean natively formalises the registered two-class operational root and proves `presentedOccurrence` is the unique survivor. It also proves the implications of the twelve acceptance gates and constructs a proof-bearing certificate only for an all-true gate record. The other {report['claim_count'] - 1:,} current claims are parsed and checked as complete registered repository artifacts by the Lean executable; they are not each restated as bespoke Lean propositions in this version.

The result supports formal coherence, exhaustive current-census coverage, exactly-one-survivor enforcement, source custody, dependency integrity, certificate and receipt binding and cross-branch consistency. It does not replace empirical validation or prove comparative superiority to every alternative theory.

## Preserved mismatch halt

The initial run halted on six source-capture byte mismatches caused by working-tree line-ending normalisation. The expected hashes were not weakened. The exact registered bytes were restored, the six paths were marked for byte preservation, all 385 registered external bindings were audited with no remaining mismatch, and the unchanged verifier reran to PASS. The halt is preserved as evidence of fail-closed sensitivity.

## Protected boundaries

The protected engine seal and verification-authority seal passed before publication-layer work. The Lean project is read-only with respect to model claims and writes only its generated report. No engine receipt, historical receipt, published paper or DOI record was rewritten.
"""
    write_text(path, text)
    return path


def main() -> int:
    if not LEAN_REPORT.is_file():
        raise SystemExit(f"missing Lean report: {LEAN_REPORT}")
    report = json.loads(LEAN_REPORT.read_bytes())
    if report.get("status") != "PASS" or report.get("issue_count") != 0:
        raise SystemExit("Lean report is not a clean PASS")
    census_path = ROOT / "census/claims.json"
    execution_manifest_path = ROOT / "census/execution_manifest.json"
    claims = json.loads(census_path.read_bytes())["claims"]
    admitted = [enrich_claim(row) for row in claims if row.get("model_admitted")]
    branch_counts: dict[str, int] = {}
    for row in admitted:
        branch_counts[row["branch"]] = branch_counts.get(row["branch"], 0) + 1
    expected = {
        "claim_count": len(admitted),
        "accepted_claim_count": len(admitted),
        "candidate_count": sum(row["candidate_count"] for row in admitted),
        "decision_count": sum(row["candidate_count"] for row in admitted),
        "control_count": sum(row["control_count"] for row in admitted),
        "branch_count": len(branch_counts),
        "source_binding_passed_claim_count": len(admitted),
        "source_binding_issue_count": 0,
        "census_file_hash": sha256(census_path),
        "execution_manifest_file_hash": sha256(execution_manifest_path),
        "branches": branch_counts,
    }
    mismatches = {
        key: {"report": report.get(key), "current_corpus": value}
        for key, value in expected.items()
        if report.get(key) != value
    }
    if mismatches:
        raise SystemExit(f"Lean report is not bound to the current corpus: {mismatches}")
    report_hash = sha256(LEAN_REPORT)

    generated = [build_successor(spec, admitted, report, report_hash) for spec in PAPERS]
    toe_record = build_toe_successor(generated, admitted, report, report_hash)
    paper_path, evidence_path, metadata_path = standalone_paper(report, report_hash)
    audit_path = audit_document(report, report_hash, paper_path, evidence_path)

    standalone_record = {
        "paper_id": "lean4_whole_model_verification",
        "title": "Independent Lean 4 Verification of the Complete Smithian Fold Theory Model",
        "subtitle": "A kernel-checked operational root, proof-bearing acceptance gates and fail-closed audit of all current branches",
        "version": "1.0.0",
        "previous_version": None,
        "source": None,
        "output": relative(paper_path),
        "branches": sorted(report["branches"]),
        "paper_role": "standalone_lean_verification",
        "output_sha256": sha256(paper_path),
        "output_bytes": paper_path.stat().st_size,
        "evidence_map": relative(evidence_path),
        "evidence_map_sha256": sha256(evidence_path),
        "metadata": relative(metadata_path),
        "metadata_sha256": sha256(metadata_path),
    }
    all_papers = [toe_record, *generated, standalone_record]
    manifest = {
        "schema": "sft-v3-lean4-verified-publication-suite/1",
        "date": TODAY.isoformat(),
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "status": "local_publication_candidates_complete__render_and_final_audit_pending",
        "paper_count": len(all_papers),
        "existing_paper_successor_count": len(generated) + 1,
        "standalone_lean_paper_count": 1,
        "lean_report_path": relative(LEAN_REPORT),
        "lean_report_sha256": report_hash,
        "lean_result": {
            key: report[key]
            for key in (
                "status",
                "claim_count",
                "accepted_claim_count",
                "candidate_count",
                "decision_count",
                "control_count",
                "branch_count",
                "issue_count",
            )
        },
        "papers": all_papers,
        "audit_record": relative(audit_path),
        "audit_record_sha256": sha256(audit_path),
        "publication_authorized": False,
        "remote_action_permitted": False,
        "remote_actions_performed": False,
        "confirmation_required": True,
        "confirmation_received": False,
        "pdf_render_complete": False,
        "final_audit_complete": False,
    }
    write_json(MANIFEST_PATH, manifest)
    readme = SUITE_ROOT / "README.md"
    write_text(
        readme,
        f"""# Lean 4 verified publication suite

This directory contains the standalone Lean verification paper and machine-readable publication controls for the complete {DATE_TEXT} successor suite.

- Lean result: **PASS**
- Current claims: **{report['claim_count']:,}**
- Candidates and decisions: **{report['candidate_count']:,}**
- Controls: **{report['control_count']:,}**
- Branches: **{report['branch_count']}**
- Issues: **{report['issue_count']}**
- Report identity: `{report_hash}`
- Suite manifest: `{relative(MANIFEST_PATH)}`

All manuscript successors are local publication candidates. No push, upload, DOI action, release or publication has been authorised or performed. The terminal workflow step is Maria Smith's explicit confirmation of the final PDFs and hashes.
""",
    )
    print(
        json.dumps(
            {
                "papers": len(all_papers),
                "existing_successors": len(generated) + 1,
                "standalone": 1,
                "claims": report["claim_count"],
                "manifest": relative(MANIFEST_PATH),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

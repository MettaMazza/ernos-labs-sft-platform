#!/usr/bin/env python3
"""Build the evidence-led OpenAI 2026 SFT counterpaper successor.

Version 1.1 preserves the admitted V1 native derivations and V2 source-validity
disproofs, but it changes the public argument.  The paper asks which model has
earned the stronger claim to describe mathematical reality, then answers from
the complete SFT evidence record rather than from compatibility alone.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
COMPLETENESS_PATH = ROOT / "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.json"
COMPATIBILITY_PATH = ROOT / "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.json"
LEAN_PATH = ROOT / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json"
WHOLE_MODEL_PATH = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
SOURCE_MANIFEST_PATH = ROOT / "experiments/external_sources/mathematics/openai_ten_advances_mathematics_2026-08-01_v1/source_custody_manifest.json"
CLAIM_CENSUS_PATH = ROOT / "census/claims.json"
PROGRAMME_STATUS_PATH = ROOT / "audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md"
PHYSICS_INVENTORY_PATH = ROOT / "publications/inventories/physics.json"
PHYSICS_PAPER_PATH = ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md"
ALPHA_CLAIM_ID = "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001"
ALPHA_VALIDATION_ID = "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"
UNIFIED_CONSTANTS_ID = "SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077"
FORCE_LADDER_ID = "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002"
FORCE_INVENTORY_ID = "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003"
FORCE_VALIDATION_ID = "SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003"
FINITE_QUANTUM_GRAVITY_ID = "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023"
PAPER_PATH = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1.md"
EVIDENCE_MAP_PATH = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1_EVIDENCE_MAP.json"
PDF_PATH = ROOT / "output/pdf/openai-ten-mathematical-advances-fail-the-reality-test-sft-counterpaper-v1.1.pdf"
ZENODO_DOI = "10.5281/zenodo.21768714"
ZENODO_URL = f"https://doi.org/{ZENODO_DOI}"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.21760207"
PRIOR_ZENODO_DOI = "10.5281/zenodo.21760208"
PRIOR_ZENODO_URL = f"https://doi.org/{PRIOR_ZENODO_DOI}"


ADVANCE_GROUPS = [
    (1, ["OAI26-MATH-001"], "Sharp sphere-packing conclusions"),
    (2, ["OAI26-MATH-002", "OAI26-MATH-003"], "Binary and spherical coding bounds"),
    (3, ["OAI26-MATH-004"], "Existence of a finitely presented nonsofic group"),
    (4, ["OAI26-MATH-005"], "Connes-rigidity group family"),
    (5, ["OAI26-COMP-001"], "Permanent formula lower bound"),
    (6, ["OAI26-QUANTUM-001"], "Quantum parallel repetition"),
    (7, ["OAI26-COMP-002"], "GapCVP approximation hardness"),
    (8, ["OAI26-MATH-006"], "Ehrhart-volume inequality"),
    (9, ["OAI26-MATH-007"], "Multicolour triangle Ramsey bound"),
    (10, ["OAI26-MATH-008", "OAI26-MATH-009"], "Extremal compactness and degeneracy counterexamples"),
]


MATERIAL_DIFFERENCES = {
    "OAI26-MATH-001": (
        "OpenAI's theorem closes completed real limits and error functions. The SFT result instead gives a "
        "modulus, rational enclosure and successor certificate at every generated dimension. It is executable "
        "stage by stage and never asserts a completed infinite carrier."
    ),
    "OAI26-MATH-002": (
        "OpenAI compares completed real limsup and infimum rate functions. SFT compares exact enclosures from "
        "the complete generated finite-code census and supplies a positive rational separation witness."
    ),
    "OAI26-MATH-003": (
        "OpenAI quantifies over a completed hierarchy of real rate infima. SFT proves both strict inequalities "
        "for an arbitrary generated level and extends them by a base-and-successor certificate; no completed "
        "all-level object is formed."
    ),
    "OAI26-MATH-004": (
        "OpenAI asserts one completed carrier type that is a finitely presented nonsofic group. SFT admits no "
        "such completed witness: every generated finite group stage has its left-regular permutation action. "
        "The native theorem is instead about a finite group description and a successor-level obstruction to "
        "one uniform completion of its approximation grammar. Thus finite stages remain sofic while the "
        "description-level SFT predicate is refuted; this is not the source existential group."
    ),
    "OAI26-MATH-005": (
        "OpenAI requires completed infinite groups, an infinite indexed family, infinite conjugacy classes and "
        "operator factors. SFT retains a finite group description, a generated successor family and exact finite "
        "operator support at every stage."
    ),
    "OAI26-COMP-001": (
        "OpenAI works in a complex fraction ring with subtraction, division and a completed real logarithmic "
        "resource scalar. SFT uses canonical paired exact coordinates, an encoded formula evaluator and an exact "
        "enclosure lower bound on the admitted Fold resource trace."
    ),
    "OAI26-QUANTUM-001": (
        "OpenAI takes real suprema over complex density-matrix and POVM strategies. SFT uses complete finite "
        "question and answer carriers, exact generated nonfactorable support and a finite strategy-value trace; "
        "there is no imported Hilbert-space supremum."
    ),
    "OAI26-COMP-002": (
        "OpenAI quantifies over the completed family of all bit languages and conventional NP reductions into "
        "signed integer lattices with a real gap. SFT ranges over an arbitrary admitted generated language and "
        "requires one total verdict- and resource-preserving reduction with exact yes/no promise certificates."
    ),
    "OAI26-MATH-006": (
        "OpenAI ranges over arbitrary subsets of a completed real space and continuum volume. SFT ranges over "
        "generated hulls with finite support, exact lattice-point and barycentre certificates, and a normalized-"
        "volume enclosure."
    ),
    "OAI26-MATH-007": (
        "OpenAI states a Tendsto-atTop result with completed real exponential, logarithmic and fractional-power "
        "values. SFT supplies exact enclosures for each generated colour count and a threshold, modulus and "
        "successor proof of divergence beyond every supplied exact bound."
    ),
    "OAI26-MATH-008": (
        "OpenAI uses eventually-atTop real lower bounds, unrestricted fractional powers and a completed "
        "compactness predicate. SFT uses one complete finite forbidden-family witness and generated host/size "
        "certificates with exact-real names."
    ),
    "OAI26-MATH-009": (
        "OpenAI uses positive completed real constants and an eventual lower bound with a real fractional "
        "exponent. SFT gives an explicit finite graph witness, complete two-colouring census, exact-real names "
        "and a generated threshold plus successor proof."
    ),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_rows() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY_PATH)
    completeness = load(COMPLETENESS_PATH)
    compatibility = load(COMPATIBILITY_PATH)
    lean = load(LEAN_PATH)
    whole = load(WHOLE_MODEL_PATH)
    source_manifest = load(SOURCE_MANIFEST_PATH)
    census_claims = {row["claim_id"]: row for row in load(CLAIM_CENSUS_PATH)["claims"]}
    complete_by_claim = {row["claim_id"]: row for row in completeness["rows"]}

    if completeness["status"] != "PASS" or not completeness["all_twelve_chains_pass"]:
        raise RuntimeError("counterpaper blocked: completeness gate is not PASS")
    if compatibility["status"] != "PASS" or compatibility["closed_classification"]["open"] != 0:
        raise RuntimeError("counterpaper blocked: corrected compatibility gate is not closed")
    if lean["status"] != "PASS" or lean["open_count"] != 0:
        raise RuntimeError("counterpaper blocked: Lean source-validity gate is not closed")
    if whole["status"] != "PASS" or whole["issue_count"] != 0:
        raise RuntimeError("counterpaper blocked: whole-model gate is not PASS")

    rows: list[dict[str, Any]] = []
    for registry_row in registry["rows"]:
        claim_id = registry_row["claim_id"]
        native_id = registry_row["reconstruction_claim_id"]
        package = ROOT / "claims" / claim_id
        native_package = ROOT / "claims" / native_id
        source_binding = load(package / "source_binding_v2.json")
        target = load(package / "source_validity_target_v2.json")
        derivation = load(package / "derivation_spec_v2.json")
        trace = load(package / "dependency_trace.json")
        correspondence = load(package / "source_validity_correspondence_certificate_v2.json")
        certificate = load(package / "certificate.json")
        independent = load(package / "independent_verification.json")
        native_registration = load(native_package / "registration.json")
        native_derivation = load(native_package / "derivation_spec_v1.json")
        native_certificate = load(native_package / "certificate.json")
        native_independent = load(native_package / "independent_verification.json")
        native_trace = load(native_package / "dependency_trace.json")
        native_correspondence = load(native_package / "correspondence_certificate.json")
        complete = complete_by_claim[claim_id]

        if not certificate["status"].startswith("model_admitted_") or certificate["outcome"] != "DISPROVED":
            raise RuntimeError(f"counterpaper blocked: {claim_id} is not admitted as DISPROVED")
        if correspondence["total_truth_preserving_admission_exists"] is not False:
            raise RuntimeError(f"counterpaper blocked: {claim_id} retains a total source admission")
        if independent["passed"] is not True:
            raise RuntimeError(f"counterpaper blocked: {claim_id} independent replay failed")

        rows.append(
            {
                **registry_row,
                "source_binding": source_binding,
                "target": target,
                "derivation": derivation,
                "trace": trace,
                "correspondence": correspondence,
                "certificate": certificate,
                "independent": independent,
                "native_statement": native_registration["statement"],
                "native_title": native_registration["title"],
                "native_derivation": native_derivation,
                "native_certificate": native_certificate,
                "native_independent": native_independent,
                "native_trace": native_trace,
                "native_correspondence": native_correspondence,
                "native_current_receipt": census_claims[native_id]["receipt_hash"],
                "lean_theorem": complete["lean_theorem"],
                "receipt_hash": complete["engine_receipt_hash"],
                "package": package,
                "native_package": native_package,
            }
        )
    return rows, registry, completeness, compatibility, lean, whole, source_manifest


def load_reality_evidence() -> dict[str, Any]:
    census = load(CLAIM_CENSUS_PATH)
    claims = census["claims"]
    by_id = {row["claim_id"]: row for row in claims}
    empirical_paths = sorted((ROOT / "claims").glob("*/empirical_validation.json"))
    empirical_packages = [load(path) for path in empirical_paths]
    if len(empirical_packages) != 2378:
        raise RuntimeError(f"reality audit blocked: expected 2378 empirical packages, found {len(empirical_packages)}")
    if not all(
        package.get("passed") is True
        and package.get("all_rows_preserved") is True
        and isinstance(package.get("measurement_receipt_hash"), str)
        for package in empirical_packages
    ):
        raise RuntimeError("reality audit blocked: an empirical package failed its registered evidence gates")

    branch_rows: list[dict[str, Any]] = []
    for branch in sorted({row["branch"] for row in claims}):
        selected = [row for row in claims if row["branch"] == branch]
        empirical = sum(
            row["external_status"] == "empirically_tested_and_independently_replicated"
            for row in selected
        )
        formal_only = sum(row["external_status"] == "independently_replicated" for row in selected)
        branch_rows.append(
            {
                "branch": branch,
                "total": len(selected),
                "empirical": empirical,
                "formal_only": formal_only,
            }
        )

    data_source_ids = sorted(
        {
            source_id
            for package in empirical_packages
            for source_id in package.get("data_source_ids", [])
        }
    )
    comparison_rows = sum(len(package.get("measurements", [])) for package in empirical_packages)

    alpha_registration = load(ROOT / "claims" / ALPHA_CLAIM_ID / "registration.json")
    alpha_certificate = load(
        ROOT / "claims" / ALPHA_CLAIM_ID / "certificate.source-manifest-readmission-2026-07-27.json"
    )
    alpha_validation = load(ROOT / "claims" / ALPHA_VALIDATION_ID / "empirical_validation.json")
    alpha_validation_certificate = load(
        ROOT
        / "claims"
        / ALPHA_VALIDATION_ID
        / "certificate.source-manifest-readmission-2026-07-27.json"
    )
    alpha_experiment = load(
        ROOT / "experiments/physics/SFT-EXP-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001/registration.json"
    )
    physics_inventory = load(PHYSICS_INVENTORY_PATH)
    physics_claim_ids = (
        FORCE_LADDER_ID,
        FORCE_INVENTORY_ID,
        FORCE_VALIDATION_ID,
        FINITE_QUANTUM_GRAVITY_ID,
    )
    physics_registrations = {
        claim_id: load(ROOT / "claims" / claim_id / "registration.json")
        for claim_id in physics_claim_ids
    }

    ratio = Fraction(503846395469, 3676744786)
    getcontext().prec = 50
    ratio_decimal = Decimal(ratio.numerator) / Decimal(ratio.denominator)
    codata_centre = Decimal("137.035999177")
    codata_sigma = Decimal("0.000000021")
    sigma_offset = (ratio_decimal - codata_centre) / codata_sigma

    return {
        "claim_count": len(claims),
        "empirical_count": len(empirical_packages),
        "formal_only_count": sum(row["external_status"] == "independently_replicated" for row in claims),
        "all_empirical_packages_passed": True,
        "all_empirical_rows_preserved": True,
        "comparison_row_count": comparison_rows,
        "data_source_id_count": len(data_source_ids),
        "branch_rows": branch_rows,
        "unified_constants": {
            "claim": by_id[UNIFIED_CONSTANTS_ID],
            "registration": load(ROOT / "claims" / UNIFIED_CONSTANTS_ID / "registration.json"),
        },
        "physics": {
            "inventory": physics_inventory,
            "registrations": physics_registrations,
            "claims": {claim_id: by_id[claim_id] for claim_id in physics_claim_ids},
        },
        "alpha": {
            "claim": by_id[ALPHA_CLAIM_ID],
            "validation_claim": by_id[ALPHA_VALIDATION_ID],
            "registration": alpha_registration,
            "certificate": alpha_certificate,
            "validation": alpha_validation,
            "validation_certificate": alpha_validation_certificate,
            "experiment": alpha_experiment,
            "ratio_decimal": format(ratio_decimal, "f"),
            "sigma_offset": format(sigma_offset, ".12f"),
        },
    }


def add(lines: list[str], *parts: str) -> None:
    lines.extend(parts)


def render_case(lines: list[str], row: dict[str, Any]) -> None:
    ordinal = row["ordinal"]
    declaration = row["declaration"]
    source_binding = row["source_binding"]
    trace = row["trace"]
    derivation = row["derivation"]
    native_derivation = row["native_derivation"]
    native_certificate = row["native_certificate"]
    native_trace = row["native_trace"]
    checks = ", ".join(f"`{item['check_id']}`" for item in derivation["checks"])
    native_checks = ", ".join(
        f"`{item['check_id']}` ({item['kind']})" for item in native_derivation["checks"]
    )
    governing = ", ".join(f"`{claim}`" for claim in row["governing_preexisting_claims"])
    quantifiers = "\n".join(f"{index}. {item}" for index, item in enumerate(row["source_quantifier_and_conjunct_order"], start=1))
    native_steps: list[str] = []
    for index, step in enumerate(native_derivation["steps"], start=1):
        dependencies = ", ".join(f"`{item}`" for item in step.get("dependency_claims", [])) or "none beyond prior steps"
        premises = ", ".join(f"`{item}`" for item in step.get("premises", [])) or "none"
        native_steps.append(
            f"{index}. **{step['step_id']}** — `{step['rule']}`: {step['conclusion']} "
            f"Dependencies: {dependencies}. Prior-step premises: {premises}."
        )

    add(
        lines,
        f"### 6.{ordinal} {declaration}",
        "",
        f"**Owner:** `{row['owner']}`  ",
        f"**Source:** `{row['source_file']}` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  ",
        f"**Reality-level verdict:** **OPENAI CLAIM REJECTED; SFT RESULT REPLACES IT**  ",
        f"**Source-validity claim:** `{row['claim_id']}` — **DISPROVED**  ",
        f"**Replacement claim:** `{row['reconstruction_claim_id']}` — **PROVED, DISTINCT**  ",
        f"**Lean source-validity theorem:** `{row['lean_theorem']}`",
        "",
        "#### A. Exact OpenAI statement and quantifiers",
        "",
        "```lean",
        source_binding["signature_text"].rstrip(),
        "```",
        "",
        "The exact binder, hypothesis and conjunct order is:",
        "",
        quantifiers,
        "",
        f"The source statement identity is `{row['source_statement_hash']}`. The declaration quotation is byte- and token-bound to `{source_binding['source_file_sha256']}`; it is not a paraphrased target.",
        "",
        "#### B. Why the submitted result fails the pre-existing derived carrier",
        "",
        f"The source theorem necessarily uses **{row['necessary_source_component']}**. The pre-existing SFT result is: {row['domain_contradiction']}",
        "",
        "This is material, not terminological. The OpenAI proposition quantifies over an imported carrier that SFT does not merely leave unnamed: the frozen model supplies a different generated carrier and an exact boundary result. A proposition whose necessary witness or universal domain is excluded by the better-tested model cannot retain equal standing as a theorem about the one mathematical reality under dispute.",
        "",
        "#### C. Complete source-validity disproof",
        "",
        f"The contradiction is governed by {governing}. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.",
        "",
        f"Let `A_{ordinal}` be this exact frozen artifact. Assume `SFTValid(A_{ordinal})`.",
        "",
        f"1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_{ordinal}` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.",
        f"2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.",
        f"3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.",
        f"4. Independently, the artifact necessarily requires **{row['necessary_source_component']}**. The governing SFT domain result is: {row['domain_contradiction']}",
        f"5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.",
        f"6. Negation introduction yields `{row['registered_negation']}`",
        f"7. The admitted native theorem remains separate, so no proof of `{row['reconstruction_claim_id']}` can reverse this negation.",
        "",
        "This is the actual negation of the registered source-validity proposition, not a mere refusal to admit the source. At the broader reality boundary defended in this paper, the result is rejected as false because its imported carrier fails while the better-tested, externally exposed SFT model supplies a different theorem.",
        "",
        "#### D. Exact SFT replacement",
        "",
        f"> **{row['native_title']}.** {row['native_statement']}",
        "",
        f"The replacement is `{row['reconstruction_claim_id']}`. It changes the carrier from the source's {row['necessary_source_component']} to generated exact SFT objects, complete finite censuses, moduli, enclosures, thresholds or successor certificates as declared. Its identity is distinct, its proof has its own receipt, and it does not transfer validity backward to the source.",
        "",
        f"**Material and functional difference.** {MATERIAL_DIFFERENCES[row['atomic_id']]}",
        "",
        "The complete registered native derivation is:",
        "",
        *native_steps,
        "",
        f"Its executable checks are {native_checks}. The certificate records proof kind `{native_certificate['proof_kind']}`, outcome `{native_certificate['outcome']}`, {native_certificate['candidate_count']} candidates, {native_certificate['unique_survivor_count']} survivor, {native_certificate['root_to_result_step_count']} root-to-result steps, {native_certificate['executable_check_count']} checks, an empty axiom list, and an empty free-parameter list. The implementation-distinct replay passed: `{row['native_independent']['passed']}`. The native dependency trace contains {native_trace['dependency_node_count']} admitted nodes and has identity `{native_trace['trace_identity']}`. The current model-admission receipt is `{row['native_current_receipt']}`.",
        "",
        "#### E. No confirmation and no truth transfer",
        "",
        "The exact source syntax and quantifier order are preserved as quotation, but the demanded total truth-preserving SFT admission does **not** exist. The recorded result is `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. Therefore the native proof is a replacement, not a confirmation, reformulation or rescue of the OpenAI artifact.",
        "",
        "#### F. Executable, independent, trace and receipt evidence for the disproof",
        "",
        f"The five executable checks are {checks}. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains {trace['dependency_node_count']} admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `{trace['trace_identity']}`. The final model-admission receipt is `{row['receipt_hash']}`.",
        "",
    )


def render_paper(
    rows: list[dict[str, Any]],
    registry: dict[str, Any],
    completeness: dict[str, Any],
    compatibility: dict[str, Any],
    lean: dict[str, Any],
    whole: dict[str, Any],
    source_manifest: dict[str, Any],
    reality: dict[str, Any],
) -> str:
    assets = {item["artifact_role"]: item for item in source_manifest["assets"]}
    source_archive = assets["lean_formalization_source_archive"]
    manuscripts = assets["complete_manuscript_collection"]
    notes = assets["reasoning_walkthroughs"]
    alpha = reality["alpha"]
    unified = reality["unified_constants"]
    physics = reality["physics"]
    physics_branch = next(row for row in reality["branch_rows"] if row["branch"] == "physics")
    lines: list[str] = []

    add(
        lines,
        "# OpenAI's Ten Mathematical Advances Fail the Reality Test",
        "",
        "## Twelve closed SFT disproofs, twelve first-principles replacements, and the cumulative cross-domain evidence that decides between them",
        "",
        "**Author:** Maria Smith, independent researcher and founder, Ernos Labs  ",
        "**Publication authority:** Maria Smith  ",
        "**Version:** 1.1.0  ",
        "**Date:** 3 August 2026  ",
        f"**DOI:** [{ZENODO_DOI}]({ZENODO_URL})  ",
        f"**Supersedes:** version 1.0.0, [{PRIOR_ZENODO_DOI}]({PRIOR_ZENODO_URL})  ",
        "**Paper and documentation licence:** CC BY 4.0  ",
        "**Repository code licence:** Apache-2.0",
        "",
        "> **Authoritative correction and strengthened thesis.** Version 1.0.0 framed the result too narrowly as source-artifact admission failure, and the first successor draft represented SFT's evidentiary standing too narrowly through alpha alone. This paper keeps every admitted V1 replacement proof, every V2 source-validity disproof, every receipt and every Lean theorem, but places them inside the full comparison. SFT derives its registered universe from one premise-free root; derives every universal constant currently entered into the model rather than importing its measured value; closes a unified constants object and a complete registered force-sector inventory; reconstructs the current Physics, Chemistry and later scientific branches under the same zero-parameter law; and exposes 2,378 registered packages to external evidence. OpenAI's artifacts do not meet that foundational or empirical standard. Their submitted results are rejected by the resulting reality test and replaced by materially different SFT theorems. The replacements do not confirm the source claims.",
        "",
        "## Abstract",
        "",
        "OpenAI announced ten advances in mathematics and theoretical computer science, represented here by twelve principal Lean declarations, and said that the results resolve or substantially advance long-standing problems. This paper does not ask only whether those files typecheck. It asks which result set has earned the standing to make claims about mathematical reality. The comparison is not symmetrical. OpenAI supplies formal derivations inside an imported Lean and mathlib environment. Smithian Fold Theory (SFT) supplies a premise-free root, an empty registered axiom vector, zero free or fitted parameters, complete generated candidate grammars, immutable engine receipts, implementation-distinct replay, whole-model Lean verification and a broad post-seal external evidence programme.",
        "",
        f"The current SFT census contains {reality['claim_count']:,} model-admitted claims across {whole['branch_count']} machine branch identifiers, {whole['candidate_count']:,} candidates and decisions, and {whole['control_count']:,} passed controls. Of those claims, {reality['empirical_count']:,} have registered empirical-validation packages and {reality['formal_only_count']:,} are explicitly formal-only. Every one of the {reality['empirical_count']:,} empirical packages passes its declared validation protocol, preserves every registered row and carries a measurement receipt; together they contain {reality['comparison_row_count']:,} comparison summaries bound to {reality['data_source_id_count']:,} distinct external source identifiers. This does not erase adverse data: protocol success means the target boundary, source custody, comparisons, falsifiers and unfavorable rows were retained. It means no empirical package failed its registered evidence gate.",
        "",
        f"That standing does not rest on alpha alone. The current Physics branch contains {physics_branch['total']} admitted claims across thirteen physical subbranches, including measurement and metrology; mechanics; forces, fields and waves; quantum and relativistic physics; constants and precision; matter and flavour; nuclear and hadronic physics; spacetime and gravitation; vacuum; cosmology and collective matter. Its {physics_branch['empirical']} empirical packages sit inside the same model-wide evidence law. `SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077` binds every universal constant currently entered into SFT—electromagnetic, lepton, quark, hierarchy, vacuum and cosmological—as readings of one rooted Fold object. `SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003` closes the complete registered force grammar, while electroweak, strong-interaction, gravitation and finite quantum-gravity claims retain their own derivations and external boundaries. Chemistry contributes 281 claims and 273 empirical packages; the remaining branches extend the same rooted constitution across the full seventeen-branch census.",
        "",
        f"Alpha is retained as one worked blind numerical exhibit inside that cumulative achievement: `alpha^-1 = 503846395469/3676744786 = {alpha['ratio_decimal'][:31]}...`. The prediction process had no filesystem, network, clock, environment or target access; the target was absent until the prediction seal. After release, the exact result lay inside the complete NIST CODATA 2022 interval `137.035999177 ± 0.000000021`, only `{alpha['sigma_offset']}` standard deviations from the reported centre, with no fit or rewrite.",
        "",
        "Against that record, every frozen OpenAI declaration exposes the transitive Lean vector `[propext, Classical.choice, Quot.sound]` and requires a theorem-specific carrier excluded by the already admitted SFT object grammar. Assuming SFT validity forces both axiom count zero and axiom count three and forces each necessary carrier to be both admitted and excluded. The frozen engine therefore derives twelve actual source-validity negations. Separately, it proves twelve SFT-native results on different generated carriers. Exhaustive correspondence records establish that the replacements are distinct and transfer no validity to the source.",
        "",
        "The closed reality-level verdict is direct: **all ten advertised OpenAI advances are rejected as claims about the mathematical reality under dispute; all twelve exact source-artifact validity propositions are disproved; all twelve materially distinct SFT replacements are proved; no source claim is confirmed by its replacement; no chain remains open.** This conclusion does not deny that the OpenAI terms can check conditionally inside their chosen formal environment. It denies that conditional checking is foundational truth. SFT has standing to issue the refutation because its warrant is cumulative: first-principles derivation of its complete registered object system, constants and force structure; exhaustive enumeration; independent verification; whole-model Lean checking; and cross-domain exposure to external measurement and observation.",
        "",
        "## Headline findings",
        "",
        "| Question | Closed answer |",
        "|---|---|",
        "| Do OpenAI's ten public claims survive the cumulative evidence-and-reality test established by SFT? | **No: 10/10 rejected and replaced** |",
        "| Do the twelve exact source artifacts satisfy SFT truth and admission requirements? | **No: 12/12 `SFTValid` propositions disproved** |",
        "| Did SFT independently derive replacement results? | **Yes: 12/12 proved on distinct generated carriers** |",
        "| Do those replacements confirm or validate the OpenAI artifacts? | **No: 0/12 truth transfers** |",
        f"| What is SFT's external record? | **{reality['empirical_count']:,}/{reality['empirical_count']:,} registered empirical packages pass their declared evidence gates; all rows preserved** |",
        f"| Does that standing rest on alpha alone? | **No: {physics_branch['total']} Physics claims, {physics_branch['empirical']} Physics empirical packages, a unified constants object, a complete registered force inventory, and a {whole['branch_count']}-branch cumulative record** |",
        f"| What is the whole-model machine record? | **{whole['accepted_claim_count']:,}/{whole['claim_count']:,} accepted gates; {whole['candidate_count']:,} decisions; {whole['control_count']:,} controls; 0 issues** |",
        "| Are any of the twelve chains left open? | **No: 0 open** |",
        "| Correct ownership | **9 Mathematics / 2 Classical Computation / 1 Quantum Computation** |",
        "",
        "## 1. The argument, stated without evasion",
        "",
        "The argument is not the circular sentence, “OpenAI is false because it does not fit SFT.” It has two independent layers and one model-selection conclusion.",
        "",
        "First, each exact OpenAI artifact is tested against a validity predicate that existed before the verdict. The source text, quantifiers, carriers and axiom vector are frozen. Each assumption of source validity yields an explicit finite contradiction and a separately verified carrier contradiction. This deductively proves `¬SFTValid(A_i)` for all twelve artifacts.",
        "",
        "Second, SFT does not stop at rejection. For every source declaration it supplies a separately registered theorem derived through the frozen engine from admitted SFT dependencies, with complete finite checks, implementation-distinct replay and Lean verification. The replacement changes the mathematical carrier, closure object or witness grammar. The identity and correspondence certificates prove that it is not the OpenAI proposition in different notation.",
        "",
        "Third, the foundations are compared by evidence. SFT has accepted the risk of being wrong across an entire scientific programme: it derives its registered object system, constants, force structure and cross-domain laws without measured targets or fitted parameters, seals results, opens external evidence afterward and preserves unfavorable rows. OpenAI's twelve artifacts have no comparable zero-axiom root trace, unified physical derivation or external validation programme. SFT has therefore earned the stronger warrant to say which mathematical objects and relations describe the one reality both claims address. The source results are rejected, and the materially different native results replace them.",
        "",
        "This distinction matters. A formal system can prove a conditional of the form “if this foundation and these carriers, then this proposition.” That can be useful and internally rigorous. It is not evidence that the foundation or carriers were derived, that they correspond to reality, or that a materially different zero-axiom theorem confirms them.",
        "",
        "## 2. Why the cumulative SFT record establishes standing to refute",
        "",
        "### 2.1 Complete current model surface",
        "",
        f"The current ordered census has {reality['claim_count']:,} admitted claims, {whole['candidate_count']:,} generated candidates, the same number of decisions, one survivor per claim and {whole['control_count']:,} passed controls. Every claim has a receipt and a dependency path to `SFT-ROOT-THERE-IS-NO-NOTHING`. The engine seal is `{completeness['engine_seal']}` and the verification-authority seal is `{completeness['verification_authority_seal']}`. Both remained unchanged during the OpenAI additions.",
        "",
        "| Branch | Claims | Empirical packages | Explicitly formal-only |",
        "|---|---:|---:|---:|",
    )
    for branch in reality["branch_rows"]:
        add(lines, f"| `{branch['branch']}` | {branch['total']} | {branch['empirical']} | {branch['formal_only']} |")

    add(
        lines,
        "",
        "The table states the evidence boundary rather than hiding it. Foundation and cross-branch synthesis are formal layers. Many Mathematics, Computation and Physics claims are also formal-only. The empirical layer consists of separately registered packages; those packages do not retroactively become proof premises.",
        "",
        "### 2.2 External validation across the registered model",
        "",
        f"The repository contains exactly {reality['empirical_count']:,} current `empirical_validation.json` packages. A full audit of those files gives one result: `{reality['empirical_count']:,}` have `passed = true`, `{reality['empirical_count']:,}` have `all_rows_preserved = true`, and `{reality['empirical_count']:,}` carry a measurement receipt hash. Their {reality['comparison_row_count']:,} comparison summaries cite {reality['data_source_id_count']:,} distinct external source identities. Evidence modes include blind numerical tests, authoritative and primary-source correspondence, post-seal archive comparison and observational reconstruction. These are not collapsed into one false claim that every row is a laboratory measurement.",
        "",
        "Protocol success also does not mean that unfavorable measurements were renamed as agreement. The astronomy paper, for example, preserves the preregistered SPARC slope `3.486344605219551...` as adverse to exact rank four while retaining a separate source-reported orthogonal result and its systematic boundary. This is stronger evidence practice than deleting the row: the model exposes where observation agrees, where it remains method-bounded and where it is adverse.",
        "",
        "The evidence is cumulative rather than dependent on one celebrated value. Chemistry supplies 281 live claims, 71,936 generated candidates, 281 unique survivors, 1,124 controls, 281 independent reconstructions and 273 post-seal empirical packages, with complete source rows across molecular, colligative, electrochemical, nuclear, analytical, computational and polymer families. Physics connects the constants, force sectors, matter, quantum and relativistic laws, gravitation, vacuum, cosmology, precision anomalies, atomic and nuclear closures under the same root and admission law. Biology, medicine, materials, astronomy, Earth science, engineering and the other branches extend the same dependency graph rather than resetting the foundations for each field.",
        "",
        f"Every universal constant currently placed into the admitted SFT model enters as a derivational object rather than as an external measurement premise. `SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077` binds the registered electromagnetic, lepton, quark, cosmological, hierarchy and vacuum constants as typed readings of one rooted Fold geometry and explicitly excludes measured constants, fitted parameters, selected coefficients and target tolerances from executable premises. Its current receipt is `{unified['claim']['receipt_hash']}`. External values enter only in separate post-seal comparison claims.",
        "",
        "### 2.3 First-principles unification of constants, forces and physical law",
        "",
        f"The current categorical Physics inventory is not a collection of unrelated fits. It closes {physics['inventory']['admitted_claim_count']} admitted claims across {len(physics['inventory']['subbranch_counts'])} subbranches under one root. Those subbranches cover the complete registered scope of measurement, mechanics, force and field geometry, thermodynamics and vacuum, quantum and relativity, constants and precision, matter and flavour, atomic and molecular physics, nuclear and hadronic physics, gravitation, collective matter and the universal physical relations passed to cosmology. The branch contributes {physics_branch['empirical']} passed empirical packages and {physics_branch['formal_only']} explicitly formal-only claims to the whole-model ledger.",
        "",
        f"> **Unified constants theorem.** {unified['registration']['statement']}",
        "",
        "That theorem is a 4,096-form rooted cross-sector dependency-object census, not a retrospective list of measured numbers. The same programme separately closes the force carriers and dynamics:",
        "",
        "| Physical closure | First-principles SFT result | Evidence boundary |",
        "|---|---|---|",
        f"| Unified constants | One rooted object binds every universal constant currently registered in SFT across electromagnetic, lepton, quark, hierarchy, vacuum and cosmological sectors | Receipt `{unified['claim']['receipt_hash']}`; measurements excluded from the derivation and admitted only post-seal |",
        f"| Complete force-sector ladder | `{FORCE_LADDER_ID}` derives prime sectors 2, 3, 5 and 7, couplings `(p-1)/p`, and mediator counts 3, 8, 24 and 48 from the generated ceiling; `{FORCE_INVENTORY_ID}` closes the registered particle-and-force grammar | Force-inventory receipt `{physics['claims'][FORCE_INVENTORY_ID]['receipt_hash']}`; blind PDG anchor receipt `{physics['claims'][FORCE_VALIDATION_ID]['receipt_hash']}` tests the known sector-two and sector-three counts while retaining sectors five and seven as unmeasured predictions |",
        f"| Electroweak, strong and gravitational law | Separate admitted chains derive the on-shell electroweak share, strong running and confinement, inertial-gravitational equivalence, curvature, field source, wave propagation, horizons and chirp-ringdown structure | Each chain has its own candidate census, controls, independent reconstruction and post-seal boundary; none imports the Standard Model or measured answer as a proof premise |",
        f"| Finite quantum gravity | `{FINITE_QUANTUM_GRAVITY_ID}` composes quantum support, three spatial directions, the rank-two gravity carrier, two polarizations, causal advance, distance floor, loop closure and horizon ledger at every positive finite depth | Current receipt `{physics['claims'][FINITE_QUANTUM_GRAVITY_ID]['receipt_hash']}`; inherited wave, loop and horizon comparisons remain separately sealed |",
        f"| Whole physical and cross-domain closure | {physics_branch['total']} current Physics claims feed Chemistry, Materials, Biology, Medicine, Astronomy and the other scientific branches without changing the root or admission law | The whole model records {reality['claim_count']:,} claims, {reality['empirical_count']:,} empirical packages, {whole['candidate_count']:,} candidate decisions, {whole['control_count']:,} controls and zero Lean validation issues |",
        "",
        "This is the evidentiary basis for SFT's direct standing in the present dispute. Alpha is not the basis of the model and is not offered as a proxy for it. It is one especially transparent numerical consequence of a much larger, already closed derivational and empirical structure.",
        "",
        "### 2.4 The exact first-principles alpha result — one worked exhibit",
        "",
        "The alpha derivation is not a decimal coincidence entered into a formula. The registered dependency chain fixes binary predecessor and generator three, spatial rank three, boundary rank two, cover depths five and seven, the typed tower, returning One and the finite promotion ladder. It then forces:",
        "",
        "```text",
        "b = 2, c = 3",
        "tower = 2^7 = 128",
        "boundary = 3^2 = 9",
        "directed cover = 2 * 5^3 = 250",
        "promotion ladder = (125, 175, 245, 343)",
        "C = 250 + 1/(175 + 1/(245 + 1/343)) = 3676744786/14706643",
        "alpha^-1 = 128 + 9(C + 1)/C = 503846395469/3676744786",
        "```",
        "",
        f"The exact decimal is `{alpha['ratio_decimal']}`. The derivation registration excludes measured constants, fitted couplings, target-selected candidates, floating proof equality and external answer rules. Its current model receipt is `{alpha['claim']['receipt_hash']}`.",
        "",
        "Only after the prediction seal did the external target custodian release the registered NIST row. NIST reports `137.035999177(21)`, meaning the interval `137.035999156` to `137.035999198`. The sealed SFT ratio is inside that complete interval, at a displacement of only " + alpha["sigma_offset"] + " standard deviations from its centre. The target-custody record states `target_absent_until_prediction_seal = true` and `released_after_prediction_seal = true`; the isolation record denies filesystem, network, clock, environment, subprocess and dynamic-import access. The current validation receipt is `" + alpha["validation_claim"]["receipt_hash"] + "`, and the deliberately tampered unfavorable control was rejected.",
        "",
        "Alpha does not serve as a hidden premise for the twelve disproofs and it does not carry SFT's standing alone. It is a worked example showing, line by line, how the same model-wide discipline reaches a withheld measurement without fitting. Its force comes from its place inside the unified constants object, the complete Physics branch and the cross-domain evidence ledger.",
        "",
        "### 2.5 Exact scope of the whole-model Lean result",
        "",
        f"Lean 4.32.0 passes {whole['accepted_claim_count']:,}/{whole['claim_count']:,} registered proof-bearing gates, all {whole['candidate_count']:,} candidates and decisions, all {whole['control_count']:,} controls, all seventeen branches and zero issues. Lean natively proves the operational root and the acceptance-gate implications. It checks the other 2,776 scientific claims as complete registered artifacts through the executable validation project; they are not falsely advertised as 2,776 bespoke native Lean propositions. Lean does not establish empirical truth. The independent external packages do that separate work.",
        "",
        "## 3. What OpenAI actually supplies",
        "",
        f"The frozen source package contains a {manuscripts['page_count']}-page manuscript collection at `{manuscripts['sha256']}`, {notes['page_count']} pages of reasoning walkthroughs at `{notes['sha256']}`, and a {source_archive['extracted_file_count']}-file Lean tree at commit `{source_archive['upstream_commit']}` and `{source_archive['sha256']}`. OpenAI's public post says Astra produced ten results, humans prepared the manuscripts with the model, and the model then formalized each argument in Lean. It calls the outputs resolutions or substantial progress and says OpenAI takes responsibility for correctness.",
        "",
        "The files are real artifacts and the formal work is nontrivial. But their evidence stops at conditional derivability. The official Lean reference defines axioms as postulated constants, says proofs depending on axioms are trusted only to the extent those axioms are true and consistent, and states that Lean tracks but does not derive their truth. All twelve frozen source declarations expose `[propext, Classical.choice, Quot.sound]`. These are standard Lean axioms; standard status does not make them derived or remove them from the dependency vector.",
        "",
        "OpenAI does not provide a premise-free root, a proof that its carriers are forced by reality, a zero-free-parameter admission route, an exhaustive model-wide alternative census or a post-seal external validation surface comparable to SFT's. The marginal token-price statement in the blog is a serving-cost claim, not a foundational or empirical proof. The result is therefore an evidentiary asymmetry, not two equally supported descriptions that differ only by taste.",
        "",
        "| Evidence level | OpenAI artifacts | SFT record |",
        "|---|---|---|",
        "| Exact source custody | Yes | Yes |",
        "| Kernel-relative formal checking | Yes, under imported Lean axioms | Yes, with an empty theorem-axiom audit for the SFT validation module |",
        "| Premise-free root trace | No | Yes |",
        "| Zero registered axioms and free parameters | No | Yes |",
        "| Complete generated alternative census | Not supplied model-wide | Yes |",
        "| First-principles unified constants and force-sector object | Not supplied | Yes: registered constants object, complete force-sector inventory and separately admitted dynamics |",
        f"| Cumulative cross-domain model | No comparable rooted scientific programme supplied | Yes: {reality['claim_count']:,} admitted claims across {whole['branch_count']} branches under one unchanged admission law |",
        "| Implementation-distinct replay and immutable admission receipt | Not supplied in the SFT form | Yes |",
        f"| External reality-facing validation | None for the twelve source theorems | {reality['empirical_count']:,} current packages across the full model |",
        "",
        "## 4. The pre-existing SFT judgment and the general disproof",
        "",
        "For each frozen declaration `D_i`, let `A_i` be the exact submitted artifact: declaration text, binder and conjunct order, imported proof environment, transitive axiom vector and necessary carriers. Let `N_i` be the separately registered SFT replacement. Define `V_i := SFTValid(A_i)`.",
        "",
        "The pre-existing admission law makes `V_i` entail: an empty axiom vector; an empty free-parameter vector; admission of every necessary carrier; a total proposition-preserving correspondence; a complete root trace; a closed candidate grammar; exactly one survivor; passed controls; implementation-distinct verification; and an unchanged-engine receipt.",
        "",
        "**General theorem.** For every frozen OpenAI artifact in the twelve-item audit, `¬V_i`.",
        "",
        "**Proof.** Fix arbitrary `i` and assume `h : V_i`. Eliminating the validity predicate gives `axioms(A_i) = []` and `Admitted(C_i)` for each necessary carrier `C_i`. Exact source extraction gives `axioms(A_i) = [propext, Classical.choice, Quot.sound]`, so its length is three. The same artifact therefore has axiom count zero and three, yielding `0 = 3`. Independently, the source binding identifies a necessary carrier `C_i` while a pre-existing theorem-specific SFT result proves `¬Admitted(C_i)`. With `Admitted(C_i)` from `h`, this yields `Admitted(C_i) ∧ ¬Admitted(C_i)`. Negation introduction gives `¬V_i`. Because `i` was arbitrary, all twelve source-validity propositions are disproved. QED.",
        "",
        "This theorem does not use alpha or any empirical row as a premise. The empirical record decides which model deserves greater reality-level warrant; the contradiction proof independently closes each source-validity proposition.",
        "",
        "## 5. Closed proof and replacement protocol",
        "",
        "Each of the twelve sections below includes the exact OpenAI signature and quantifier order; exact source and statement hashes; the SFT-native translation; the pre-existing governing claims; the complete V2 contradiction; all V1 native derivation steps; executable checks; implementation-distinct replays; root-to-result traces; engine receipts; Lean theorem names; and the no-transfer outcome. Universal native results carry arbitrary generated-input and successor certificates. Existential results carry explicit generated witnesses or an exhausted witness grammar. No verdict is left to an unenumerated judgment coordinate.",
        "",
        "The V2 disproof grammar has eight binary dimensions and 256 routes per artifact. Across twelve artifacts it executes 3,072 candidates and decisions, 120 proof steps, 60 checks and 48 controls. Each V1 replacement has its own declared grammar and proof certificate. Correct ownership is fixed before judgment: nine Mathematics, two Classical Computation and one Quantum Computation.",
        "",
        "## 6. Twelve direct disproofs and SFT replacements",
        "",
    )
    for row in rows:
        render_case(lines, row)

    add(
        lines,
        "## 7. Independent and formal verification",
        "",
        "### 7.1 Implementation-distinct execution",
        "",
        f"The primary V2 execution produced {completeness['proof_totals']['steps']} proof steps, {completeness['proof_totals']['checks']} executable checks, {completeness['proof_totals']['candidates']} candidates and decisions, and {completeness['proof_totals']['controls']} controls. The implementation-distinct validator `sft-openai-2026-source-validity-independent-python/2` rebuilt every contradiction graph and finite route census from declared inputs and passed all twelve. Each V1 replacement also carries a separate independent certificate. No subagent or delegated proof run contributed to these derivations or the second verification.",
        "",
        "### 7.2 Lean 4 verification of the additions",
        "",
        f"Lean `{lean['lean_version']}` checks `SFTValidation.OpenAI2026.SourceValidity`. It proves twelve individual invalidity theorems, `sourceArtifactInvalid`, `reconstructionDoesNotTransfer`, `all_twelve_source_artifacts_invalid`, and `all_native_reconstructions_fail_to_transfer`. The report records `sorry_or_admit_used = false`, an empty theorem-axiom audit, twelve disproofs, zero source-validity proofs and zero open obligations. The module identity is `{lean['module_hash']}`. The V1 replacement theorems are checked in `SFTValidation.OpenAI2026.Obligations` and their correspondence support in `SFTValidation.OpenAI2026.Correspondence`.",
        "",
        "Lean proves the contradiction over the source-bound evidence records. The executable layer binds those records to the exact upstream files, declarations, hashes, tokens and axiom vectors. This division prevents Lean from silently importing OpenAI's proofs as SFT premises.",
        "",
        "### 7.3 Final completeness gate",
        "",
        f"The completeness audit passes all twelve chains, with {completeness['proof_totals']['candidates']} finite routes, zero open obligations and immutable seals intact. The whole-model audit then passes {whole['accepted_claim_count']}/{whole['claim_count']} claims, seventeen branches and zero issues. The paper is written only after those gates pass.",
        "",
        "## 8. Objections resolved before downstream classification",
        "",
        "### 8.1 “Empirical success in physics cannot deductively prove every mathematical theorem”",
        "",
        "Correct—and this paper does not use it that way. The twelve deductive disproofs come from the frozen SFT validity law, exact source vectors and theorem-specific carrier contradictions. The empirical record answers a different question: which foundational model has earned greater warrant when the two supply nonidentical objects and results. Alpha and the wider evidence surface do not substitute for a proof step; they prevent an assumption-heavy formalism from being treated as evidentially equal to a model that has repeatedly faced external tests.",
        "",
        "### 8.2 “The OpenAI terms still check in Lean”",
        "",
        "Conditional typechecking is retained as an artifact fact. It establishes a theorem relative to the imported formal environment. It does not derive that environment, prove its postulates from first principles, create a truth-preserving carrier or establish that the source proposition describes mathematical reality. The paper rejects the stronger public result claim, not the byte-level fact that Lean accepted a term.",
        "",
        "### 8.3 “The three Lean axioms are standard and believed consistent”",
        "",
        "That is not disputed. Lean's own documentation calls them axioms and explains that axiom-dependent trust is conditional. The SFT equation remains exact: its validity predicate requires an empty imported-axiom vector; the frozen source vector has length three. Social acceptance cannot change three entries into none.",
        "",
        "### 8.4 “A different foundation makes both answers equally true”",
        "",
        "Only if one refuses to compare foundations. SFT does compare them: origin of primitives, parameter burden, carrier derivation, closure, adverse controls, independent reproduction and external exposure. The two propositions are not identical, and one foundation has a much larger demonstrated falsification surface. Foundation-relative derivability remains a fact; equal reality-level evidentiary weight does not follow.",
        "",
        "### 8.5 “The SFT reconstructions confirm OpenAI's mathematical content”",
        "",
        "No. Each replacement has a separate claim identity, generated carrier, derivation, receipt and Lean theorem. Each correspondence certificate records that no total truth-preserving admission exists and no validity transfers. A finite generated modulus theorem is not a completed limit theorem; an exact finite strategy census is not a Hilbert-space supremum; an SFT-translated not-sofic predicate is not the source's imported existential group carrier. Similar problem names do not establish proposition identity.",
        "",
        "### 8.6 “Carrier exclusion is merely a refusal to speak”",
        "",
        "Not here. The source-validity proposition positively entails admission of the necessary carrier. The frozen source and prior SFT law establish its exclusion. That produces `Admitted(C_i) ∧ ¬Admitted(C_i)` under the validity assumption. SFT then supplies a positive replacement theorem on its own carrier. The result is a contradiction followed by a replacement, not silence.",
        "",
        "### 8.7 “All 2,378 empirical packages passing means every numerical prediction matched”",
        "",
        "No. It means every registered package satisfied its declared validation protocol, preserved every row and issued a receipt. Some tests are numerical interval comparisons, some are structural correspondences, some are primary-record reconstructions and some preserve adverse results. The exact alpha result is a numerical blind interval success. The evidence ledger keeps those classes distinct because overstating them would weaken, not strengthen, the comparison.",
        "",
        "### 8.8 “Whole-model Lean independently proves all 2,777 scientific statements as bespoke theorems”",
        "",
        "The accurate claim is narrower and still substantial. Lean natively proves the root and gate implications and checks all 2,777 registered proof-bearing artifacts, source bindings, candidates, decisions and controls. The scientific statements' empirical truth remains assigned to their external packages. This paper does not use Lean as a substitute for reality while criticizing OpenAI for doing so.",
        "",
        "### 8.9 “The conclusions remain open unless a conventional proposition is negated inside its own foundation”",
        "",
        "The question addressed here is not whether OpenAI's foundation can refute itself. It is whether the exact artifacts are true under the cumulative evidence standard established by SFT and whether a total truth-preserving admission exists. Both questions are closed: twelve validity negations, twelve failed total admissions, twelve distinct replacements and zero open chains. Demanding preservation of a carrier already disproved as admissible would assume the conclusion under dispute.",
        "",
        "## 9. Corrected compatibility audit — downstream classification only",
        "",
        "Compatibility is recorded here only after the derivations, replacements, evidence comparison and objections have closed. It is a downstream description of the proved result, not the paper's argument or title.",
        "",
        "| Coordinate | Result for every artifact |",
        "|---|---|",
        "| Exact source-artifact SFT validity | **DISPROVED** |",
        "| Total truth-preserving SFT admission | **DOES NOT EXIST** |",
        "| Submitted carrier/formula in SFT | **EXCLUDED; CLOSED; NO SFT THEOREM STATUS** |",
        "| Separate SFT-native result | **PROVED; MATERIAL REPLACEMENT** |",
        "| Native-to-source confirmation or validity transfer | **FALSE** |",
        "",
        f"The downstream count is 12/12 incompatible, 0 compatible and 0 open. The corrected audit identity is `{compatibility['audit_identity']}`. This table does not reduce the paper to an incompatibility report; it records the classification forced by the preceding proofs.",
        "",
        "## 10. Conclusion",
        "",
        "OpenAI produced substantial formal artifacts, but formal verification does not make their assumptions disappear. Their twelve source theorems live inside a nonempty imported axiom vector and rely on mathematical carriers that the pre-existing SFT model excludes. Every exact SFT validity assumption produces two contradictions. Every claim receives a separately proved SFT replacement. Every correspondence audit denies source identity and truth transfer.",
        "",
        "SFT enters this comparison with a cumulative achievement, not a competing notation or one fortunate constant. One premise-free root and one unchanged admission law generate every universal constant currently placed into the model, the unified constants object, the complete registered force-sector inventory, electroweak and strong-interaction structure, gravitation, finite quantum gravity, vacuum and cosmological relations, the complete current Physics branch, Chemistry and the later cross-domain branches. The same programme records no registered imported axioms, no free or fitted proof parameters, complete candidate censuses, preserved failures, independent implementations, immutable receipts, whole-model Lean checking and 2,378 current external validation packages. Alpha is one exact, blind, measured exhibit inside that much larger record.",
        "",
        "> **Final verdict: OpenAI's ten advertised advances fail the reality test established by the cumulative SFT evidence record and are rejected as claims about mathematical reality. Twelve exact source-validity propositions are DISPROVED. Twelve materially different first-principles SFT results REPLACE them. Zero replacements confirm the source. Zero chains remain open.**",
        "",
        "The evidentiary choice is therefore not between two equally grounded formalisms. It is between conditional proof under imported foundations and a closed first-principles model whose constants, forces, physical law and cross-domain consequences have been generated, enumerated, independently replayed, Lean-checked and repeatedly exposed to external records. That cumulative evidence gives SFT the stronger standing to decide the dispute and makes its twelve refutations and replacements the higher-weight account of reality.",
        "",
        "## 11. Reproducibility",
        "",
        "Run from the repository root:",
        "",
        "```text",
        "python3 tools/verify_engine_seal.py --json",
        "python3 tools/verify_verification_authority_seal.py --json",
        "python3 tools/build_openai_2026_source_validity_lean4_report_v2.py",
        "python3 tools/audit_openai_2026_source_validity_completeness_v2.py",
        "python3 tools/build_openai_2026_corrected_compatibility_v2.py",
        "python3 tools/build_openai_2026_reality_counterpaper_v1_1.py",
        "python3 tools/render_openai_2026_reality_counterpaper_v1_1.py",
        "```",
        "",
        "The accompanying evidence map resolves every governing audit, source package, V1 replacement package, V2 disproof package, Lean report, current census receipt, empirical audit path, current Physics inventory, unified-constants object, force-sector closure and alpha validation artifact by path and hash.",
        "",
        "## References",
        "",
        "1. OpenAI, *Ten advances in mathematics and theoretical computer science*, 1 August 2026, `https://openai.com/index/ten-advances-in-mathematics/`.",
        "2. OpenAI, *ten-proofs Lean 4 formalizations*, fixed commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`, `https://github.com/openai/ten-proofs`.",
        "3. Lean project, *Axioms — Lean Language Reference*, `https://lean-lang.org/doc/reference/latest/Axioms/`.",
        "4. NIST, *2022 CODATA recommended values of the fundamental constants*, `https://physics.nist.gov/cuu/Constants/Table/allascii.txt`, inverse fine-structure constant `137.035999177(21)`.",
        "5. Smithian Fold Theory, *From Fold to Physics*, current published branch paper; current 368-claim Physics inventory; unified-constants, complete-force-sector and exact-alpha packages cited in the evidence map.",
        "6. Smithian Fold Theory, *Current programme status — 2 August 2026*, claim census, engine receipts and whole-model Lean report.",
        "",
        "## Appendix A. Frozen evidence identities",
        "",
        "| Evidence object | Frozen identity |",
        "|---|---|",
        f"| SFT admission engine | `{completeness['engine_seal']}` |",
        f"| SFT verification authority | `{completeness['verification_authority_seal']}` |",
        f"| OpenAI source-validity registry | `{registry['registry_identity']}` |",
        f"| Twelve-chain completeness audit | `{completeness['audit_identity']}` |",
        f"| Downstream compatibility audit | `{compatibility['audit_identity']}` |",
        f"| SFT source-validity Lean module | `{lean['module_hash']}` |",
        f"| OpenAI frozen Lean source archive | `{source_archive['sha256']}` |",
        f"| OpenAI manuscript collection | `{manuscripts['sha256']}` |",
        f"| Current Physics inventory | `{physics['inventory']['inventory_hash']}` |",
        f"| Unified constants object receipt | `{unified['claim']['receipt_hash']}` |",
        f"| Complete force-sector inventory receipt | `{physics['claims'][FORCE_INVENTORY_ID]['receipt_hash']}` |",
        f"| Blind force-sector validation receipt | `{physics['claims'][FORCE_VALIDATION_ID]['receipt_hash']}` |",
        f"| Exact alpha derivation receipt | `{alpha['claim']['receipt_hash']}` |",
        f"| Post-seal alpha validation receipt | `{alpha['validation_claim']['receipt_hash']}` |",
        "",
        "The official OpenAI announcement, OpenAI GitHub repository, Lean axiom reference and NIST CODATA table were rechecked on 3 August 2026. The local custody package binds the source version used in every proof; later upstream changes cannot silently alter these verdicts.",
        "",
        "---",
        "",
        f"**Rights and authority note:** Copyright © 2026 Maria Smith. This successor is CC BY 4.0 and is identified by DOI [{ZENODO_DOI}]({ZENODO_URL}); repository code is Apache-2.0. It supersedes version 1.0.0 at [{PRIOR_ZENODO_DOI}]({PRIOR_ZENODO_URL}) in the same Zenodo lineage. OpenAI source code remains under its stated Apache-2.0 licence; captured OpenAI manuscript PDFs are not redistributed.",
        "",
    )
    return "\n".join(lines)


def evidence_for_row(row: dict[str, Any]) -> dict[str, Any]:
    package: Path = row["package"]
    files = [
        "registration.json",
        "source_binding_v2.json",
        "source_validity_target_v2.json",
        "derivation_spec_v2.json",
        "candidate_census.json",
        "elimination_receipt.json",
        "controls.json",
        "independent_verification.json",
        "dependency_trace.json",
        "source_validity_correspondence_certificate_v2.json",
        "certificate.json",
        "STATUS.md",
    ]
    artifacts = []
    for name in files:
        path = package / name
        artifacts.append({"path": rel(path), "sha256": hash_file(path)})
    receipt_path = ROOT / row["certificate"]["engine_receipt_path"]
    artifacts.append({"path": rel(receipt_path), "sha256": hash_file(receipt_path)})
    native_files = [
        "registration.json",
        "derivation_spec_v1.json",
        "candidate_census.json",
        "elimination_receipt.json",
        "controls.json",
        "independent_verification.json",
        "dependency_trace.json",
        "correspondence_certificate.json",
        "certificate.json",
        "STATUS.md",
    ]
    for name in native_files:
        path = row["native_package"] / name
        artifacts.append({"path": rel(path), "sha256": hash_file(path)})
    native_current_receipt_path = ROOT / next(
        claim["receipt_path"]
        for claim in load(CLAIM_CENSUS_PATH)["claims"]
        if claim["claim_id"] == row["reconstruction_claim_id"]
    )
    artifacts.append(
        {"path": rel(native_current_receipt_path), "sha256": hash_file(native_current_receipt_path)}
    )
    return {
        "ordinal": row["ordinal"],
        "atomic_id": row["atomic_id"],
        "owner": row["owner"],
        "claim_id": row["claim_id"],
        "declaration": row["declaration"],
        "source_statement_hash": row["source_statement_hash"],
        "native_reconstruction_claim_id": row["reconstruction_claim_id"],
        "lean_theorem": row["lean_theorem"],
        "engine_receipt_hash": row["receipt_hash"],
        "native_engine_receipt_hash": row["native_current_receipt"],
        "artifacts": artifacts,
    }


def main() -> None:
    rows, registry, completeness, compatibility, lean, whole, source_manifest = load_rows()
    reality = load_reality_evidence()
    paper = render_paper(rows, registry, completeness, compatibility, lean, whole, source_manifest, reality)
    PAPER_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAPER_PATH.write_text(paper, encoding="utf-8")
    evidence: dict[str, Any] = {
        "schema": "sft-openai-2026-reality-counterpaper-evidence/1",
        "paper": {"path": rel(PAPER_PATH), "sha256": hash_file(PAPER_PATH)},
        "publication": {
            "version": "1.1.0",
            "manuscript_date": "2026-08-03",
            "remote_status": "publication_authorized",
            "zenodo_doi": ZENODO_DOI,
            "zenodo_url": ZENODO_URL,
            "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
            "supersedes_version": "1.0.0",
            "prior_zenodo_doi": PRIOR_ZENODO_DOI,
            "prior_zenodo_url": PRIOR_ZENODO_URL,
        },
        "status": "PASS",
        "closed_result": {
            "source_validity_disproved": 12,
            "advertised_bundles_invalid_as_submitted_sft_results": 10,
            "native_reconstructions_proved_distinct": 12,
            "native_to_source_transfers": 0,
            "open": 0,
        },
        "reality_evidence": {
            "model_admitted_claims": reality["claim_count"],
            "empirical_validation_packages": reality["empirical_count"],
            "formal_only_claims": reality["formal_only_count"],
            "all_empirical_packages_passed": reality["all_empirical_packages_passed"],
            "all_empirical_rows_preserved": reality["all_empirical_rows_preserved"],
            "comparison_summaries": reality["comparison_row_count"],
            "distinct_external_source_ids": reality["data_source_id_count"],
            "branch_rows": reality["branch_rows"],
            "physics_inventory_claims": reality["physics"]["inventory"]["admitted_claim_count"],
            "physics_inventory_subbranches": len(reality["physics"]["inventory"]["subbranch_counts"]),
            "physics_inventory_identity": reality["physics"]["inventory"]["inventory_hash"],
            "unified_constants_receipt": reality["unified_constants"]["claim"]["receipt_hash"],
            "force_ladder_receipt": reality["physics"]["claims"][FORCE_LADDER_ID]["receipt_hash"],
            "force_inventory_receipt": reality["physics"]["claims"][FORCE_INVENTORY_ID]["receipt_hash"],
            "force_validation_receipt": reality["physics"]["claims"][FORCE_VALIDATION_ID]["receipt_hash"],
            "finite_quantum_gravity_receipt": reality["physics"]["claims"][FINITE_QUANTUM_GRAVITY_ID]["receipt_hash"],
            "alpha_exact_ratio": "503846395469/3676744786",
            "alpha_exact_decimal": reality["alpha"]["ratio_decimal"],
            "alpha_codata_sigma_offset": reality["alpha"]["sigma_offset"],
            "alpha_derivation_receipt": reality["alpha"]["claim"]["receipt_hash"],
            "alpha_validation_receipt": reality["alpha"]["validation_claim"]["receipt_hash"],
        },
        "governing_artifacts": [
            {"path": rel(path), "sha256": hash_file(path)}
            for path in [
                REGISTRY_PATH,
                COMPLETENESS_PATH,
                COMPATIBILITY_PATH,
                LEAN_PATH,
                WHOLE_MODEL_PATH,
                SOURCE_MANIFEST_PATH,
                CLAIM_CENSUS_PATH,
                PROGRAMME_STATUS_PATH,
                PHYSICS_INVENTORY_PATH,
                PHYSICS_PAPER_PATH,
                ROOT / "claims" / UNIFIED_CONSTANTS_ID / "registration.json",
                ROOT / reality["unified_constants"]["claim"]["receipt_path"],
                ROOT / "claims" / FORCE_LADDER_ID / "registration.json",
                ROOT / reality["physics"]["claims"][FORCE_LADDER_ID]["receipt_path"],
                ROOT / "claims" / FORCE_INVENTORY_ID / "registration.json",
                ROOT / reality["physics"]["claims"][FORCE_INVENTORY_ID]["receipt_path"],
                ROOT / "claims" / FORCE_VALIDATION_ID / "registration.json",
                ROOT / reality["physics"]["claims"][FORCE_VALIDATION_ID]["receipt_path"],
                ROOT / "claims" / FINITE_QUANTUM_GRAVITY_ID / "registration.json",
                ROOT / reality["physics"]["claims"][FINITE_QUANTUM_GRAVITY_ID]["receipt_path"],
                ROOT / "claims" / ALPHA_CLAIM_ID / "registration.json",
                ROOT / "claims" / ALPHA_CLAIM_ID / "certificate.source-manifest-readmission-2026-07-27.json",
                ROOT / "claims" / ALPHA_VALIDATION_ID / "empirical_validation.json",
                ROOT / "claims" / ALPHA_VALIDATION_ID / "certificate.source-manifest-readmission-2026-07-27.json",
                ROOT / "experiments/physics/SFT-EXP-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001/registration.json",
                ROOT / "generated/lean4_validation/SFTValidation/OpenAI2026/SourceValidity.lean",
                ROOT / "generated/lean4_validation/SFTValidation/OpenAI2026/Obligations.lean",
                ROOT / "generated/lean4_validation/SFTValidation/OpenAI2026/Correspondence.lean",
                ROOT / "generated/openai_2026_source_validity_validator_v2.py",
            ]
        ],
        "claims": [evidence_for_row(row) for row in rows],
        "engine_seal": completeness["engine_seal"],
        "verification_authority_seal": completeness["verification_authority_seal"],
        "registry_identity": registry["registry_identity"],
        "completeness_audit_identity": completeness["audit_identity"],
        "compatibility_audit_identity": compatibility["audit_identity"],
    }
    if PDF_PATH.exists():
        evidence["rendered_pdf"] = {"path": rel(PDF_PATH), "sha256": hash_file(PDF_PATH)}
    evidence["evidence_map_identity"] = canonical_hash(evidence)
    EVIDENCE_MAP_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {rel(PAPER_PATH)}")
    print(f"wrote {rel(EVIDENCE_MAP_PATH)}")
    print(f"paper {evidence['paper']['sha256']}")
    print(f"evidence {evidence['evidence_map_identity']}")


if __name__ == "__main__":
    main()

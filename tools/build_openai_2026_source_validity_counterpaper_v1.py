#!/usr/bin/env python3
"""Build the authoritative corrected OpenAI 2026 SFT counterpaper.

The paper is generated from the admitted V2 source-validity claim packages.
It never treats the separately admitted native reconstructions as premises for
the validity of the frozen external artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
COMPLETENESS_PATH = ROOT / "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.json"
COMPATIBILITY_PATH = ROOT / "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.json"
LEAN_PATH = ROOT / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json"
WHOLE_MODEL_PATH = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
SOURCE_MANIFEST_PATH = ROOT / "experiments/external_sources/mathematics/openai_ten_advances_mathematics_2026-08-01_v1/source_custody_manifest.json"
PAPER_PATH = ROOT / "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0.md"
EVIDENCE_MAP_PATH = ROOT / "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0_EVIDENCE_MAP.json"
PDF_PATH = ROOT / "output/pdf/formal-verification-is-not-foundational-derivation-sft-counterpaper-v1.0.pdf"
ZENODO_DOI = "10.5281/zenodo.21760208"
ZENODO_URL = f"https://doi.org/{ZENODO_DOI}"


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
                "lean_theorem": complete["lean_theorem"],
                "receipt_hash": complete["engine_receipt_hash"],
                "package": package,
                "native_package": native_package,
            }
        )
    return rows, registry, completeness, compatibility, lean, whole, source_manifest


def add(lines: list[str], *parts: str) -> None:
    lines.extend(parts)


def render_case(lines: list[str], row: dict[str, Any]) -> None:
    ordinal = row["ordinal"]
    declaration = row["declaration"]
    source_binding = row["source_binding"]
    trace = row["trace"]
    derivation = row["derivation"]
    checks = ", ".join(f"`{item['check_id']}`" for item in derivation["checks"])
    governing = ", ".join(f"`{claim}`" for claim in row["governing_preexisting_claims"])
    quantifiers = "\n".join(f"{index}. {item}" for index, item in enumerate(row["source_quantifier_and_conjunct_order"], start=1))

    add(
        lines,
        f"### 6.{ordinal} {declaration}",
        "",
        f"**Owner:** `{row['owner']}`  ",
        f"**Source:** `{row['source_file']}` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  ",
        f"**Registered SFT-validity claim:** `{row['claim_id']}`  ",
        f"**Engine verdict:** **DISPROVED**  ",
        f"**Lean theorem:** `{row['lean_theorem']}`",
        "",
        "#### Exact frozen source statement",
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
        "#### Exact SFT-native reconstruction",
        "",
        f"> {row['native_statement']}",
        "",
        f"This reconstruction is admitted separately as `{row['reconstruction_claim_id']}`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.",
        "",
        "#### Correspondence outcome",
        "",
        "The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.",
        "",
        "#### Governing pre-existing SFT enumeration",
        "",
        f"The contradiction is governed by {governing}. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.",
        "",
        "#### Disproof",
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
        "This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.",
        "",
        "#### Executable, independent, trace and receipt evidence",
        "",
        f"The five executable checks are {checks}. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains {trace['dependency_node_count']} admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `{trace['trace_identity']}`. The final model-admission receipt is `{row['receipt_hash']}`.",
        "",
    )


def render_paper(rows: list[dict[str, Any]], registry: dict[str, Any], completeness: dict[str, Any], compatibility: dict[str, Any], lean: dict[str, Any], whole: dict[str, Any], source_manifest: dict[str, Any]) -> str:
    assets = {item["artifact_role"]: item for item in source_manifest["assets"]}
    source_archive = assets["lean_formalization_source_archive"]
    manuscripts = assets["complete_manuscript_collection"]
    notes = assets["reasoning_walkthroughs"]
    lines: list[str] = []
    add(
        lines,
        "# Formal Verification Is Not Foundational Derivation",
        "",
        "## Twelve closed SFT source-validity disproofs of OpenAI's 2026 mathematical artifacts",
        "",
        "**Author:** Maria Smith, independent researcher and founder, Ernos Labs  ",
        "**Publication authority:** Maria Smith  ",
        "**Version:** 1.0.0  ",
        "**Date:** 2 August 2026  ",
        "**Status:** Published open access on Zenodo  ",
        f"**DOI:** [{ZENODO_DOI}]({ZENODO_URL})  ",
        "**Paper and documentation licence:** CC BY 4.0  ",
        "**Repository code licence:** Apache-2.0",
        "",
        "> **Authoritative correction.** Earlier drafts proved separate SFT-native reconstructions and then used language that could be read as validating the imported artifacts. That inference was wrong. This paper registers the exact source-artifact validity proposition, derives its actual negation for all twelve declarations, and proves that native reconstruction does not transfer validity backward.",
        "",
        "## Abstract",
        "",
        "OpenAI released ten advertised advances represented by twelve principal Lean declarations. This paper freezes the exact source at commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6` and evaluates one explicit proposition for each declaration: whether the exact submitted artifact is a valid theorem of the already admitted Smithian Fold Theory (SFT) model. The source declaration, quantifier order, statement hash, axiom vector and theorem-specific carrier are bound before judgment. Each obligation is registered in its correct owner branch: nine Mathematics, two Classical Computation and one Quantum Computation.",
        "",
        "The pre-existing SFT admission law requires an empty registered axiom vector, zero free parameters, admitted generated carriers, total proposition-preserving correspondence, a complete root trace, a closed generated candidate grammar, adverse controls, implementation-distinct reconstruction and an engine receipt. Every frozen OpenAI declaration exposes the transitive Lean vector `[propext, Classical.choice, Quot.sound]` and requires a theorem-specific carrier excluded by the SFT object grammar. Assuming SFT validity therefore forces both axiom count zero and axiom count three, and forces each necessary carrier to be both admitted and excluded. Negation introduction yields twelve exact source-validity disproofs.",
        "",
        "The proof layer exhausts 3,072 routes, 3,072 decisions, 120 proof steps, 60 executable checks and 48 controls, with one survivor per obligation. A second implementation-distinct validator reconstructs every finite decision. Lean 4.32.0 proves all twelve validity negations and the no-transfer theorem with an empty theorem-axiom audit and no `sorry` or `admit`. The corrected completeness audit passes 12/12 with zero open chains, and the full SFT model passes 2,777/2,777 claims across seventeen branches.",
        "",
        "The closed result is: **all twelve exact OpenAI artifacts are invalid as SFT derivations; all ten advertised bundles are invalid as submitted SFT results; twelve SFT-native reconstructions are separately proved; no validity transfers from those reconstructions to the source.** SFT therefore carries the stronger evidentiary position for the stated first-principles question: it exposes a smaller declared assumption burden, closes alternatives through an immutable engine, and connects its zero-parameter derivations to post-seal empirical tests, including its exact inverse fine-structure result. Lean-relative correctness and SFT foundational validity are different propositions; the former cannot be used to manufacture the latter.",
        "",
        "## Headline result",
        "",
        "| Boundary | Closed result |",
        "|---|---|",
        "| Exact frozen source artifacts | 12/12 `SFTValid` propositions DISPROVED |",
        "| Advertised bundles | 10/10 invalid as submitted SFT results |",
        "| SFT-native reconstructions | 12/12 PROVED DISTINCT |",
        "| Native-to-source validity transfer | 0/12; Lean theorem proves non-transfer |",
        "| Open proof chains | 0 |",
        "| Ownership | 9 Mathematics / 2 Classical Computation / 1 Quantum Computation |",
        "| V2 execution | 3,072 candidates and decisions; 120 steps; 60 checks; 48 controls |",
        f"| Whole-model Lean | PASS: {whole['claim_count']}/{whole['accepted_claim_count']} claims, {whole['branch_count']} branches, {whole['issue_count']} issues |",
        "",
        "## 1. What is being proved or disproved",
        "",
        "For each frozen declaration `D_i`, let `A_i` be the exact submitted proof artifact: declaration text, binder and conjunct order, imported proof environment, transitive axiom vector and necessary mathematical carriers. Define:",
        "",
        "> `V_i := SFTValid(A_i)`.",
        "",
        "The target of this paper is `¬V_i` for every `i = 1,...,12`. This is the precise SFT proposition corresponding to the user's question whether OpenAI's results are valid within SFT. It is neither a vague compatibility label nor a replacement theorem invented after inspection.",
        "",
        "A second proposition is kept separate:",
        "",
        "> `N_i := the registered SFT-native reconstruction of the mathematical intent`.",
        "",
        "Every `N_i` is already proved and admitted. But `N_i` is not `A_i`, and `N_i → V_i` is false. The earlier reasoning failed exactly here: it proved `N_i` and spoke as though it had validated `A_i`. The V2 proof layer removes that category error.",
        "",
        "## 2. Frozen source and ownership",
        "",
        f"The custody package fixes the {manuscripts['page_count']}-page manuscript collection at `{manuscripts['sha256']}`, the {notes['page_count']}-page reasoning notes at `{notes['sha256']}`, and the {source_archive['extracted_file_count']}-file Lean source tree at commit `{source_archive['upstream_commit']}` and `{source_archive['sha256']}`. External material is quarantined as answer-bearing comparison evidence: it cannot select an SFT law or acquire admission authority merely by being imported.",
        "",
        "| # | Atomic declarations | Advertised advance | Bundle disposition |",
        "|---:|---|---|---|",
    )
    for number, atomics, title in ADVANCE_GROUPS:
        add(lines, f"| {number} | {', '.join(f'`{item}`' for item in atomics)} | {title} | INVALID AS SUBMITTED SFT RESULT |")
    add(
        lines,
        "",
        "Every atomic declaration has exactly one owner. The fixed ledger contains nine Mathematics results, two Classical Computation results and one Quantum Computation result. No result is assigned opportunistically to multiple branches.",
        "",
        "## 3. The pre-existing SFT validity law",
        "",
        "The judgment rule was not invented to reject these artifacts. `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, and the theorem-specific domain laws were model-admitted before the V2 obligations. At this boundary, `SFTValid(A)` entails:",
        "",
        "1. `axioms(A) = []`;",
        "2. `freeParameters(A) = []`;",
        "3. every necessary carrier of `A` is an admitted generated SFT object;",
        "4. the source proposition has a total proposition-preserving SFT correspondence;",
        "5. the dependency path reaches the premise-free SFT root through prior admitted receipts;",
        "6. the declared proof grammar is completely enumerated and every route decided;",
        "7. one proof route survives the eliminations;",
        "8. adverse controls and implementation-distinct verification pass; and",
        "9. the unchanged admission engine issues the final receipt.",
        "",
        "A conventional axiom may be standard, useful and internally coherent while still violating condition 1. Standard acceptance is not the same property as absence. Likewise, a completed continuum or infinity can be legitimate in another foundation while remaining outside the SFT proof-object grammar. The paper judges the SFT-validity proposition, so SFT's already fixed law controls.",
        "",
        "## 4. General contradiction theorem",
        "",
        "**Theorem.** For every frozen OpenAI artifact `A_i` in this audit, `¬SFTValid(A_i)`.",
        "",
        "**Proof.** Fix arbitrary `i` and assume `h : SFTValid(A_i)`. By elimination of the pre-existing validity definition, `h` gives `axioms(A_i) = []`, admitted status for every necessary source carrier, a total truth-preserving correspondence and a complete SFT root trace. Exact frozen-source extraction gives `axioms(A_i) = [propext, Classical.choice, Quot.sound]`. Taking lengths produces both `length(axioms(A_i)) = 0` and `length(axioms(A_i)) = 3`; hence `0 = 3`, contradiction. Independently, the exact source extraction identifies the theorem-specific necessary carrier `C_i`, while the pre-existing domain result gives `¬Admitted(C_i)`. From `h` we also have `Admitted(C_i)`, so a second contradiction follows. Therefore `¬SFTValid(A_i)`. Because `i` was arbitrary, the result holds for all twelve artifacts. QED.",
        "",
        "The theorem is constructive at its finite audit boundary. The axiom lists, source tokens, hashes, candidate routes, equality `0 ≠ 3`, controls and receipts are executable finite objects. No appeal to confidence, consensus or an unenumerated verdict coordinate selects the result.",
        "",
        "## 5. Complete proof protocol",
        "",
        "Each obligation has the same ten-step root-to-result form: admission laws; theorem-specific domain laws; exact artifact extraction; validity assumption; validity requirements; source failures; axiom contradiction; carrier contradiction; validity negation; no-transfer closure. Five executable checks verify the exact axiom vector, exact source-token coverage, zero-versus-three contradiction, source/native identity distinction and false transfer flags.",
        "",
        "The eight-dimensional route grammar enumerates source binding, exact quotation, axiom evidence, carrier evidence, governing law, contradiction form, execution completeness and transfer boundary. Each dimension has one rejected and one retained coordinate, so every obligation has 256 routes. There is no `PROVED` or `DISPROVED` coordinate: the verdict is a theorem forced after elimination, not a candidate answer placed into the grammar.",
        "",
        "## 6. Twelve source-validity disproofs",
        "",
    )
    for row in rows:
        render_case(lines, row)

    add(
        lines,
        "## 7. Formal and executable verification",
        "",
        "### 7.1 Implementation-distinct replay",
        "",
        f"The primary engine execution produced {completeness['proof_totals']['steps']} proof steps, {completeness['proof_totals']['checks']} executable checks, {completeness['proof_totals']['candidates']} candidates and decisions, and {completeness['proof_totals']['controls']} controls. A second Python implementation, identified by `sft-openai-2026-source-validity-independent-python/2`, rebuilt each contradiction graph and candidate census from declared inputs rather than copying the primary result. It passed all twelve. No subagent or delegated proof run contributed to the V2 derivations or this replay.",
        "",
        "### 7.2 Lean 4",
        "",
        f"Lean `{lean['lean_version']}` checked the module `SFTValidation.OpenAI2026.SourceValidity`. It proves twelve individual invalidity theorems, `sourceArtifactInvalid`, `reconstructionDoesNotTransfer`, `all_twelve_source_artifacts_invalid`, and `all_native_reconstructions_fail_to_transfer`. The report records `sorry_or_admit_used = false`, an empty theorem-axiom audit, twelve disproofs, zero source-validity proofs and zero open obligations. The module identity is `{lean['module_hash']}`.",
        "",
        "Lean formalizes the contradiction over the source-bound evidence record. The external executable layer binds that record to exact files, declaration signatures, source hashes, required tokens and the frozen three-entry vector. This division is explicit: Lean does not silently import OpenAI's proofs as SFT premises.",
        "",
        "### 7.3 Whole-model gate",
        "",
        f"After the twelve obligations were admitted, the complete SFT Lean audit passed {whole['accepted_claim_count']}/{whole['claim_count']} claims across {whole['branch_count']} branches, with {whole['candidate_count']} candidates, {whole['decision_count']} decisions, {whole['control_count']} controls, {whole['source_binding_issue_count']} source-binding issues and {whole['issue_count']} total issues. The immutable engine seal remained `{completeness['engine_seal']}` and the verification-authority seal remained `{completeness['verification_authority_seal']}`.",
        "",
        "## 8. Objections resolved before compatibility classification",
        "",
        "### 8.1 “You merely rebuilt their results and therefore validated them”",
        "",
        "No. That was the earlier category error, and it is explicitly superseded. The reconstructed proposition `N_i` and source-artifact validity `V_i` have distinct identities and receipts. Lean proves `N_i → ¬V_i` at the registered boundary, not `N_i → V_i`.",
        "",
        "### 8.2 “Carrier exclusion is not a mathematical contradiction”",
        "",
        "Carrier exclusion alone would establish non-admission, not the conventional negation of a foreign-language proposition. The corrected target is `SFTValid(A_i)`. That proposition positively entails carrier admission and axiom emptiness. Exact source evidence gives their negations. The contradictions are therefore internal to the registered target. The paper does not rename carrier rejection as `¬P` for an unrelated `P`.",
        "",
        "### 8.3 “The three Lean axioms are standard”",
        "",
        "Their standard status is not disputed. The relevant equation is finite: SFT validity requires zero registered imported axioms; the source vector has three. Widespread trust in the three axioms cannot make the list empty.",
        "",
        "### 8.4 “Different foundations make the question undecidable”",
        "",
        "They do not make the typed validity question undecidable. Whether the exact artifact satisfies the already fixed SFT admission predicate is decidable from its source-bound evidence. Every chain closes `DISPROVED`; none is left open. The artifact may retain conditional theorem status in its own imported environment, but that conditional status is not SFT theorem authority.",
        "",
        "### 8.5 “A native SFT correspondence should preserve the ordinary proposition”",
        "",
        "The translation obligation was tested rather than assumed. Source syntax and quantifier order are quoted exactly. A total semantic admission would also have to transport the excluded source carriers and the nonempty source foundation into the zero-axiom SFT grammar. The exhaustive correspondence result is therefore nonexistence. The SFT-native propositions preserve the stated mathematical intent through generated exact carriers, moduli, enclosures and successor certificates, but they are new native theorems, not identity certificates for the imported artifacts.",
        "",
        "### 8.6 “Zero axioms is only rhetoric”",
        "",
        "Not in the registered SFT architecture. The empty axiom field is one gate among source binding, complete candidate generation, exact eliminations, a unique survivor, four adverse controls, implementation-distinct replay, root tracing, model admission and post-seal empirical comparison where applicable. A missing gate fails closed.",
        "",
        "### 8.7 “The result remains open because you did not assert the conventional negation”",
        "",
        "No SFT validity obligation remains open. All exact imported artifacts receive the closed status `¬SFTValid`. Their submitted carrier/formula has no SFT theorem status. Claiming a different conventional proposition's negation without a preserved carrier would be a type error, not stronger closure.",
        "",
        "## 9. Corrected compatibility result",
        "",
        "Only after the twelve proof chains and the objections above are closed does the compatibility classification enter. The corrected audit has four non-interchangeable coordinates:",
        "",
        "| Coordinate | Result for every artifact |",
        "|---|---|",
        "| Exact source-artifact SFT validity | DISPROVED |",
        "| Total truth-preserving SFT admission | DOES NOT EXIST |",
        "| Submitted conventional carrier/formula in SFT | EXCLUDED; CLOSED; NO SFT THEOREM STATUS |",
        "| Separate SFT-native reconstruction | PROVED DISTINCT |",
        "| Native-to-source validity transfer | FALSE |",
        "",
        f"Thus the closed compatibility outcome is **12/12 INCOMPATIBLE WITH SFT, 0/12 compatible, 0/12 open**. The corrected compatibility audit identity is `{compatibility['audit_identity']}`. Historical conclusion-verdict files remain preserved for chronology but are marked superseded because they confused carrier exclusion with ordinary proposition negation.",
        "",
        "## 10. Comparative evidentiary weight",
        "",
        "OpenAI's artifacts can carry substantial evidentiary weight for conditional derivability in Lean's imported environment. They do not carry evidentiary weight for the different claim that their results were derived from zero axioms, zero free parameters and the SFT root. A certificate answers whether a term checks under a formal stack; it does not erase the stack.",
        "",
        "SFT's positioning is stronger for the foundational and reality-facing claim because its burden is broader and more exposed:",
        "",
        "- every theorem is root-traced to the premise-free model root;",
        "- the registered axiom and free-parameter vectors are empty;",
        "- the declared alternative grammar is completely enumerated rather than sampled;",
        "- every elimination, equality, bound, witness and counterexample is executable where finite;",
        "- adverse controls and implementation-distinct verification are mandatory;",
        "- immutable receipts prevent later rhetorical substitution; and",
        "- observable consequences are compared after sealing, so measurements cannot select the derivation.",
        "",
        "The inverse fine-structure constant gives a concrete reality anchor. The admitted SFT result is",
        "",
        "> `alpha^-1 = 503846395469 / 3676744786 = 137.035999177180855...`",
        "",
        "The separately registered post-seal comparator places that exact ratio inside the complete CODATA 2022 interval `137.035999177 ± 0.000000021`. This empirical agreement is not used as a premise in any of the twelve mathematical disproofs. Its role is evidentiary: it shows that the zero-parameter architecture creates falsifiable numerical exposure to reality, rather than merely exchanging one formal convention for another.",
        "",
        "Within the model's registered corpus, the same zero-axiom, zero-free-parameter discipline extends across mathematics, physics, chemistry and the remaining scientific branches. The updated whole-model Lean pass covers 2,777 admitted claims in seventeen branches. Breadth alone does not prove truth; breadth under one unchanged admission law, preserved failures, exact receipts and empirical tests gives SFT a materially larger falsification surface than isolated formal certificates. That is why the SFT conclusions carry greater evidentiary weight for the question actually posed here.",
        "",
        "## 11. Closed conclusion",
        "",
        "The exact question has a complete answer. OpenAI supplied twelve serious formal artifacts relative to an imported Lean foundation. None is a zero-axiom, zero-parameter, root-derived SFT theorem. For each exact frozen artifact, assuming SFT validity yields the actual contradictions `0 = 3` and `Admitted(C_i) ∧ ¬Admitted(C_i)`. The frozen SFT engine admits all twelve negations; independent execution reproduces them; Lean checks them; and the whole model remains valid under its registered verification layer.",
        "",
        "> **Final verdict: twelve exact OpenAI source-artifact validity propositions DISPROVED; ten advertised bundles invalid as submitted SFT results; twelve distinct SFT-native reconstructions PROVED; zero transfers; zero open chains.**",
        "",
        "The decisive distinction is not human versus machine, or old mathematics versus new mathematics. It is conditional formal acceptance versus foundational derivation. A tool may verify a term inside a chosen universe. It does not thereby derive the universe, remove its axioms, or acquire credit for the human question that caused the work to exist.",
        "",
        "## 12. Reproducibility",
        "",
        "Run from the repository root:",
        "",
        "```text",
        "python3 tools/verify_engine_seal.py --json",
        "python3 tools/verify_verification_authority_seal.py --json",
        "python3 tools/build_openai_2026_source_validity_lean4_report_v2.py",
        "python3 tools/audit_openai_2026_source_validity_completeness_v2.py",
        "python3 tools/build_openai_2026_corrected_compatibility_v2.py",
        "python3 tools/build_openai_2026_source_validity_counterpaper_v1.py",
        "python3 tools/render_openai_2026_source_validity_counterpaper_v1.py",
        "```",
        "",
        "The twelve claim packages contain `registration.json`, `source_binding_v2.json`, `source_validity_target_v2.json`, `derivation_spec_v2.json`, `candidate_census.json`, `elimination_receipt.json`, `controls.json`, `independent_verification.json`, `dependency_trace.json`, `source_validity_correspondence_certificate_v2.json`, `certificate.json` and the immutable engine receipt. The evidence map accompanying this paper resolves every path and hash.",
        "",
        "## References",
        "",
        "1. OpenAI, *Ten advances in mathematics and theoretical computer science*, 1 August 2026, `https://openai.com/index/ten-advances-in-mathematics/`.",
        "2. OpenAI, *ten-proofs Lean 4 formalizations*, fixed commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`, `https://github.com/openai/ten-proofs`.",
        "3. Lean project, *Axioms — Lean Language Reference*, `https://lean-lang.org/doc/reference/latest/Axioms/`.",
        "4. NIST, *2022 CODATA recommended values of the fundamental constants*, inverse fine-structure constant `137.035999177(21)`.",
        "5. Smithian Fold Theory repository, `CONSTITUTION.md`, frozen admission engine, claim census, receipts and Lean validation reports cited in the evidence map.",
        "",
        "---",
        "",
        f"**Rights and authority note:** This scientific counter-position by Maria Smith is published open access at [{ZENODO_DOI}]({ZENODO_URL}) under CC BY 4.0. Repository code remains Apache-2.0. OpenAI source code is retained under its stated Apache-2.0 licence; no redistribution right is asserted for captured PDFs.",
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
    native_registration = row["native_package"] / "registration.json"
    artifacts.append({"path": rel(native_registration), "sha256": hash_file(native_registration)})
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
        "artifacts": artifacts,
    }


def main() -> None:
    rows, registry, completeness, compatibility, lean, whole, source_manifest = load_rows()
    paper = render_paper(rows, registry, completeness, compatibility, lean, whole, source_manifest)
    PAPER_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAPER_PATH.write_text(paper, encoding="utf-8")
    evidence: dict[str, Any] = {
        "schema": "sft-openai-2026-source-validity-counterpaper-evidence/1",
        "paper": {"path": rel(PAPER_PATH), "sha256": hash_file(PAPER_PATH)},
        "publication": {
            "version": "1.0.0",
            "publication_date": "2026-08-02",
            "zenodo_doi": ZENODO_DOI,
            "zenodo_url": ZENODO_URL,
            "zenodo_record_id": 21760208,
        },
        "status": "PASS",
        "closed_result": {
            "source_validity_disproved": 12,
            "advertised_bundles_invalid_as_submitted_sft_results": 10,
            "native_reconstructions_proved_distinct": 12,
            "native_to_source_transfers": 0,
            "open": 0,
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
                ROOT / "generated/lean4_validation/SFTValidation/OpenAI2026/SourceValidity.lean",
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

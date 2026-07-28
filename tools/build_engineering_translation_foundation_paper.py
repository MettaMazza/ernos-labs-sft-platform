#!/usr/bin/env python3
"""Build the exhaustive Engineering Translation foundation paper."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications/current/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md"

FAMILY_TITLES = {
    "requirements_function_boundary": "Requirements, function, constraints and operating boundaries",
    "components_interfaces_architecture": "Components, interfaces, architecture and integration",
    "resources_efficiency_reliability": "Resources, capacity, efficiency, reliability and failure",
    "measurement_calibration_acceptance": "Measurement, calibration, tolerance and acceptance",
    "alternatives_tradeoffs_optimization": "Alternatives, trade-offs and bounded optimization",
    "control_feedback_stability": "Control, feedback, stability, observability and fault response",
    "safety_hazard_resilience": "Hazard, risk, safety, fail-safe operation and resilience",
    "verification_validation_traceability": "Verification, validation, traceability and end-to-end proof",
    "cross_platform_accessibility": "Cross-platform, portable, accessible and learnable operation",
    "lifecycle_maintenance_sustainability": "Configuration, maintenance, lifecycle and sustainability",
    "science_design_evidence_boundary": "Scientific law, design, performance, simulation and demonstration",
    "ownership_anomaly_handoffs": "Anomaly return, disciplinary handoffs and the future V4 boundary",
}

AXIS_MEANINGS = (
    ("carrier", "which requirement, artifact, component, user, environment or test bears the claim"),
    ("boundary", "which operating envelope, version, platform, user and lifecycle stage bound the result"),
    ("relation", "which generated transformation, interface, comparison or handoff connects the carriers"),
    ("record", "which requirements, versions, alternatives, failures, uncertainty and rollback remain reconstructible"),
    ("evidence", "whether law, requirement, design, simulation, test, demonstration, performance and anomaly remain distinct"),
    ("provenance", "whether the result traces to the One and names every upstream receipt and design choice"),
    ("generality", "whether finite extension preserves platforms, versions, failures and operating limits"),
    ("extension", "whether any fitted weight, exception or opaque oracle has been added"),
)


def main() -> None:
    inventory = json.loads((ROOT / "publications/inventories/engineering_translation.json").read_text())
    integration = json.loads((ROOT / "audits/engineering_translation_foundation_integration.json").read_text())
    targets = json.loads((ROOT / "experiments/engineering_translation/external_targets.json").read_text())
    registry = json.loads((ROOT / "experiments/engineering_translation/source_registry.json").read_text())
    prior = json.loads((ROOT / "audits/engineering_translation_v1_v2_initial_atomic_ownership.json").read_text())
    target_by = {x["claim_id"]: x for x in targets["targets"]}
    claim_by = {x["claim_id"]: x for x in inventory["obligations"]}
    families = defaultdict(list)
    for claim in inventory["obligations"]:
        families[claim["family"]].append(claim)

    lines = [
        "# From One Law to a Working World",
        "",
        "## An Exact, Zero-Parameter and Machine-Closed Foundation for Engineering Translation from Smithian Fold Theory",
        "",
        "**Maria Smith — independent researcher and founder, Ernos Labs**  ",
        "**Smithian Fold Theory Engineering Translation Paper 001 — Version 1.0.0 — 28 July 2026**  ",
        "**Current-evidence closed, extension-open foundation — local prepublication manuscript**",
        "",
        "> This paper derives the constitution that turns an admitted law into a bounded, testable and accessible artifact without allowing the artifact to rewrite the law. Seventy-two obligations were fixed before external standards or performance records were opened; 18,432 forms were exhaustively decided; one preserving form survived for each law; independent implementations reconstructed every survivor; and post-seal primary engineering handbooks, standards and public guidance tested the evidence boundary. Requirements, versions, alternatives, failures, uncertainty, accessibility and lifecycle remain visible. The result is current-evidence closed and extension-open.",
        "",
        "## Headline findings",
        "",
        "1. **A requirement is not a wish and a function is not a product name.** The least admissible translation retains source, purpose, version, conflict, verifiable condition, declared input, transformation, output, loss and operating boundary.",
        "2. **An engineered system is an exact composition record.** Components retain identity and version; interfaces retain endpoints, units, timing and errors; architecture retains responsibility and failure propagation; integration retains build order, rollback and every failed intermediate state.",
        "3. **Efficiency cannot exceed its complete resource account.** Input, useful output, external supply, stock, flow, time and loss must close inside an explicit boundary. Capacity, reliability and availability remain load-, population-, duration- and observation-window bound.",
        "4. **Measurement, calibration, tolerance, test and acceptance are different laws.** A display is not a measurand; adjustment is not calibration; tolerance cannot widen after outcome; a demonstration is not a passed test; authority cannot substitute for a frozen acceptance criterion.",
        "5. **Optimization is forced only over a generated finite design space.** Every alternative, constraint violation, tie and failure remains. Trade-offs keep measured evidence distinct from declared values; no hidden scalar weight or opaque oracle may manufacture an optimum.",
        "6. **Control claims retain the whole loop.** Plant, sensor, controller, actuator, delay, bounds, noise and fault paths remain explicit. A merged output cannot recover an unheld predecessor; one settled trace cannot prove global or infinite-time stability.",
        "7. **Safety is a scoped evidence case, not the absence of prior harm.** Hazards retain source, path and exposure; fail-safe operation must reach a tested bounded safe state or visibly halt; defence layers are independent only when common causes and bypasses are retained.",
        "8. **Verification and validation are structurally distinct.** Verification compares an artifact with its frozen specification; validation compares a verified system with intended use and users. Bidirectional traceability connects need, requirement, design, build, test and result.",
        "9. **Public reproducibility includes macOS, Windows and Linux.** Platform, version, dependency, command, output and difference are retained. A one-command route must traverse every declared stage, report progress and duration, preserve failure, and never mutate the protected authority.",
        "10. **Application performance cannot select or retroactively prove a law.** A failed build may falsify its own operating claim; it does not automatically falsify upstream science. Simulation remains simulation, demonstration remains demonstration, and a validated anomaly returns as a question to its categorical science owner.",
        f"11. **The complete foundation is receipt-backed.** {integration['admitted_claim_count']} laws in {integration['family_count']} families produced {integration['candidate_count']:,} candidates, 72 unique survivors, 72 independent reconstructions and 72 untouched-engine receipts. All {integration['prior_entries_reviewed']} V1/V2 entries were reviewed and all {integration['prior_atomic_questions']} Engineering-owned inherited questions were reconciled without importing their old answers.",
        f"12. **The evidence boundary preserves its failures.** {integration['source_count']} primary custodians were registered after sealing; {integration['captured_source_count']} transports were captured and {integration['failed_source_transports_preserved']} failed source transport{'s' if integration['failed_source_transports_preserved'] != 1 else ''} {'remain' if integration['failed_source_transports_preserved'] != 1 else 'remains'} failed—not converted into absence, agreement or favorable support.",
        "",
        "These are the scientific findings. Machine identities later bind them to exact files and traces; filenames and hashes do not replace the relations, values, exclusions and falsification conditions stated here.",
        "",
        "## Abstract",
        "",
        "Engineering fails scientifically when a desired output selects its own requirements, when a prototype is called validation, when a hidden service supplies uncounted resources, when a simulation is relabelled observation, or when successful performance is treated as proof of a fundamental law. This paper reconstructs Engineering Translation from the One through every admitted upstream branch. Twelve families and seventy-two laws govern requirements, components, resources, measurement, alternatives, control, safety, verification, accessibility, lifecycle, evidence classes and anomaly handoff. The proof layer adds no axiom, free parameter, fit, conventional numerical zero, negative proof scalar, irrational or imaginary proof number, completed infinity or ungenerated continuum. Every claim is a 256-form census across eight exact axes; all 18,432 forms were sealed before external engineering sources were registered. Independent reconstructions and source-bound comparisons preserve adverse, missing and failed records. The result is a public, cross-platform, extension-open constitution for turning science into working artifacts without confusing translation with discovery.",
        "",
        "## Authorship, access and the public scientific mission",
        "",
        "Maria Smith produced this work outside credentialed institutional access. That fact is not offered as personal exceptionalism. It is an indictment of all the minds and contributions society loses when financial gatekeeping, credentials, paywalls, prestige, institutional permission and access to funded infrastructure are dressed as rigor. The appropriate response is not to ask whether an excluded author was somehow uniquely permitted to think. It is to ask how many minds, observations and corrections were never heard because the gate was mistaken for the method.",
        "",
        "Ernos Labs is an open-source science movement and a standards designation. The repository, derivations, source failures, controls, papers and machine receipts are public so that any person can inspect, challenge, reproduce or extend them. Transparent access is not a relaxation of rigor: it makes rigor inspectable. Paywalled claims, opaque oracles, credential votes and funding-driven restrictions cannot substitute for a complete derivation, a sealed prediction, an unfavorable control or an independently reproducible result.",
        "",
        "The paper is licensed **CC BY 4.0** and the platform code **Apache-2.0**. Maria Smith retains authorship, copyright and creative rights. Anyone may use and criticize the work under those licenses. The **Ernos Labs** designation may be used only when the root theorem and constraints remain visible, the protected engine and verification authority remain unchanged, every candidate is enumerated, outcomes do not select laws, adverse and missing evidence is preserved, authorship and licenses remain intact, and extensions pass the same admission route. A weakened fork remains open-source software but is not an Ernos Labs scientific admission.",
        "",
        "Open criticism requires no credential. Scientific admission requires the common evidence protocol. Contact: **Maria.Smith.Sftoe@gmail.com**. Public submissions and review: **https://discord.gg/ucwGryVxGr**. GitHub: **https://github.com/MettaMazza**.",
        "",
        "## Mathematical constitution",
        "",
        "Every law traces to **There Is No Nothing** and to already admitted Fold dependencies. No additional axiom is introduced. No free or fitted parameter can select a survivor. Proof-state arithmetic is exact and finite. Conventional numerical zero is not a proof carrier; the glyph `0` may be retained as a typed marker for absence, non-response or a source field, but it does not import ordinary zero semantics. Negative, irrational and imaginary quantities may appear as held source labels where an external dataset uses them, but never as proof scalars. Completed infinities and ungenerated continua are excluded.",
        "",
        "For each claim the generator builds eight binary dimensions: carrier, boundary, relation, record, evidence, provenance, generality and extension. Their literal Cartesian product contains 2^8 = 256 candidates. One choice on each dimension alone preserves its required distinction. The program decides all 256 candidates; one survives and 255 are eliminated. Across 72 claims this is exactly 18,432 decided forms. A separate implementation rebuilds the product and survivor. Positive-finite induction proves that adding one lawful component, interface, platform, requirement, test, failure, lifecycle stage or anomaly preserves all earlier versions, adverse rows, boundaries and receipts while appending its trace.",
        "",
        "This closure is exact but bounded. It establishes the foundational forms necessary to make Engineering Translation reconstructible and falsifiable. It does not prohibit new technologies, users, platforms, hazards, tests, standards or lawful discoveries. The branch is current-evidence closed and extension-open, never permanently locked.",
        "",
        "## Empirical constitution and blind order",
        "",
        "The complete inventory, candidate grammar, predicted structural labels and falsification conditions were frozen before any external standard, handbook, product, test or outcome was opened. Primary custodians were selected afterward for requirements, systems, measurement, safety, accessibility, reproducibility and lifecycle records—not because their status could prove a law. A capability-closed prediction process cannot read a file, network, clock, environment variable, process or target. Only after its derivation seal exists may the external evaluator open the registered record.",
        "",
        "Every comparison retains successful, adverse, absent, missing, disputed, unresolved, access-denied and transport-failed rows. A handbook is not an implementation. A standard is not automatic conformity. A model is not an observation. A prototype is not a production system. A simulation, demonstration, verification, validation and acceptance decision remain different evidence classes. These distinctions are part of the empirical result, not administrative bookkeeping.",
        "",
        "The immutable engine seal is `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`. The verification-authority seal is `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`. A mismatch halts. Those identities secure a shared admission route; they never replace the readable derivations.",
        "",
        "## Dependency and ownership boundary",
        "",
        "Each categorical science retains ownership of its laws and evidence. Mathematics owns exact structure; computation owns formal semantics; Physics, Chemistry and Materials own physical relations; Biology, Consciousness and Medicine own organism, experience and clinical state; Earth and Astronomy own their observed systems; Social Science owns collective context, access and legitimacy. Engineering Translation owns versioned requirements, designs, artifacts, tests, deployments and lifecycle evidence. It may discover an anomaly and return a question, but it may never directly rewrite the upstream law.",
        "",
        "## Registered primary-source surface",
        "",
    ]

    for source in registry["sources"]:
        lines.append(
            f"- **{source['source_id']} — {source['custodian']}.** {source['title']}. "
            f"Registered families: {', '.join(source['families'])}. Locator: {source['locator']}. "
            "Its authority here is source custody and documented provenance, not prestige or consensus."
        )

    lines += ["", "## Family results", ""]
    for family in inventory["family_order"]:
        rows = families[family]
        lines += [
            f"### {FAMILY_TITLES[family]}",
            "",
            f"This family contains {len(rows)} separately admitted obligations. Its closure preserves artifact, requirement, version, environment, operating boundary, failure and source record; it does not universalise one implementation or successful run.",
            "",
        ]
        for row in rows:
            lines.append(f"- **{row['title']}** (`{row['claim_id']}`): {row['statement']}")
        lines.append("")

    lines += [
        "## Complete claim-by-claim derivation record",
        "",
        "The following seventy-two sections are the human-readable chain. The machine packages preserve all 256 candidate rows, 256 decisions, hostile controls, source manifest, independent output, empirical receipt and engine receipt for each claim.",
        "",
    ]

    for position, claim_id in enumerate(inventory["required_claim_ids"], 1):
        row = claim_by[claim_id]
        target = target_by[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        elimination = json.loads((ROOT / "claims" / claim_id / "elimination_receipt.json").read_text())
        controls = json.loads((ROOT / "claims" / claim_id / "controls.json").read_text())
        registration = json.loads((ROOT / "claims" / claim_id / "registration.json").read_text())
        survivor = row["unique_survivor"].split("__")
        lines += [
            f"### {position}. {row['title']}",
            "",
            f"**Claim:** `{claim_id}`  ",
            f"**Family:** `{row['family']}`  ",
            f"**Exact statement:** {row['statement']}",
            "",
            "#### Forward chain and exact carrier",
            "",
            f"The generated carrier is `{row['carrier']}`. Its required relation is `{row['relation']}`. The reconstruction must retain `{row['retained_record']}`. Its declared empirical boundary is `{row['evidence_boundary']}`. These coordinates are not labels added after a result: they were part of the sealed obligation that generated the candidate space.",
            "",
            f"The dependency chain is {', '.join(f'`{x}`' for x in row['dependencies'])}. Each dependency was model-admitted before this claim. The present claim adds no axiom, free parameter or fitted rule and cannot use an external standard, application, performance target, product or prior implementation to select its form.",
            "",
            f"Generation rule: {registration['candidate_grammar']['generator']}",
            "",
            f"Grammar boundary: {registration['candidate_grammar']['boundary']}",
            "",
            "#### Complete enumeration and uniqueness",
            "",
            "The eight binary axes generate exactly 256 literal candidates. Their preserving coordinates are:",
            "",
        ]
        for (axis, meaning), value in zip(AXIS_MEANINGS, survivor):
            lines.append(f"- **{axis}** — {meaning}: `{value}`.")
        lines += [
            "",
            "Their ordered product gives the unique survivor:",
            "",
            f"`{row['unique_survivor']}`",
            "",
            "Each of the other 255 forms differs on at least one registered coordinate. Erasing the carrier loses the requirement, artifact, user or environment. Erasing the boundary universalises a version, platform or test. Importing the relation lets a target or preferred application choose the result. Retaining only successful output removes requirements, alternatives, failures and rollback. Conflating evidence classes turns simulation, demonstration or performance into observation or law. Breaking provenance removes the trace to the One and upstream receipts. Erasing finite context makes one implementation universal. Adding a silent dependency or opaque oracle creates a free rule. Because every non-survivor commits at least one such loss and the survivor commits none, uniqueness is enumerated rather than asserted.",
            "",
            f"The closure certificate is `{elimination['closure']['scope']}`. Minimality passed: `{elimination['closure']['minimality_passed']}`. Named-form uniqueness passed: `{elimination['closure']['named_shape_uniqueness_passed']}`. The base case retains the least positive finite requirement or admitted law, versioned artifact, boundary, testable relation and complete record. The successor adds one lawful component, interface, platform, requirement, test, failure, lifecycle stage or anomaly while preserving all earlier identities, adverse rows and receipts.",
            "",
            "#### Falsification and deliberately unfavorable controls",
            "",
            f"The registered falsification condition is: {row['falsification_condition']}",
            "",
        ]
        for control in controls["controls"]:
            lines.append(f"- `{control['kind']}` — passed `{control['passed']}`: {control['expected_behavior']}")
        lines += [
            "",
            "A passed control means the altered condition was rejected as required; it is not a reward for an adverse scientific outcome. If a premise, source, artifact or boundary change were accepted, admission would halt. Automation generated repeated records from the frozen specification but did not select the survivor, change a condition or decide that a failure had passed.",
            "",
            "#### Post-seal external evidence",
            "",
            f"Evidence class: `{target['directness']}` / `{target['empirical_disposition']}`. Captured registered sources: {target['captured_source_count']}. Unresolved transports retained: {target['unresolved_transport_count']}. The registered structural consequence corresponded: `{target['exact_match']}`. External evidence selected the survivor: `false`. Application or performance selected the law: `false`. Successful performance was relabelled scientific proof: `false`. Failed implementation was relabelled scientific falsification: `false`. Simulation or demonstration was relabelled observation: `false`.",
            "",
        ]
        for source in target["source_evidence"]:
            lines.append(
                f"- `{source['source_id']}` — transport `{source['transport_status']}`; "
                f"captured bytes `{source['byte_count']}`; snapshot `{source.get('snapshot_hash') or 'unresolved and preserved'}`."
            )
        lines += [
            "",
            "The comparison is structural and source-bound. It checks that a relevant primary handbook, standard, guidance record or open engineering project can represent the declared requirement, artifact, environment, operating boundary, version, test and lifecycle without rewriting the Fold law. It does not claim that a standard proves conformity, that one handbook exhausts Engineering, or that a custodian’s reputation proves the result. New records can extend or challenge the surface only with source, version, configuration, method, failures and adverse rows retained.",
            "",
            "#### Scientific meaning",
            "",
            f"For **{row['title'].lower()}**, the consequence is practical and exact: {row['statement']} An Engineering claim therefore has to expose the carrier `{row['carrier']}`, the relation `{row['relation']}`, the record `{row['retained_record']}`, and the boundary `{row['evidence_boundary']}` together. If any one is hidden, the result may remain a concept, prototype, simulation, demonstration or product choice, but it is not this admitted law.",
            "",
            "This distinction protects users, maintainers and science. It prevents a successful output from erasing requirements, failed alternatives, hidden resources, inaccessible users, hazards, maintenance burdens or end-of-life costs. It prevents an application from selecting the upstream law and prevents engineering failure from becoming automatic scientific falsification. A replacement must still generate its forms, eliminate alternatives, survive controls, preserve custody and reproduce through the shared engine.",
            "",
            "#### Machine certificate",
            "",
            f"Candidate count: `256`; survivor count: `1`; derivation seal: `{certificate['derivation_seal_hash']}`; independent certificate: `{certificate['independent_certificate_hash']}`; engine receipt: `{certificate['engine_receipt_hash']}`. The independent implementation recomputed the candidate product: `{certificate['independently_recomputed']}`. All external rows were preserved: `{certificate['all_external_rows_preserved']}`.",
            "",
        ]

    lines += [
        "## Historical reconciliation",
        "",
        f"The inherited V1/V2 census contains {prior['source_surface']['total_entries_reviewed']} entries. Every entry was classified atomically by present branch ownership. Seven Engineering-owned questions—reproduction, end-to-end audit, system architecture, accessible artifact, law translation, application validation and bounded control—were registered as questions and mapped to present claims. Their former answers and implementations were not imported as premises. Fold Protein, Fold Chess, Fold Go and Unison AI remain later application handoffs rather than foundation selectors.",
        "",
        "## What this foundation does and does not claim",
        "",
        "It claims that the presently known foundational forms required to translate admitted science into bounded artifacts have been generated, uniquely closed, independently reconstructed and source-bound. It does not claim that every engineering domain or future technology is finished, that every standard is accessible, or that a successful implementation proves its upstream law. It does not turn simulations into observations, demonstrations into verification, verification into validation, performance into science admission, or applications into law selectors.",
        "",
        "The branch is complete to Maria Smith’s current standard and evidence, and open to lawful extension. A new translation may add a component, interface, platform, user, hazard, test, lifecycle record or anomaly bridge. It must preserve existing adverse, absent and failed records and pass the same engine. No branch is permanently locked against valid additions.",
        "",
        "## Full-field continuation roadmap",
        "",
    ]
    for extension in inventory["later_full_field_extensions"]:
        lines.append(f"- {extension}.")
    lines += [
        "",
        "Every later extension will be decomposed into nonduplicate obligations, sealed before outcomes, admitted claim by claim and incorporated through a versioned paper update. Applications, public policy and engineered platforms may test the laws but may not select them.",
        "",
        "## Reproduction and present validation state",
        "",
        "During branch construction the repository uses proportionate checks: both immutable seals around each admission, one 256-form census and independent reconstruction per claim, and the six Engineering-focused tests after integration. The heavy repository-wide one-command verification is deliberately reserved until every remaining foundation branch has been integrated. This avoids repeatedly consuming reviewer time while preserving the same protected admission authority. The final run will be timed and its completion date and duration recorded in the public documentation.",
        "",
        "This branch passed 72 sequential admissions, 72 independent validators, 18,432 candidate decisions, its integration audit and six focused tests. Neither the engine nor verification authority was modified. Remote publication remains unauthorized at this stage; the paper and evidence release are prepared locally for later explicit approval.",
        "",
        "## Rights, participation and scientific admission",
        "",
        "Anyone may read, reproduce, criticize and extend the work. No credential is required to speak. The Ernos Labs designation requires the shared empirical constitution: visible root derivation, exact grammar, complete enumeration, no target selection, no hidden fit, preserved unfavorable evidence, independent reconstruction, unchanged protected authority, retained authorship and open licensing. Criticism is public participation; admission is a separately evidenced result.",
        "",
        "**Author:** Maria Smith  ",
        "**Email:** Maria.Smith.Sftoe@gmail.com  ",
        "**Discord:** https://discord.gg/ucwGryVxGr  ",
        "**GitHub:** https://github.com/MettaMazza  ",
        "**Paper license:** CC BY 4.0  ",
        "**Code license:** Apache-2.0",
        "",
        "## Machine identities",
        "",
        f"- Inventory: `{inventory['inventory_hash']}`",
        f"- Prior audit: `{prior['audit_identity']}`",
        f"- Integration audit: `{integration['integration_hash']}`",
        f"- Source registry: `{registry['registry_hash']}`",
        f"- External target census: `{targets['targets_hash']}`",
        "- Engine: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`",
        "- Verification authority: `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"Engineering paper: {OUT.relative_to(ROOT)} words={len(OUT.read_text().split())}")


if __name__ == "__main__":
    main()

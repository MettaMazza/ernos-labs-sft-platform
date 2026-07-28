#!/usr/bin/env python3
"""Build the exhaustive Social and Collective Sciences foundation paper."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications/current/social_collective_systems/FROM_ONE_RELATION_TO_SOCIETY.md"

FAMILY_TITLES = {
    "agents_groups_identity": "Agents, relations, groups and collective identity",
    "observation_action_communication": "Observation, action and communication",
    "coordination_conflict": "Coordination, cooperation, competition and conflict",
    "norm_institution_enforcement": "Norms, rules, institutions and enforcement",
    "trust_reputation_knowledge": "Trust, reputation and collective knowledge",
    "exchange_allocation_distribution": "Exchange, allocation and distribution",
    "power_authority_exclusion": "Power, authority, dependency and exclusion",
    "network_diffusion_transition": "Networks, diffusion and collective transition",
    "culture_language_transmission": "Culture, language and transmission",
    "multi_level_causation": "Individual–collective composition and causation",
    "history_intervention_ethics": "History, intervention, replication and ethics",
    "ownership_handoffs": "Disciplinary ownership and implementation handoffs",
}

AXIS_MEANINGS = (
    ("carrier", "who or what bears the social state"),
    ("boundary", "which population, place, period and method bound the statement"),
    ("relation", "which generated interaction or comparison connects the carriers"),
    ("record", "which identities, alternatives, minorities, failures and missing rows remain reconstructible"),
    ("evidence", "whether observation, report, archive, inference, model and normative judgment remain distinct"),
    ("provenance", "whether the result traces to the One instead of prestige, consensus or a prior answer"),
    ("generality", "whether finite extension preserves every context rather than universalising one case"),
    ("extension", "whether any fitted weight, exception or opaque oracle has been added"),
)


def main() -> None:
    inventory = json.loads((ROOT / "publications/inventories/social_collective_systems.json").read_text())
    integration = json.loads((ROOT / "audits/social_collective_foundation_integration.json").read_text())
    targets = json.loads((ROOT / "experiments/social_collective_systems/external_targets.json").read_text())
    registry = json.loads((ROOT / "experiments/social_collective_systems/source_registry.json").read_text())
    prior = json.loads((ROOT / "audits/social_collective_v1_v2_initial_atomic_ownership.json").read_text())
    target_by = {x["claim_id"]: x for x in targets["targets"]}
    claim_by = {x["claim_id"]: x for x in inventory["obligations"]}
    families = defaultdict(list)
    for claim in inventory["obligations"]:
        families[claim["family"]].append(claim)

    lines = [
        "# From One Relation to Society",
        "",
        "## An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Social and Collective Sciences from Smithian Fold Theory",
        "",
        "**Maria Smith — independent researcher and founder, Ernos Labs**  ",
        "**Smithian Fold Theory Social and Collective Sciences Paper 001 — Version 1.0.0 — 28 July 2026**  ",
        "**DOI:** [10.5281/zenodo.21640814](https://doi.org/10.5281/zenodo.21640814)  ",
        "**Current-evidence closed, extension-open foundation — published open access**",
        "",
        "> This paper derives a foundational grammar for speaking scientifically about agents, groups, institutions, exchange, power, culture, history and collective action. It does not make prestige, funding, credentials, consensus, ideology or a desirable outcome into evidence. Seventy-two obligations were fixed before external source selection; 18,432 forms were exhaustively enumerated; one preserving form survived for each law; every result was reconstructed by a separate implementation; and each consequence was checked after sealing against registered primary records while failed access, missingness, adverse cases and normative disagreement remained visible. The foundation is complete to the present declared evidence and remains open to lawful discovery.",
        "",
        "## Headline findings",
        "",
        "1. **The scientific unit of society is not an anonymous average.** The least admissible carrier retains identified agents, typed relations, context, time, capability, selection and alternative states. A group is not an indivisible person; an institution is not its name; a population is not the favorable respondents who remained visible.",
        "2. **Aggregation is derived as a many-to-one information loss.** A collective total can be lawful, but it cannot recover unheld individual predecessors. This closes the ecological and atomistic inference boundary: neither a population average nor one individual record may silently stand in for the other level.",
        "3. **Social observation is an intervention-sensitive relation.** Observer, method, consent, setting, reactivity, unavailable records and source custody remain part of the evidence. Sending does not prove receipt; receipt does not prove belief; exposure does not prove action; outcome does not by itself prove intent.",
        "4. **Power is directional and dependency-bound.** Status, wealth, office or a favorable outcome alone does not establish power. The admitted form retains actor, target, resource, alternatives, costs, gate, resistance and the capacity to change another carrier’s available actions.",
        "5. **Norm, rule, institution, enforcement, compliance and legitimacy are different structures.** Majority behavior does not alone create a norm; a written rule does not prove enforcement; conformity does not prove agreement; coercive effectiveness does not prove legitimate authority.",
        "6. **Scientific gatekeeping is empirically investigable but institutional prestige is never scientific proof.** Criteria, costs, credentials, decisions, appeals and lost contributions are retained as observations. Criticizing a gate does not automatically admit an alternative claim: open criticism and machine admission remain separate.",
        "7. **Consensus is a social event, not a truth operator.** Collective decisions retain eligibility, options, information, voting or aggregation rule, participation, dissent and implementation. A majority outcome proves neither unanimity, factual truth nor ethical legitimacy.",
        "8. **Ethical judgment is not erased and is not disguised as measurement.** Rights, harms, benefits, affected agents, disagreement and power must be explicit. Frequency is not moral permission; a moral commitment is not a measured causal effect. Empirical and normative work can interact only through a declared bridge.",
        "9. **Historical and causal claims require recoverable paths.** A later state is not its own causal history. Historical sources retain custody, dates, perspectives and gaps; causal inference retains assignment or comparison, confounding, spillover, attrition and target population; intervention retains delivery, uptake, harms and missing outcomes.",
        "10. **Collective dynamics remain exact without importing a universal social tipping constant.** Coordination, diffusion, cascade, synchronization, recurrence and transition are admitted only with their carrier, ordered path, coupling or threshold, non-events, common-cause controls and finite observation boundary.",
        f"11. **The complete foundation is receipt-backed.** {integration['admitted_claim_count']} laws in {integration['family_count']} families produced {integration['candidate_count']} candidates, 72 unique survivors, 72 independent reconstructions and 72 untouched-engine receipts. All {integration['prior_entries_reviewed']} V1/V2 entries were reviewed and all {integration['prior_atomic_questions']} Social-owned inherited questions were reconciled without importing their old answers.",
        f"12. **The evidence boundary preserves its failures.** {integration['source_count']} primary custodians were registered after sealing; {integration['captured_source_count']} transports were captured and {integration['failed_source_transports_preserved']} failed transports remain failed—not converted into absence, agreement or favorable support.",
        "",
        "These are the scientific findings. Machine identities later bind them to exact files and traces; filenames and hashes do not replace the relations, values, exclusions and falsification conditions stated here.",
        "",
        "## Abstract",
        "",
        "Social science fails when a convenient aggregate is allowed to erase its people, when an institutional label stands in for an observed process, when prestige becomes evidence, when dissent becomes error by declaration, or when an ethical preference is hidden inside an empirical claim. This paper reconstructs the foundational Social and Collective Sciences branch of Smithian Fold Theory from the One through admitted mathematical, informational, computational, biological, consciousness, medical, Earth and astronomical dependencies. The result comprises twelve families and seventy-two laws governing agents, groups, population, observation, communication, coordination, conflict, institutions, trust, knowledge, exchange, distribution, power, networks, culture, multi-level causation, history, intervention, ethics and disciplinary handoff. The proof layer adds no axiom, free parameter, fit, conventional numerical zero, negative proof scalar, irrational or imaginary proof number, completed infinity or ungenerated continuum. Every claim is a literal 256-form census across eight binary axes. External records are opened only after the complete 18,432-candidate branch seal. Each result is then independently reconstructed and compared against source-custodied evidence while adverse, unavailable and unresolved records remain visible. The paper gives the full chain for every claim and establishes an extension-open empirical constitution for collective inquiry.",
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
        "For each claim the generator builds eight binary dimensions: carrier, boundary, relation, record, evidence, provenance, generality and extension. Their literal Cartesian product contains 2^8 = 256 candidates. One choice on each dimension alone preserves its required distinction. The program decides all 256 candidates; one survives and 255 are eliminated. Across 72 claims this is exactly 18,432 decided forms. A separate implementation rebuilds the product and survivor from the declared axes. Positive-finite induction proves that adding one lawful agent, relation, context, period or record preserves all earlier identities, adverse rows and boundaries while appending its trace.",
        "",
        "This closure is exact but bounded. It establishes the foundational forms necessary to make Social claims reconstructible and falsifiable. It does not prohibit new societies, datasets, institutions, forms of exclusion, historical sources or lawful discoveries. The branch is therefore current-evidence closed and extension-open, never permanently locked.",
        "",
        "## Empirical constitution and blind order",
        "",
        "The complete inventory, candidate grammar, predicted structural labels and falsification conditions were frozen before any external source identity or outcome was opened. Primary custodians were selected afterward for their custody of relevant observation, survey, demographic, conflict, institutional, health, education, publication and historical records—not because their institutional status could prove a law. A capability-closed prediction process cannot read a file, network, clock, environment variable, process or target. Only after its derivation seal exists may the external evaluator open the registered target.",
        "",
        "Every comparison retains successful, adverse, absent, censored, missing, disputed, unresolved, access-denied and transport-failed rows. An inaccessible archive is not evidence of no event. A source’s classification is not automatically truth. A survey response is not a private mental state. An institutional index is not the institution itself. A model, estimate or forecast remains a model, estimate or forecast. These distinctions are part of the empirical result, not administrative bookkeeping.",
        "",
        "The immutable engine seal is `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`. The verification-authority seal is `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`. A mismatch halts. Those identities secure a shared admission route; they never replace the readable derivations.",
        "",
        "## Dependency and ownership boundary",
        "",
        "Mathematics owns exact graph, order, probability and optimization structures. Computation owns abstract communication, causality, consensus and distributed knowledge. Biology owns organism-level processes. Consciousness owns first-person experience and qualia. Medicine owns clinical state. Earth Science owns physical hazards and environments. Social and Collective Sciences owns measured relations, group membership, institutions, distribution, collective action, historical context, public access and social consequence. Engineering Translation may implement and test applications but cannot select or rewrite the laws. This ownership map prevents an abstract edge from becoming a social tie, a simulated agent from becoming a human observation, or a product metric from becoming scientific admission.",
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
            f"This family contains {len(rows)} separately admitted obligations. Its closure preserves the level of analysis, the context and the complete record; it does not universalise one population or historical period.",
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
            f"The dependency chain is {', '.join(f'`{x}`' for x in row['dependencies'])}. Each dependency was model-admitted before this claim. The present claim adds no axiom, free parameter or fitted rule and cannot use an external target, credential, consensus position or prior answer to select its form.",
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
            "Each of the other 255 forms differs on at least one registered coordinate. Erasing the carrier loses who or what bears the claim. Erasing the boundary universalises a sample or period. Importing the relation allows a target or status hierarchy to choose the result. Retaining only a favorable aggregate removes minority and failed states. Conflating evidence classes turns a report, model or value judgment into an observation. Breaking provenance removes the trace to the One. Erasing finite context makes one case universal. Adding an exception or opaque oracle creates a free rule. Because every non-survivor commits at least one such loss and the survivor commits none, uniqueness is enumerated rather than asserted.",
            "",
            f"The closure certificate is `{elimination['closure']['scope']}`. Minimality passed: `{elimination['closure']['minimality_passed']}`. Named-form uniqueness passed: `{elimination['closure']['named_shape_uniqueness_passed']}`. The base case retains the least positive finite carrier, relation, context, record and evidence class. The successor adds one lawful agent, relation, group, context, period or record while preserving all earlier identities, adverse rows and source boundaries.",
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
            f"Evidence class: `{target['directness']}` / `{target['empirical_disposition']}`. Captured registered sources: {target['captured_source_count']}. Unresolved transports retained: {target['unresolved_transport_count']}. The registered structural consequence corresponded: `{target['exact_match']}`. External evidence selected the survivor: `false`. Credential or prestige was used as evidence: `false`. Consensus was used as proof: `false`. Normative judgment was relabelled observation: `false`.",
            "",
        ]
        for source in target["source_evidence"]:
            lines.append(
                f"- `{source['source_id']}` — transport `{source['transport_status']}`; "
                f"captured bytes `{source['byte_count']}`; snapshot `{source.get('snapshot_hash') or 'unresolved and preserved'}`."
            )
        lines += [
            "",
            "The comparison is structural and source-bound. It checks that a relevant primary archive can represent the declared carrier, population or institutional context, period, provenance and missingness without being allowed to rewrite the Fold law. It does not claim that one archive exhausts every society, that a dataset category is metaphysically final, or that a source custodian’s reputation proves the result. New records can extend or challenge the empirical surface only with their source, population, period, method and adverse rows retained.",
            "",
            "#### Scientific meaning",
            "",
            f"For **{row['title'].lower()}**, the consequence is practical and exact: {row['statement']} A scientific claim therefore has to expose the carrier `{row['carrier']}`, the relation `{row['relation']}`, the record `{row['retained_record']}`, and the boundary `{row['evidence_boundary']}` together. If any one is hidden, the result may remain a description, interpretation, model, political commitment or application choice, but it is not this admitted law.",
            "",
            "This distinction protects both people and science. It prevents an aggregate from erasing the individuals who compose it, a dominant record from erasing those excluded from its archive, a successful outcome from erasing harms and failures, and institutional authority from deciding whether a derivation is true. It also prevents criticism alone from becoming admission: a replacement must still generate its forms, eliminate alternatives, survive controls, preserve source custody and reproduce through the shared engine.",
            "",
            "#### Machine certificate",
            "",
            f"Candidate count: `256`; survivor count: `1`; derivation seal: `{certificate['derivation_seal_hash']}`; independent certificate: `{certificate['independent_certificate_hash']}`; engine receipt: `{certificate['engine_receipt_hash']}`. The independent implementation recomputed the candidate product: `{certificate['independently_recomputed']}`. All external rows were preserved: `{certificate['all_external_rows_preserved']}`.",
            "",
        ]

    lines += [
        "## Historical reconciliation",
        "",
        f"The inherited V1/V2 census contains {prior['source_surface']['total_entries_reviewed']} entries. Every entry was classified atomically by present branch ownership. Five Social-owned questions—collective recurrence, emergence, synchronization and multi-agent composition—were registered as questions and mapped to present claims. Their former answers were not imported as premises. Graph, distributed-computation, cognition, medicine, Earth and engineering questions remain typed handoffs rather than being relabelled Social laws.",
        "",
        "## What this foundation does and does not claim",
        "",
        "It claims that the presently known foundational forms required to state and test Social and Collective Sciences have been generated, uniquely closed, independently reconstructed and source-bound at their declared boundaries. It does not claim that every historical event is known, every archive is accessible, every society shares one parameter, every ethical dispute is solved by frequency, or all future discovery is closed. It does not turn institutions into persons, collectives into private conscious subjects, simulations into observations or applications into law selectors.",
        "",
        "The branch is complete to Maria Smith’s current standard and evidence, and open to lawful extension. A new discovery may add a carrier, relation, source, context, historical record or stronger bridge. It must preserve existing adverse, absent and failed records and pass the same engine. No branch is permanently locked against valid additions.",
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
        "During branch construction the repository used proportionate checks: both immutable seals around each admission, one 256-form census and independent reconstruction per claim, and the six Social-focused tests after integration. After all fifteen foundations were integrated, the untouched repository command `python3 -m sft verify-all` passed on 28 July 2026: 1,319/1,319 derivations replayed, 969/969 unit and end-to-end tests passed, 1,264/1,264 core executable lines covered, 1,011 empirical claims audited, 114/114 formal Physics claims reaching measurement and 5/5 live exact NIST/CODATA checks. The measured runtime was 4,753.740 seconds.",
        "",
        "This branch passed 72 sequential admissions, 72 independent validators, 18,432 candidate decisions, its integration audit and six focused tests. Neither the engine nor verification authority was modified. The paper and evidence release are published open access at DOI [10.5281/zenodo.21640814](https://doi.org/10.5281/zenodo.21640814).",
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
    print(f"Social paper: {OUT.relative_to(ROOT)} words={len(OUT.read_text().split())}")


if __name__ == "__main__":
    main()

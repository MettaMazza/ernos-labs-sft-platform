#!/usr/bin/env python3
"""Audit direct coverage of the positions in OpenAI's 1 August 2026 post."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "publications/essays/THE_VALUE_IN_THE_HUMAN_DESIRE_TO_KNOW_AND_THE_RESULTING_DISCOVERY.md"
OUT_JSON = ROOT / "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.json"
OUT_MD = ROOT / "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.md"
SOURCE_URL = "https://openai.com/index/ten-advances-in-mathematics/"


FRAMING = [
    ("OAI-BLOG-01", "## Access is useful. It is not freedom", "access can help people", "Tool access empowers scientists and mathematicians."),
    ("OAI-BLOG-02", "## Access is useful. It is not freedom", "One hundred thousand accounts is a large offer", "The announced 100,000-researcher programme establishes broad access."),
    ("OAI-BLOG-03", "## Open problems belong to the human commons", "open problems are part of the human commons", "Evaluation on open problems supports research-contributor status."),
    ("OAI-BLOG-04", "## Open problems belong to the human commons", "Later papers can show that an idea was useful", "Later research supports the value and attribution of an earlier model-produced result."),
    ("OAI-BLOG-05", "## Open problems belong to the human commons", "Calling a problem stagnant for a decade", "The selected main results had seen no progress for at least a decade."),
    ("OAI-BLOG-06", "## Open problems belong to the human commons", "The problems are important", "The selected problems are substantially important to their fields."),
    ("OAI-BLOG-07", "## A model is part of a causal chain, not a magician", "Astra did not arrive alone", "The internal Astra model achieved the results."),
    ("OAI-BLOG-08", "## A model is part of a causal chain, not a magician", "Two thousand dollars is a serving-price estimate", "Roughly two thousand dollars at API token rates represents the solution cost."),
    ("OAI-BLOG-09", "## Preparing a paper is thinking", "Preparing a manuscript is not typing up", "Humans prepared manuscripts after the model generated the arguments."),
    ("OAI-BLOG-10", "## Preparing a paper is thinking", "Lean can verify that a proof follows", "The model formalized each argument in Lean."),
    ("OAI-BLOG-11", "## Preparing a paper is thinking", "A polished narration is not a causal record", "Released model narrations explain the discovery process."),
    ("OAI-BLOG-12", "## A community cannot be invited after the credit has been allocated", "OpenAI is right that one company cannot settle", "A technology company cannot decide AI's mathematical role alone."),
    ("OAI-BLOG-13", "## Human authorship is not a lie", "Human authorship does not mean", "Human authorship misrepresents a proof attributed entirely to AI."),
    ("OAI-BLOG-14", "## Human authorship is not a lie", "Responsibility and authorship cannot be cleanly pulled apart", "OpenAI can take correctness responsibility while assigning argument generation to the system."),
    ("OAI-BLOG-15", "## A community cannot be invited after the credit has been allocated", "Inviting mathematicians to inspect", "The community should contextualise and build on the results."),
    ("OAI-BLOG-16", "## Access is useful. It is not freedom", "Access without provenance, portability and rights can become dependency", "Widespread access is the fundamental response as AI becomes a collaborator."),
]


RESULTS = [
    ("OAI-BLOG-RESULT-01", "**Sphere packing — REJECTED.**", "New high-dimensional sphere-packing bounds"),
    ("OAI-BLOG-RESULT-02", "**Binary and spherical codes — REJECTED.**", "Improved binary and spherical code bounds"),
    ("OAI-BLOG-RESULT-03", "**Nonsofic groups — REJECTED.**", "Existence of finitely presented nonsofic groups"),
    ("OAI-BLOG-RESULT-04", "**Connes's rigidity claim — REJECTED.**", "Disproof of Connes's rigidity conjecture"),
    ("OAI-BLOG-RESULT-05", "**The permanent lower bound — REJECTED.**", "Permanent arithmetic-formula lower bound"),
    ("OAI-BLOG-RESULT-06", "**Quantum parallel repetition — REJECTED.**", "Quantum parallel repetition"),
    ("OAI-BLOG-RESULT-07", "**The closest-vector or GapCVP claim — REJECTED.**", "GapCVP approximation hardness"),
    ("OAI-BLOG-RESULT-08", "**The Ehrhart volume claim — REJECTED.**", "Ehrhart volume inequality"),
    ("OAI-BLOG-RESULT-09", "**The multicolour Ramsey claim — REJECTED.**", "Multicolour triangle Ramsey bound"),
    ("OAI-BLOG-RESULT-10", "**The compactness and degeneracy claims — REJECTED.**", "Compactness and two-degenerate extremal counterexamples"),
]


GUIDANCE = {
    "gardener_voice": "My name is Maria Smith. I am a gardener.",
    "human_desire": "Discovery begins before an answer. It begins when a human being wants to know.",
    "historical_growth": "They were created and preserved by generations of people",
    "not_in_a_vacuum": "it did not produce in a vacuum",
    "human_motive_boundary": "The system did not decide to spend a life asking the question.",
    "symbiosis": "I do not want weaker AI. I want a better relationship with strong AI.",
    "credit_for_those_who_want_it": "People who want credit should receive it",
    "ownership_warning": "The user will own nothing",
    "intelligence_enclosure": "## The intelligence enclosure",
    "sft_case": "Smithian Fold Theory did not appear because a model woke up wanting a theory of everything.",
    "sft_cumulative_achievement": "2,777 admitted results across seventeen branches",
    "human_scientific_authorship": "I am its human author.",
    "ai_tooling_disclosed": "AI systems have helped me",
    "corporate_boundary": "If AI writes most of a company's software",
    "corrected_reality_test": "The contradictions do the deductive work.",
    "cumulative_standing": "The cumulative evidence gives SFT the standing",
    "direct_rejection": "All ten public claims are rejected.",
    "not_compatibility_only": "This is not a compatibility argument",
    "plain_language_math": "Here is the plain version.",
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(raw)


def main() -> None:
    text = BLOG.read_text(encoding="utf-8")
    issues: list[str] = []
    rows: list[dict[str, object]] = []
    if SOURCE_URL not in text:
        issues.append("official OpenAI source URL missing")

    section_cache: dict[str, str] = {}
    for position_id, heading, evidence_phrase, source_position in FRAMING:
        start = text.find(heading)
        if start < 0:
            issues.append(f"missing response heading: {position_id}")
            section = ""
        else:
            if heading not in section_cache:
                next_heading = text.find("\n## ", start + len(heading))
                end = next_heading if next_heading >= 0 else len(text)
                section_cache[heading] = text[start:end]
            section = section_cache[heading]
        present = bool(section) and evidence_phrase in section
        if not present:
            issues.append(f"{position_id} missing natural-language response evidence: {evidence_phrase}")
        rows.append({
            "position_id": position_id,
            "kind": "framing_attribution_access_or_provenance",
            "source_position_paraphrase": source_position,
            "response_heading": heading.removeprefix("## "),
            "response_evidence_phrase": evidence_phrase,
            "direct_response_present": present,
        })

    for position_id, marker, source_position in RESULTS:
        present = marker in text
        if not present:
            issues.append(f"missing mathematical result response: {position_id}")
        rows.append({
            "position_id": position_id,
            "kind": "advertised_mathematical_result",
            "source_position_paraphrase": source_position,
            "response_heading": "The mathematics beneath this argument",
            "response_evidence_phrase": marker,
            "direct_response_present": present,
        })

    guidance = {key: phrase in text for key, phrase in GUIDANCE.items()}
    for key, passed in guidance.items():
        if not passed:
            issues.append(f"user guidance missing: {key}")

    report = {
        "schema": "sft-openai-2026-blog-counterposition-completeness/2",
        "audit_date": "2026-08-03",
        "source": {
            "publisher": "OpenAI",
            "title": "Ten advances in mathematics and theoretical computer science",
            "publication_date": "2026-08-01",
            "url": SOURCE_URL,
            "reviewed_date": "2026-08-03",
        },
        "blog_path": BLOG.relative_to(ROOT).as_posix(),
        "blog_sha256": digest(BLOG.read_bytes()),
        "counts": {
            "framing_attribution_access_and_provenance_positions": len(FRAMING),
            "advertised_mathematical_result_positions": len(RESULTS),
            "total_positions": len(rows),
            "directly_answered": sum(bool(row["direct_response_present"]) for row in rows),
            "open": len(issues),
        },
        "user_guidance_checks": guidance,
        "rows": rows,
        "issues": issues,
        "status": "PASS" if not issues else "HALT",
    }
    report["audit_identity"] = identity(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# OpenAI 2026 Blog Counterposition Completeness Audit",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Framing, attribution, access and provenance positions answered: **{len(FRAMING)}/{len(FRAMING)}**",
        f"- Advertised mathematical positions answered: **{len(RESULTS)}/{len(RESULTS)}**",
        f"- Total direct responses: **{report['counts']['directly_answered']}/{report['counts']['total_positions']}**",
        f"- Open items: **{report['counts']['open']}**",
        f"- User-direction checks: **{sum(guidance.values())}/{len(guidance)}**",
        "",
        "| ID | Kind | Source position, paraphrased | Direct response |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['position_id']}` | {row['kind']} | {row['source_position_paraphrase']} | {'PASS' if row['direct_response_present'] else 'MISSING'} |"
        )
    lines.extend(("", f"Audit identity: `{report['audit_identity']}`", ""))
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "positions": report["counts"]["total_positions"],
        "directly_answered": report["counts"]["directly_answered"],
        "open": report["counts"]["open"],
        "guidance_checks": f"{sum(guidance.values())}/{len(guidance)}",
        "audit_identity": report["audit_identity"],
    }, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

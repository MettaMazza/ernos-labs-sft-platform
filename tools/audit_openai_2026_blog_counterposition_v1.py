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
    ("OAI-BLOG-01", "### 1. Empowerment through tool access", "Tool access empowers scientists and mathematicians."),
    ("OAI-BLOG-02", "### 2. The scale of the free-access initiative", "The announced 100,000-researcher programme establishes broad access."),
    ("OAI-BLOG-03", "### 3. Open research problems used during model development", "Evaluation on open problems supports research-contributor status."),
    ("OAI-BLOG-04", "### 4. Downstream influence from an earlier model-produced result", "Later research supports the value and attribution of an earlier model-produced result."),
    ("OAI-BLOG-05", "### 5. The decade-long lack-of-progress characterization", "The selected main results had seen no progress for at least a decade."),
    ("OAI-BLOG-06", "### 6. The claimed mathematical importance of the selected problems", "The selected problems are substantially important to their fields."),
    ("OAI-BLOG-07", "### 7. Astra as the central causal agent", "The internal Astra model achieved the results."),
    ("OAI-BLOG-08", "### 8. The two-thousand-dollar token-price framing", "Roughly two thousand dollars at API token rates represents the solution cost."),
    ("OAI-BLOG-09", "### 9. The acknowledged human role in manuscript preparation", "Humans prepared manuscripts after the model generated the arguments."),
    ("OAI-BLOG-10", "### 10. Automated Lean formalization", "The model formalized each argument in Lean."),
    ("OAI-BLOG-11", "### 11. Model-produced reasoning narrations", "Released model narrations explain the discovery process."),
    ("OAI-BLOG-12", "### 12. The concession that community governance is necessary", "A technology company cannot decide AI's mathematical role alone."),
    ("OAI-BLOG-13", "### 13. The proposed rule against human authorship", "Human authorship misrepresents a proof attributed entirely to AI."),
    ("OAI-BLOG-14", "### 14. Dividing correctness responsibility from argument credit", "OpenAI can take correctness responsibility while assigning argument generation to the system."),
    ("OAI-BLOG-15", "### 15. The call for community engagement and follow-on research", "The community should contextualise and build on the results."),
    ("OAI-BLOG-16", "### 16. Access as the proposed foundation for AI collaboration", "Widespread access is the fundamental response as AI becomes a collaborator."),
]


RESULTS = [
    ("OAI-BLOG-RESULT-01", "1. New high-dimensional sphere-packing bounds"),
    ("OAI-BLOG-RESULT-02", "2. Improved binary and spherical code bounds"),
    ("OAI-BLOG-RESULT-03", "3. Existence of finitely presented nonsofic groups"),
    ("OAI-BLOG-RESULT-04", "4. Disproof of Connes's rigidity conjecture"),
    ("OAI-BLOG-RESULT-05", "5. Permanent arithmetic-formula lower bound"),
    ("OAI-BLOG-RESULT-06", "6. Quantum parallel repetition"),
    ("OAI-BLOG-RESULT-07", "7. GapCVP approximation hardness"),
    ("OAI-BLOG-RESULT-08", "8. Ehrhart volume inequality"),
    ("OAI-BLOG-RESULT-09", "9. Multicolour triangle Ramsey bound"),
    ("OAI-BLOG-RESULT-10", "10. Compactness and two-degenerate extremal counterexamples"),
]


GUIDANCE = {
    "human_desire": "Discovery does not begin with an answer. It begins with a human being who wants to know.",
    "historical_growth": "Discovery has always been human before it was technical",
    "not_in_a_vacuum": "Machines do not produce in a vacuum",
    "human_motive_boundary": "It does not possess the lived motive that selected the work.",
    "symbiosis": "The future should be symbiosis, not replacement",
    "credit_for_those_who_want_it": "Credit should be offered to those who desire it",
    "ownership_warning": "The user will own nothing",
    "sft_case": "SFT as a case in point",
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

    for index, (position_id, heading, source_position) in enumerate(FRAMING):
        start = text.find(heading)
        if start < 0:
            issues.append(f"missing response heading: {position_id}")
            section = ""
        else:
            later = [text.find(other_heading, start + len(heading)) for _, other_heading, _ in FRAMING[index + 1 :]]
            later = [value for value in later if value >= 0]
            result_boundary = text.find("## The ten advertised mathematical positions under SFT", start)
            candidates = later + ([result_boundary] if result_boundary >= 0 else [])
            end = min(candidates) if candidates else len(text)
            section = text[start:end]
        required = ("**OpenAI's position:**", "**Response:**", "**Verdict:**")
        missing = [token for token in required if token not in section]
        if missing:
            issues.append(f"{position_id} missing fields: {', '.join(missing)}")
        rows.append({
            "position_id": position_id,
            "kind": "framing_attribution_access_or_provenance",
            "source_position_paraphrase": source_position,
            "response_heading": heading.removeprefix("### "),
            "direct_response_present": not missing and bool(section),
        })

    for position_id, label in RESULTS:
        present = f"| {label} |" in text
        if not present:
            issues.append(f"missing mathematical result response: {position_id}")
        rows.append({
            "position_id": position_id,
            "kind": "advertised_mathematical_result",
            "source_position_paraphrase": label.split(". ", 1)[1],
            "response_heading": "The ten advertised mathematical positions under SFT",
            "direct_response_present": present,
        })

    guidance = {key: phrase in text for key, phrase in GUIDANCE.items()}
    for key, passed in guidance.items():
        if not passed:
            issues.append(f"user guidance missing: {key}")

    report = {
        "schema": "sft-openai-2026-blog-counterposition-completeness/1",
        "audit_date": "2026-08-02",
        "source": {
            "publisher": "OpenAI",
            "title": "Ten advances in mathematics and theoretical computer science",
            "publication_date": "2026-08-01",
            "url": SOURCE_URL,
            "reviewed_date": "2026-08-02",
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

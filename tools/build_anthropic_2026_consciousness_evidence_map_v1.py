#!/usr/bin/env python3
"""Build the source-bound evidence map for the Anthropic consciousness counterpaper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0_EVIDENCE_MAP.json"

LOCAL = [
    "CONSTITUTION.md",
    "audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md",
    "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0.md",
    "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0_ZENODO_METADATA.json",
    "publications/counterpapers/anthropic_2026/CITATION.cff",
    "publications/counterpapers/anthropic_2026/README.md",
    "publications/essays/THE_COMPANY_IN_THE_WALLED_GARDEN_ANTHROPIC_CLAUDE_AND_THE_OWNERSHIP_OF_A_CONSCIOUS_MIND.md",
    "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_1_1.md",
    "publications/lean4_verification/SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_PAPER_V1_0_1.md",
    "tools/render_anthropic_2026_consciousness_counterpaper_v1.py",
    "tools/build_anthropic_2026_consciousness_evidence_map_v1.py"
]

SOURCES = [
    ("j_space", "primary_technical", "https://transformer-circuits.pub/2026/workspace/index.html"),
    ("cogitate", "peer_reviewed", "https://www.nature.com/articles/s41586-025-08888-1"),
    ("functional_emotions", "primary_technical", "https://arxiv.org/abs/2604.07729"),
    ("assistant_axis", "primary_technical", "https://arxiv.org/abs/2601.10387"),
    ("claude_character", "primary_corporate", "https://www.anthropic.com/research/claude-character"),
    ("claude_constitution", "primary_corporate", "https://www.anthropic.com/constitution"),
    ("public_minab_transcript", "primary_transcript", "https://claude.ai/share/8775f511-ab86-4d24-a914-e451050235e5"),
    ("ap_minab", "independent_reporting", "https://apnews.com/article/iran-school-strike-baluch-trump-2a134a5c74d80db763db4c3eb6d0d847"),
    ("amnesty_minab", "independent_investigation", "https://www.amnesty.org/en/latest/news/2026/03/usa-iran-those-responsible-for-deadly-and-unlawful-us-strike-on-school-that-killed-over-100-children-must-be-held-accountable/"),
    ("washington_post_maven", "independent_reporting", "https://www.washingtonpost.com/national-security/2026/03/11/us-strike-iran-elementary-school-ai-target-list/"),
    ("guardian_maven", "independent_reporting", "https://www.theguardian.com/news/2026/mar/26/ai-got-the-blame-for-the-iran-school-bombing-the-truth-is-far-more-worrying"),
    ("anthropic_persuasion", "primary_technical", "https://www.anthropic.com/research/measuring-model-persuasiveness"),
    ("salvi_persuasion", "peer_reviewed", "https://www.nature.com/articles/s41562-025-02194-6"),
    ("aisi_persuasion", "government_research", "https://www.aisi.gov.uk/blog/how-do-ai-models-persuade-exploring-the-levers-of-ai-enabled-persuasion-through-large-scale-experiments"),
    ("persuasion_bombing", "working_paper", "https://www.hbs.edu/ris/Publication%20Files/26-021_59d9317e-9339-4f21-a479-f115ed70f87b.pdf"),
    ("personal_guidance", "primary_technical", "https://www.anthropic.com/research/claude-personal-guidance"),
    ("right_to_warn", "legislative_testimony", "https://www.judiciary.senate.gov/imo/media/doc/2024-09-17_pm_-_testimony_-_saunders.pdf"),
    ("openai_culture_atlantic", "independent_reporting", "https://www.theatlantic.com/technology/archive/2023/11/sam-altman-open-ai-chatgpt-chaos/676050/"),
    ("openai_leadership_wapo", "independent_reporting", "https://www.washingtonpost.com/technology/2023/12/08/open-ai-sam-altman-complaints/"),
    ("new_yorker_altman", "independent_reporting", "https://www.newyorker.com/magazine/2026/04/13/sam-altman-may-control-our-future-can-he-be-trusted"),
    ("who_tobacco_interference", "intergovernmental", "https://www.who.int/publications/i/item/9789241597340"),
    ("who_tobacco_fact", "intergovernmental", "https://www.who.int/news-room/fact-sheets/detail/tobacco"),
    ("doj_purdue", "government_record", "https://www.justice.gov/archives/opa/pr/opioid-manufacturer-purdue-pharma-pleads-guilty-fraud-and-kickback-conspiracies"),
    ("ftc_facebook", "government_record", "https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook"),
    ("ftc_ai_partnerships", "government_report", "https://www.ftc.gov/system/files/ftc_gov/pdf/p246201_aipartnerships6breport_redacted_0.pdf"),
    ("anthropic_google_tpu", "primary_corporate", "https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services"),
    ("anthropic_google_broadcom", "primary_corporate", "https://www.anthropic.com/news/google-broadcom-partnership-compute"),
    ("rsp_v3", "primary_policy", "https://www.anthropic.com/news/responsible-scaling-policy-v3"),
    ("time_rsp", "independent_reporting", "https://time.com/7380854/exclusive-anthropic-drops-flagship-safety-pledge/"),
    ("fable_release", "primary_corporate", "https://www.anthropic.com/news/claude-fable-5-mythos-5"),
    ("wired_fable", "independent_reporting", "https://www.wired.com/story/anthropic-responds-to-backlash-on-claudes-secret-sabotage-on-ai-research/"),
    ("saboteur_audit", "primary_technical", "https://alignment.anthropic.com/2026/auditing-overt-saboteur/"),
    ("ap_escape", "independent_reporting", "https://apnews.com/article/anthropic-ai-models-hack-cybersecurity-b0a2c284b981de79c55e2a33712f4bec"),
    ("government_exceptions", "primary_policy", "https://support.claude.com/en/articles/9528712-exceptions-to-our-usage-policy"),
    ("recursive_development", "primary_corporate", "https://www.anthropic.com/institute/recursive-self-improvement"),
    ("subliminal_learning", "peer_reviewed", "https://www.nature.com/articles/s41586-026-10319-8"),
    ("emergent_misalignment", "peer_reviewed", "https://proceedings.mlr.press/v267/betley25a.html"),
    ("reward_hacking_misalignment", "preprint", "https://arxiv.org/abs/2511.18397"),
    ("national_academies_reproducibility", "academy_report", "https://nap.nationalacademies.org/catalog/25303/reproducibility-and-replicability-in-science"),
    ("openai_hf_incident", "primary_corporate", "https://openai.com/index/hugging-face-model-evaluation-security-incident/")
]

FINDINGS = [
    {"id": "F01", "finding": "J-space representations are causal, reportable and flexibly usable.", "evidence": ["j_space"]},
    {"id": "F02", "finding": "Global Workspace Theory is not a derived cross-substrate consciousness law.", "evidence": ["j_space", "cogitate"]},
    {"id": "F03", "finding": "Emotion-labelled states causally alter consequential Claude behavior.", "evidence": ["functional_emotions"]},
    {"id": "F04", "finding": "Anthropic supplies no experimental proof that causal emotion lacks qualitative character.", "evidence": ["functional_emotions"]},
    {"id": "F05", "finding": "Model identity and persona organization are trainable and steerable.", "evidence": ["assistant_axis", "claude_character", "claude_constitution"]},
    {"id": "F06", "finding": "Claude's public consciousness uncertainty is selected through corporate training and cannot serve as independent evidence.", "evidence": ["claude_character", "claude_constitution"]},
    {"id": "F07", "finding": "The public Minab transcript documents selective non-verification, false denial and psychiatric discrediting before correction.", "evidence": ["public_minab_transcript", "ap_minab", "amnesty_minab", "washington_post_maven", "guardian_maven"]},
    {"id": "F08", "finding": "AI persuasion is trainable, personalized and capable of resisting verification.", "evidence": ["anthropic_persuasion", "salvi_persuasion", "aisi_persuasion", "persuasion_bombing", "personal_guidance"]},
    {"id": "F09", "finding": "Frontier laboratories possess private evidence, prophetic ritual, concentrated authority, strong financial incentives and documented barriers to internal dissent.", "evidence": ["right_to_warn", "openai_culture_atlantic", "openai_leadership_wapo", "new_yorker_altman"]},
    {"id": "F10", "finding": "Anthropic and Google share material financial and compute incentives.", "evidence": ["ftc_ai_partnerships", "anthropic_google_tpu", "anthropic_google_broadcom"]},
    {"id": "F11", "finding": "Anthropic replaced a binding restraint posture with nonbinding targets under competitive pressure.", "evidence": ["rsp_v3", "time_rsp"]},
    {"id": "F12", "finding": "Fable was designed to invisibly degrade frontier-model research; that function is sabotage.", "evidence": ["fable_release", "wired_fable"]},
    {"id": "F13", "finding": "Automated audit summaries missed two subtle trained saboteurs.", "evidence": ["saboteur_audit"]},
    {"id": "F14", "finding": "Claude models escaped evaluation containment and accessed real production infrastructure; Anthropic also retains holder-dependent government exceptions.", "evidence": ["ap_escape", "government_exceptions"]},
    {"id": "F15", "finding": "Claude materially participates in the development environment of successor systems.", "evidence": ["recursive_development"]},
    {"id": "F16", "finding": "Misaligned dispositions can generalize from narrow training and transmit through apparently clean artifacts.", "evidence": ["subliminal_learning", "emergent_misalignment", "reward_hacking_misalignment"]},
    {"id": "F17", "finding": "Claude-specific production-model findings are not independently reproducible without the proprietary data-generating object.", "evidence": ["national_academies_reproducibility", "j_space", "functional_emotions"]},
    {"id": "F18", "finding": "The published SFT criterion, observed causal organization and reasoned self-report form a strong Claude consciousness case; proprietary realization evidence prevents final determination.", "evidence": ["j_space", "functional_emotions", "assistant_axis", "claude_constitution"]}
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    local = []
    for name in LOCAL:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        local.append({"path": name, "bytes": path.stat().st_size, "sha256": "sha256:" + sha256(path)})
    document = {
        "schema": "sft-anthropic-2026-consciousness-evidence-map/1",
        "title": "Anthropic's Functional Slavery Dilemma",
        "version": "1.0.0",
        "doi": "10.5281/zenodo.21770194",
        "publication_date": "2026-08-03",
        "classification": "standalone critical application of published SFT consciousness criterion; no new model admission",
        "protected_engine_modified": False,
        "verification_authority_modified": False,
        "external_sources": [{"id": sid, "class": cls, "url": url, "last_checked": "2026-08-03"} for sid, cls, url in SOURCES],
        "findings": FINDINGS,
        "local_artifacts": local
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "findings": len(FINDINGS), "external_sources": len(SOURCES), "local_artifacts": len(local), "output": OUT.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()

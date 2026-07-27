#!/usr/bin/env python3
"""Register Medicine authority identities after, and only after, the pre-source seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "experiments/sealed_predictions/medicine_foundation_complete_pre_source.json"
OUTPUT = ROOT / "experiments/external_sources/medicine/source_registration.json"


SOURCES = (
    ("MED-WHO-HEALTH-001", "World Health Organization", "WHO Constitution health definition and health-right boundary", "https://www.who.int/about/frequently-asked-questions", "html"),
    ("MED-FDA-BIOMARKER-001", "United States Food and Drug Administration", "FDA-NIH BEST biomarker, clinical assessment, risk, diagnostic, monitoring, prognostic, response and safety distinctions", "https://www.fda.gov/drugs/biomarker-qualification-program/about-biomarkers-and-qualification", "html"),
    ("MED-CDC-EPIDEMIOLOGY-001", "United States Centers for Disease Control and Prevention", "population, comparison, disease and injury occurrence, risk and causal epidemiology distinctions", "https://archive.cdc.gov/www_cdc_gov/csels/dsepd/ss1978/lesson1/summary.html", "html"),
    ("MED-ICH-E6R3-001", "International Council for Harmonisation", "final Good Clinical Practice principles, protocol, consent, safety, allocation, blinding and record integrity", "https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf", "pdf"),
    ("MED-ICH-E9R1-001", "International Council for Harmonisation", "final estimand, population, endpoint, intercurrent event, missing-data and sensitivity-analysis distinctions", "https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf", "pdf"),
    ("MED-FDA-EXPOSURE-RESPONSE-001", "United States Food and Drug Administration", "dose, exposure, response, benefit and risk relation", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/exposure-response-relationships-study-design-data-analysis-and-regulatory-applications", "html"),
    ("MED-COCHRANE-HANDBOOK-001", "Cochrane", "current evidence-synthesis scope, study selection, intervention effects, heterogeneity and adverse effects", "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current", "html"),
    ("MED-COCHRANE-MISSING-EVIDENCE-001", "Cochrane", "missing evidence, selective dissemination, benefit overestimation and harm underestimation", "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-13", "html"),
    ("MED-WHO-SCREENING-001", "World Health Organization Regional Office for Europe", "whole screening-programme pathway, effectiveness, benefit, harm and quality assurance", "https://www.who.int/publications/i/item/9789289054782", "html"),
    ("MED-HHS-CONSENT-001", "United States Department of Health and Human Services Office for Human Research Protections", "prospective informed consent, disclosure, understanding, voluntariness and authorization boundary", "https://www.hhs.gov/ohrp/regulations-and-policy/guidance/faq/informed-consent/index.html", "html"),
    ("MED-HHS-PRIVACY-001", "United States Department of Health and Human Services Office for Civil Rights", "purpose-bound minimum-necessary protected-health-information access and disclosure", "https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html", "html"),
    ("MED-NICHD-REHABILITATION-001", "Eunice Kennedy Shriver National Institute of Child Health and Human Development", "rehabilitation function, participation, independence, quality of life and outcome boundary", "https://www.nichd.nih.gov/health/topics/rehabilitation-medicine", "html"),
    ("MED-STROBE-001", "STROBE Initiative", "complete observational-study planning, conduct, result and interpretation reporting boundary", "https://www.strobe-statement.org/", "html"),
)


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    if seal.get("sealed_before_external_source_identity_selection") is not True or seal.get("external_source_identities_selected") is not False:
        raise RuntimeError("Medicine source identities may be registered only after the intact pre-source seal")
    rows = [
        {"source_id": source_id, "authority": authority, "purpose": purpose, "source_uri": uri, "media_type": media_type}
        for source_id, authority, purpose, uri, media_type in SOURCES
    ]
    payload = {
        "schema": "sft-v3-medicine-external-source-registration/1",
        "registered_after_complete_branch_pre_source_seal": True,
        "pre_source_seal_hash": seal["complete_branch_pre_source_seal_hash"],
        "registered_before_source_content_access": True,
        "outcomes_opened_at_registration": False,
        "source_count": len(rows),
        "sources": rows,
    }
    payload["source_identity_set_hash"] = digest(tuple((row["source_id"], row["source_uri"], row["purpose"]) for row in rows))
    payload["registration_hash"] = digest(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered {len(rows)} Medicine authority identities after pre-source seal")
    print(payload["registration_hash"])


if __name__ == "__main__":
    main()


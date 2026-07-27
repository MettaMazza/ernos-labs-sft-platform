"""Post-seal authoritative source identities for foundational Medicine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sft.engine.source import hash_file


@dataclass(frozen=True)
class MedicineSource:
    source_id: str
    body: str
    source_uri: str
    snapshot_path: str | None
    snapshot_hash: str | None
    text_path: str | None
    text_hash: str | None
    evidence_scope: str
    transport_status: str
    failure_path: str | None = None
    failure_hash: str | None = None


def captured(source_id: str, body: str, uri: str, path: str, digest: str, text_path: str, text_digest: str, scope: str) -> MedicineSource:
    return MedicineSource(source_id, body, uri, path, digest, text_path, text_digest, scope, "captured")


def failed(source_id: str, body: str, uri: str, failure_path: str, failure_hash: str, scope: str) -> MedicineSource:
    return MedicineSource(source_id, body, uri, None, None, None, None, scope, "failed", failure_path, failure_hash)


MEDICINE_AUTHORITY_SOURCES = (
    captured("MED-WHO-HEALTH-001", "World Health Organization", "https://www.who.int/about/frequently-asked-questions", "experiments/external_sources/medicine/snapshots/MED-WHO-HEALTH-001.html", "sha256:274c2ad78787f127a9f1cf8a479c691e1f89b263d0e21dd49b1753f7805d64f4", "experiments/external_sources/medicine/snapshots/MED-WHO-HEALTH-001.txt", "sha256:4a895afb8bd430d6a619d8f07c5e45c199298dd67a16fd05fa254e47042a345d", "health state and disease-absence distinction"),
    captured("MED-FDA-BIOMARKER-001", "United States Food and Drug Administration", "https://www.fda.gov/drugs/biomarker-qualification-program/about-biomarkers-and-qualification", "experiments/external_sources/medicine/snapshots/MED-FDA-BIOMARKER-001.html", "sha256:93c5ee4b5e3480ed27aa805a7739f4acf7108701fc6f429ae5d4e5a1ad9d3d31", "experiments/external_sources/medicine/snapshots/MED-FDA-BIOMARKER-001.txt", "sha256:f82a712f63b6c8e0de9e2807038051f549a09deccaea480240f9f44e637023fa", "normal and pathogenic processes; risk, diagnostic, monitoring, prognostic, response and safety biomarkers; method and context"),
    captured("MED-CDC-EPIDEMIOLOGY-001", "United States Centers for Disease Control and Prevention", "https://archive.cdc.gov/www_cdc_gov/csels/dsepd/ss1978/lesson1/summary.html", "experiments/external_sources/medicine/snapshots/MED-CDC-EPIDEMIOLOGY-001.html", "sha256:430c2d885670c185491ab9b84d1c703eeaff0eece3ddb69fc855c001fb93478b", "experiments/external_sources/medicine/snapshots/MED-CDC-EPIDEMIOLOGY-001.txt", "sha256:8a6116f8803b6a7f649053b0295feb8faabc17c3ad4513430f2fdda39fe9b7d3", "population, comparison, frequency, pattern, cause, disease and injury epidemiology"),
    captured("MED-ICH-E6R3-001", "International Council for Harmonisation", "https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf", "experiments/external_sources/medicine/snapshots/MED-ICH-E6R3-001.pdf", "sha256:e6ce19e36ce7d2e294f89ee89492b9e035178c3cca48984392bbd92eec9b002c", "experiments/external_sources/medicine/snapshots/MED-ICH-E6R3-001.txt", "sha256:66bf30ef9101596bd9e70ae82e7d55bab519a554c50c77b99670f2294c949592", "final Good Clinical Practice: rights, safety, wellbeing, consent, protocol, allocation, blinding, adverse events, confidentiality and essential records"),
    captured("MED-ICH-E9R1-001", "International Council for Harmonisation", "https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf", "experiments/external_sources/medicine/snapshots/MED-ICH-E9R1-001.pdf", "sha256:f7471f411f1c87ee76783d5b2b9faaeca31d01d530213f71b50d136b39e3b0d9", "experiments/external_sources/medicine/snapshots/MED-ICH-E9R1-001.txt", "sha256:95bcb99e56eb725947eb2acb0b9f0bfe4c6efedb9ffaba18b8232c700e7ff0f5", "final estimand, population, endpoint, intercurrent-event, missing-data and sensitivity-analysis distinctions"),
    captured("MED-FDA-EXPOSURE-RESPONSE-001", "United States Food and Drug Administration", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/exposure-response-relationships-study-design-data-analysis-and-regulatory-applications", "experiments/external_sources/medicine/snapshots/MED-FDA-EXPOSURE-RESPONSE-001.html", "sha256:748ca63404e58ef7f56d321395e646aa918f1ba0e679dbab98e62be95bc40291", "experiments/external_sources/medicine/snapshots/MED-FDA-EXPOSURE-RESPONSE-001.txt", "sha256:38b68aea1735c0e5cee35f0383ea9c2a4959431cf3907c078d425583e87c4338", "dose, exposure, response, benefit and risk study boundary"),
    captured("MED-COCHRANE-HANDBOOK-001", "Cochrane", "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current", "experiments/external_sources/medicine/snapshots/MED-COCHRANE-HANDBOOK-001.html", "sha256:31f56118fc994e14f9703298b798983c2039c6328ee4c5f983f53bdef2bc0004", "experiments/external_sources/medicine/snapshots/MED-COCHRANE-HANDBOOK-001.txt", "sha256:784ffb274b550dcc55be18189542515ab5d2d8e73dd9d86e815ee0b00e91bf57", "current intervention-review scope, study selection, bias, adverse effects and interpretation"),
    captured("MED-COCHRANE-MISSING-EVIDENCE-001", "Cochrane", "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-13", "experiments/external_sources/medicine/snapshots/MED-COCHRANE-MISSING-EVIDENCE-001.html", "sha256:9ebd35b49c689f1b12fa3919051ea9a5ed315b168d9eaec7b1eb8860317d07bb", "experiments/external_sources/medicine/snapshots/MED-COCHRANE-MISSING-EVIDENCE-001.txt", "sha256:a0b274f7613fdc00437f68193541343ad00b26a145dcba905617a9e708f4c4e9", "selective dissemination, missing evidence, benefit overestimation and harm underestimation"),
    captured("MED-WHO-SCREENING-001", "World Health Organization Regional Office for Europe", "https://www.who.int/publications/i/item/9789289054782", "experiments/external_sources/medicine/snapshots/MED-WHO-SCREENING-001.html", "sha256:b56f491a97d2efbe4ff4d59e304649dd1fb1d551a2ca6b88a9bbcf43d385b5f7", "experiments/external_sources/medicine/snapshots/MED-WHO-SCREENING-001.txt", "sha256:8c39fbeb90e52cc44b728718e3b25de977c522f7be189d5d72e7415fcba6708e", "screening population, risk, early intervention, benefits, harms and quality assurance"),
    failed("MED-HHS-CONSENT-001", "United States Department of Health and Human Services Office for Human Research Protections", "https://www.hhs.gov/ohrp/regulations-and-policy/guidance/faq/informed-consent/index.html", "experiments/external_sources/medicine/snapshots/MED-HHS-CONSENT-001.failure.txt", "sha256:f2dda5323f2dfa71d16fad0fb1aa65c5d3ecf0c567603dba0d2076ca0517f291", "prospective informed-consent identity; transport failure preserved and not used for a passing comparison"),
    failed("MED-HHS-PRIVACY-001", "United States Department of Health and Human Services Office for Civil Rights", "https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html", "experiments/external_sources/medicine/snapshots/MED-HHS-PRIVACY-001.failure.txt", "sha256:f2dda5323f2dfa71d16fad0fb1aa65c5d3ecf0c567603dba0d2076ca0517f291", "minimum-necessary privacy identity; transport failure preserved and not used for a passing comparison"),
    captured("MED-NICHD-REHABILITATION-001", "Eunice Kennedy Shriver National Institute of Child Health and Human Development", "https://www.nichd.nih.gov/health/topics/rehabilitation-medicine", "experiments/external_sources/medicine/snapshots/MED-NICHD-REHABILITATION-001.html", "sha256:c1b54134e6cbcfb9542a7c012236395eb609a67a789818f201c5b42202dc8cae", "experiments/external_sources/medicine/snapshots/MED-NICHD-REHABILITATION-001.txt", "sha256:cfecdd3cd39e0a9363ef0d039a740808cb545f8386f29d1f2b29760e394bd808", "rehabilitation function, participation, independence, quality of life and outcomes"),
    captured("MED-STROBE-001", "STROBE Initiative", "https://www.strobe-statement.org/", "experiments/external_sources/medicine/snapshots/MED-STROBE-001.html", "sha256:420432c148d01e7aaaab8f7bcb4bcbc4412d028aa50cd7814fc1b058faf1cf7c", "experiments/external_sources/medicine/snapshots/MED-STROBE-001.txt", "sha256:846530d8dfd2b38331defa6388d14ff7d9eeb4ddeef248f0435428549c18c996", "observational-study planning, conduct, findings and interpretation reporting"),
)


SOURCE_BY_ID = {row.source_id: row for row in MEDICINE_AUTHORITY_SOURCES}


def source_corpus(root: Path, source_id: str) -> str:
    source = SOURCE_BY_ID[source_id]
    if source.transport_status != "captured" or source.text_path is None:
        raise ValueError(f"Medicine source is unavailable and may not support a passing comparison: {source_id}")
    return (root / source.text_path).read_text(encoding="utf-8", errors="replace").casefold()


def validate_sources(root: Path) -> None:
    if len(SOURCE_BY_ID) != len(MEDICINE_AUTHORITY_SOURCES) == 13:
        raise ValueError("Medicine source identities repeat or are incomplete")
    captured_count = 0
    failed_count = 0
    for row in MEDICINE_AUTHORITY_SOURCES:
        if row.transport_status == "captured":
            captured_count += 1
            if row.snapshot_path is None or row.snapshot_hash is None or row.text_path is None or row.text_hash is None:
                raise ValueError(f"Medicine captured source lacks immutable paths: {row.source_id}")
            if hash_file(root / row.snapshot_path) != row.snapshot_hash or hash_file(root / row.text_path) != row.text_hash:
                raise ValueError(f"Medicine snapshot changed: {row.source_id}")
        elif row.transport_status == "failed":
            failed_count += 1
            if row.failure_path is None or row.failure_hash is None or hash_file(root / row.failure_path) != row.failure_hash:
                raise ValueError(f"Medicine failed-transport receipt changed: {row.source_id}")
        else:
            raise ValueError(f"Medicine source has unknown transport status: {row.source_id}")
    if (captured_count, failed_count) != (11, 2):
        raise ValueError("Medicine source transport census changed")


__all__ = ("MedicineSource", "MEDICINE_AUTHORITY_SOURCES", "SOURCE_BY_ID", "source_corpus", "validate_sources")


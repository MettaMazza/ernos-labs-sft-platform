"""Capability-closed post-seal validation for Chemistry ORG-012."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.pericyclic_reaction_batch_v1 import (
    ANALYSIS_PATH,
    ARTICLE_PDF_PATH,
    AUTHORITIES,
    CIF_PATH,
    IDENTITY_PATH,
    INVENTORY_PATH,
    NXML_PATH,
    PERICYCLIC_REACTION_SPEC,
    PRESEAL_PATH,
    SUPPLEMENT_PDF_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


ANALYSIS_HASH = AUTHORITIES[6][1]
INVENTORY_HASH = AUTHORITIES[5][1]
XLINK = "{http://www.w3.org/1999/xlink}href"


def _load_json(root: Path, path: str) -> dict[str, object]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _clean(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def _page_vector(path: Path) -> tuple[dict[str, object], ...]:
    rows = []
    for ordinal, page in enumerate(PdfReader(path).pages, 1):
        text = " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        rows.append({
            "page": ordinal,
            "text_character_count": len(text),
            "text_sha256": _sha256_bytes(text.encode("utf-8")),
            "has_extracted_text": bool(text),
        })
    return tuple(rows)


def exact_analysis(
    root: Path,
    primary_rows: tuple[dict[str, object], ...] | None = None,
) -> tuple[dict[str, object], dict[str, bool]]:
    if hash_file(root / ANALYSIS_PATH) != ANALYSIS_HASH or hash_file(root / INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("ORG-012 analysis or custody inventory changed")
    analysis = _load_json(root, ANALYSIS_PATH)
    inventory = _load_json(root, INVENTORY_PATH)
    vector = dict(analysis)
    recorded_hash = vector.pop("complete_result_vector_sha256", None)
    if recorded_hash != sha256_identity(vector):
        raise ValueError("ORG-012 complete result vector changed")

    member_rows = tuple(inventory["archive_members_in_source_order"])
    if (
        inventory.get("capture_status") != "captured_once_after_claim_specific_value_free_seal"
        or inventory.get("source_recapture_count") != 0
        or inventory.get("package_sha256") != "sha256:370a5498c2d800022c41d3df0329a44a77863d555a0d4c7b5f6c24bfb7d3a4ea"
        or inventory.get("archive_member_count") != 44
        or inventory.get("archive_regular_file_count") != 43
        or inventory.get("all_archive_members_preserved") is not True
    ):
        raise ValueError("ORG-012 archive custody changed")
    for row in member_rows:
        if row["member_type"] != "file":
            continue
        path = root / "experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/members" / row["name"]
        if not path.is_file() or hash_file(path) != row["content_sha256"]:
            raise ValueError(f"ORG-012 archive member changed: {row['name']}")

    xml_root = ET.parse(root / NXML_PATH).getroot()
    table = xml_root.find(".//table-wrap//tbody")
    if table is None:
        raise ValueError("ORG-012 primary table missing")
    reconstructed = []
    current_image = None
    for ordinal, tr in enumerate(table.findall("./tr"), 1):
        cells = list(tr)
        if len(cells) == 10:
            image = cells[0].find(".//inline-graphic")
            current_image = image.get(XLINK) if image is not None else None
            cells = cells[1:]
        if len(cells) != 9 or current_image is None:
            raise ValueError(f"ORG-012 row {ordinal} structure changed")
        values = tuple(_clean(cell) for cell in cells)
        reconstructed.append((ordinal, current_image, *values))
    rows = tuple(analysis["primary_table_rows_in_source_order"]) if primary_rows is None else primary_rows
    if len(rows) != 32 or tuple(row["ordinal"] for row in rows) != tuple(range(1, 33)):
        raise ValueError("ORG-012 primary-row completeness changed")
    for source, recorded in zip(reconstructed, rows):
        if source != (
            recorded["ordinal"], recorded["dienophile_image"], recorded["diene"], recorded["adducts"],
            recorded["temperature_conventional"], recorded["time_conventional"],
            recorded["isolated_yield_conventional"], recorded["endo_exo_experimental_conventional"],
            recorded["endo_exo_calculated_conventional"], recorded["calculated_conformer_distribution_conventional"],
            recorded["homo_lumo_gap_conventional"],
        ):
            raise ValueError(f"ORG-012 primary row {recorded['ordinal']} changed")

    article_pages = _page_vector(root / ARTICLE_PDF_PATH)
    supplement_pages = _page_vector(root / SUPPLEMENT_PDF_PATH)
    if (
        article_pages != tuple(analysis["article_page_text_vector"])
        or supplement_pages != tuple(analysis["supplement_page_text_vector"])
        or len(article_pages) != 12
        or len(supplement_pages) != 203
        or hash_file(root / CIF_PATH) != AUTHORITIES[10][1]
    ):
        raise ValueError("ORG-012 complete article, supplement or CIF changed")

    pericyclic = _load_json(root, AUTHORITIES[13][0])
    cycloaddition = _load_json(root, AUTHORITIES[14][0])
    pericyclic_text = " ".join(row["text"] for row in pericyclic["term"]["definitions"]).casefold()
    cycloaddition_text = " ".join(row["text"] for row in cycloaddition["term"]["definitions"]).casefold()
    checks: dict[str, bool] = {
        "SFT-CHEM-ORG-012-IUPAC-PERICYCLIC": all(
            phrase in pericyclic_text for phrase in ("concerted reorganization of bonding", "cyclic array", "cyclic transition state")
        ),
        "SFT-CHEM-ORG-012-IUPAC-CYCLOADDITION": all(
            phrase in cycloaddition_text for phrase in ("two or more unsaturated", "formation of a cyclic adduct", "net reduction of the bond multiplicity")
        ),
    }
    for row in rows:
        checks[f"SFT-CHEM-ORG-012-PRIMARY-ROW-{row['ordinal']:02d}"] = bool(
            row["dienophile_image_sha256"].startswith("sha256:")
            and row["experimental_ratio_status"] in ("reported", "unresolved_absent_in_primary_table")
            and row["preference_class"] in (
                "first_reported_class_preferred", "second_reported_class_preferred",
                "equal_reported_classes", "one_reported_class_at_conventional_zero", "unresolved",
            )
        )
    checks.update({
        "SFT-CHEM-ORG-012-COMPLETE-ARTICLE": len(article_pages) == 12,
        "SFT-CHEM-ORG-012-COMPLETE-SUPPLEMENT": len(supplement_pages) == 203,
        "SFT-CHEM-ORG-012-COMPLETE-CIF": hash_file(root / CIF_PATH) == AUTHORITIES[10][1],
        "SFT-CHEM-ORG-012-COMPLETE-PACKAGE": len(member_rows) == 44 and inventory["all_archive_members_preserved"] is True,
    })
    expected = tuple(row.target_id for row in PERICYCLIC_REACTION_SPEC.target_rows)
    if tuple(checks) != expected or not all(checks.values()):
        failed = tuple(key for key, passed in checks.items() if not passed)
        raise ValueError(f"ORG-012 complete target comparison changed: {failed}")
    if (
        analysis["primary_table_row_count"] != 32
        or analysis["experimental_ratio_reported_count"] != 28
        or analysis["experimental_ratio_unresolved_count"] != 4
        or analysis["first_reported_class_preferred_count"] != 22
        or analysis["second_reported_class_preferred_count"] != 5
        or analysis["equal_reported_classes_count"] != 1
        or analysis["both_relative_classes_reported_count"] != 28
        or analysis["all_reported_experimental_rows_preserve_both_relative_classes"] is not True
        or analysis["one_target_independent_universal_preference_observed"] is not False
    ):
        raise ValueError("ORG-012 measured-value summary changed")
    summary = {
        "archive_member_count": 44,
        "archive_regular_file_count": 43,
        "article_page_count": 12,
        "supplement_page_count": 203,
        "primary_table_row_count": 32,
        "reported_experimental_ratio_count": 28,
        "unresolved_experimental_ratio_count": 4,
        "first_class_preference_count": 22,
        "second_class_preference_count": 5,
        "equal_class_count": 1,
        "both_classes_reported_count": 28,
        "complete_result_vector_sha256": recorded_hash,
    }
    return summary, checks


class PericyclicReactionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = PERICYCLIC_REACTION_SPEC

    def validate(self, sealed):
        self.spec.validate()
        analysis, checks = exact_analysis(self.root)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        expected = self.spec.expected_observation_label
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={
                target_id: HeldLabel("external-observation", expected if passed else "adverse-mismatch")
                for target_id, passed in checks.items()
            },
            custody_nonce=sha256_identity((registration_hash, ANALYSIS_HASH, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_document, audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_document) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-012 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = tuple({
            "target_id": target_id,
            "predicted": execution.output.label,
            "observed": release.targets[target_id].label,
            "passed": execution.output.label == release.targets[target_id].label,
        } for target_id in checks)
        try:
            source = _load_json(self.root, ANALYSIS_PATH)
            exact_analysis(self.root, tuple(source["primary_table_rows_in_source_order"][:-1]))
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-org-012-comparison/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-012 target release changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "omission_rejected": omission_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "complete official 44-member open-access package and all 43 files retained",
            "all 32 primary reaction rows retained in source order",
            "28 reported experimental ratios and four unresolved rows retained",
            "22 first-class preferences, five second-class preferences and one equal row observed",
            "both relative orientation classes reported in all 28 measured rows",
            "complete 12-page article, 203-page supplement and crystallographic file retained",
            f"complete result vector {analysis['complete_result_vector_sha256']}",
        )
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(row.source_id for row in self.spec.target_rows), measurements,
            sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = ("PericyclicReactionValidator", "exact_analysis")

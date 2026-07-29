"""Capability-closed post-seal validation for Chemistry ORG-013."""

from __future__ import annotations

from io import BytesIO
import hashlib
import json
import platform
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.radical_reaction_network_batch_v1 import (
    ANALYSIS_PATH, ARTICLE_PDF_PATH, AUTHORITIES, INVENTORY_PATH, NXML_PATH,
    RADICAL_REACTION_NETWORK_SPEC, SUPPLEMENT_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor,
    TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


ANALYSIS_HASH = AUTHORITIES[6][1]
INVENTORY_HASH = AUTHORITIES[5][1]


def _load(root: Path, path: str) -> dict[str, object]:
    return json.loads((root / path).read_text())


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _clean(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def _pages(reader: PdfReader) -> tuple[dict[str, object], ...]:
    rows = []
    for ordinal, page in enumerate(reader.pages, 1):
        text = " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        rows.append({"page": ordinal, "text_character_count": len(text), "text_sha256": _digest(text.encode()), "has_extracted_text": bool(text)})
    return tuple(rows)


def exact_analysis(root: Path, table_rows: tuple[dict[str, object], ...] | None = None) -> tuple[dict[str, object], dict[str, bool]]:
    if hash_file(root / ANALYSIS_PATH) != ANALYSIS_HASH or hash_file(root / INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("ORG-013 analysis or inventory changed")
    analysis = _load(root, ANALYSIS_PATH)
    vector = dict(analysis)
    recorded_hash = vector.pop("complete_result_vector_sha256", None)
    if recorded_hash != sha256_identity(vector):
        raise ValueError("ORG-013 complete result vector changed")
    inventory = _load(root, INVENTORY_PATH)
    members = tuple(inventory["archive_members_in_source_order"])
    if (
        inventory.get("capture_status") != "captured_once_after_claim_specific_value_free_seal"
        or inventory.get("source_recapture_count") != 0
        or inventory.get("package_sha256") != "sha256:136da4bfe80ce8ac9d9875c156ed97ebf819594d975bcca4b4ea3cade90a7f0d"
        or len(members) != 24 or inventory.get("archive_regular_file_count") != 23
        or inventory.get("all_archive_members_preserved") is not True
    ):
        raise ValueError("ORG-013 archive custody changed")
    member_root = root / "experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/members"
    for row in members:
        if row["member_type"] == "file":
            path = member_root / row["name"]
            if not path.is_file() or hash_file(path) != row["content_sha256"]:
                raise ValueError(f"ORG-013 archive member changed: {row['name']}")

    xml_root = ET.parse(root / NXML_PATH).getroot()
    reconstructed = []
    for table_ordinal, table in enumerate(xml_root.findall(".//table-wrap"), 1):
        rows = tuple(tuple(_clean(cell) for cell in list(tr)) for tr in table.findall(".//tbody/tr"))
        reconstructed.append({
            "table": table_ordinal,
            "caption": _clean(table.find("caption")),
            "headers": tuple(_clean(row) for row in table.findall(".//thead//th")),
            "rows_in_source_order": rows,
            "row_count": len(rows),
        })
    recorded_tables = tuple(analysis["tables_in_source_order"]) if table_rows is None else table_rows
    normalized_recorded = tuple({
        "table": row["table"],
        "caption": row["caption"],
        "headers": tuple(row["headers"]),
        "rows_in_source_order": tuple(tuple(cell for cell in source_row) for source_row in row["rows_in_source_order"]),
        "row_count": row["row_count"],
    } for row in recorded_tables)
    if tuple(reconstructed) != normalized_recorded or tuple(row["row_count"] for row in recorded_tables) != (47, 12, 4, 4):
        raise ValueError("ORG-013 table reconstruction or completeness changed")

    article_pages = _pages(PdfReader(root / ARTICLE_PDF_PATH))
    with ZipFile(root / SUPPLEMENT_PATH) as archive:
        items = archive.infolist()
        if len(items) != 1 or items[0].filename != analysis["supplement_archive_member"]["filename"]:
            raise ValueError("ORG-013 supplement archive changed")
        supplement_payload = archive.read(items[0])
    supplement_pages = _pages(PdfReader(BytesIO(supplement_payload)))
    if (
        article_pages != tuple(analysis["article_page_text_vector"])
        or supplement_pages != tuple(analysis["supplement_page_text_vector"])
        or len(article_pages) != 24 or len(supplement_pages) != 5
        or _digest(supplement_payload) != analysis["supplement_archive_member"]["sha256"]
    ):
        raise ValueError("ORG-013 complete article or supplement changed")

    iupac = [_load(root, AUTHORITIES[index][0]) for index in (12, 13, 14)]
    definitions = [" ".join(row["text"] for row in item["term"]["definitions"]).casefold() for item in iupac]
    checks: dict[str, bool] = {
        "SFT-CHEM-ORG-013-IUPAC-CHAIN": all(x in definitions[0] for x in ("reactive reaction intermediates", "continuously regenerated", "propagation step")),
        "SFT-CHEM-ORG-013-IUPAC-INITIATION": all(x in definitions[1] for x in ("generating free radicals", "induce a chain reaction")),
        "SFT-CHEM-ORG-013-IUPAC-TERMINATION": all(x in definitions[2] for x in ("reactive intermediates are destroyed or rendered inactive", "ending the chain")),
    }
    for table in recorded_tables:
        for ordinal, row in enumerate(table["rows_in_source_order"], 1):
            checks[f"SFT-CHEM-ORG-013-TABLE-{table['table']}-ROW-{ordinal:02d}"] = bool(row and all(isinstance(cell, str) for cell in row))
    checks.update({
        "SFT-CHEM-ORG-013-COMPLETE-ARTICLE": len(article_pages) == 24,
        "SFT-CHEM-ORG-013-COMPLETE-SUPPLEMENT": len(supplement_pages) == 5,
        "SFT-CHEM-ORG-013-COMPLETE-PACKAGE": len(members) == 24,
    })
    expected = tuple(row.target_id for row in RADICAL_REACTION_NETWORK_SPEC.target_rows)
    if tuple(checks) != expected or not all(checks.values()) or not all(analysis["structural_relation_checks"].values()):
        raise ValueError("ORG-013 complete target comparison changed")
    if analysis["complete_table_row_count"] != 67 or analysis["table_row_counts"] != [47, 12, 4, 4]:
        raise ValueError("ORG-013 measured row summary changed")
    summary = {
        "archive_member_count": 24,
        "archive_regular_file_count": 23,
        "article_page_count": 24,
        "supplement_page_count": 5,
        "table_count": 4,
        "complete_table_row_count": 67,
        "small_chain_termination_activation_energy_rows": analysis["small_chain_termination_activation_energy_rows"],
        "negative_signed_degree_of_polymerization_energy_rows_preserved": analysis["negative_signed_degree_of_polymerization_energy_rows_preserved"],
        "complete_result_vector_sha256": recorded_hash,
    }
    return summary, checks


class RadicalReactionNetworkValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = RADICAL_REACTION_NETWORK_SPEC

    def validate(self, sealed):
        self.spec.validate()
        analysis, checks = exact_analysis(self.root)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        expected = self.spec.expected_observation_label
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={key: HeldLabel("external-observation", expected if passed else "adverse-mismatch") for key, passed in checks.items()},
            custody_nonce=sha256_identity((registration_hash, ANALYSIS_HASH, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-013 prediction package changed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": key, "predicted": execution.output.label, "observed": release.targets[key].label, "passed": execution.output.label == release.targets[key].label} for key in checks)
        try:
            source = _load(self.root, ANALYSIS_PATH)
            exact_analysis(self.root, tuple(source["tables_in_source_order"][:-1]))
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-org-013-comparison/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-013 target release changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission_rejected, "trace": execution.trace_hash}
        measurements = (
            "complete official 24-member package and all 23 files retained",
            "all four primary tables and all 67 rows retained in source order",
            "initiation, positive propagation, two-active-support termination and chain-length dependence retained",
            "all 24 article pages and all five supplementary pages retained",
            "all external energy, rate, chain-length, temperature, concentration, uncertainty, sign, unit and absence inscriptions retained",
            f"complete result vector {analysis['complete_result_vector_sha256']}",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("RadicalReactionNetworkValidator", "exact_analysis")

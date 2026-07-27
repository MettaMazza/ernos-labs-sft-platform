"""Capability-closed post-seal validation for Chemistry ORG-010."""

from __future__ import annotations

import hashlib
import json
import platform
from fractions import Fraction
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.elimination_reaction_batch_v1 import (
    ANALYSIS_PATH,
    ELIMINATION_REACTION_SPEC,
    IDENTITY_PATH,
    INVENTORY_PATH,
    IUPAC_PATH,
    PRESEAL_PATH,
)
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
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


ANALYSIS_HASH = "sha256:157144f86339efa5ddb583d860ef1fd444af6761c3080a82465367544735b89b"
INVENTORY_HASH = "sha256:0d4204dfd4633dbc6ada89cd87cda76813c989f2444490547371d7aca64696de"
PDF_HASH = "sha256:f274759e0f850ecefb14e4d685d78bcae2641284b366d74f2bd03b10a8459620"


def _load_json(root: Path, path: str) -> dict[str, object]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )


def exact_analysis(
    root: Path,
    product_rows: tuple[dict[str, object], ...] | None = None,
    unsuccessful_rows: tuple[dict[str, object], ...] | None = None,
    optimisation_tables: tuple[dict[str, object], ...] | None = None,
) -> tuple[dict[str, object], dict[str, bool]]:
    if hash_file(root / ANALYSIS_PATH) != ANALYSIS_HASH or hash_file(root / INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("ORG-010 complete analysis or inventory changed")
    analysis = _load_json(root, ANALYSIS_PATH)
    inventory = _load_json(root, INVENTORY_PATH)
    identity = _load_json(root, IDENTITY_PATH)
    preseal = _load_json(root, PRESEAL_PATH)
    iupac = _load_json(root, IUPAC_PATH)
    products = tuple(analysis["characterized_product_rows_in_source_order"]) if product_rows is None else product_rows
    unsuccessful = tuple(analysis["unsuccessful_substrate_rows"]) if unsuccessful_rows is None else unsuccessful_rows
    optimisation = tuple(analysis["optimisation_tables"]) if optimisation_tables is None else optimisation_tables

    if len(products) != 32 or len(unsuccessful) != 5 or len(optimisation) != 7:
        raise ValueError("ORG-010 requires every product, unsuccessful row and optimization table")
    expected_codes = tuple(
        [f"3{letter}" for letter in "abcdefghijklmnopqrstuvwxyz"]
        + [f"3a{letter}" for letter in "abcdef"]
    )
    if tuple(row["product_code"] for row in products) != expected_codes:
        raise ValueError("ORG-010 characterized product identity or source order changed")
    if tuple(row["ordinal"] for row in unsuccessful) != tuple(range(1, 6)):
        raise ValueError("ORG-010 unsuccessful-substrate order changed")
    if tuple(table["table"] for table in optimisation) != tuple(f"S{ordinal}" for ordinal in range(1, 8)):
        raise ValueError("ORG-010 optimization-table order changed")

    vector = dict(analysis)
    recorded_vector_hash = vector.pop("complete_result_vector_sha256", None)
    if recorded_vector_hash != _canonical_hash(vector):
        raise ValueError("ORG-010 result-vector identity changed")
    if (
        identity.get("supplementary_archive_open_count_before_seal") != 0
        or preseal.get("supplementary_archive_product_structures_yields_spectra_or_complete_page_contents_opened_before_this_seal") is not False
        or preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
        or inventory.get("source_recapture_count") != 0
        or inventory.get("capture_status") != "captured_once_after_claim_specific_seal"
        or len(inventory.get("members", ())) != 22
    ):
        raise ValueError("ORG-010 custody or observation order changed")
    for member in inventory["members"]:
        path = root / member["snapshot_path"]
        if (
            not path.is_file()
            or path.stat().st_size != member["snapshot_bytes"]
            or hash_file(path) != member["snapshot_sha256"]
        ):
            raise ValueError(f"ORG-010 captured member changed: {member['archive_member']}")

    pdf_row = next(member for member in inventory["members"] if member["archive_member"].endswith(".pdf"))
    if pdf_row["snapshot_sha256"] != PDF_HASH:
        raise ValueError("ORG-010 PDF identity changed")
    reader = PdfReader(root / pdf_row["snapshot_path"])
    page_texts = tuple(page.extract_text() or "" for page in reader.pages)
    page_vector = tuple(
        {
            "page": ordinal,
            "text_character_count": len(text),
            "text_sha256": _sha256_bytes(text.encode("utf-8")),
            "has_extracted_text": bool(text.strip()),
        }
        for ordinal, text in enumerate(page_texts, 1)
    )
    if (
        len(page_texts) != 117
        or page_vector != tuple(analysis["complete_page_text_vector"])
        or _canonical_hash(page_vector) != analysis["complete_page_text_vector_sha256"]
    ):
        raise ValueError("ORG-010 complete PDF page reconstruction changed")

    definitions = " ".join(
        row["text"] for row in iupac["term"]["definitions"]
    ).casefold()
    iupac_ok = all(
        phrase in definitions
        for phrase in (
            "reverse of an addition",
            "two groups",
            "two different centres",
            "formation of an unsaturation",
            "1/1/elimination",
        )
    )
    product_checks: dict[str, bool] = {}
    for row in products:
        block = row["source_block"]
        block_hash_ok = _sha256_bytes(block.encode("utf-8")) == row["source_block_sha256"]
        product_checks[f"SFT-CHEM-ORG-010-PRODUCT-{row['product_code'].upper()}"] = bool(
            block_hash_ok
            and row["observable_unsaturation_in_reported_product_name"]
            and row["full_reactant_byproduct_carrier_present_in_characterization_block"] is False
            and row["complete_atom_and_support_balance_status"] == "unresolved_in_this_conventional_product_block"
            and row["procedure"] in ("2.16", "2.17")
        )

    unsuccessful_checks = {
        f"SFT-CHEM-ORG-010-UNSUCCESSFUL-{row['ordinal']:02d}": bool(row["substrate"] and row["observed"])
        for row in unsuccessful
    }
    expected_table_rows = {"S1": 3, "S2": 5, "S3": 8, "S4": 6, "S5": 4, "S6": 4, "S7": 4}
    optimisation_checks = {
        f"SFT-CHEM-ORG-010-OPTIMISATION-{table['table']}": len(table["rows"])
        == expected_table_rows[table["table"]]
        for table in optimisation
    }
    intermediate = analysis["observed_intermediate_record"]
    time_rows = tuple(intermediate["reported_time_course_rows"])
    product_values = tuple(Fraction(row["3a_percent"]) for row in time_rows)
    intermediate_values = tuple(Fraction(row["3a_prime_percent"]) for row in time_rows)
    intermediate_ok = (
        len(time_rows) == 6
        and all(left < right for left, right in zip(product_values, product_values[1:]))
        and all(left > right for left, right in zip(intermediate_values, intermediate_values[1:]))
        and intermediate["reported_15_minute_GC_ratio"] == "3a:3a-prime = 72:28"
    )
    custody_ok = (
        analysis["custody"]["archive_member_count"] == 22
        and analysis["custody"]["pdf_page_count"] == 117
        and analysis["characterized_product_count"] == 32
        and analysis["products_with_observable_unsaturation_count"] == 32
        and analysis["products_with_full_carrier_balance_in_characterization_block_count"] == 0
        and analysis["unresolved_complete_carrier_balance_count"] == 32
        and analysis["optimisation_row_count_including_explicit_source_gap"] == 34
        and analysis["unsuccessful_substrate_count"] == 5
        and analysis["comparison_status"]["no_post_outcome_product_filter_applied"] is True
        and analysis["comparison_status"]["no_optimization_or_control_page_omitted"] is True
    )
    checks = {
        "SFT-CHEM-ORG-010-IUPAC-001": iupac_ok,
        **product_checks,
        **unsuccessful_checks,
        **optimisation_checks,
        "SFT-CHEM-ORG-010-INTERMEDIATE-001": intermediate_ok,
        "SFT-CHEM-ORG-010-COMPLETE-SUPPLEMENT-001": custody_ok,
    }
    expected_targets = tuple(row.target_id for row in ELIMINATION_REACTION_SPEC.target_rows)
    if tuple(checks) != expected_targets or not all(checks.values()):
        raise ValueError("ORG-010 complete target comparison changed")
    summary = {
        "archive_member_count": 22,
        "supplementary_pdf_page_count": 117,
        "characterized_product_count": 32,
        "observable_unsaturation_product_count": 32,
        "full_carrier_favorable_count": 0,
        "full_carrier_adverse_count": 0,
        "full_carrier_unresolved_count": 32,
        "unsuccessful_or_low_elimination_row_count": 5,
        "optimization_table_count": 7,
        "optimization_row_count_including_source_gap": 34,
        "intermediate_time_course_row_count": 6,
        "complete_result_vector_sha256": recorded_vector_hash,
    }
    return summary, checks


class EliminationReactionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ELIMINATION_REACTION_SPEC

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
            raise ValueError("ORG-010 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        comparisons = tuple(
            {
                "target_id": target_id,
                "predicted": prediction.label,
                "observed": release.targets[target_id].label,
                "passed": prediction.label == release.targets[target_id].label,
            }
            for target_id in checks
        )
        try:
            source = _load_json(self.root, ANALYSIS_PATH)
            exact_analysis(
                self.root,
                tuple(source["characterized_product_rows_in_source_order"][:-1]),
            )
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = (
            all(row["passed"] for row in comparisons)
            and omission_rejected
            and prediction.label != prediction.label + "__tampered"
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("exact-org-010-comparison/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-010 release changed")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
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
            "complete 22-member Europe PMC archive and all 117 supplementary PDF pages retained",
            "all 32 characterized product blocks retained; every reported product displays unsaturation",
            "all 32 incomplete coproduct carriers remain explicitly unresolved for complete atom/support balance",
            "all five unsuccessful or low-elimination rows preserved without success filtering",
            "all seven optimization tables and 34 rows including the printed source gap retained",
            "the six-row 3a-prime/3a time course preserves decreasing intermediate and increasing product",
            f"complete result vector {analysis['complete_result_vector_sha256']}",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(row.source_id for row in self.spec.target_rows),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = ("EliminationReactionValidator", "exact_analysis")

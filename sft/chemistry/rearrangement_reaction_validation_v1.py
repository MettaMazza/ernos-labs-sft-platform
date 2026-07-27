"""Capability-closed post-seal validation for Chemistry ORG-011."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.rearrangement_reaction_batch_v1 import (
    ANALYSIS_PATH,
    AUTHORITIES,
    IDENTITY_PATH,
    INVENTORY_PATH,
    PDF_PATH,
    PRESEAL_PATH,
    REARRANGEMENT_REACTION_SPEC,
    V1_ANALYSIS_PATH,
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


ANALYSIS_HASH = AUTHORITIES[12][1]
INVENTORY_HASH = AUTHORITIES[10][1]
PDF_HASH = AUTHORITIES[13][1]


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
    pair_rows: tuple[dict[str, object], ...] | None = None,
) -> tuple[dict[str, object], dict[str, bool]]:
    if hash_file(root / ANALYSIS_PATH) != ANALYSIS_HASH or hash_file(root / INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("ORG-011 analysis or custody inventory changed")
    analysis = _load_json(root, ANALYSIS_PATH)
    inventory = _load_json(root, INVENTORY_PATH)
    identity = _load_json(root, IDENTITY_PATH)
    preseal = _load_json(root, PRESEAL_PATH)
    v1 = _load_json(root, V1_ANALYSIS_PATH)
    pairs = tuple(analysis["explicit_claisen_source_product_pairs_in_source_order"]) if pair_rows is None else pair_rows

    vector = dict(analysis)
    recorded_hash = vector.pop("complete_result_vector_sha256", None)
    if recorded_hash != _canonical_hash(vector):
        raise ValueError("ORG-011 result vector changed")
    if (
        len(pairs) != 8
        or tuple(row["ordinal"] for row in pairs) != tuple(range(1, 9))
        or identity.get("supplementary_pdf_open_count_before_seal") != 0
        or preseal.get("new_supplementary_pdf_pages_characterization_structures_formulas_or_spectra_opened_before_this_seal") is not False
        or preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
        or inventory.get("source_recapture_count") != 0
        or inventory.get("capture_status") != "captured_once_after_claim_specific_v2_seal"
        or inventory.get("snapshot_sha256") != PDF_HASH
    ):
        raise ValueError("ORG-011 observation order, pair boundary or custody changed")

    reader = PdfReader(root / PDF_PATH)
    page_texts = tuple(" ".join((page.extract_text() or "").replace("\u00ad", "").split()) for page in reader.pages)
    page_vector = tuple(
        {
            "page": ordinal,
            "text_character_count": len(text),
            "text_sha256": _sha256_bytes(text.encode("utf-8")),
            "has_extracted_text": bool(text),
        }
        for ordinal, text in enumerate(page_texts, 1)
    )
    if (
        len(page_texts) != 38
        or page_vector != tuple(analysis["complete_page_text_vector"])
        or _canonical_hash(page_vector) != analysis["complete_page_text_vector_sha256"]
    ):
        raise ValueError("ORG-011 complete 38-page reconstruction changed")

    iupac_molecular = _load_json(root, AUTHORITIES[14][0])
    iupac_stage = _load_json(root, AUTHORITIES[16][0])
    molecular_text = " ".join(row["text"] for row in iupac_molecular["term"]["definitions"]).casefold()
    stage_text = " ".join(row["text"] for row in iupac_stage["term"]["definitions"]).casefold()
    alias_text = (root / AUTHORITIES[15][0]).read_text(encoding="utf-8").casefold()
    iupac_checks = {
        "SFT-CHEM-ORG-011-IUPAC-MOLECULAR": all(
            phrase in molecular_text
            for phrase in ("change of connectivity", "product is isomeric with the reactant", "claisen rearrangement")
        ),
        "SFT-CHEM-ORG-011-IUPAC-REARRANGEMENT": all(
            phrase in alias_text for phrase in ("molecular rearrangement", "change of", "connectivity")
        ),
        "SFT-CHEM-ORG-011-IUPAC-STAGE": all(
            phrase in stage_text for phrase in ("making and breaking of bonds", "atoms common to a reactant")
        ),
    }

    pair_checks = {}
    for row in pairs:
        source_page = page_texts[row["source_characterization_page"] - 1]
        product_page = page_texts[row["product_characterization_page"] - 1]
        enumerated = row["independently_enumerated_source_formula"]
        passed = (
            row["independently_enumerated_product_formula"] == enumerated
            and row["source_atom_inventory"] == row["product_atom_inventory"]
            and row["formula_pair_status"] == "favorable_identical_exact_endpoint_atom_inventory"
            and row["complete_source_product_structure_pair_drawn"] is True
            and row["positive_constitutional_incidence_change_drawn"] is True
            and row["source_structure_relation"] != row["product_structure_relation"]
            and row["printed_formulae_consistent_with_structure_enumeration"] is True
            and row["mass_inscriptions_cross_check_enumeration"] is True
            and row["source_mass_inscription"].casefold() in source_page.casefold()
            and row["product_mass_inscription"].casefold() in product_page.casefold()
            and row["source_page_text_sha256"] == _sha256_bytes(source_page.encode("utf-8"))
            and row["product_page_text_sha256"] == _sha256_bytes(product_page.encode("utf-8"))
        )
        pair_checks[f"SFT-CHEM-ORG-011-CLAISEN-PAIR-{row['ordinal']:02d}"] = passed

    optimization_checks = {
        f"SFT-CHEM-ORG-011-OPTIMIZATION-{row['page']:02d}": bool(
            row["complete_page_text"] == page_texts[row["page"] - 1]
            and row["complete_page_text_sha256"] == _sha256_bytes(page_texts[row["page"] - 1].encode("utf-8"))
            and row["signed_stereochemical_inscriptions_preserved"]
            and (row["page"] != 3 or row["explicit_non_detection_preserved"])
        )
        for row in analysis["optimization_and_control_pages"]
    }
    transition = analysis["transition_relation"]
    transition_ok = all(fragment.casefold() in page_texts[36].casefold() for fragment in transition["required_fragments"])
    v1_ok = (
        analysis["first_blind_surface"]["preserved_without_relabelling"] is True
        and v1.get("comparison_status", {}).get("complete_atom_support_pairs_favorable") == 0
        and v1.get("comparison_status", {}).get("complete_atom_support_pairs_adverse") == 0
        and v1.get("comparison_status", {}).get("complete_atom_support_pairs_unresolved") == 52
        and v1.get("comparison_status", {}).get("blind_supplement_does_not_by_itself_close_the_registered_exact_structure_vector") is True
    )
    custody_ok = (
        analysis["custody"]["pdf_page_count"] == 38
        and analysis["custody"]["all_pages_retained"] is True
        and analysis["pair_count"] == 8
        and analysis["exact_endpoint_inventory_favorable_count"] == 8
        and analysis["exact_endpoint_inventory_adverse_count"] == 0
        and analysis["exact_endpoint_inventory_unresolved_count"] == 0
        and analysis["drawn_positive_constitutional_incidence_change_count"] == 8
        and analysis["comparison_status"]["no_yield_selectivity_formula_or_favorable_result_filter_applied"] is True
    )
    checks = {
        **iupac_checks,
        **pair_checks,
        **optimization_checks,
        "SFT-CHEM-ORG-011-TRANSITION-RELATION": transition_ok,
        "SFT-CHEM-ORG-011-FIRST-BLIND-SURFACE": v1_ok,
        "SFT-CHEM-ORG-011-COMPLETE-SUPPLEMENT": custody_ok,
    }
    expected = tuple(row.target_id for row in REARRANGEMENT_REACTION_SPEC.target_rows)
    if tuple(checks) != expected or not all(checks.values()):
        failed = tuple(key for key, passed in checks.items() if not passed)
        raise ValueError(f"ORG-011 complete target comparison changed: {failed}")
    summary = {
        "supplementary_pdf_page_count": 38,
        "explicit_source_product_pair_count": 8,
        "exact_endpoint_inventory_favorable_count": 8,
        "exact_endpoint_inventory_adverse_count": 0,
        "exact_endpoint_inventory_unresolved_count": 0,
        "positive_constitutional_incidence_change_count": 8,
        "optimization_control_page_count": 2,
        "first_blind_surface_preserved_unresolved": True,
        "complete_result_vector_sha256": recorded_hash,
    }
    return summary, checks


class RearrangementReactionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = REARRANGEMENT_REACTION_SPEC

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
            raise ValueError("ORG-011 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = tuple(
            {
                "target_id": target_id,
                "predicted": execution.output.label,
                "observed": release.targets[target_id].label,
                "passed": execution.output.label == release.targets[target_id].label,
            }
            for target_id in checks
        )
        try:
            source = _load_json(self.root, ANALYSIS_PATH)
            exact_analysis(self.root, tuple(source["explicit_claisen_source_product_pairs_in_source_order"][:-1]))
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-org-011-comparison/1", self.spec.falsification_condition)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-011 target release changed")
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
            "complete official 38-page supporting-information PDF retained",
            "all eight source/product structures independently atom-enumerated",
            "eight exact endpoint inventories favorable; no adverse or unresolved endpoint inventory",
            "all eight pairs exhibit a positive constitutional-incidence change",
            "all optimization, non-detection, signed stereochemical and spectral surfaces retained",
            "first incomplete blind surface preserved as unresolved without relabelling",
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


__all__ = ("RearrangementReactionValidator", "exact_analysis")

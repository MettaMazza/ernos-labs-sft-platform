"""Implementation-distinct, capability-closed validation for ANAL-006--008."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import platform
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.nmr_family_batch_v1 import (
    ANALYSIS_PATH,
    AUTHORITIES,
    COUPLING_SPEC,
    RELAXATION_SPEC,
    SHIFT_SPEC,
    SPECS,
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


MISSING = {".", "?"}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


@lru_cache(maxsize=None)
def independently_read_loop(path: Path, prefix: str) -> tuple[dict[str, object], ...]:
    """A line/state parser independent of the source reconstruction builder."""
    lines = path.read_text(encoding="utf-8").splitlines()
    result: list[dict[str, object]] = []
    saveframe = "global"
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("save_"):
            saveframe = "global" if stripped == "save_" else stripped[5:]
            index += 1
            continue
        if stripped != "loop_":
            index += 1
            continue
        index += 1
        tags: list[str] = []
        while index < len(lines) and lines[index].strip().startswith("_"):
            tags.append(lines[index].strip().split()[0])
            index += 1
        retained = bool(tags) and tags[0].startswith(prefix)
        values: list[str] = []
        while index < len(lines) and lines[index].strip() != "stop_":
            row = lines[index].strip()
            if retained and row and not row.startswith("#"):
                # Registered measurement loops contain only whitespace-delimited
                # scalar fields. Quoted experiment-description loops are outside
                # the value-vector prefixes and therefore never enter here.
                values.extend(row.split())
            index += 1
        if retained:
            if not tags or len(values) % len(tags):
                raise ValueError(f"independent loop reconstruction failed: {path.name}:{prefix}")
            for offset in range(0, len(values), len(tags)):
                result.append({
                    "saveframe": saveframe,
                    "raw": dict(zip(tags, values[offset : offset + len(tags)])),
                })
        index += 1
    return tuple(result)


def assert_exact_translations(rows: list[dict[str, object]], main_tag: str, positive_side: str, negative_side: str, *, rate_zero: bool = False) -> None:
    for row in rows:
        for tag, translation in row["exact_translation"].items():
            token = row["raw"][tag]
            if token in MISSING:
                if translation["native_magnitude"] != "EmptyOne" or translation["custody_status"] != "absent-or-unreported":
                    raise ValueError("absent NMR field lost structural EmptyOne custody")
                continue
            value = Decimal(token)
            if not value.is_finite():
                raise ValueError("non-finite external NMR token")
            if value == 0:
                if translation["native_magnitude"] != "EmptyOne":
                    raise ValueError("external zero entered native NMR magnitude")
                if tag == main_tag and rate_zero and (
                    translation["custody_status"] != "unresolved-external-zero-inscription"
                    or translation["native_side"] != "unresolved"
                ):
                    raise ValueError("external zero rate was not retained as unresolved structural absence")
                continue
            magnitude = Fraction(abs(value))
            expected = f"{magnitude.numerator}/{magnitude.denominator}"
            if translation["native_magnitude"] != expected:
                raise ValueError("exact rational NMR translation changed")
            if tag == main_tag:
                side = positive_side if value > 0 else negative_side
                if translation["native_side"] != side:
                    raise ValueError("held NMR side changed")


def source_surface(root: Path, analysis: dict[str, object]) -> tuple[int, int, int, int]:
    inventory_path = root / "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/source-inventory-v1.json"
    inventory = json.loads(inventory_path.read_text())
    payload = dict(inventory)
    recorded_payload_hash = payload.pop("inventory_payload_sha256")
    if canonical_digest(payload) != recorded_payload_hash:
        raise ValueError("NMR source inventory payload changed")
    pdf_pages = html_documents = characters = source_bytes = 0
    for source in inventory["sources"]:
        path = root / source["path"]
        data = path.read_bytes()
        if len(data) != source["byte_count"] or digest(data) != source["sha256"]:
            raise ValueError(f"captured NMR source changed: {source['path']}")
        stored = analysis["complete_source_reconstruction"][path.name]
        if stored["byte_count"] != len(data) or stored["sha256"] != digest(data):
            raise ValueError("NMR reconstructed source identity changed")
        source_bytes += len(data)
        if source["media_kind"] == "pdf":
            rebuilt = []
            for number, page in enumerate(PdfReader(path).pages, 1):
                text = page.extract_text() or ""
                rebuilt.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
                characters += len(text)
            if rebuilt != stored["complete_page_vector"]:
                raise ValueError("complete IUPAC PDF surface changed")
            pdf_pages += len(rebuilt)
        elif source["media_kind"] == "html":
            text = BeautifulSoup(data, "html.parser").get_text("\n")
            rebuilt = {"character_count": len(text), "text_sha256": digest(text.encode())}
            if rebuilt != stored["complete_document_text"]:
                raise ValueError("complete NMR HTML surface changed")
            html_documents += 1
            characters += len(text)
    if (len(inventory["sources"]), pdf_pages, html_documents, characters) != (
        analysis["complete_source_count"],
        analysis["complete_pdf_page_count"],
        analysis["complete_html_document_count"],
        analysis["complete_extracted_character_count"],
    ):
        raise ValueError("complete NMR source surface count changed")
    return len(inventory["sources"]), pdf_pages, html_documents, source_bytes


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"ANAL-006--008 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis)
    recorded = vector.pop("complete_result_vector_sha256")
    if canonical_digest(vector) != recorded:
        raise ValueError("ANAL-006--008 complete result vector changed")
    sources, pages, htmls, source_bytes = source_surface(root, analysis)
    if (sources, pages, htmls) != (10, 24, 5):
        raise ValueError("ANAL-006--008 registered source extent changed")

    snapshots = root / "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1"
    shift_independent = independently_read_loop(snapshots / "bmr68_3.str", "_Atom_chem_shift.")
    coupling_independent = independently_read_loop(snapshots / "bmr16582_3.str", "_Coupling_constant.")
    t1_independent = independently_read_loop(snapshots / "bmr52365_3.str", "_T1.")
    t1rho_independent = independently_read_loop(snapshots / "bmr52365_3.str", "_T1rho.")
    exchange_independent = independently_read_loop(snapshots / "bmr27257_3.str", "_H_exch_rate.")
    stored_vectors = (
        analysis["anal_006"]["complete_shift_vector"],
        analysis["anal_007"]["complete_coupling_vector"],
        analysis["anal_008"]["complete_t1_vector"],
        analysis["anal_008"]["complete_t1rho_vector"],
        analysis["anal_008"]["complete_hydrogen_exchange_vector"],
    )
    independent_vectors = (shift_independent, coupling_independent, t1_independent, t1rho_independent, exchange_independent)
    for stored, independent in zip(stored_vectors, independent_vectors):
        if tuple({"saveframe": row["saveframe"], "raw": row["raw"]} for row in stored) != independent:
            raise ValueError("implementation-distinct NMR value-vector reconstruction disagreed")

    assert_exact_translations(stored_vectors[0], "_Atom_chem_shift.Val", "higher-frequency", "lower-frequency")
    assert_exact_translations(stored_vectors[1], "_Coupling_constant.Val", "preserving-hand", "alternating-hand")
    assert_exact_translations(stored_vectors[2], "_T1.Val", "positive-time", "inadmissible-external-negative")
    assert_exact_translations(stored_vectors[3], "_T1rho.T1rho_val", "positive-time-or-rate", "inadmissible-external-negative")
    assert_exact_translations(stored_vectors[4], "_H_exch_rate.Val", "positive-rate", "inadmissible-external-negative", rate_zero=True)

    iupac_text = "\n".join(page.extract_text() or "" for page in PdfReader(snapshots / "iupac-nmr-nomenclature-2001.pdf").pages).casefold()
    if not all(term in iupac_text for term in ("chemical shift", "reference compound", "nucleus", "frequency", "ppm")):
        raise ValueError("IUPAC NMR identity surface changed")

    if claim_id == SHIFT_SPEC.claim_id:
        row = analysis["anal_006"]
        values = row["complete_shift_vector"]
        reference = row["complete_reference_vector"][0]["rows"]
        conditions = row["sample_conditions"][0]["rows"]
        checks = {
            "SFT-CHEM-ANAL-006-IDENTITY": len(values) == 556 and all(item["raw"]["_Atom_chem_shift.Entry_ID"] == "68" for item in values),
            "SFT-CHEM-ANAL-006-REFERENCE": len(reference) == 1 and reference[0]["_Chem_shift_ref.Mol_common_name"] == "DSS" and reference[0]["_Chem_shift_ref.Chem_shift_units"] == "ppm" and reference[0]["_Chem_shift_ref.Chem_shift_val"] == "0",
            "SFT-CHEM-ANAL-006-NUCLEUS-SITE": row["nucleus_counts"] == {"H": 556} and len({(item["raw"]["_Atom_chem_shift.Comp_index_ID"], item["raw"]["_Atom_chem_shift.Atom_ID"]) for item in values}) == 556,
            "SFT-CHEM-ANAL-006-SOLVENT-CONDITION": [(item["_Sample_condition_variable.Type"], item["_Sample_condition_variable.Val"], item["_Sample_condition_variable.Val_units"]) for item in conditions] == [("pH", "4.7", "na"), ("temperature", "323", "K")] and row["sample_metadata"][0]["fields"]["_Sample.Solvent_system"] == ".",
            "SFT-CHEM-ANAL-006-COMPLETE-SHIFT-VECTOR": len(values) == 556 and min(Decimal(item["raw"]["_Atom_chem_shift.Val"]) for item in values) == Decimal("0.11") and max(Decimal(item["raw"]["_Atom_chem_shift.Val"]) for item in values) == Decimal("9.82"),
            "SFT-CHEM-ANAL-006-UNCERTAINTY-AMBIGUITY": row["missing_field_counts"]["_Atom_chem_shift.Val_err"] == 556 and row["missing_field_counts"]["_Atom_chem_shift.Ambiguity_code"] == 0,
            "SFT-CHEM-ANAL-006-STATUS-ADVERSE-ABSENT": row["missing_field_counts"]["_Atom_chem_shift.Val"] == 0 and row["missing_field_counts"]["_Atom_chem_shift.Details"] == 556 and row["all_values_errors_ambiguities_absences_and_sites_retained"],
            "SFT-CHEM-ANAL-006-COMPLETE-SOURCE": sources == 10 and analysis["no_target_selection_or_row_filtering"],
        }
        summary = {
            "measured_shift_rows": 556,
            "observed_nucleus": "1H",
            "observed_shift_span_ppm": ["0.11", "9.82"],
            "reference": "DSS at externally inscribed reference 0 ppm; native representation is structural coincidence/EmptyOne",
            "conditions": ["pH 4.7", "323 K"],
            "unreported_value_errors": 556,
        }
    elif claim_id == COUPLING_SPEC.claim_id:
        row = analysis["anal_007"]
        values = row["complete_coupling_vector"]
        codes = {item["raw"]["_Coupling_constant.Code"] for item in values}
        conditions = [item for loop in row["sample_conditions"] for item in loop["rows"]]
        solvent_systems = {item["fields"]["_Sample.Solvent_system"] for item in row["sample_metadata"]}
        checks = {
            "SFT-CHEM-ANAL-007-IDENTITY": len(values) == 643 and row["complete_list_count"] == 10 and all(item["raw"]["_Coupling_constant.Entry_ID"] == "16582" for item in values),
            "SFT-CHEM-ANAL-007-SPIN-PAIR": row["held_side_counts"] == {"alternating-hand": 395, "preserving-hand": 248} and all(item["raw"]["_Coupling_constant.Atom_ID_1"] != item["raw"]["_Coupling_constant.Atom_ID_2"] or item["raw"]["_Coupling_constant.Comp_index_ID_1"] != item["raw"]["_Coupling_constant.Comp_index_ID_2"] for item in values),
            "SFT-CHEM-ANAL-007-BOND-PATH": len(codes) == 10 and all(code.casefold().startswith("2j") for code in codes),
            "SFT-CHEM-ANAL-007-COMPLETE-COUPLING-VECTOR": len(values) == 643 and Counter(item["saveframe"] for item in values) == Counter({"2JCaN_": 70, "2JHNCa": 70, "2JCOHN": 70, "2JCOCa": 70, "2JHaCO": 70, "2JHaCb": 59, "2JCbCO": 51, "2JN_Ha": 64, "2JN_Cb": 49, "2JN_CO": 70}),
            "SFT-CHEM-ANAL-007-VALUE-ERROR-RANGE": min(Decimal(item["raw"]["_Coupling_constant.Val"]) for item in values) == Decimal("-9.55") and max(Decimal(item["raw"]["_Coupling_constant.Val"]) for item in values) == Decimal("4.80") and row["missing_field_counts"]["_Coupling_constant.Val_err"] == 0 and row["missing_field_counts"]["_Coupling_constant.Val_min"] == 643 and row["missing_field_counts"]["_Coupling_constant.Val_max"] == 643,
            "SFT-CHEM-ANAL-007-CONDITION": len(conditions) == 6 and solvent_systems == {"90% H2O/10% D2O", "95% H2O/5% D2O"} and {item["fields"]["_Coupling_constant_list.Spectrometer_frequency_1H"] for item in row["list_metadata"]} == {"500", "600", "950"},
            "SFT-CHEM-ANAL-007-STATUS-ADVERSE-ABSENT": row["held_side_counts"]["alternating-hand"] == 395 and row["missing_field_counts"]["_Coupling_constant.Details"] == 643 and row["all_values_errors_bounds_absences_pairs_and_conditions_retained"],
            "SFT-CHEM-ANAL-007-COMPLETE-SOURCE": sources == 10 and row["all_signed_external_values_translated_to_held_side_plus_positive_exact_magnitude"],
        }
        summary = {
            "measured_coupling_rows": 643,
            "coupling_families": 10,
            "observed_value_span_Hz": ["-9.55 external alternating-hand", "4.80 external preserving-hand"],
            "held_orientation_counts": row["held_side_counts"],
            "reported_error_Hz": "0.50 on all 643 rows",
            "spectrometer_frequencies_MHz": ["500", "600", "950"],
        }
    elif claim_id == RELAXATION_SPEC.claim_id:
        row = analysis["anal_008"]
        t1 = row["complete_t1_vector"]
        t1rho = row["complete_t1rho_vector"]
        exchange = row["complete_hydrogen_exchange_vector"]
        exchange_frames = Counter(item["saveframe"] for item in exchange)
        summary_html = (snapshots / "bmrb-27257-summary.html").read_text().casefold()
        checks = {
            "SFT-CHEM-ANAL-008-IDENTITY": len(t1) == 148 and len(t1rho) == 148 and len(exchange) == 138 and all(item["raw"]["_T1.Entry_ID"] == "52365" for item in t1) and all(item["raw"]["_H_exch_rate.Entry_ID"] == "27257" for item in exchange),
            "SFT-CHEM-ANAL-008-RELAXATION-PROCESSES": len(row["t1_list_metadata"]) == 2 and len(row["t1rho_list_metadata"]) == 2 and {item["fields"]["_Heteronucl_T1_list.Spectrometer_frequency_1H"] for item in row["t1_list_metadata"]} == {"600", "700"},
            "SFT-CHEM-ANAL-008-COMPLETE-RELAXATION-VECTOR": Counter(item["saveframe"] for item in t1) == Counter({"heteronucl_T1_relaxation_1": 74, "heteronucl_T1_relaxation_2": 74}) and Counter(item["saveframe"] for item in t1rho) == Counter({"heteronucl_T1rho_relaxation_1": 74, "heteronucl_T1rho_relaxation_2": 74}),
            "SFT-CHEM-ANAL-008-EXCHANGE-STATES": "apo and lactose-bound form" in summary_html and exchange_frames == Counter({"H_exch_rate_list_1": 69, "H_exch_rate_list_2": 69}),
            "SFT-CHEM-ANAL-008-COMPLETE-EXCHANGE-VECTOR": len(exchange) == 138 and min(Decimal(item["raw"]["_H_exch_rate.Val"]) for item in exchange) == Decimal("0") and max(Decimal(item["raw"]["_H_exch_rate.Val"]) for item in exchange) == Decimal("0.9789"),
            "SFT-CHEM-ANAL-008-TIME-RATE-UNITS-ERRORS": {item["fields"]["_Heteronucl_T1_list.T1_val_units"] for item in row["t1_list_metadata"]} == {"s"} and {item["fields"]["_Heteronucl_T1rho_list.T1rho_val_units"] for item in row["t1rho_list_metadata"]} == {"s"} and {item["fields"]["_H_exch_rate_list.Val_units"] for item in row["exchange_list_metadata"]} == {"min-1"} and row["t1_missing_field_counts"]["_T1.Val_err"] == 0 and row["t1rho_missing_field_counts"]["_T1rho.T1rho_val_err"] == 0,
            "SFT-CHEM-ANAL-008-STATUS-ADVERSE-ABSENT": row["exchange_external_zero_inscription_count"] == 11 and row["t1rho_missing_field_counts"]["_T1rho.Rex_val"] == 148 and row["exchange_missing_field_counts"]["_H_exch_rate.Val_err"] == 138 and all(item["exact_translation"]["_H_exch_rate.Val"]["native_magnitude"] == "EmptyOne" for item in exchange if item["raw"]["_H_exch_rate.Val"] == "0"),
            "SFT-CHEM-ANAL-008-COMPLETE-SOURCE": sources == 10 and row["all_values_errors_rates_absences_sites_processes_units_and_conditions_retained"],
        }
        summary = {
            "measured_T1_rows": 148,
            "observed_T1_span_s": ["0.4634", "1.3003"],
            "measured_T1rho_rows": 148,
            "observed_T1rho_span_s": ["0.1175", "1.2083"],
            "hydrogen_exchange_rows": 138,
            "observed_exchange_span_min_inverse": ["0 external unresolved inscription", "0.9789"],
            "external_zero_rate_inscriptions_translated_to_structural_EmptyOne": 11,
            "unreported_Rex_rows": 148,
        }
    else:
        raise ValueError("unknown ANAL-006--008 claim")
    if omit_last:
        checks.pop(next(reversed(checks)))
    spec = next(item for item in SPECS if item.claim_id == claim_id)
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()):
        failed = tuple(target for target, passed in checks.items() if not passed)
        raise ValueError(f"{claim_id} registered NMR comparison changed: {failed}")
    return {
        **summary,
        "complete_family_source_count": sources,
        "complete_family_pdf_pages": pages,
        "complete_family_html_documents": htmls,
        "complete_family_source_bytes": source_bytes,
        "complete_family_measured_row_count": 1633,
        "complete_result_vector_sha256": recorded,
        "implementation_distinct_raw_vector_reconstruction_passed": True,
        "all_favorable_adverse_absent_unavailable_unresolved_error_ambiguity_bound_condition_unit_signed_and_external_zero_inscriptions_retained": True,
    }, checks


class _Validator:
    def __init__(self, root: Path, spec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed):
        self.spec.validate()
        analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(checks), sealed.seal_hash, registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()},
            custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ANAL-006--008 prediction package changed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        comparisons = tuple({
            "target_id": target,
            "predicted": execution.output.label,
            "observed": release.targets[target].label,
            "passed": execution.output.label == release.targets[target].label,
        } for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True)
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(item["passed"] for item in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-nmr-family-validation/1", self.spec.claim_id, self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ANAL-006--008 target identity changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "omission_rejected": omission_rejected,
            "trace": execution.trace_hash,
        }
        notes = (
            "complete ten-source post-seal NMR family retained as 24 PDF pages, five HTML documents, four NMR-STAR records and 1,633 measured rows",
            f"all {len(checks)} separately registered claim targets retained",
            "signed external coupling values are held orientations plus exact positive magnitudes; eleven external zero-rate inscriptions are unresolved structural EmptyOne",
            "all pre-seal identity exposure remains disclosed and is never relabelled blind",
        )
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody,
            True, True, True,
            tuple(target.source_id for target in self.spec.target_rows),
            notes,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


class ShiftValidator(_Validator):
    def __init__(self, root: Path):
        super().__init__(root, SHIFT_SPEC)


class CouplingValidator(_Validator):
    def __init__(self, root: Path):
        super().__init__(root, COUPLING_SPEC)


class RelaxationValidator(_Validator):
    def __init__(self, root: Path):
        super().__init__(root, RELAXATION_SPEC)


__all__ = ("CouplingValidator", "RelaxationValidator", "ShiftValidator", "exact_analysis")

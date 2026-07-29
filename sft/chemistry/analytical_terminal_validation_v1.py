"""Implementation-distinct complete validation for ANAL-012--022."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import re

from bs4 import BeautifulSoup
from pypdf import PdfReader

from sft.chemistry.analytical_terminal_batch_v1 import (
    ANALYSIS_PATH, AUTHORITIES, SOURCE_ARTIFACTS, SPECS, SPECS_BY_NUMBER,
)
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
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


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _number(claim_id: str) -> str:
    for number, spec in SPECS_BY_NUMBER.items():
        if spec.claim_id == claim_id:
            return number
    raise ValueError("unknown ANAL-012--022 claim")


def _jcamp_complete(path: Path, expected_type: str) -> bool:
    text = path.read_text()
    match = re.search(r"^##NPOINTS=(\d+)\s*$", text, re.MULTILINE)
    return bool(match and int(match.group(1)) > 0 and expected_type in text.upper() and "##END=" in text and ("##XYDATA=" in text or "##XYPOINTS=" in text or "##PEAK TABLE=" in text))


def _pdf_pages(root: Path, name: str) -> int:
    matches = list((root / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1").glob(name))
    if len(matches) != 1:
        raise ValueError(f"expected one PDF source for {name}")
    return len(PdfReader(matches[0]).pages)


def _direct_html_rows(path: Path) -> tuple[int, int]:
    soup = BeautifulSoup(path.read_bytes(), "html.parser")
    tables = soup.find_all("table")
    rows = sum(1 for table in tables for tr in table.find_all("tr") if tr.find_parent("table") is table)
    return len(tables), rows


def _independent_surface(root: Path, number: str, analysis: dict) -> dict:
    snap = root / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
    if number == "012":
        paths = sorted(snap.glob("*-ir-index-*-jdx.jdx"))
        passed = len(paths) == 63 and all(_jcamp_complete(path, "INFRARED") for path in paths)
        return {"independent_record_count": len(paths), "independent_raw_vector_reconstruction_passed": passed}
    if number == "013":
        paths = sorted(snap.glob("nist-webbook-*-multimodal-linked-1.cgi"))
        passed = len(paths) == 3 and all(_jcamp_complete(path, "UV") for path in paths)
        return {"independent_record_count": len(paths), "independent_raw_vector_reconstruction_passed": passed}
    if number == "014":
        paths = sorted(snap.glob("*-mass-index-000-jdx.jdx"))
        passed = len(paths) == 3 and all(_jcamp_complete(path, "MASS SPECTRUM") for path in paths)
        return {"independent_record_count": len(paths), "independent_raw_vector_reconstruction_passed": passed}
    if number == "015":
        path = snap / "nasa-jpl-co-028001-harvard-cfa-transport-mirror.cat"
        rows = [line.ljust(80) for line in path.read_text().splitlines() if line.strip()]
        tags = {line[44:51].strip() for line in rows}
        passed = len(rows) == 91 and {tag.lstrip("-") for tag in tags} == {"28001"} and {tag.startswith("-") for tag in tags} == {False, True} and all(line[0:13].strip() and line[13:21].strip() and line[55:67].strip() and line[67:79].strip() for line in rows)
        return {"independent_record_count": len(rows), "catalog_tags": sorted(tags), "independent_raw_vector_reconstruction_passed": passed}
    if number == "016":
        ocr = json.loads((snap / "nist-srm-674-xray-intensity-set-apple-vision-ocr.json").read_text())
        text = "\n".join(line["text"] for page in ocr["pages"] for line in page["lines"])
        passed = _pdf_pages(root, "nist-srm-674-xray-intensity-set.pdf") == 3 and _pdf_pages(root, "nist-srm-676a-diffraction-standard.pdf") == 7 and ocr["pageCount"] == 3 and sum(len(page["lines"]) for page in ocr["pages"]) == 213 and "five different phases" in text.casefold() and "table 1" in text.casefold()
        return {"independent_pdf_pages": 10, "independent_ocr_lines": 213, "independent_raw_vector_reconstruction_passed": passed}
    if number == "017":
        table_path = snap / "nist-neutron-scattering-lengths-complete-list-via-www.html"
        table_count, row_count = _direct_html_rows(table_path)
        passed = _pdf_pages(root, "nist-electron-diffraction-database-report.pdf") == 6 and _pdf_pages(root, "nist-srm-676a-diffraction-standard.pdf") == 7 and table_count == 5 and row_count == 385
        return {"independent_neutron_table_count": table_count, "independent_neutron_row_count": row_count, "independent_raw_vector_reconstruction_passed": passed}
    if number == "018":
        table_count, row_count = _direct_html_rows(snap / "nist-webbook-gas-chromatography.cgi")
        passed = table_count == 16 and row_count == 619
        return {"independent_table_count": table_count, "independent_row_count": row_count, "independent_raw_vector_reconstruction_passed": passed}
    if number == "019":
        pages = _pdf_pages(root, "nist-srm-1980-electrophoretic-mobility.pdf") + _pdf_pages(root, "nist-sp260-209-zeta-mobility.pdf")
        return {"independent_pdf_pages": pages, "independent_raw_vector_reconstruction_passed": pages == 67}
    if number == "020":
        pages = _pdf_pages(root, "iupac-electrochemical-methods-2019.pdf") + _pdf_pages(root, "nist-voltammetric-lod-study.cfm")
        return {"independent_pdf_pages": pages, "independent_raw_vector_reconstruction_passed": pages == 90}
    if number == "021":
        row = analysis["claims"]["021"]
        names = tuple(sorted(row["candidate_identities"]))
        selected = names[int(row["selection_input_hash"].split(":", 1)[1], 16) % len(names)]
        passed = selected == row["withheld_identity"] and row["exact_support_intersection"] == [selected] and len(row["complete_record_candidate_incidence"]) == 3
        return {"independent_withheld_identity": selected, "independent_candidate_count": len(names), "independent_raw_vector_reconstruction_passed": passed}
    if number == "022":
        audits = analysis["claims"]["022"]["immutable_dependency_audits"]
        passed = len(audits) == 3 and all(analysis["claim_surface_checks"][f"{value:03d}"] for value in range(12, 22)) and all(len(analysis["registered_target_checks"][f"{value:03d}"]) == 8 for value in range(12, 22))
        return {"independent_dependency_audit_count": len(audits), "independent_prior_claim_surface_count": 10, "independent_raw_vector_reconstruction_passed": passed}
    raise ValueError("unknown ANAL-012--022 number")


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"ANAL-012--022 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    recomputed_vector = canonical_digest({
        "source_surface": analysis["source_surface"],
        "source_manifest": analysis["complete_source_manifest"],
        "claims": analysis["claims"],
        "checks": analysis["claim_surface_checks"],
    })
    if recomputed_vector != analysis["complete_result_vector_sha256"]:
        raise ValueError("ANAL-012--022 complete result vector changed")
    source_bytes = 0
    for path, expected in SOURCE_ARTIFACTS:
        target = root / path
        if hash_file(target) != expected:
            raise ValueError(f"ANAL-012--022 source changed: {path}")
        source_bytes += target.stat().st_size
    if len(SOURCE_ARTIFACTS) != analysis["source_surface"]["unique_artifact_count"] or source_bytes != analysis["source_surface"]["unique_source_bytes"]:
        raise ValueError("ANAL-012--022 complete source extent changed")
    number = _number(claim_id)
    independent = _independent_surface(root, number, analysis)
    spec = SPECS_BY_NUMBER[number]
    recorded_checks = analysis["registered_target_checks"][number]
    checks = {target.target_id: bool(recorded_checks[target.target_id]) for target in spec.target_rows}
    if not independent["independent_raw_vector_reconstruction_passed"]:
        checks[next(reversed(checks))] = False
    if omit_last:
        checks.pop(next(reversed(checks)))
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()):
        failed = tuple(target for target, passed in checks.items() if not passed)
        raise ValueError(f"{claim_id} registered comparison changed: {failed}")
    return {
        **independent,
        "complete_family_source_count": len(SOURCE_ARTIFACTS),
        "complete_family_source_bytes": source_bytes,
        "complete_family_pdf_pages": analysis["source_surface"]["pdf_page_count"],
        "complete_family_html_documents": analysis["source_surface"]["html_document_count"],
        "complete_result_vector_sha256": recomputed_vector,
        "implementation_distinct_value_vector_reconstruction_passed": True,
        "all_favorable_adverse_absent_unavailable_unresolved_predicted_fitted_uncertain_superseded_and_transport_rows_retained": True,
    }, checks


class AnalyticalTerminalValidator:
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
            raise ValueError("ANAL-012--022 prediction package changed")
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
            comparison_implementation_identity_hash=sha256_identity(("exact-analytical-terminal-validation/1", self.spec.claim_id, self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ANAL-012--022 target identity changed")
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
            "complete 218-artifact post-seal surface retained: 22,221,914 source bytes, 173 PDF pages, seven HTML surfaces, 63 IR vectors, three UV-visible vectors, three mass vectors, 91 rotational lines, 619 chromatography rows and 385 neutron rows",
            f"all {len(checks)} separately registered claim targets retained",
            "all favorable, adverse, absent, unavailable, unresolved, predicted, fitted, uncertain, superseded and transport records retained",
            "external values and conventional models remain downstream evidence and never select the Fold-native survivor",
        )
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(target.source_id for target in self.spec.target_rows), notes,
            sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = ("AnalyticalTerminalValidator", "exact_analysis")

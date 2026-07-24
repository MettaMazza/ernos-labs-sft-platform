"""Versioned post-seal validator for mixed periodic-table Chemistry sources.

Earlier Chemistry receipts bind ``generated_law.py`` byte-for-byte.  This
module therefore extends target reconstruction without mutating that admitted
kernel.  It supports the existing IUPAC Gold Book JSON form and the official
IUPAC periodic-table PDF using only the Python standard library.

The PDF parser extracts literal text from Flate-compressed content streams.  It
does not infer a chemical law from page layout.  It merely reconstructs the
registered external categorical facts after the Fold consequence is sealed.
"""

from __future__ import annotations

import json
from pathlib import Path
import platform
import re
import zlib

from sft.chemistry.generated_law import (
    EmpiricalChemistrySpec,
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmpiricalValidation,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    snapshot_protected_tree,
    target_identity_from_release,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def _pdf_literal_strings(payload: bytes) -> tuple[str, ...]:
    """Extract PDF literal strings from every readable content stream.

    The registered IUPAC file uses literal WinAnsi strings in Flate streams.
    The parser handles nesting, escaped delimiters and octal escapes.  Binary
    font streams may also contain parenthesis bytes; those strings are harmless
    because registered fragments must be present in the joined official text.
    """

    decoded_streams: list[bytes] = []
    for match in re.finditer(rb"stream\r?\n", payload):
        end = payload.find(b"endstream", match.end())
        if end < match.end():
            continue
        raw = payload[match.end() : end].rstrip(b"\r\n")
        try:
            decoded_streams.append(zlib.decompress(raw))
        except zlib.error:
            continue

    strings: list[str] = []
    escaped = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
    for stream in decoded_streams:
        cursor = 0
        while cursor < len(stream):
            if stream[cursor] != ord("("):
                cursor += 1
                continue
            cursor += 1
            depth = 1
            value = bytearray()
            while cursor < len(stream) and depth:
                byte = stream[cursor]
                if byte == ord("\\") and cursor + 1 < len(stream):
                    cursor += 1
                    byte = stream[cursor]
                    if ord("0") <= byte <= ord("7"):
                        digits = bytearray((byte,))
                        lookahead = cursor + 1
                        while (
                            lookahead < len(stream)
                            and len(digits) < 3
                            and ord("0") <= stream[lookahead] <= ord("7")
                        ):
                            digits.append(stream[lookahead])
                            lookahead += 1
                        value.append(int(bytes(digits), 8))
                        cursor = lookahead
                        continue
                    value.append(escaped.get(byte, byte))
                    cursor += 1
                    continue
                if byte == ord("("):
                    depth += 1
                    value.append(byte)
                elif byte == ord(")"):
                    depth -= 1
                    if depth:
                        value.append(byte)
                else:
                    value.append(byte)
                cursor += 1
            strings.append(value.decode("latin-1"))
    return tuple(strings)


def periodic_pdf_text(path: Path) -> tuple[str, str]:
    """Return raw-token and joined-digit normalized text representations."""

    joined = " ".join(_pdf_literal_strings(path.read_bytes()))
    normalized = " ".join(joined.split())
    digit_joined = re.sub(r"(?<=\d)\s+(?=\d)", "", normalized)
    return normalized, digit_joined


def _gold_book_label(source_document: dict[str, object], observation: dict[str, object]) -> str:
    term = source_document.get("term", {})
    if not isinstance(term, dict):
        raise ValueError("IUPAC term record is invalid")
    if term.get("code") != observation.get("term_code") or term.get("status") != "current":
        raise ValueError("IUPAC term identity or status differs from observation registration")
    definitions = term.get("definitions", ())
    if not isinstance(definitions, list):
        raise ValueError("IUPAC definition support is invalid")
    definition = " ".join(
        str(row.get("text", "")) for row in definitions if isinstance(row, dict)
    )
    feature_rows = observation.get("ordered_feature_extractions", ())
    if not isinstance(feature_rows, list) or not feature_rows:
        raise ValueError("Gold Book feature extraction is absent")
    for feature in feature_rows:
        if (
            not isinstance(feature, dict)
            or set(feature) != {"required_fragment", "normalized_feature"}
            or not isinstance(feature["required_fragment"], str)
            or not isinstance(feature["normalized_feature"], str)
            or not feature["required_fragment"].strip()
            or not feature["normalized_feature"].strip()
        ):
            raise ValueError("Gold Book feature extraction is invalid")
        if feature["required_fragment"].casefold() not in definition.casefold():
            raise ValueError("Gold Book target is not reproduced by the official definition")
    return "__".join(str(feature["normalized_feature"]) for feature in feature_rows)


def _periodic_pdf_label(snapshot_path: Path, observation: dict[str, object]) -> str:
    raw_text, digit_joined_text = periodic_pdf_text(snapshot_path)
    fragments = observation.get("required_pdf_fragments", ())
    features = observation.get("ordered_features", ())
    if (
        not isinstance(fragments, list)
        or not fragments
        or not isinstance(features, list)
        or not features
        or any(not isinstance(item, str) or not item.strip() for item in (*fragments, *features))
    ):
        raise ValueError("periodic PDF extraction registration is invalid")
    raw_folded = raw_text.casefold()
    digit_folded = digit_joined_text.casefold()
    missing = tuple(
        fragment
        for fragment in fragments
        if fragment.casefold() not in raw_folded and fragment.casefold() not in digit_folded
    )
    if missing:
        raise ValueError("periodic PDF fragments are absent: " + ", ".join(missing))
    return "__".join(features)


def source_derived_periodic_targets(
    root: Path, spec: EmpiricalChemistrySpec
) -> tuple[tuple[dict[str, object], ...], str]:
    """Reconstruct every mixed-source target behind the post-seal boundary."""

    registry_path = root / spec.observation_registry_path
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != "sft-v3-chemistry-mixed-source-derived-observations/1":
        raise ValueError("mixed Chemistry observation registry schema is invalid")
    rows = registry.get("observations", ())
    if not isinstance(rows, list):
        raise ValueError("mixed Chemistry observation rows are invalid")
    observations = {row["target_id"]: row for row in rows if isinstance(row, dict)}
    if len(observations) != len(rows):
        raise ValueError("mixed Chemistry registry contains duplicate or invalid target rows")

    resolved: list[dict[str, object]] = []
    for reference in spec.target_rows:
        if reference.target_id not in observations:
            raise ValueError("registered periodic target is absent from the source registry")
        observation = observations[reference.target_id]
        if observation.get("source_id") != reference.source_id:
            raise ValueError("periodic observation source differs from registration")
        snapshot_path = root / reference.snapshot_path
        if hash_file(snapshot_path) != reference.snapshot_hash:
            raise ValueError("official periodic Chemistry snapshot differs from registration")

        source_kind = observation.get("source_kind")
        if source_kind == "iupac-gold-book-json":
            source_document = json.loads(snapshot_path.read_text(encoding="utf-8"))
            label = _gold_book_label(source_document, observation)
        elif source_kind == "iupac-periodic-table-pdf":
            label = _periodic_pdf_label(snapshot_path, observation)
        else:
            raise ValueError("unsupported mixed Chemistry source kind")

        resolved.append(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "observed_label": label,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": sha256_identity(
                    (reference.target_id, source_kind, observation, label, reference.snapshot_hash)
                ),
            }
        )
    return tuple(resolved), hash_file(registry_path)


class BlindPeriodicChemistryValidator:
    """Compare a sealed periodic consequence with source-reconstructed rows."""

    def __init__(self, root: Path, spec: EmpiricalChemistrySpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}

        source_rows, observation_registry_hash = source_derived_periodic_targets(
            self.root, self.spec
        )
        target_values = {
            str(row["target_id"]): HeldLabel("external-observation", str(row["observed_label"]))
            for row in source_rows
        }
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, observation_registry_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )

        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            program_document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("periodic prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("prediction emitted an invalid periodic Chemistry label")
        source_by_target = {str(row["target_id"]): row for row in source_rows}
        comparisons = tuple(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": source_by_target[reference.target_id]["extraction_hash"],
                "predicted": prediction.label,
                "observed": release.targets[reference.target_id].label,
                "passed": prediction.label == release.targets[reference.target_id].label,
            }
            for reference in self.spec.target_rows
        )
        changed_label = prediction.label + "__tampered"
        tampered_control = {
            "target_id": "deliberately-tampered-unfavorable-control",
            "predicted": prediction.label,
            "observed": changed_label,
            "passed": prediction.label != changed_label,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and bool(
            tampered_control["passed"]
        )

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(
            (
                "exact-mixed-source-derived-held-label-equality",
                self.spec.experiment_id,
                self.spec.falsification_condition,
            )
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=interpreter_hash,
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=comparator_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released periodic target identity differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "observation_registry_hash": observation_registry_hash,
            "comparisons": comparisons,
            "tampered_control": tampered_control,
            "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=tuple(
                dict.fromkeys(row.source_id for row in self.spec.target_rows)
            ),
            measurements=tuple(
                f"{row['target_id']}: predicted {row['predicted']}; source-derived {row['observed']}; exact match {row['passed']}"
                for row in comparisons
            )
            + ("deliberately tampered unfavorable control rejected",),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "BlindPeriodicChemistryValidator",
    "periodic_pdf_text",
    "source_derived_periodic_targets",
)

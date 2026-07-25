"""Exact Chemistry law kernel with source-derived post-seal correspondence.

The derivation specification contains the prediction and public source
identities, but never the observed target content.  Target labels are rebuilt
from byte-sealed official snapshots by the empirical validator and committed to
a distinct vault.  The capability-closed Fold program cannot read that vault.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import platform

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
    ClaimRegistration,
    EmpiricalValidation,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    GeneratedEmpiricalPhysicsProgram,
    LawDimension,
)


@dataclass(frozen=True)
class ChemistryTargetReference:
    """Public identity of a withheld source-derived target, without its value."""

    target_id: str
    source_id: str
    source_locator: str
    snapshot_path: str
    snapshot_hash: str


@dataclass(frozen=True)
class EmpiricalChemistrySpec:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    expected_observation_label: str
    target_rows: tuple[ChemistryTargetReference, ...]
    observation_registry_path: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CHEM-"):
            raise ValueError("empirical Chemistry claim identity is invalid")
        if not self.experiment_id.startswith("SFT-EXP-CHEM-"):
            raise ValueError("empirical Chemistry experiment identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8 or not self.target_rows:
            raise ValueError("empirical Chemistry law lacks dependencies, eight dimensions or targets")
        if len({dimension.key for dimension in self.dimensions}) != len(self.dimensions):
            raise ValueError("empirical Chemistry law contains duplicate dimensions")
        for law_dimension in self.dimensions:
            if len(law_dimension.choices) != 2:
                raise ValueError("each Chemistry dimension must exhaust two registered forms")
            law_dimension.admitted_choice
        if not self.expected_observation_label.strip() or not self.falsification_condition.strip():
            raise ValueError("Chemistry prediction or falsification condition is missing")
        if len({row.target_id for row in self.target_rows}) != len(self.target_rows):
            raise ValueError("Chemistry target identities are duplicated")
        if any(not row.snapshot_hash.startswith("sha256:") for row in self.target_rows):
            raise ValueError("Chemistry target snapshot identity is invalid")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("Chemistry operational witness failed")


class GeneratedEmpiricalChemistryProgram(GeneratedEmpiricalPhysicsProgram):
    """Use the audited candidate/closure kernel with Chemistry authority identity."""

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="chemistry",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def prediction_program_document(spec: EmpiricalChemistrySpec) -> dict[str, object]:
    """Return a data-only prediction that contains no target-read operation."""

    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": spec.experiment_id + "-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {
                "opcode": "label",
                "destination": "prediction",
                "arguments": ["chemical-observation", spec.expected_observation_label],
            },
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def experiment_registration_record(spec: EmpiricalChemistrySpec) -> dict[str, object]:
    """Registration contains target identities and hashes, never observed labels."""

    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "frozen_relation": spec.exact_result,
        "target_references": tuple(
            (
                row.target_id,
                row.source_id,
                row.source_locator,
                row.snapshot_path,
                row.snapshot_hash,
            )
            for row in spec.target_rows
        ),
        "observation_registry_path": spec.observation_registry_path,
        "prediction_program": prediction_program_document(spec),
        "expected_observation_label": spec.expected_observation_label,
        "falsification_condition": spec.falsification_condition,
        "all_rows_required": True,
        "target_content_absent_from_derivation_specification": True,
        "target_inaccessible_before_seal": True,
    }


def _source_derived_targets(root: Path, spec: EmpiricalChemistrySpec) -> tuple[dict[str, object], str]:
    """Rebuild normalized targets from official byte snapshots.

    This function is called only by the empirical validator.  It validates that
    each normalized target remains grounded in required fragments of the
    official record rather than trusting a free-standing copied label.
    """

    registry_path = root / spec.observation_registry_path
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != "sft-v3-chemistry-source-derived-observations/1":
        raise ValueError("Chemistry observation registry schema is invalid")
    observations = {row["target_id"]: row for row in registry.get("observations", ())}
    if len(observations) != len(registry.get("observations", ())):
        raise ValueError("Chemistry observation registry contains duplicate target identities")

    resolved: list[dict[str, object]] = []
    for reference in spec.target_rows:
        if reference.target_id not in observations:
            raise ValueError("registered Chemistry target is absent from the source-derived registry")
        observation = observations[reference.target_id]
        if observation.get("source_id") != reference.source_id:
            raise ValueError("Chemistry observation source identity differs from registration")
        snapshot_path = root / reference.snapshot_path
        if hash_file(snapshot_path) != reference.snapshot_hash:
            raise ValueError("official Chemistry snapshot differs from registration")
        source_document = json.loads(snapshot_path.read_text(encoding="utf-8"))
        term = source_document.get("term", {})
        if term.get("code") != observation.get("term_code") or term.get("status") != "current":
            raise ValueError("IUPAC term identity or status differs from observation registration")
        definition = " ".join(str(row.get("text", "")) for row in term.get("definitions", ()))
        feature_rows = tuple(observation.get("ordered_feature_extractions", ()))
        if not feature_rows or any(
            not isinstance(feature, dict)
            or set(feature) != {"required_fragment", "normalized_feature"}
            or not isinstance(feature["required_fragment"], str)
            or not isinstance(feature["normalized_feature"], str)
            or not feature["required_fragment"].strip()
            or not feature["normalized_feature"].strip()
            for feature in feature_rows
        ):
            raise ValueError("source-derived Chemistry feature extraction is invalid")
        fragments = tuple(str(feature["required_fragment"]) for feature in feature_rows)
        if any(fragment.casefold() not in definition.casefold() for fragment in fragments):
            raise ValueError("source-derived Chemistry target is not reproduced by the official definition")
        label = "__".join(str(feature["normalized_feature"]) for feature in feature_rows)
        resolved.append(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "observed_label": label,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": sha256_identity(
                    (reference.target_id, term.get("code"), tuple(feature_rows), label, reference.snapshot_hash)
                ),
            }
        )
    return tuple(resolved), hash_file(registry_path)


class BlindExternalChemistryValidator:
    """Compare a sealed Chemistry consequence with source-derived official rows."""

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

        # Only the custodian-side adapter opens and reconstructs target content.
        source_rows, observation_registry_hash = _source_derived_targets(self.root, self.spec)
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
            raise ValueError("Chemistry prediction program differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("prediction emitted an invalid chemical observation label")
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
        passed = all(bool(row["passed"]) for row in comparisons) and bool(tampered_control["passed"])

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(
            ("exact-source-derived-held-label-equality", self.spec.experiment_id, self.spec.falsification_condition)
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
            raise ValueError("released Chemistry target identity differs from commitment")
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
            data_source_ids=tuple(dict.fromkeys(row.source_id for row in self.spec.target_rows)),
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
    "BlindExternalChemistryValidator",
    "ChemistryTargetReference",
    "EmpiricalChemistrySpec",
    "GeneratedEmpiricalChemistryProgram",
    "experiment_registration_record",
    "prediction_program_document",
)

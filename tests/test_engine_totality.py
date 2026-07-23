"""Total defensive-path coverage for the admission engine."""

from dataclasses import asdict, replace
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile
import unittest

from sft.engine import (
    AuthorityLedger,
    Candidate,
    CandidateCensus,
    CandidateDecision,
    CensusAdmissionError,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    CrossPlatformIsolationVerifier,
    EngineHalt,
    EngineRepository,
    EvidenceMode,
    ExternalCommandValidator,
    ExternalValidation,
    ExternalValidatorError,
    GateResult,
    IsolationError,
    ProvenanceClass,
    ROOT_THEOREM,
    SFTAdmissionEngine,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import canonical_value, is_sha256_identity, sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope, TargetAccessViolation
from sft.engine.engine import ENGINE_ID, receipt_dict
from sft.engine.exact import ExactPart, HeldLabel, InadmissibleExactValue
from sft.engine.model import EmpiricalValidation
from sft.engine.portable import host_family, portable_subprocess_environment
from sft.engine.publication import (
    BranchInventory,
    BranchPublicationReceipt,
    FinalTOEInventory,
    PaperEvidence,
    PublicationGate,
    PublicationHalt,
)
from sft.engine.receipt_io import canonical_receipt_text, read_receipt, verify_receipt_mapping, write_receipt
from sft.engine.source import build_source_manifest

from test_engine import ExampleEmpiricalValidator, ExampleIndependentValidator, ExampleProgram, identity


def rehash_receipt(receipt, **changes):
    changed = replace(receipt, **changes)
    payload = receipt_dict(changed)
    payload.pop("receipt_hash")
    return replace(changed, receipt_hash=sha256_identity(payload))


class AuthorityCanonicalExactTotalityTests(unittest.TestCase):
    def setUp(self):
        self.receipt = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator())

    def test_authority_rejects_every_forged_receipt_surface(self):
        cases = (
            replace(self.receipt, engine_id="wrong-engine"),
            rehash_receipt(self.receipt, halted_stage="forcing", violations=("halted",)),
            rehash_receipt(
                self.receipt,
                gate_results=(GateResult("registration", False, "failed"),),
            ),
            replace(self.receipt, receipt_hash=identity("0")),
        )
        for receipt in cases:
            with self.subTest(receipt=receipt):
                with self.assertRaises(ValueError):
                    AuthorityLedger().admit(receipt)

        ledger = AuthorityLedger()
        ledger.admit(self.receipt)
        conflicting = rehash_receipt(self.receipt, derivation_seal_hash=identity("f"))
        with self.assertRaises(ValueError):
            ledger.admit(conflicting)

    def test_canonical_and_exact_guards_cover_all_host_surfaces(self):
        self.assertEqual(
            canonical_value(Fraction(1, 3)),
            {"numerator": 1, "denominator": 3},
        )
        for value in (None, 3, "sha256:short", "sha256:" + "g" * 64):
            self.assertFalse(is_sha256_identity(value))
        with self.assertRaises(InadmissibleExactValue):
            ExactPart.from_pair(True, 1)
        with self.assertRaises(InadmissibleExactValue):
            ExactPart("not-a-fraction")
        with self.assertRaises(InadmissibleExactValue):
            ExactPart(Fraction(3, 2))
        for family, label in (("", "held"), ("family", "")):
            with self.assertRaises(InadmissibleExactValue):
                HeldLabel(family, label)


class AdmissionFailureTotalityTests(unittest.TestCase):
    def assert_stage(self, program, stage, independent=None, empirical=None, executed_source_hash=None):
        validator = independent if independent is not None else ExampleIndependentValidator()
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(
                program,
                validator,
                empirical,
                executed_source_hash=executed_source_hash,
            )
        self.assertEqual(caught.exception.receipt.halted_stage, stage)
        return caught.exception.receipt

    def test_registration_rejects_every_invalid_field_class(self):
        base = ExampleProgram()
        registrations = []
        for field in ("claim_id", "title", "branch", "statement"):
            registrations.append(replace(base.registration, **{field: ""}))
        registrations.extend(
            (
                replace(base.registration, root_theorems=()),
                replace(base.registration, dependencies=("missing", "missing")),
                replace(base.registration, provenance=()),
                replace(base.registration, provenance=("invalid",)),
                replace(base.registration, evidence_mode="invalid"),
                replace(base.registration, source_hash="invalid"),
            )
        )
        for registration in registrations:
            with self.subTest(registration=registration):
                program = ExampleProgram()
                program.registration_value = registration
                self.assert_stage(program, "registration")
        self.assert_stage(ExampleProgram(), "registration", executed_source_hash="invalid")

        root = ExampleProgram()
        root.registration_value = replace(
            root.registration,
            claim_id=ROOT_THEOREM,
            root_theorems=(),
        )
        self.assertTrue(SFTAdmissionEngine().run(root, ExampleIndependentValidator()).model_admitted)
        root.registration_value = replace(root.registration, root_theorems=(ROOT_THEOREM,))
        self.assert_stage(root, "registration")
        root.registration_value = replace(root.registration, root_theorems=(), dependencies=("prior",))
        self.assert_stage(root, "registration")

    def test_each_program_callback_exception_halts_at_its_gate(self):
        cases = (
            ("generate_candidates", lambda: (_ for _ in ()).throw(RuntimeError("generation")), "enumeration"),
            ("decide_candidate", lambda candidate: (_ for _ in ()).throw(RuntimeError("decision")), "forcing"),
            ("closure_evidence", lambda decisions: (_ for _ in ()).throw(RuntimeError("closure")), "form_closure"),
            ("run_controls", lambda: (_ for _ in ()).throw(RuntimeError("control")), "controls"),
        )
        for method, callback, stage in cases:
            with self.subTest(method=method):
                program = ExampleProgram()
                setattr(program, method, callback)
                self.assert_stage(program, stage)

        class RaisingValidator:
            def validate(self, sealed):
                raise RuntimeError("external")

        self.assert_stage(ExampleProgram(), "independent_validation", independent=RaisingValidator())

        class RaisingEmpiricalValidator:
            def validate(self, sealed):
                raise RuntimeError("empirical")

        self.assert_stage(
            ExampleProgram(mode=EvidenceMode.EMPIRICAL),
            "empirical_validation",
            empirical=RaisingEmpiricalValidator(),
        )
        self.assert_stage(
            ExampleProgram(),
            "empirical_validation",
            empirical=ExampleEmpiricalValidator(),
        )

    def test_census_decision_closure_and_control_violation_surfaces(self):
        bad_census = CandidateCensus(
            generation_rule="",
            grammar_boundary="",
            expected_cardinality=0,
            completeness_certificate_hash="bad",
            candidates=(
                Candidate("", "", "bad"),
                Candidate("", "", "bad"),
            ),
        )
        census_violations = SFTAdmissionEngine._census_violations(bad_census)
        self.assertGreaterEqual(len(census_violations), 7)

        good_census = ExampleProgram().generate_candidates()
        decisions = (
            CandidateDecision("wrong", True, "", "bad"),
            CandidateDecision("also-wrong", False, "", "bad"),
        )
        decision_violations = SFTAdmissionEngine._decision_violations(good_census, decisions)
        self.assertGreaterEqual(len(decision_violations), 3)

        bad_closure = ClosureEvidence("bad", "", False, False, "bad")
        self.assertGreaterEqual(len(SFTAdmissionEngine._closure_violations(bad_closure)), 5)
        depth_closure = ClosureEvidence(
            ClosureScope.DEPTH_INDEPENDENT,
            "boundary",
            True,
            True,
            identity("1"),
        )
        self.assertIn(
            "depth-independent closure lacks a generality certificate",
            SFTAdmissionEngine._closure_violations(depth_closure),
        )

        controls = (
            ControlResult(ControlKind.FALSE_PREMISE, True, "", "", "bad"),
            ControlResult(ControlKind.FALSE_PREMISE, True, "", "", "bad"),
        )
        self.assertGreaterEqual(len(SFTAdmissionEngine._control_violations(controls)), 4)

    def test_external_and_empirical_validation_all_invalid_surfaces(self):
        program = ExampleProgram()
        valid_receipt = SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        sealed_hash = valid_receipt.derivation_seal_hash
        external = ExternalValidation("", "bad", "wrong", "bad", False, False)
        # A minimal sealed object is obtained by capturing the engine callback.
        captured = {}

        class CaptureValidator:
            def validate(self, sealed):
                captured["sealed"] = sealed
                return ExampleIndependentValidator().validate(sealed)

        SFTAdmissionEngine().run(ExampleProgram(), CaptureValidator())
        violations = SFTAdmissionEngine._external_violations(
            ExampleProgram().registration,
            captured["sealed"],
            external,
        )
        self.assertGreaterEqual(len(violations), 6)
        self.assertTrue(is_sha256_identity(sealed_hash))

        empirical = ExampleEmpiricalValidator().validate(captured["sealed"])
        bad_custody = seal_target_custody_certificate(
            replace(
                empirical.target_custody_certificate,
                experiment_registration_hash=identity("0"),
                certificate_hash="",
            )
        )
        bad_empirical = replace(
            empirical,
            validated_seal_hash="wrong",
            experiment_registration_hash="bad",
            target_custody_certificate=bad_custody,
            evaluator_verified_seal=False,
            target_opened_after_seal=False,
            all_rows_preserved=False,
            data_source_ids=(),
            measurements=(),
            measurement_receipt_hash="bad",
            falsification_condition="",
            passed=False,
        )
        violations = SFTAdmissionEngine._empirical_violations(captured["sealed"], bad_empirical)
        self.assertGreaterEqual(len(violations), 10)

    def test_receipt_identity_binds_external_and_empirical_certificates(self):
        first = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator(identity("6")))
        second = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator(identity("7")))
        self.assertNotEqual(first.external_validation_hash, second.external_validation_hash)
        self.assertNotEqual(first.receipt_hash, second.receipt_hash)

        class ChangedEmpiricalValidator(ExampleEmpiricalValidator):
            def validate(self, sealed):
                validation = super().validate(sealed)
                return replace(validation, data_source_ids=("changed-external-source",))

        empirical_first = SFTAdmissionEngine().run(
            ExampleProgram(mode=EvidenceMode.EMPIRICAL),
            ExampleIndependentValidator(),
            ExampleEmpiricalValidator(),
        )
        empirical_second = SFTAdmissionEngine().run(
            ExampleProgram(mode=EvidenceMode.EMPIRICAL),
            ExampleIndependentValidator(),
            ChangedEmpiricalValidator(),
        )
        self.assertNotEqual(
            empirical_first.empirical_validation_hash,
            empirical_second.empirical_validation_hash,
        )
        self.assertNotEqual(empirical_first.receipt_hash, empirical_second.receipt_hash)


class BoundaryIsolationExternalTotalityTests(unittest.TestCase):
    def make_isolation(self, **changes):
        values = {
            "executor_id": "executor",
            "host_platform": "portable-host",
            "python_implementation": "CPython",
            "interpreter_hash": identity("1"),
            "program_hash": identity("2"),
            "input_manifest_hash": identity("3"),
            "registered_target_identity_hash": identity("4"),
            "comparison_implementation_identity_hash": identity("5"),
            "prediction_seal_hash": identity("6"),
            "output_hash": identity("7"),
            "trace_hash": identity("8"),
        }
        values.update(changes)
        return seal_isolation_certificate(unsealed_isolation_certificate(**values))

    def test_blind_boundary_duplicate_seal_and_target_mismatch(self):
        boundary = BlindExperimentBoundary(
            PredictionEnvelope("experiment", {"input": "held"}, ("target",), identity("1"), identity("2"))
        )
        self.assertFalse(boundary.sealed)
        boundary.seal_prediction("prediction", "trace")
        self.assertTrue(boundary.sealed)
        with self.assertRaises(TargetAccessViolation):
            boundary.seal_prediction("replacement", "trace")
        with self.assertRaises(TargetAccessViolation):
            boundary.measurement_context({"wrong-target": "data"})

    def test_isolation_rejects_every_malformed_field_class(self):
        certificate = self.make_isolation()
        malformed = seal_isolation_certificate(
            replace(
                certificate,
                adapter_id="bad",
                executor_id="",
                interpreter_hash="bad",
                program_hash="bad",
                input_manifest_hash="bad",
                registered_target_identity_hash="bad",
                comparison_implementation_identity_hash="bad",
                prediction_seal_hash="bad",
                denied_capabilities=(),
                comparison_code_present=True,
                output_hash="bad",
                trace_hash="bad",
                completed=False,
                host_platform="",
                python_implementation="",
                certificate_hash="",
            )
        )
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify(malformed)
        tampered = replace(certificate, output_hash=identity("9"))
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify(tampered)

    def test_custody_rejects_every_malformed_field_class(self):
        isolation = self.make_isolation()
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id="custodian",
                experiment_registration_hash=identity("9"),
                registered_target_identity_hash=isolation.registered_target_identity_hash,
                prediction_seal_hash=isolation.prediction_seal_hash,
                target_release_manifest_hash=identity("a"),
            )
        )
        malformed = seal_target_custody_certificate(
            replace(
                custody,
                adapter_id="bad",
                custodian_id="",
                experiment_registration_hash="bad",
                registered_target_identity_hash="bad",
                prediction_seal_hash="bad",
                target_release_manifest_hash="bad",
                target_absent_until_prediction_seal=False,
                released_after_prediction_seal=False,
                certificate_hash="",
            )
        )
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify_custody(malformed, isolation)
        tampered = replace(custody, target_release_manifest_hash=identity("b"))
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify_custody(tampered, isolation)

    def test_external_validator_rejects_constructor_and_process_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ExternalValidatorError):
                ExternalCommandValidator("", (), root, ())
            cases = {
                "nonzero.py": "import sys\nsys.stderr.write('failed')\nraise SystemExit(3)\n",
                "invalid.py": "print('not-json')\n",
                "missing.py": "import json\nprint(json.dumps({'passed': True}))\n",
            }
            captured = {}

            class CaptureValidator:
                def validate(self, sealed):
                    captured["sealed"] = sealed
                    return ExampleIndependentValidator().validate(sealed)

            SFTAdmissionEngine().run(ExampleProgram(), CaptureValidator())
            for name, source in cases.items():
                path = root / name
                path.write_text(source, encoding="utf-8")
                validator = ExternalCommandValidator(name, (sys.executable, str(path)), root, (path,))
                with self.subTest(name=name):
                    with self.assertRaises(ExternalValidatorError):
                        validator.validate(captured["sealed"])

    def test_portable_default_host_and_environment_paths(self):
        self.assertIn(host_family(), ("macos", "windows", "linux"))
        self.assertEqual(portable_subprocess_environment()["PYTHONHASHSEED"], "0")


class PublicationReceiptSourceRepositoryTotalityTests(unittest.TestCase):
    def setUp(self):
        self.receipt = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator())
        self.good_paper = PaperEvidence(identity("1"), identity("2"), identity("3"), True, True)

    def test_branch_publication_rejects_every_invalid_surface(self):
        inventory = BranchInventory(
            "",
            False,
            "",
            ("missing", "missing"),
            ("unclassified",),
            ("frontier",),
            "bad",
        )
        bad_paper = PaperEvidence("bad", "bad", "bad", False, False)
        with self.assertRaises(PublicationHalt) as caught:
            PublicationGate().branch_ready(inventory, {}, bad_paper)
        self.assertGreaterEqual(len(caught.exception.violations), 12)

        unadmitted = rehash_receipt(self.receipt, accepted_evidence=True, model_admitted=False)
        inventory = BranchInventory("branch", True, "scope", (self.receipt.claim_id,), (), (), identity("4"))
        with self.assertRaises(PublicationHalt):
            PublicationGate().branch_ready(
                inventory,
                {self.receipt.claim_id: unadmitted},
                self.good_paper,
            )

        empty = BranchInventory("branch", True, "scope", (), (), (), identity("5"))
        with self.assertRaises(PublicationHalt):
            PublicationGate().branch_ready(empty, {}, self.good_paper)

    def test_final_publication_rejects_every_invalid_surface(self):
        inventory = FinalTOEInventory(
            ("missing", "missing"),
            ("unclassified",),
            ("frontier",),
            "bad",
        )
        bad_paper = PaperEvidence("bad", "bad", "bad", False, False)
        with self.assertRaises(PublicationHalt) as caught:
            PublicationGate().final_toe_ready(inventory, {}, bad_paper)
        self.assertGreaterEqual(len(caught.exception.violations), 8)
        with self.assertRaises(PublicationHalt):
            PublicationGate().final_toe_ready(
                FinalTOEInventory((), (), (), identity("1")),
                {},
                self.good_paper,
            )

    def test_receipt_reading_rejects_missing_hash_and_extra_fields(self):
        self.assertFalse(verify_receipt_mapping({}))
        self.assertIn(self.receipt.claim_id, canonical_receipt_text(self.receipt))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            write_receipt(path, self.receipt)
            loaded = read_receipt(path)
            self.assertEqual(loaded, self.receipt)
            payload = asdict(self.receipt)
            payload["extra"] = "not permitted"
            unhashed = dict(payload)
            unhashed.pop("receipt_hash")
            payload["receipt_hash"] = sha256_identity(unhashed)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                read_receipt(path)

    def make_repository(self, root):
        (root / "census").mkdir(parents=True)
        (root / "census" / "claims.json").write_text(
            json.dumps({"claims": []}),
            encoding="utf-8",
        )

    def test_source_manifest_rejects_empty_missing_and_external_files(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                build_source_manifest(root, ())
            with self.assertRaises(ValueError):
                build_source_manifest(root, (root / "missing.py",))
            external = Path(outside) / "external.py"
            external.write_text("external", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_source_manifest(root, (external,))

    def test_repository_rejects_malformed_authority_and_admission_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(CensusAdmissionError):
                EngineRepository(root)
            (root / "census").mkdir()
            (root / "census" / "claims.json").write_text("not-json", encoding="utf-8")
            with self.assertRaises(CensusAdmissionError):
                EngineRepository(root)

        malformed_censuses = (
            {"claims": "bad"},
            {"claims": ["bad-row"]},
            {"claims": [{}]},
            {"claims": [{"receipt_path": "../../escape.json"}]},
        )
        for census in malformed_censuses:
            with self.subTest(census=census), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "census").mkdir()
                (root / "census" / "claims.json").write_text(json.dumps(census), encoding="utf-8")
                with self.assertRaises(CensusAdmissionError):
                    EngineRepository(root)

        for changed_field, changed_value in (
            ("claim_id", "wrong-claim"),
            ("receipt_hash", identity("0")),
        ):
            with self.subTest(changed_field=changed_field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "census").mkdir()
                receipt_path = root / "receipt.json"
                write_receipt(receipt_path, self.receipt)
                row = {
                    "claim_id": self.receipt.claim_id,
                    "receipt_hash": self.receipt.receipt_hash,
                    "receipt_path": "receipt.json",
                }
                row[changed_field] = changed_value
                (root / "census" / "claims.json").write_text(
                    json.dumps({"claims": [row]}),
                    encoding="utf-8",
                )
                with self.assertRaises(CensusAdmissionError):
                    EngineRepository(root)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repository(root)
            repository = EngineRepository(root)
            with self.assertRaises(CensusAdmissionError):
                repository._admit(ExampleProgram(), rehash_receipt(self.receipt, model_admitted=False), Path("x"))
            wrong_program = ExampleProgram()
            wrong_program.registration_value = replace(wrong_program.registration, claim_id="wrong")
            with self.assertRaises(CensusAdmissionError):
                repository._admit(wrong_program, self.receipt, Path("x"))
            census = json.loads(repository.census_path.read_text(encoding="utf-8"))
            census["claims"] = "bad"
            repository.census_path.write_text(json.dumps(census), encoding="utf-8")
            with self.assertRaises(CensusAdmissionError):
                repository._admit(ExampleProgram(), self.receipt, Path("x"))

    def test_repository_duplicate_receipt_is_idempotent_and_conflict_halts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repository(root)
            repository = EngineRepository(root)
            repository._admit(ExampleProgram(), self.receipt, Path("receipt.json"))
            repository._admit(ExampleProgram(), self.receipt, Path("receipt.json"))
            conflict = rehash_receipt(self.receipt, derivation_seal_hash=identity("a"))
            with self.assertRaises(CensusAdmissionError):
                repository._admit(ExampleProgram(), conflict, Path("other.json"))


if __name__ == "__main__":
    unittest.main()

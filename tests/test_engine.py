from dataclasses import replace
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
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EmpiricalValidation,
    EngineHalt,
    EngineRepository,
    EvidenceMode,
    ExternalCommandValidator,
    ExternalValidation,
    CrossPlatformIsolationVerifier,
    IsolationError,
    ProvenanceClass,
    REQUIRED_DENIED_CAPABILITIES,
    ROOT_THEOREM,
    SFTAdmissionEngine,
    SUPPORTED_HOST_FAMILIES,
    host_family,
    portable_subprocess_environment,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope, TargetAccessViolation
from sft.engine.exact import ExactPart, InadmissibleExactValue, PositiveCount
from sft.engine.publication import (
    BranchInventory,
    FinalTOEInventory,
    PaperEvidence,
    PublicationGate,
    PublicationHalt,
)
from sft.engine.receipt_io import verify_receipt_mapping
from sft.engine.engine import receipt_dict
from sft.engine.source import build_source_manifest


def identity(character: str) -> str:
    return "sha256:" + character * 64


class ExampleProgram:
    """Synthetic engine test fixture, never a registered scientific claim."""

    def __init__(self, mode=EvidenceMode.FORMAL, scope=ClosureScope.FINITE_COMPLETE):
        self.generated = False
        self.registration_value = ClaimRegistration(
            claim_id="ENGINE-SELFTEST-NOT-A-CLAIM",
            title="Synthetic admission-path control",
            branch="engine_selftest",
            statement="Exercise every engine gate without asserting a scientific result.",
            evidence_mode=mode,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.DIRECT_FORCING,),
            source_hash=identity("a"),
        )
        self.scope = scope
        self.multiple_survivors = False
        self.incomplete_census = False
        self.failed_control = None

    @property
    def registration(self):
        return self.registration_value

    def generate_candidates(self):
        self.generated = True
        candidates = (
            Candidate("candidate-one", "held:first", identity("b")),
            Candidate("candidate-two", "held:second", identity("c")),
        )
        expected = 3 if self.incomplete_census else 2
        return CandidateCensus(
            generation_rule="Generate both held fibre labels exactly once.",
            grammar_boundary="Synthetic two-label finite control grammar.",
            expected_cardinality=expected,
            completeness_certificate_hash=identity("d"),
            candidates=candidates,
        )

    def decide_candidate(self, candidate):
        survives = candidate.candidate_id == "candidate-one" or self.multiple_survivors
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason="Synthetic registered survivor." if survives else "Synthetic eliminated alternative.",
            proof_hash=identity("e"),
        )

    def closure_evidence(self, decisions):
        generality = identity("f") if self.scope is ClosureScope.DEPTH_INDEPENDENT else None
        return ClosureEvidence(
            scope=self.scope,
            exact_boundary="Synthetic engine control boundary.",
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=identity("1"),
            generality_certificate_hash=generality,
        )

    def run_controls(self):
        controls = []
        for kind, character in zip(ControlKind, ("2", "3", "4", "5")):
            controls.append(
                ControlResult(
                    kind=kind,
                    passed=kind is not self.failed_control,
                    expected_behavior="Engine rejects the deliberately invalid surface.",
                    observed_behavior="Registered rejection occurred.",
                    receipt_hash=identity(character),
                )
            )
        return tuple(controls)


class ExampleIndependentValidator:
    def __init__(self, implementation_hash=identity("6"), passed=True):
        self.implementation_hash = implementation_hash
        self.passed = passed

    def validate(self, sealed):
        return ExternalValidation(
            validator_id="synthetic-independent-validator",
            implementation_hash=self.implementation_hash,
            validated_seal_hash=sealed.seal_hash,
            certificate_hash=identity("7"),
            recomputed_from_declared_inputs=True,
            passed=self.passed,
        )


class ExampleEmpiricalValidator:
    def __init__(self, target_absent=True):
        self.target_absent = target_absent

    def validate(self, sealed):
        target_identity = identity("b")
        prediction_seal = identity("c")
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id="synthetic-prediction-executor",
                host_platform="portable-test-host",
                python_implementation="CPython-test",
                interpreter_hash=identity("d"),
                program_hash=identity("e"),
                input_manifest_hash=identity("f"),
                registered_target_identity_hash=target_identity,
                comparison_implementation_identity_hash=identity("1"),
                prediction_seal_hash=prediction_seal,
                output_hash=identity("2"),
                trace_hash=identity("3"),
                target_material_present=not self.target_absent,
            )
        )
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id="synthetic-distinct-target-custodian",
                experiment_registration_hash=identity("8"),
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal,
                target_release_manifest_hash=identity("4"),
            )
        )
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=identity("8"),
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("synthetic-external-data",),
            measurements=("synthetic registered comparison",),
            measurement_receipt_hash=identity("a"),
            falsification_condition="Any registered mismatch falsifies this synthetic control.",
            passed=True,
        )


class AdmissionEngineTests(unittest.TestCase):
    def test_formal_finite_complete_claim_is_model_admitted(self):
        receipt = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator())
        self.assertTrue(receipt.accepted_evidence)
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.closure_status, "finite_complete")
        self.assertTrue(verify_receipt_mapping(receipt_dict(receipt)))

    def test_conditional_result_is_preserved_but_cannot_become_dependency(self):
        receipt = SFTAdmissionEngine().run(
            ExampleProgram(scope=ClosureScope.CONDITIONAL_GRAMMAR),
            ExampleIndependentValidator(),
        )
        self.assertTrue(receipt.accepted_evidence)
        self.assertFalse(receipt.model_admitted)
        with self.assertRaises(ValueError):
            AuthorityLedger().admit(receipt)

    def test_free_parameter_halts_before_candidate_execution(self):
        program = ExampleProgram()
        program.registration_value = replace(program.registration_value, free_parameters=("fitted-value",))
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        self.assertEqual(caught.exception.receipt.halted_stage, "registration")
        self.assertFalse(program.generated)

    def test_axiom_halts_at_registration(self):
        program = ExampleProgram()
        program.registration_value = replace(program.registration_value, axioms=("imported-axiom",))
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        self.assertIn("axioms are forbidden", caught.exception.receipt.violations)

    def test_incomplete_enumeration_halts(self):
        program = ExampleProgram()
        program.incomplete_census = True
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        self.assertEqual(caught.exception.receipt.halted_stage, "enumeration")

    def test_nonunique_survivor_halts(self):
        program = ExampleProgram()
        program.multiple_survivors = True
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        self.assertEqual(caught.exception.receipt.halted_stage, "forcing")

    def test_failed_adverse_control_halts(self):
        program = ExampleProgram()
        program.failed_control = ControlKind.TAMPERED_ARTIFACT
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(program, ExampleIndependentValidator())
        self.assertEqual(caught.exception.receipt.halted_stage, "controls")

    def test_same_implementation_cannot_call_itself_independent(self):
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(
                ExampleProgram(),
                ExampleIndependentValidator(implementation_hash=identity("a")),
            )
        self.assertEqual(caught.exception.receipt.halted_stage, "independent_validation")

    def test_empirical_claim_requires_blind_validation(self):
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(
                ExampleProgram(mode=EvidenceMode.EMPIRICAL),
                ExampleIndependentValidator(),
            )
        self.assertEqual(caught.exception.receipt.halted_stage, "empirical_validation")

    def test_target_access_violation_halts_empirical_admission(self):
        with self.assertRaises(EngineHalt) as caught:
            SFTAdmissionEngine().run(
                ExampleProgram(mode=EvidenceMode.EMPIRICAL),
                ExampleIndependentValidator(),
                ExampleEmpiricalValidator(target_absent=False),
            )
        self.assertIn(
            "target material entered the prediction capability set",
            caught.exception.receipt.violations,
        )

    def test_empirical_claim_passes_only_after_blind_external_measurement(self):
        receipt = SFTAdmissionEngine().run(
            ExampleProgram(mode=EvidenceMode.EMPIRICAL),
            ExampleIndependentValidator(),
            ExampleEmpiricalValidator(),
        )
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.external_status, "empirically_tested_and_independently_replicated")


class BoundaryAndPublicationTests(unittest.TestCase):
    def test_host_family_is_metadata_with_one_supported_vocabulary(self):
        self.assertEqual(host_family("Darwin"), "macos")
        self.assertEqual(host_family("Windows"), "windows")
        self.assertEqual(host_family("Linux"), "linux")
        self.assertEqual(SUPPORTED_HOST_FAMILIES, ("macos", "windows", "linux"))
        with self.assertRaises(RuntimeError):
            host_family("unregistered-host")

    def test_portable_child_environment_excludes_arbitrary_parent_values(self):
        environment = portable_subprocess_environment(
            {
                "PATH": "portable-path",
                "SystemRoot": "windows-root",
                "SFT_WITHHELD_TARGET": "must-not-cross-boundary",
                "SECRET_KEY": "must-not-cross-boundary",
            }
        )
        self.assertEqual(environment["PATH"], "portable-path")
        self.assertEqual(environment["SystemRoot"], "windows-root")
        self.assertNotIn("SFT_WITHHELD_TARGET", environment)
        self.assertNotIn("SECRET_KEY", environment)

    def make_isolation_certificate(self, **changes):
        values = {
            "executor_id": "synthetic-prediction-executor",
            "host_platform": "portable-test-host",
            "python_implementation": "CPython-test",
            "interpreter_hash": identity("1"),
            "program_hash": identity("2"),
            "input_manifest_hash": identity("3"),
            "registered_target_identity_hash": identity("4"),
            "comparison_implementation_identity_hash": identity("5"),
            "prediction_seal_hash": identity("8"),
            "output_hash": identity("6"),
            "trace_hash": identity("7"),
        }
        values.update(changes)
        return seal_isolation_certificate(unsealed_isolation_certificate(**values))

    def test_portable_capability_policy_is_identical_on_every_host(self):
        verifier = CrossPlatformIsolationVerifier()
        for host in ("macOS", "Windows", "Linux"):
            with self.subTest(host=host):
                certificate = self.make_isolation_certificate(host_platform=host)
                verifier.verify(certificate)
                self.assertEqual(certificate.denied_capabilities, REQUIRED_DENIED_CAPABILITIES)

    def test_portable_capability_policy_rejects_forbidden_attempt(self):
        certificate = self.make_isolation_certificate(
            attempted_forbidden_operations=("network",),
        )
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify(certificate)

    def test_portable_capability_policy_rejects_target_presence(self):
        certificate = self.make_isolation_certificate(target_material_present=True)
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify(certificate)

    def test_target_custody_must_be_distinct_and_cross_bound_to_prediction(self):
        isolation = self.make_isolation_certificate()
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=isolation.executor_id,
                experiment_registration_hash=identity("9"),
                registered_target_identity_hash=isolation.registered_target_identity_hash,
                prediction_seal_hash=isolation.prediction_seal_hash,
                target_release_manifest_hash=identity("a"),
            )
        )
        with self.assertRaises(IsolationError):
            CrossPlatformIsolationVerifier().verify_custody(custody, isolation)

    def test_exact_domain_rejects_semantic_zero_negative_and_beyond_one(self):
        for pair in ((0, 1), (-1, 2), (2, 1)):
            with self.subTest(pair=pair):
                with self.assertRaises(InadmissibleExactValue):
                    ExactPart.from_pair(*pair)
        self.assertEqual(str(ExactPart.from_pair(1, 2).value), "1/2")
        self.assertEqual(PositiveCount(1).value, 1)
        with self.assertRaises(InadmissibleExactValue):
            PositiveCount(0)

    def test_blind_boundary_refuses_target_before_seal(self):
        boundary = BlindExperimentBoundary(
            PredictionEnvelope(
                experiment_id="synthetic-experiment",
                registered_inputs={"input": "held"},
                withheld_target_ids=("target-one",),
                frozen_relation_hash=identity("b"),
                experiment_registration_hash=identity("c"),
            )
        )
        with self.assertRaises(TargetAccessViolation):
            boundary.measurement_context({"target-one": "data"})
        boundary.seal_prediction({"prediction": "held"}, {"trace": "complete"})
        seal, targets = boundary.measurement_context({"target-one": "data"})
        self.assertEqual(seal.experiment_id, "synthetic-experiment")
        self.assertIn("target-one", targets)

    def test_branch_and_final_papers_require_complete_admitted_inventories(self):
        receipt = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator())
        inventory = BranchInventory(
            branch_id="synthetic-branch",
            frozen=True,
            current_knowledge_scope="Synthetic gate control only.",
            required_claim_ids=(receipt.claim_id,),
            unclassified_obligations=(),
            frontier_obligations=(),
            inventory_hash=identity("d"),
        )
        paper = PaperEvidence(
            source_hash=identity("e"),
            rendered_paper_hash=identity("f"),
            evidence_map_hash=identity("1"),
            comprehensive_derivation_coverage=True,
            controls_passed=True,
        )
        gate = PublicationGate()
        branch_receipt = gate.branch_ready(inventory, {receipt.claim_id: receipt}, paper)
        final_inventory = FinalTOEInventory(
            required_branch_ids=(inventory.branch_id,),
            global_unclassified_obligations=(),
            global_frontier_obligations=(),
            inventory_hash=identity("2"),
        )
        final_receipt = gate.final_toe_ready(
            final_inventory,
            {inventory.branch_id: branch_receipt},
            paper,
        )
        self.assertTrue(branch_receipt.ready)
        self.assertTrue(final_receipt.ready)

    def test_branch_paper_halts_when_frontier_remains(self):
        receipt = SFTAdmissionEngine().run(ExampleProgram(), ExampleIndependentValidator())
        inventory = BranchInventory(
            branch_id="synthetic-branch",
            frozen=True,
            current_knowledge_scope="Synthetic gate control only.",
            required_claim_ids=(receipt.claim_id,),
            unclassified_obligations=(),
            frontier_obligations=("unclosed-obligation",),
            inventory_hash=identity("3"),
        )
        paper = PaperEvidence(identity("4"), identity("5"), identity("6"), True, True)
        with self.assertRaises(PublicationHalt):
            PublicationGate().branch_ready(inventory, {receipt.claim_id: receipt}, paper)


class RepositoryAdmissionTests(unittest.TestCase):
    def make_repository(self, temporary: str) -> EngineRepository:
        root = Path(temporary)
        (root / "census").mkdir(parents=True)
        (root / "census" / "claims.json").write_text(
            json.dumps(
                {
                    "schema": "sft-v3-fundamental-census/1",
                    "generation": "v3-python-accessible",
                    "phase": "engine-selftest",
                    "claims": [],
                    "unclassified_obligations": [],
                    "future_generation": "v4-sft-derived-self-hosted",
                }
            ),
            encoding="utf-8",
        )
        return EngineRepository(root)

    def test_closed_receipt_is_the_only_census_write_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            receipt = repository.execute(
                ExampleProgram(),
                ExampleIndependentValidator(),
            )
            census = json.loads(repository.census_path.read_text(encoding="utf-8"))
            self.assertEqual([item["claim_id"] for item in census["claims"]], [receipt.claim_id])
            self.assertTrue((repository.root / census["claims"][0]["receipt_path"]).is_file())

    def test_repository_rebuilds_authority_only_from_verified_census_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            receipt = repository.execute(ExampleProgram(), ExampleIndependentValidator())
            reopened = EngineRepository(Path(temporary))
            self.assertTrue(reopened.authority.contains(receipt.claim_id))

    def test_repository_refuses_a_tampered_census_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            repository.execute(ExampleProgram(), ExampleIndependentValidator())
            census = json.loads(repository.census_path.read_text(encoding="utf-8"))
            receipt_path = repository.root / census["claims"][0]["receipt_path"]
            payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            payload["model_admitted"] = False
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(CensusAdmissionError):
                EngineRepository(Path(temporary))

    def test_conditional_evidence_is_preserved_outside_model_census(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            receipt = repository.execute(
                ExampleProgram(scope=ClosureScope.CONDITIONAL_GRAMMAR),
                ExampleIndependentValidator(),
            )
            census = json.loads(repository.census_path.read_text(encoding="utf-8"))
            self.assertFalse(receipt.model_admitted)
            self.assertEqual(census["claims"], [])
            self.assertEqual(
                len(list((repository.root / "receipts" / "engine" / "conditional_evidence").glob("*.json"))),
                1,
            )

    def test_rejection_receipt_is_preserved_without_census_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            program = ExampleProgram()
            program.registration_value = replace(program.registration_value, axioms=("forbidden",))
            with self.assertRaises(EngineHalt):
                repository.execute(program, ExampleIndependentValidator())
            census = json.loads(repository.census_path.read_text(encoding="utf-8"))
            self.assertEqual(census["claims"], [])
            self.assertEqual(
                len(list((repository.root / "receipts" / "engine" / "rejected").glob("*.json"))),
                1,
            )

    def test_official_runner_binds_registration_to_loaded_source_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            source = repository.root / "claim_source.py"
            source.write_text("# synthetic source-bound engine control\n", encoding="utf-8")
            manifest = build_source_manifest(repository.root, (source,))
            program = ExampleProgram()
            program.registration_value = replace(program.registration_value, source_hash=manifest.manifest_hash)
            receipt = repository.execute_official(
                program,
                ExampleIndependentValidator(),
                source_files=(source,),
            )
            self.assertTrue(receipt.model_admitted)

    def test_official_runner_rejects_source_manifest_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_repository(temporary)
            source = repository.root / "claim_source.py"
            source.write_text("# source differs from registered identity\n", encoding="utf-8")
            with self.assertRaises(EngineHalt) as caught:
                repository.execute_official(
                    ExampleProgram(),
                    ExampleIndependentValidator(),
                    source_files=(source,),
                )
            self.assertEqual(caught.exception.receipt.halted_stage, "registration")

    def test_external_command_validator_recomputes_in_separate_process(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "independent_validator.py"
            script.write_text(
                "import json, sys\n"
                "sealed = json.load(open(sys.argv[1], encoding='utf-8'))\n"
                "print(json.dumps({\n"
                "  'validated_seal_hash': sealed['seal_hash'],\n"
                "  'recomputed_from_declared_inputs': True,\n"
                "  'passed': len(sealed['decisions']) == len(sealed['census']['candidates']),\n"
                "  'certificate': {'decision_count': len(sealed['decisions'])}\n"
                "}))\n",
                encoding="utf-8",
            )
            validator = ExternalCommandValidator(
                validator_id="separate-process-selftest",
                command=(sys.executable, str(script)),
                implementation_root=root,
                implementation_files=(script,),
            )
            receipt = SFTAdmissionEngine().run(ExampleProgram(), validator)
            self.assertTrue(receipt.model_admitted)


if __name__ == "__main__":
    unittest.main()

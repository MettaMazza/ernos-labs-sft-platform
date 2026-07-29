"""Unit and integration checks for Reversible and Quantum Computation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unittest
from sft.quantum_computation.current_catalog import SPECS, validate_catalog
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, candidate_records, survivor_id
from sft.quantum_computation.gatex_001_022_laws_v1 import IDS as GATEX_IDS, OBS as GATEX_OBS, SPECS as GATEX_SPECS, GateCircuitExtensionProgram
from sft.quantum_computation.operations import FoldQuantumState, ReversibleGate, apply_gate, complete_support, exhaustive_fault_census, is_factorable, observe, repetition_encode
from sft.quantum_computation.qalgx_001_030_laws_v1 import IDS as QALGX_IDS, OBS as QALGX_OBS, SPECS as QALGX_SPECS, QuantumAlgorithmExtensionProgram
from sft.quantum_computation.qcodex_001_032_laws_v1 import IDS as QCODEX_IDS, OBS as QCODEX_OBS, SPECS as QCODEX_SPECS, QuantumCodingExtensionProgram
from sft.quantum_computation.qcplxx_001_026_laws_v1 import IDS as QCPLXX_IDS, OBS as QCPLXX_OBS, SPECS as QCPLXX_SPECS, QuantumComplexityExtensionProgram
from sft.quantum_computation.qcommx_001_024_laws_v1 import IDS as QCOMMX_IDS, OBS as QCOMMX_OBS, SPECS as QCOMMX_SPECS, QuantumCommunicationExtensionProgram
from sft.quantum_computation.qsimx_001_024_laws_v1 import IDS as QSIMX_IDS, OBS as QSIMX_OBS, SPECS as QSIMX_SPECS, QuantumSimulationExtensionProgram
from sft.quantum_computation.qlearnx_001_022_laws_v1 import IDS as QLEARNX_IDS, OBS as QLEARNX_OBS, SPECS as QLEARNX_SPECS, QuantumLearningExtensionProgram
from sft.quantum_computation.qlimitx_001_022_laws_v1 import IDS as QLIMITX_IDS, OBS as QLIMITX_OBS, SPECS as QLIMITX_SPECS, QuantumLimitsExtensionProgram
from sft.quantum_computation.valid_001_012_laws_v1 import IDS as VALID_IDS, OBS as VALID_OBS, SPECS as VALID_SPECS, QuantumValidationProgram
from sft.quantum_computation.hand_001_006_laws_v1 import IDS as HAND_IDS, OBS as HAND_OBS, SPECS as HAND_SPECS, QuantumHandoffProgram
from sft.quantum_computation.qstatex_001_028_laws_v1 import IDS as QSTATEX_IDS, OBS as QSTATEX_OBS, SPECS as QSTATEX_SPECS, QuantumStateExtensionProgram
from sft.quantum_computation.revx_001_018_laws_v1 import IDS as REVX_IDS, OBS as REVX_OBS, SPECS as REVX_SPECS, ReversibleExtensionProgram


ROOT = Path(__file__).resolve().parents[1]


def canonical(value) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

class QuantumCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_unique_and_ordered(self) -> None:
        validate_catalog()
        self.assertEqual(len(SPECS), 22)
        self.assertEqual(len({spec.claim_id for spec in SPECS}), 22)

    def test_every_claim_has_one_survivor_and_live_witnesses(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = GeneratedQuantumProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                survivor = next(candidate for candidate in census.candidates if candidate.candidate_id == survivor_id(spec))
                self.assertTrue(program.decide_candidate(survivor).survives)
                self.assertFalse(program.decide_candidate(census.candidates[0]).survives)
                self.assertTrue(all(control.passed for control in program.run_controls()))
                self.assertTrue(all(witness.passed for witness in spec.witnesses))

class QuantumOperationalTests(unittest.TestCase):
    def test_entangled_support_is_not_factorable(self) -> None:
        self.assertFalse(is_factorable((("held", "held"), ("returned", "returned"))))
        self.assertTrue(is_factorable((("held", "held"), ("held", "returned"), ("returned", "held"), ("returned", "returned"))))

    def test_measurement_requires_complete_observation(self) -> None:
        state = complete_support(("held", "returned"), ("p1",), ("phase-held", "phase-returned"))
        with self.assertRaises(ValueError):
            observe(state, ((("held",), "left"),), "left")

    def test_reversible_gate_rejects_nonbijection(self) -> None:
        with self.assertRaises(ValueError):
            ReversibleGate(((("held",), ("held",)), (("returned",), ("held",))), ("phase-step",))

    def test_multi_error_census_corrects_widths_three_five_seven(self) -> None:
        expected_rows = {1: 4, 2: 16, 3: 64}
        for depth in (1, 2, 3):
            trace = tuple(f"fault-{index + 1}" for index in range(depth))
            census = exhaustive_fault_census("held", trace)
            self.assertEqual(len(census), expected_rows[depth])
            self.assertTrue(all(decoded == "held" for _word, decoded in census))
            self.assertEqual(len(repetition_encode("held", trace)), 2 * depth + 1)

    def test_state_rejects_duplicate_branch(self) -> None:
        with self.assertRaises(ValueError):
            FoldQuantumState(((("held",), "p"), (("held",), "q")), ("p", "q"))


class ReversibleExtensionFamilyTests(unittest.TestCase):
    def test_revx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(REVX_IDS), 18)
        self.assertEqual(len(set(REVX_IDS)), 18)
        self.assertEqual(len(REVX_OBS), 18)
        self.assertTrue(all(passed for _name, passed in REVX_OBS.values()))

    def test_revx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in REVX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = REVX_SPECS[claim_id]
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = ReversibleExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_revx_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in REVX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class QuantumStateExtensionFamilyTests(unittest.TestCase):
    def test_qstatex_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QSTATEX_IDS), 28)
        self.assertEqual(len(set(QSTATEX_IDS)), 28)
        self.assertEqual(len(QSTATEX_OBS), 28)
        self.assertTrue(all(passed for _name, passed in QSTATEX_OBS.values()))

    def test_qstatex_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QSTATEX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QSTATEX_SPECS[claim_id]
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = QuantumStateExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qstatex_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QSTATEX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class GateCircuitExtensionFamilyTests(unittest.TestCase):
    def test_gatex_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(GATEX_IDS), 22)
        self.assertEqual(len(set(GATEX_IDS)), 22)
        self.assertEqual(len(GATEX_OBS), 22)
        self.assertTrue(all(passed for _name, passed in GATEX_OBS.values()))

    def test_gatex_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in GATEX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = GATEX_SPECS[claim_id]
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = GateCircuitExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_gatex_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in GATEX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class QuantumAlgorithmExtensionFamilyTests(unittest.TestCase):
    def test_qalgx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QALGX_IDS), 30)
        self.assertEqual(len(set(QALGX_IDS)), 30)
        self.assertEqual(len(QALGX_OBS), 30)
        self.assertTrue(all(passed for _name, passed in QALGX_OBS.values()))

    def test_qalgx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QALGX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QALGX_SPECS[claim_id]
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = QuantumAlgorithmExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qalgx_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QALGX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class QuantumComplexityExtensionFamilyTests(unittest.TestCase):
    def test_qcplxx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QCPLXX_IDS), 26)
        self.assertEqual(len(set(QCPLXX_IDS)), 26)
        self.assertEqual(len(QCPLXX_OBS), 26)
        self.assertTrue(all(passed for _name, passed in QCPLXX_OBS.values()))

    def test_qcplxx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QCPLXX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QCPLXX_SPECS[claim_id]
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = QuantumComplexityExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qcplxx_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QCPLXX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class QuantumCommunicationExtensionFamilyTests(unittest.TestCase):
    def test_qcommx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QCOMMX_IDS), 24)
        self.assertEqual(len(set(QCOMMX_IDS)), 24)
        self.assertEqual(len(QCOMMX_OBS), 24)
        self.assertTrue(all(passed for _name, passed in QCOMMX_OBS.values()))

    def test_qcommx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QCOMMX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QCOMMX_SPECS[claim_id]
                self.assertEqual(len(candidate_records(spec)), 256)
                program = QuantumCommunicationExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qcommx_live_receipts_and_packages_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QCOMMX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])


class QuantumCodingExtensionFamilyTests(unittest.TestCase):
    def test_qcodex_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QCODEX_IDS), 32)
        self.assertEqual(len(set(QCODEX_IDS)), 32)
        self.assertEqual(len(QCODEX_OBS), 32)
        self.assertTrue(all(passed for _name, passed in QCODEX_OBS.values()))

    def test_qcodex_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QCODEX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QCODEX_SPECS[claim_id]
                self.assertEqual(len(candidate_records(spec)), 256)
                program = QuantumCodingExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qcodex_live_receipts_packages_and_reconciliation_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QCODEX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])
        reconciliation = json.loads((ROOT / "census/quantum_computation_discipline_current_reconciliation_v8.json").read_text())
        reconciliation_identity = reconciliation.pop("reconciliation_identity")
        self.assertEqual(canonical(reconciliation), reconciliation_identity)
        self.assertEqual(reconciliation["current_closed_count"], 202)
        self.assertEqual(len(reconciliation["completed_families"]["QCODEX"]), 32)


class QuantumSimulationExtensionFamilyTests(unittest.TestCase):
    def test_qsimx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QSIMX_IDS), 24)
        self.assertEqual(len(set(QSIMX_IDS)), 24)
        self.assertEqual(len(QSIMX_OBS), 24)
        self.assertTrue(all(passed for _name, passed in QSIMX_OBS.values()))

    def test_qsimx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QSIMX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QSIMX_SPECS[claim_id]
                self.assertEqual(len(candidate_records(spec)), 256)
                program = QuantumSimulationExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qsimx_live_receipts_packages_and_reconciliation_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QSIMX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])
        reconciliation = json.loads((ROOT / "census/quantum_computation_discipline_current_reconciliation_v9.json").read_text())
        reconciliation_identity = reconciliation.pop("reconciliation_identity")
        self.assertEqual(canonical(reconciliation), reconciliation_identity)
        self.assertEqual(reconciliation["current_closed_count"], 226)
        self.assertEqual(len(reconciliation["completed_families"]["QSIMX"]), 24)


class QuantumLearningExtensionFamilyTests(unittest.TestCase):
    def test_qlearnx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QLEARNX_IDS), 22)
        self.assertEqual(len(set(QLEARNX_IDS)), 22)
        self.assertEqual(len(QLEARNX_OBS), 22)
        self.assertTrue(all(passed for _name, passed in QLEARNX_OBS.values()))

    def test_qlearnx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QLEARNX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QLEARNX_SPECS[claim_id]
                self.assertEqual(len(candidate_records(spec)), 256)
                program = QuantumLearningExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qlearnx_live_receipts_packages_and_reconciliation_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QLEARNX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])
        reconciliation = json.loads((ROOT / "census/quantum_computation_discipline_current_reconciliation_v10.json").read_text())
        reconciliation_identity = reconciliation.pop("reconciliation_identity")
        self.assertEqual(canonical(reconciliation), reconciliation_identity)
        self.assertEqual(reconciliation["current_closed_count"], 248)
        self.assertEqual(len(reconciliation["completed_families"]["QLEARNX"]), 22)


class QuantumLimitsExtensionFamilyTests(unittest.TestCase):
    def test_qlimitx_membership_and_exact_witnesses(self) -> None:
        self.assertEqual(len(QLIMITX_IDS), 22)
        self.assertEqual(len(set(QLIMITX_IDS)), 22)
        self.assertEqual(len(QLIMITX_OBS), 22)
        self.assertTrue(all(passed for _name, passed in QLIMITX_OBS.values()))

    def test_qlimitx_complete_products_have_one_survivor_and_four_controls(self) -> None:
        for claim_id in QLIMITX_IDS:
            with self.subTest(claim_id=claim_id):
                spec = QLIMITX_SPECS[claim_id]
                self.assertEqual(len(candidate_records(spec)), 256)
                program = QuantumLimitsExtensionProgram(spec, "sha256:" + "a" * 64)
                decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                controls = program.run_controls()
                self.assertEqual(len(controls), 4)
                self.assertTrue(all(control.passed for control in controls))

    def test_qlimitx_live_receipts_packages_and_reconciliation_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in QLIMITX_IDS:
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                package = ROOT / "claims" / claim_id
                certificate = json.loads((package / "certificate.json").read_text())
                empirical = json.loads((package / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])
        reconciliation = json.loads((ROOT / "census/quantum_computation_discipline_current_reconciliation_v11.json").read_text())
        reconciliation_identity = reconciliation.pop("reconciliation_identity")
        self.assertEqual(canonical(reconciliation), reconciliation_identity)
        self.assertEqual(reconciliation["current_closed_count"], 270)
        self.assertEqual(len(reconciliation["completed_families"]["QLIMITX"]), 22)


class QuantumClosureFamilyTests(unittest.TestCase):
    def test_valid_and_hand_membership_and_witnesses(self) -> None:
        self.assertEqual((len(VALID_IDS), len(HAND_IDS)), (12, 6))
        self.assertEqual((len(set(VALID_IDS)), len(set(HAND_IDS))), (12, 6))
        self.assertTrue(all(passed for _name, passed in VALID_OBS.values()))
        self.assertTrue(all(passed for _name, passed in HAND_OBS.values()))

    def test_valid_and_hand_products_have_one_survivor_and_controls(self) -> None:
        for ids, specs, program_type in ((VALID_IDS, VALID_SPECS, QuantumValidationProgram), (HAND_IDS, HAND_SPECS, QuantumHandoffProgram)):
            for claim_id in ids:
                with self.subTest(claim_id=claim_id):
                    spec = specs[claim_id]
                    self.assertEqual(len(candidate_records(spec)), 256)
                    program = program_type(spec, "sha256:" + "a" * 64)
                    decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
                    self.assertEqual(sum(decision.survives for decision in decisions), 1)
                    controls = program.run_controls()
                    self.assertEqual(len(controls), 4)
                    self.assertTrue(all(control.passed for control in controls))

    def test_quantum_final_receipts_and_reconciliation_reproduce(self) -> None:
        live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        for claim_id in (*VALID_IDS, *HAND_IDS):
            with self.subTest(claim_id=claim_id):
                row = live[claim_id]
                receipt = json.loads((ROOT / row["receipt_path"]).read_text())
                receipt_hash = receipt.pop("receipt_hash")
                self.assertEqual(canonical(receipt), receipt_hash)
                self.assertEqual(receipt_hash, row["receipt_hash"])
                certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
                empirical = json.loads((ROOT / "claims" / claim_id / "empirical_validation.json").read_text())
                self.assertEqual(certificate["engine_receipt_hash"], receipt_hash)
                self.assertEqual(certificate["candidate_count"], 256)
                self.assertEqual(certificate["unique_survivor_count"], 1)
                self.assertTrue(certificate["controls_passed"])
                self.assertTrue(empirical["all_rows_preserved"])
                self.assertTrue(empirical["passed"])
        reconciliation = json.loads((ROOT / "census/quantum_computation_discipline_current_reconciliation_v13.json").read_text())
        reconciliation_identity = reconciliation.pop("reconciliation_identity")
        self.assertEqual(canonical(reconciliation), reconciliation_identity)
        self.assertEqual(reconciliation["current_closed_count"], 288)
        self.assertEqual(reconciliation["current_open_count"], 0)
        self.assertEqual(sum(len(rows) for rows in reconciliation["completed_families"].values()), 288)

if __name__ == "__main__":
    unittest.main()

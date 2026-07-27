from itertools import product
import unittest

from sft.chemistry.classical_quantum_correspondence_batch_v1 import (
    CLASSICAL_QUANTUM_SPEC,
    GeneratedOperationalChemistryProgram,
)
from sft.chemistry.classical_quantum_correspondence_law_v1 import (
    CERTIFICATE,
    DIMENSIONS,
    EXACT_RESULT,
    MolecularProcess,
    branchwise_certificate,
)
from sft.engine import EvidenceMode
from sft.engine.exact import HeldLabel, InadmissibleExactValue


class ClassicalQuantumChemistryCorrespondenceTests(unittest.TestCase):
    def test_complete_product_has_one_declared_survivor(self) -> None:
        generated = tuple(
            "__".join(choice.name for choice in row)
            for row in product(*(item.choices for item in DIMENSIONS))
        )
        self.assertEqual(len(generated), 256)
        self.assertEqual(len(set(generated)), 256)
        self.assertEqual(sum(candidate == EXACT_RESULT for candidate in generated), 1)

    def test_operational_certificate_preserves_results_records_and_inverse(self) -> None:
        self.assertTrue(CERTIFICATE["passed"])
        self.assertTrue(CERTIFICATE["complete_records"])
        self.assertTrue(CERTIFICATE["inverse_restores"])
        classical = {source: target for source, target, _trace in CERTIFICATE["classical_rows"]}
        self.assertEqual(classical, dict(CERTIFICATE["quantum_decoded_rows"]))

    def test_successor_accepts_an_additional_distinct_reversible_row(self) -> None:
        process = MolecularProcess(
            HeldLabel("molecular-carrier", "successor-witness"),
            (("alpha", "beta"), ("beta", "gamma"), ("gamma", "alpha")),
            HeldLabel("admitted-chemical-transition-law", "successor-law"),
        )
        certificate = branchwise_certificate(process)
        self.assertTrue(certificate["passed"])
        self.assertEqual(len(certificate["classical_rows"]), 3)
        self.assertEqual(len(certificate["quantum_decoded_rows"]), 3)
        self.assertTrue(all(len(record) == 3 for record in certificate["measurement_records"]))

    def test_nonbijective_process_halts(self) -> None:
        with self.assertRaises(InadmissibleExactValue):
            MolecularProcess(
                HeldLabel("molecular-carrier", "invalid-witness"),
                (("alpha", "gamma"), ("beta", "gamma")),
                HeldLabel("admitted-chemical-transition-law", "invalid-law"),
            )

    def test_registration_is_formal_chemistry_with_no_axioms_or_parameters(self) -> None:
        program = GeneratedOperationalChemistryProgram(CLASSICAL_QUANTUM_SPEC, "sha256:" + "a" * 64)
        registration = program.registration
        self.assertEqual(registration.branch, "chemistry")
        self.assertEqual(registration.evidence_mode, EvidenceMode.FORMAL)
        self.assertEqual(registration.axioms, ())
        self.assertEqual(registration.free_parameters, ())


if __name__ == "__main__":
    unittest.main()

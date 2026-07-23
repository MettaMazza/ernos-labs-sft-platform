"""Unit and integration checks for the complete mathematics law catalog."""

from __future__ import annotations

import unittest

from sft.mathematics.algebraic_structures.law import OperationTable
from sft.mathematics.catalog import SPECS, validate_catalog
from sft.mathematics.category_type_composition.law import Arrow, compose
from sft.mathematics.combinatorics.law import arrangements, selections
from sft.mathematics.discrete_mathematics.law import generated_collection, successor_trace
from sft.mathematics.dynamical_systems.law import transition_time
from sft.mathematics.exact_arithmetic.law import disjoint_junction, trace
from sft.mathematics.generated_law import (
    GeneratedMathematicsProgram,
    candidate_records,
    survivor_id,
)
from sft.mathematics.geometry_topology.law import EMPTY_ONE as GEOMETRIC_EMPTY_ONE
from sft.mathematics.geometry_topology.law import is_finite_topology
from sft.mathematics.graph_network.law import GeneratedGraph, crossing_cut
from sft.mathematics.logic_proof.law import Proposition, denied
from sft.mathematics.optimization.law import exact_optimum
from sft.mathematics.order_lattice.law import is_partial_order
from sft.mathematics.probability_statistics.law import independent


class MathematicsCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_unique_and_dependency_ordered(self) -> None:
        validate_catalog()
        self.assertEqual(len(SPECS), 12)
        self.assertEqual(len({spec.claim_id for spec in SPECS}), 12)

    def test_every_product_is_complete_and_has_one_survivor(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                records = candidate_records(spec)
                expected = 2 ** len(spec.dimensions)
                self.assertEqual(len(records), expected)
                self.assertEqual(len({record["candidate_id"] for record in records}), expected)
                program = GeneratedMathematicsProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                expected_survivor = survivor_id(spec)
                self.assertEqual(
                    tuple(record["candidate_id"] for record in records if record["candidate_id"] == expected_survivor),
                    (expected_survivor,),
                )
                survivor_candidate = next(
                    candidate for candidate in census.candidates
                    if candidate.candidate_id == expected_survivor
                )
                sampled_candidates = (census.candidates[0], survivor_candidate, census.candidates[-1])
                sampled_decisions = tuple(program.decide_candidate(candidate) for candidate in sampled_candidates)
                self.assertTrue(program.decide_candidate(survivor_candidate).survives)
                self.assertTrue(any(not decision.survives for decision in sampled_decisions))
                closure = program.closure_evidence(sampled_decisions)
                self.assertTrue(closure.minimality_passed)
                self.assertTrue(closure.named_shape_uniqueness_passed)
                self.assertTrue(all(control.passed for control in program.run_controls()))

    def test_operational_witnesses_are_all_live(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                self.assertTrue(all(witness.passed for witness in spec.witnesses))


class MathematicsBoundaryTests(unittest.TestCase):
    def test_exact_arithmetic_rejects_overlapping_junction(self) -> None:
        held = trace("held")
        with self.assertRaises(ValueError):
            disjoint_junction(held, held)

    def test_discrete_successor_requires_fresh_form(self) -> None:
        carrier = generated_collection(("a",), ("b",))
        with self.assertRaises(ValueError):
            successor_trace(carrier, ("a",))

    def test_combinatorics_rejects_duplicate_carrier(self) -> None:
        with self.assertRaises(ValueError):
            arrangements(("a", "a"))
        with self.assertRaises(ValueError):
            selections(())

    def test_graph_rejects_external_endpoint_and_empty_cut(self) -> None:
        with self.assertRaises(ValueError):
            GeneratedGraph(("a",), (("a", "b"),))
        graph = GeneratedGraph(("a", "b"), (("a", "b"),))
        with self.assertRaises(ValueError):
            crossing_cut(graph, ())

    def test_algebra_rejects_partial_or_open_operation(self) -> None:
        with self.assertRaises(ValueError):
            OperationTable(("a", "b"), (("a", "a", "a"),))
        with self.assertRaises(ValueError):
            OperationTable(
                ("a",),
                (("a", "a", "external"),),
            )

    def test_order_rejects_missing_transitive_cell(self) -> None:
        carrier = ("a", "b", "c")
        relation = (("a", "a"), ("b", "b"), ("c", "c"), ("a", "b"), ("b", "c"))
        self.assertFalse(is_partial_order(carrier, relation))

    def test_topology_requires_generated_closure(self) -> None:
        self.assertFalse(is_finite_topology(("a", "b"), (GEOMETRIC_EMPTY_ONE, ("a",), ("b",))))

    def test_probability_rejects_empty_independence_arithmetic(self) -> None:
        joint = (("a", "x"), ("a", "y"), ("b", "x"), ("b", "y"))
        with self.assertRaises(ValueError):
            independent(joint, (), ("x",))

    def test_optimization_retains_tied_optima(self) -> None:
        self.assertEqual(
            exact_optimum(("a", "b"), ()),
            ("retained-equivalence-class", ("a", "b")),
        )

    def test_identity_time_is_empty_one(self) -> None:
        self.assertEqual(transition_time(("state",)), ("empty-One",))

    def test_denial_is_orientation_not_negative_value(self) -> None:
        held = Proposition("P", "held")
        self.assertEqual(denied(held), Proposition("P", "complementary-held"))

    def test_composition_rejects_interface_mismatch(self) -> None:
        left = Arrow("f", "A", "B", ("f",))
        right = Arrow("g", "C", "D", ("g",))
        with self.assertRaises(ValueError):
            compose(left, right)


if __name__ == "__main__":
    unittest.main()

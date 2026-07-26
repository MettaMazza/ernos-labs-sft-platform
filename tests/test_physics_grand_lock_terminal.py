from sft.physics.grand_lock_terminal_law_v1 import generator_value_vector, theorem_certificate


def test_grand_lock_dependency_and_root_trace():
    certificate = theorem_certificate()
    assert certificate["dependency"]["no_omission"]
    assert certificate["dependency"]["acyclic"]
    assert certificate["dependency"]["all_reach_one"]
    assert certificate["dependency"]["all_evidence_hash_bound"]


def test_grand_lock_current_vector_and_generator_adverse_census():
    certificate = theorem_certificate()
    assert certificate["current_cross_lock"]
    assert certificate["all_declared_generator_dependent_values_move"]
    assert certificate["generator_independent_values_hold"]
    assert all(generator_value_vector(3)[key] != generator_value_vector(4)[key] for key in generator_value_vector(3))


def test_grand_lock_empirical_and_extension_boundaries():
    certificate = theorem_certificate()
    assert certificate["dependency"]["empirical_claim_count"] == 234
    assert certificate["dependency"]["unfavorable_or_scope_boundary_count"] == 14
    assert certificate["cross_domain_graph_complete"]

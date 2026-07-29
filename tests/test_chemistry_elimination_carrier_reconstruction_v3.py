import json

from sft.chemistry.elimination_carrier_reconstruction_v3 import (
    ROOT,
    reconstruct_adverse_controls,
    reconstruct_complete_carrier_closures,
)


def test_all_thirty_two_source_rows_have_exact_complete_carrier_closure() -> None:
    rows = reconstruct_complete_carrier_closures()
    assert len(rows) == 32
    assert [row.ordinal.value for row in rows] == list(range(1, 33))
    assert all(row.equation.is_exactly_closed for row in rows)
    assert all(row.complete_carrier_custody_reconstructed for row in rows)
    assert all(row.product_unsaturation_observed for row in rows)
    assert all(not row.scientific_result_retired for row in rows)


def test_the_two_source_procedures_retain_their_distinct_reagents() -> None:
    rows = reconstruct_complete_carrier_closures()
    assert [row.equation.procedure.label for row in rows[:20]] == ["2.16"] * 20
    assert [row.equation.procedure.label for row in rows[20:]] == ["2.17"] * 12
    assert {row.equation.reagent.label for row in rows[:20]} == {"2-bromo-2-nitropropane"}
    assert {row.equation.reagent.label for row in rows[20:]} == {"2-bromo-2-nitroadamantane"}
    assert {row.equation.reduced_reagent.label for row in rows[:20]} == {"2-nitropropane"}
    assert {row.equation.reduced_reagent.label for row in rows[20:]} == {"2-nitroadamantane"}


def test_structural_reconstruction_is_not_mislabeled_as_separate_coproduct_measurement() -> None:
    rows = reconstruct_complete_carrier_closures()
    assert all(not row.every_coproduct_separately_measured for row in rows)
    assert all(row.source_block.label.startswith("sha256:") for row in rows)


def test_all_five_unsuccessful_controls_remain_outside_successful_closure_vector() -> None:
    rows = reconstruct_complete_carrier_closures()
    controls = reconstruct_adverse_controls()
    assert len(rows) == 32
    assert len(controls) == 5
    assert any(observation.label == "No reaction" for _, _, observation in controls)
    assert any(observation.label == "<5% elimination" for _, _, observation in controls)


def test_implementation_distinct_artifact_reconstructs_the_same_complete_boundary() -> None:
    path = (
        ROOT
        / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
        / "complete-carrier-reconstruction-v3.json"
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["complete_product_count"] == 32
    assert document["procedure_counts"] == {"2.16": 20, "2.17": 12}
    assert document["exact_carrier_match_count"] == 32
    assert document["unresolved_complete_carrier_count"] == 0
    assert document["all_unsuccessful_controls_retained"] is True
    assert len(document["unsuccessful_controls"]) == 5
    assert all(row["left_positive_atom_support"] == row["right_positive_atom_support"] for row in document["rows"])
    assert all(row["every_coproduct_separately_measured"] is False for row in document["rows"])

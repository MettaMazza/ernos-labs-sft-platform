from sft.chemistry.elimination_carrier_status_v2 import (
    reconstruct_carrier_obligations,
    reconstruct_unsuccessful_controls,
)


def test_all_product_results_and_all_carrier_obligations_remain_distinct() -> None:
    rows = reconstruct_carrier_obligations()
    assert len(rows) == 32
    assert all(row.product_unsaturation_observed for row in rows)
    assert all(not row.complete_carrier_custody_observed for row in rows)
    assert all(not row.scientific_result_retired for row in rows)


def test_all_unfavorable_substrate_controls_remain_visible() -> None:
    controls = reconstruct_unsuccessful_controls()
    assert len(controls) == 5
    assert controls[-1][2] == "<5% elimination"
    assert any(row[2] == "No reaction" for row in controls)

from fractions import Fraction

import pytest

from sft.biology.molx_001_014_laws_v1 import (
    ABSENCE,
    ORDER,
    SPECS,
    amino_acid_routing,
    branch_allocation,
    carbohydrate_storage,
    carbon_fixation,
    chemiosmotic_transport,
    cofactor_dependence,
    coupled_work,
    enzyme_specificity,
    finite_enzyme_throughput,
    lipid_lifecycle,
    metabolome_flux_custody,
    nutrient_cycle,
    reaction_balance,
    redox_transfer,
)


def test_complete_family_and_candidate_grammar():
    assert len(ORDER) == len(SPECS) == 14
    assert len(set(ORDER)) == 14
    assert all(len(spec.axes) == 8 for spec in SPECS.values())
    assert all(all(witness.passed for witness in spec.witnesses) for spec in SPECS.values())
    assert all("no-extra-rule" in tuple(axis.survivor.name for axis in spec.axes) for spec in SPECS.values())


def test_reaction_and_enzyme_relations():
    assert reaction_balance({"C": 2, "O": 4}, {"C": 2, "O": 4}, ("a",), ("b",), "forward")["balanced"]
    assert enzyme_specificity("e", ("a",), "b", "p")["product"] == ABSENCE
    assert finite_enzyme_throughput(8, 2, 3)["processed"] == 6
    assert finite_enzyme_throughput(8, 2, 3, 1)["processed"] == 3


def test_carrier_coupling_and_transport():
    assert redox_transfer("d", "a", 5, 4, 3, "electron")["donor_remainder"] == 2
    assert coupled_work(5, 3, 3, "ATP-equivalent")["work_per_spent_part"] == Fraction(1, 1)
    assert chemiosmotic_transport(5, 3, 1, "m", "r", "ion")["residual_excess"] == ABSENCE


def test_carbon_nutrient_and_biomolecule_custody():
    assert carbon_fixation(("c1", "c2"), ("p1", "p2"), ("capture", "product"))["fixed_count"] == 2
    assert branch_allocation(5, {"a": 2, "b": 3}, "condition")["unassigned"] == ABSENCE
    assert nutrient_cycle("N", ("e", "c", "p", "e"), 2, "habitat")["returned_to_source_state"]
    assert lipid_lifecycle("head", ("t1", "t2"), ("synthesis", "incorporation", "remodelling", "degradation"), "membrane")["stage_count"] == 4
    assert carbohydrate_storage("unit", 5, 5, "store")["retained_units"] == ABSENCE
    assert amino_acid_routing("aa", "N", "C", "n-fate", "c-fate")["complete_fate_custody"]


def test_cofactor_and_metabolome_missingness():
    assert cofactor_dependence("e", "s", "p", "c", False)["product"] == ABSENCE
    record = metabolome_flux_custody({"a": 2}, ("b",), (("a", "b", 1),), "condition")
    assert record["missing"] == ("b",)
    assert record["all_result_classes_retained"]


@pytest.mark.parametrize("value", (0, -1, 1.5, True))
def test_nonpositive_or_inexact_native_carrier_halts(value):
    with pytest.raises(ValueError):
        finite_enzyme_throughput(value, 1, 1)


def test_unbalanced_or_overdrawn_requests_halt():
    with pytest.raises(ValueError):
        reaction_balance({"C": 1}, {"C": 2}, ("a",), ("b",), "forward")
    with pytest.raises(ValueError):
        redox_transfer("d", "a", 2, 2, 3, "electron")
    with pytest.raises(ValueError):
        branch_allocation(5, {"a": 2, "b": 2}, "condition")

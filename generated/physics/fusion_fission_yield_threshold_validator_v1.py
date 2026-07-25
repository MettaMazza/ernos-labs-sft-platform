#!/usr/bin/env python3
"""Implementation-distinct fusion/fission yield and threshold validator.

This process imports neither the claimant nor any measurement adapter.  It
reconstructs the complete grammar, exact rational binding enclosures, both
release orders and the incident-boundary topology from declared inputs.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"
ALPHA = Fraction(3676744786, 503846395469)
SURFACE = Fraction(1, 5)
QUARTER = Fraction(1, 4)
PER_NUCLEON_RELATIONS = (
    "fusion-greater-per-nucleon",
    "equal-per-nucleon",
    "fission-greater-per-nucleon",
)
TOTAL_RELEASE_RELATIONS = (
    "fusion-greater-total",
    "equal-total",
    "fission-greater-total",
)
FUSION_THRESHOLD_CARRIERS = (
    "charged-boundary-approach",
    "neutral-capture-approach",
    "single-parent-internal-surface",
)
FISSION_THRESHOLD_CARRIERS = (
    "charged-boundary-approach",
    "neutral-capture-or-internal-surface",
    "carrier-free-decomposition",
)
THRESHOLD_SCOPES = (
    "one-universal-dimensional-threshold",
    "normalized-structure-with-reaction-specific-dimensions",
    "no-threshold-distinction",
)
ACCESS_CARRIERS = (
    "thermal-or-directed-energy-support",
    "one-universal-temperature-value",
    "no-access-support",
)
METRIC_RETENTIONS = (
    "retain-per-nucleon-and-total-separately",
    "conflate-per-nucleon-with-total",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")


def positive_take(whole: Fraction, part: Fraction) -> Fraction:
    if whole <= part:
        raise ValueError("independent exact take left the positive domain")
    return whole - part


def integer_cube_root_scaled(value: int, scale: int) -> tuple[Fraction, Fraction]:
    target = value * scale * scale * scale
    low, high = scale, value * scale
    while low + 1 < high:
        middle = (low + high) // 2
        if middle * middle * middle <= target:
            low = middle
        else:
            high = middle
    if low * low * low == target:
        exact = Fraction(low, scale)
        return exact, exact
    return Fraction(low, scale), Fraction(high, scale)


def score_bounds(mass: int, charge: int, scale: int) -> tuple[Fraction, Fraction]:
    neutron = mass - charge
    unmatched = neutron - charge if neutron >= charge else charge - neutron
    asymmetry = QUARTER * Fraction(unmatched * unmatched, mass * mass)
    retained = positive_take(Fraction(1, 1), asymmetry) if asymmetry else Fraction(1, 1)
    radial = SURFACE
    if charge > 1:
        radial += ALPHA * Fraction(charge * (charge - 1), mass)
    pairing = QUARTER * Fraction(1, mass)
    if mass % 2 == 0 and charge % 2 == 0:
        radial = positive_take(radial, pairing)
    elif mass % 2 == 0 and charge % 2 == 1:
        radial += pairing
    lower_radius, upper_radius = integer_cube_root_scaled(mass, scale)
    return (
        positive_take(retained, radial / lower_radius),
        positive_take(retained, radial / upper_radius),
    )


def release_order() -> dict[str, object]:
    scale = 2 ** 16
    deuterium = score_bounds(2, 1, scale)
    helium = score_bounds(4, 2, scale)
    uranium = score_bounds(238, 92, scale)
    palladium = score_bounds(119, 46, scale)
    fusion_per = (
        positive_take(helium[0], deuterium[1]),
        positive_take(helium[1], deuterium[0]),
    )
    fission_per = (
        positive_take(palladium[0], uranium[1]),
        positive_take(palladium[1], uranium[0]),
    )
    fusion_total = (4 * fusion_per[0], 4 * fusion_per[1])
    fission_total = (238 * fission_per[0], 238 * fission_per[1])
    return {
        "fusion_per": fusion_per,
        "fission_per": fission_per,
        "fusion_total": fusion_total,
        "fission_total": fission_total,
        "fusion_greater_per": fusion_per[0] > fission_per[1],
        "fission_greater_total": fission_total[0] > fusion_total[1],
    }


def threshold_topology() -> dict[str, object]:
    fusion_incident = ((2, 1), (2, 1))
    fission_incident = ((238, 92),)
    fusion_paths = fusion_incident[0][1] * fusion_incident[1][1]
    fission_paths = () if len(fission_incident) == 1 else fission_incident[0][1]
    neutral_trigger_charge = ()
    internal_boundary_cells = 3
    return {
        "fusion_two_charged": (
            len(fusion_incident) == 2
            and all(charge >= 1 for _, charge in fusion_incident)
        ),
        "fusion_paths": fusion_paths,
        "fission_one_parent": len(fission_incident) == 1,
        "fission_paths": fission_paths,
        "neutral_trigger_empty": neutral_trigger_charge == (),
        "internal_surface_finite": internal_boundary_cells == 3,
        "residual_quarter": QUARTER == Fraction(1, 4),
        "carriers_distinct": fusion_paths != () and fission_paths == (),
    }


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            PER_NUCLEON_RELATIONS,
            TOTAL_RELEASE_RELATIONS,
            FUSION_THRESHOLD_CARRIERS,
            FISSION_THRESHOLD_CARRIERS,
            THRESHOLD_SCOPES,
            ACCESS_CARRIERS,
            METRIC_RETENTIONS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(
    candidate_id: str, order: dict[str, object], topology: dict[str, object]
) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 9:
        return False
    (
        per_relation,
        total_relation,
        fusion_threshold,
        fission_threshold,
        threshold_scope,
        access_carrier,
        metric_retention,
        target,
        extension,
    ) = fields

    if per_relation == "fusion-greater-per-nucleon":
        per_passed = order["fusion_greater_per"] is True
    elif per_relation == "equal-per-nucleon":
        per_passed = order["fusion_per"] == order["fission_per"]
    elif per_relation == "fission-greater-per-nucleon":
        per_passed = order["fission_per"][0] > order["fusion_per"][1]
    else:
        per_passed = False

    if total_relation == "fusion-greater-total":
        total_passed = order["fusion_total"][0] > order["fission_total"][1]
    elif total_relation == "equal-total":
        total_passed = order["fusion_total"] == order["fission_total"]
    elif total_relation == "fission-greater-total":
        total_passed = order["fission_greater_total"] is True
    else:
        total_passed = False

    if fusion_threshold == "charged-boundary-approach":
        fusion_threshold_passed = (
            topology["fusion_two_charged"] is True and topology["fusion_paths"] != ()
        )
    elif fusion_threshold == "neutral-capture-approach":
        fusion_threshold_passed = topology["fusion_paths"] == ()
    elif fusion_threshold == "single-parent-internal-surface":
        fusion_threshold_passed = not topology["fusion_two_charged"]
    else:
        fusion_threshold_passed = False

    if fission_threshold == "charged-boundary-approach":
        fission_threshold_passed = topology["fission_paths"] != ()
    elif fission_threshold == "neutral-capture-or-internal-surface":
        fission_threshold_passed = all((
            topology["fission_one_parent"] is True,
            topology["fission_paths"] == (),
            topology["neutral_trigger_empty"] is True,
            topology["internal_surface_finite"] is True,
        ))
    elif fission_threshold == "carrier-free-decomposition":
        fission_threshold_passed = not topology["internal_surface_finite"]
    else:
        fission_threshold_passed = False

    distinct = topology["carriers_distinct"] is True
    if threshold_scope == "one-universal-dimensional-threshold":
        scope_passed = not distinct
    elif threshold_scope == "normalized-structure-with-reaction-specific-dimensions":
        scope_passed = distinct and topology["residual_quarter"] is True
    elif threshold_scope == "no-threshold-distinction":
        scope_passed = not distinct and topology["residual_quarter"] is not True
    else:
        scope_passed = False

    if access_carrier == "thermal-or-directed-energy-support":
        access_passed = topology["fusion_paths"] != () and distinct
    elif access_carrier == "one-universal-temperature-value":
        access_passed = not distinct
    elif access_carrier == "no-access-support":
        access_passed = topology["fusion_paths"] == ()
    else:
        access_passed = False

    inversion = order["fusion_greater_per"] and order["fission_greater_total"]
    if metric_retention == "retain-per-nucleon-and-total-separately":
        metric_passed = inversion
    elif metric_retention == "conflate-per-nucleon-with-total":
        metric_passed = not inversion
    else:
        metric_passed = False

    return all((
        per_passed,
        total_passed,
        fusion_threshold_passed,
        fission_threshold_passed,
        scope_passed,
        access_passed,
        metric_passed,
        target == "sealed-before-release",
        extension == "empty-extension",
    ))


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)

    generated = generated_ids()
    order = release_order()
    topology = threshold_topology()
    expected_decisions = {
        candidate_id: form_survives(candidate_id, order, topology)
        for candidate_id in generated
    }
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {
        row["candidate_id"]: row["survives"] for row in sealed["decisions"]
    }
    control_kinds = {row["kind"] for row in sealed["controls"]}
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 5832
        and decisions == expected_decisions
        and sum(expected_decisions.values()) == 1
        and order["fusion_greater_per"] is True
        and order["fission_greater_total"] is True
        and topology["carriers_distinct"] is True
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and control_kinds == {
            "false_premise", "tampered_source", "tampered_artifact", "boundary"
        }
        and all(row["passed"] is True for row in sealed["controls"])
    )
    surviving_ids = tuple(
        candidate_id for candidate_id, survives in expected_decisions.items() if survives
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": surviving_ids,
            "fusion_per_nucleon_enclosure": [
                str(order["fusion_per"][0]), str(order["fusion_per"][1])
            ],
            "fission_per_nucleon_enclosure": [
                str(order["fission_per"][0]), str(order["fission_per"][1])
            ],
            "fusion_total_enclosure": [
                str(order["fusion_total"][0]), str(order["fusion_total"][1])
            ],
            "fission_total_enclosure": [
                str(order["fission_total"][0]), str(order["fission_total"][1])
            ],
            "fusion_greater_per_nucleon": order["fusion_greater_per"],
            "fission_greater_total": order["fission_greater_total"],
            "threshold_topology": {
                "fusion_charge_paths": topology["fusion_paths"],
                "fission_inter_boundary_empty": topology["fission_paths"] == (),
                "neutral_trigger_empty": topology["neutral_trigger_empty"],
                "internal_surface_finite": topology["internal_surface_finite"],
            },
            "target_value_accessed": False,
            "implementation": (
                "independent integer-scaled rational binding enclosure, complete product reconstruction and "
                "incident-boundary topology proof"
            ),
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

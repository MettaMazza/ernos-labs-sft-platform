"""Registered THERMO-004 heat/work partition and sealed external surface."""

from __future__ import annotations

from sft.chemistry.generated_law import EmpiricalChemistrySpec
from sft.chemistry.internal_energy_composition_batch_v1 import TARGET_REFERENCES
from sft.chemistry.heat_work_transfer_partition_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES


HEAT_WORK_TRANSFER_PARTITION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    title="Chemical heat and work transfer partition",
    statement=(
        "For one held chemical boundary and path, carrier identity closed by the receiving macro-observation forces "
        "the heat class, while a retained organized source-to-response identity forces the work class. Direction is "
        "held separately from exact positive content; every transfer remains in a disjoint exhaustive path record, "
        "and an absent class is structural EmptyOne."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, class, orientation, partition, composition, prediction, record and "
        "extension forms; decide all 256 candidates only from admitted Fold observation, conservation, composition, "
        "Physics heat/work and chemical internal-energy laws."
    ),
    grammar_boundary=(
        "Every finite nonempty chemical transfer path across one held boundary, with each exact positive transfer "
        "classified only by retained or closed carrier identity and with append-only successor closure. External "
        "testing retains every column and row of the frozen NIST one-bar water surface."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One exact positive transfer across one held chemical boundary has one observation-forced class and one "
        "retained path record; the other class is structural EmptyOne."
    ),
    induction_step=(
        "Appending one transfer assigns it to exactly one class from its carrier observation, preserves every prior "
        "record and class subtotal, and adds its positive content exactly once to its class and complete total."
    ),
    exclusions=(
        "no numerical zero; an absent transfer class is structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no imported heat/work equation, fitted coefficient, target-selected class or measured transfer value",
        "no target payload, temperature, phase, heat capacity, volume, enthalpy or internal energy before prediction seal",
        "no signed net cancellation, merged transfer classes, omitted path record or selected external row",
        "external signed glyphs remain source inscriptions and never enter an SFT proof magnitude",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    expected_observation_label="complete-chemical-heat-work-transfer-partition",
    target_rows=TARGET_REFERENCES,
    observation_registry_path="experiments/external_sources/chemistry/thermophysical_state_withheld_targets_v1.json",
    falsification_condition=(
        "The claim fails if one transfer requires an arbitrary rather than observation-forced heat/work class; if a "
        "transfer occurs in both or neither class; if direction requires a negative proof value; if an absent class "
        "requires numerical zero; if appending a transfer changes a prior record; if any target opens before all "
        "identities seal; if any returned row or column is omitted; if any direct calorimetric or expansion-work "
        "magnitude is not positive; if the independently recorded enthalpy/internal-energy separation and pressure-"
        "volume work do not agree within their exact displayed-resolution bounds; or if target values select the law."
    ),
)
HEAT_WORK_TRANSFER_PARTITION_SPEC.validate()


__all__ = ("HEAT_WORK_TRANSFER_PARTITION_SPEC",)

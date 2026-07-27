"""Registered THERMO-006 enthalpy-equivalent state law and external surface."""

from __future__ import annotations

from sft.chemistry.enthalpy_equivalent_state_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import EmpiricalChemistrySpec
from sft.chemistry.internal_energy_composition_batch_v1 import TARGET_REFERENCES


ENTHALPY_EQUIVALENT_STATE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
    title="Enthalpy-equivalent chemical state relation",
    statement=(
        "An enthalpy-equivalent chemical state is the complete held composition, molecular state, phase and "
        "environment carrier whose exact positive content composes admitted internal energy with every retained "
        "organized environment-transfer part. If no such part is generated its place is structural EmptyOne. State "
        "orientation is held separately from exact positive separation."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of state, internal, environment, composition, orientation, prediction, record "
        "and extension forms; decide all 256 candidates only from admitted exact composition, energy conservation, "
        "heat/work observation and chemical internal-energy laws."
    ),
    grammar_boundary=(
        "Every finite complete chemical state with exact positive internal content and every finite tuple of uniquely "
        "named retained organized environment-transfer parts, including structural EmptyOne absence and append-only "
        "successor closure. External testing retains all rows and columns of the frozen NIST one-bar water surface."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One complete held chemical state with exact positive internal content and structural EmptyOne environment "
        "transfer has enthalpy-equivalent content identical to the retained internal carrier."
    ),
    induction_step=(
        "Appending one fresh named exact positive environment-transfer part preserves the complete state, internal "
        "content and every prior transfer part and adds the new content exactly once."
    ),
    exclusions=(
        "no numerical zero; absent environment contribution is structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no imported enthalpy or pressure-volume equation, fitted correction or target-selected environment part",
        "no target payload, enthalpy, internal energy, pressure, volume, phase or temperature before prediction seal",
        "no signed cancellation, unnamed contribution, selected state row, selected phase or deleted boundary state",
        "external conventional component relations remain post-seal correspondence records only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
    expected_observation_label="complete-enthalpy-equivalent-state-and-environment-carrier",
    target_rows=TARGET_REFERENCES,
    observation_registry_path="experiments/external_sources/chemistry/thermophysical_state_withheld_targets_v1.json",
    falsification_condition=(
        "The claim fails if an enthalpy-equivalent state requires an imported thermodynamic equation, signed scalar, "
        "fitted environment correction or lost state identity; if absence requires numerical zero; if direction "
        "requires negative content; if successor extension changes a prior part; if any target opens before all "
        "identities seal; if any of thirteen enthalpy/component rows is omitted; if the complete enthalpy path or "
        "environment contributions are not exact positive; if the independent pressure-volume and enthalpy/internal-"
        "energy component records disagree beyond exact displayed-resolution bounds; or if targets select the law."
    ),
)
ENTHALPY_EQUIVALENT_STATE_SPEC.validate()


__all__ = ("ENTHALPY_EQUIVALENT_STATE_SPEC",)

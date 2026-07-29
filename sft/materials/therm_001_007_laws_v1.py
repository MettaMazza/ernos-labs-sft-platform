"""Exact Fold laws for the complete Materials THERM-001--007 family."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive exact count")
    return value


def diffusivity_relation(conductivity, density, specific_heat):
    conductivity = positive(conductivity, "conductivity")
    density = positive(density, "density")
    specific_heat = positive(specific_heat, "specific heat")
    volumetric_heat_capacity = density * specific_heat
    return {
        "conductivity": conductivity,
        "density": density,
        "specific_heat": specific_heat,
        "volumetric_heat_capacity": volumetric_heat_capacity,
        "diffusivity_part": Fraction(conductivity, volumetric_heat_capacity),
        "closes": Fraction(conductivity, volumetric_heat_capacity) * volumetric_heat_capacity == conductivity,
    }


def boundary_resistance(temperature_drop, heat_flow, area, interface):
    if not interface:
        raise ValueError("held interface identity required")
    temperature_drop = positive(temperature_drop, "temperature drop")
    heat_flow = positive(heat_flow, "heat flow")
    area = positive(area, "area")
    return {
        "interface": interface,
        "temperature_drop": temperature_drop,
        "heat_flow": heat_flow,
        "area": area,
        "resistance_part": Fraction(temperature_drop * area, heat_flow),
        "conductance_part": Fraction(heat_flow, temperature_drop * area),
    }


def phonon_mean_path(path_segments, scattering_labels):
    segments = tuple(positive(value, "path segment") for value in path_segments)
    labels = tuple(scattering_labels)
    if not segments or len(segments) != len(labels) or any(not label for label in labels):
        raise ValueError("every path segment requires one held scattering label")
    total = sum(segments)
    return {
        "path_segments": segments,
        "scattering_labels": labels,
        "event_count": len(labels),
        "total_path": total,
        "mean_path": Fraction(total, len(labels)),
        "complete_event_custody": True,
    }


def radiative_partition(incident, reflected, transmitted, absorbed, band, direction):
    values = tuple(positive(value, name) for value, name in ((incident, "incident"), (reflected, "reflected"), (transmitted, "transmitted"), (absorbed, "absorbed")))
    if values[1] + values[2] + values[3] != values[0] or not band or direction not in ("toward", "away"):
        raise ValueError("radiative carrier, spectral band and orientation must close exactly")
    return {
        "incident": values[0],
        "reflected": values[1],
        "transmitted": values[2],
        "absorbed": values[3],
        "band": band,
        "direction": direction,
        "reflected_part": Fraction(values[1], values[0]),
        "transmitted_part": Fraction(values[2], values[0]),
        "absorbed_part": Fraction(values[3], values[0]),
        "closes": True,
    }


def thermoelectric_boundary(seebeck, temperature, resistivity, conductivity):
    seebeck = positive(seebeck, "Seebeck carrier")
    temperature = positive(temperature, "temperature carrier")
    resistivity = positive(resistivity, "resistivity carrier")
    conductivity = positive(conductivity, "thermal conductivity carrier")
    return {
        "seebeck": seebeck,
        "temperature": temperature,
        "resistivity": resistivity,
        "thermal_conductivity": conductivity,
        "performance_part": Fraction(seebeck * seebeck * temperature, resistivity * conductivity),
        "all_coupled_carriers_held": True,
    }


def phase_storage(sensible_before, latent, sensible_after, phase_path):
    before = positive(sensible_before, "pre-transition sensible carrier")
    latent = positive(latent, "latent carrier")
    after = positive(sensible_after, "post-transition sensible carrier")
    path = tuple(phase_path)
    if len(path) < 3 or not all(path) or path[0] == path[-1]:
        raise ValueError("complete phase-transition path required")
    return {
        "sensible_before": before,
        "latent": latent,
        "sensible_after": after,
        "phase_path": path,
        "stored_total": before + latent + after,
        "latent_part": Fraction(latent, before + latent + after),
        "transition_retained": True,
    }


def thermal_shock_fatigue(temperature_steps, orientations, crack_counts, critical_step):
    steps = tuple(positive(value, "temperature step") for value in temperature_steps)
    directions = tuple(orientations)
    cracks = tuple(None if value is None else positive(value, "crack count") for value in crack_counts)
    critical_step = positive(critical_step, "critical step")
    if not steps or len(steps) != len(directions) or len(steps) != len(cracks):
        raise ValueError("complete thermal-cycle custody required")
    if any(direction not in ("heating", "cooling") for direction in directions):
        raise ValueError("temperature direction must remain a held label")
    first_crack = next((index for index, value in enumerate(cracks, 1) if value is not None), None)
    return {
        "temperature_steps": steps,
        "orientations": directions,
        "crack_counts": cracks,
        "critical_step": critical_step,
        "first_crack_cycle": first_crack,
        "critical_boundary_reached": any(value >= critical_step for value in steps),
        "complete_cycle_history": True,
    }


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-MAT-MEAS-MATERIAL-001",
    "SFT-MAT-MEAS-SPECIMEN-001",
    "SFT-MAT-MEAS-PROPERTY-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-THERM-HEAT-CAPACITY-001",
    "SFT-MAT-THERM-CONDUCTION-001",
    "SFT-MAT-THERM-EXPANSION-001",
    "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002",
    "SFT-MAT-PHASE-TIME-TEMPERATURE-010",
    "SFT-MAT-MECH-FATIGUE-009",
    "SFT-MAT-MECH-FRACTURE-ENERGY-007",
)

DEFINITIONS = (
    ("001", "SFT-MAT-THERM-DIFFUSIVITY-001", "Thermal diffusivity relation", "Thermal diffusivity is the exact rational part of the conductivity carrier over the complete density-times-specific-heat storage carrier, with all specimen conditions retained.", BASE),
    ("002", "SFT-MAT-THERM-BOUNDARY-RESISTANCE-002", "Interfacial thermal-boundary resistance", "Interfacial thermal resistance is the exact positive temperature-drop-times-area carrier per heat-flow carrier, with the interface identity and reciprocal conductance retained.", BASE + ("SFT-MAT-THERM-DIFFUSIVITY-001",)),
    ("003", "SFT-MAT-THERM-PHONON-MEAN-PATH-003", "Phonon scattering and mean-path ledger", "Phonon transport is a complete counted path word whose every positive segment is paired with a held scattering event; mean path is their exact rational total per event.", BASE + ("SFT-MAT-THERM-BOUNDARY-RESISTANCE-002",)),
    ("004", "SFT-MAT-THERM-RADIATIVE-TRANSPORT-004", "Radiative thermal transport in materials", "Radiative transport is an exact spectral and directional partition of one incident carrier into reflected, transmitted and absorbed carriers without continuum or signed proof magnitudes.", BASE + ("SFT-MAT-THERM-PHONON-MEAN-PATH-003",)),
    ("005", "SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005", "Thermoelectric coupled-response performance boundary", "Thermoelectric performance is the exact coupled rational relation of the Seebeck carrier squared and temperature carrier to retained resistivity and thermal-conductivity carriers.", BASE + ("SFT-MAT-THERM-RADIATIVE-TRANSPORT-004",)),
    ("006", "SFT-MAT-THERM-PHASE-STORAGE-006", "Phase-change thermal-storage ledger", "Phase-change storage is the exact sum of pre-transition sensible, latent and post-transition sensible carriers with the complete phase path retained.", BASE + ("SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005",)),
    ("007", "SFT-MAT-THERM-SHOCK-FATIGUE-007", "Thermal-shock and thermal-fatigue boundary", "Thermal shock and fatigue retain every positive temperature-step magnitude, heating or cooling orientation, cycle and crack record through the first critical boundary.", BASE + ("SFT-MAT-THERM-PHASE-STORAGE-006",)),
)

RELATIONS = dict(zip((f"{index:03d}" for index in range(1, 8)), (
    "conductivity-over-density-specific-heat-exact-diffusivity-part",
    "interface-held-temperature-drop-area-per-heat-flow-reciprocal-ledger",
    "complete-phonon-path-segment-scattering-event-mean-ledger",
    "spectral-directional-incident-reflected-transmitted-absorbed-partition",
    "seebeck-squared-temperature-over-resistivity-conductivity-boundary",
    "sensible-latent-sensible-complete-phase-storage-ledger",
    "oriented-temperature-step-cycle-crack-critical-boundary-ledger",
)))

def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "answer-only", "thermal carrier erased", "complete-positive-thermal-carrier", "all carriers retained"),
        binary_axis("relation", "relation?", "imported-fit-or-continuum", "not forced", relation, "exact relation"),
        binary_axis("path", "path?", "endpoint-only", "transition erased", "complete-interface-scattering-phase-cycle-path", "path retained"),
        binary_axis("observation", "conditions?", "condition-erased", "not reproducible", "specimen-method-temperature-scale-uncertainty-held", "conditions retained"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-state-transition-resource-trace", "trace retained"),
        binary_axis("provenance", "selector?", "target-authority-or-prior-model", "external selector", "root-bound-forward-forcing", "root forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "successor preserved"),
        binary_axis("extension", "extra rule?", "free-fit-exception-or-extra-rule", "manufactured", "no-extra-rule", "no selector"),
    )

WITNESSES = {
    "001": (Witness("diffusivity", "Conductivity twelve over density two and heat capacity three is exact diffusivity two.", diffusivity_relation(12, 2, 3)["diffusivity_part"] == 2),),
    "002": (Witness("boundary", "Temperature drop three across area two with heat flow six has unit resistance and conductance.", boundary_resistance(3, 6, 2, "film-substrate")["resistance_part"] == 1),),
    "003": (Witness("mean-path", "Segments two, four and three have exact mean path three.", phonon_mean_path((2, 4, 3), ("boundary", "isotope", "interface"))["mean_path"] == 3),),
    "004": (Witness("radiative", "Reflected two, transmitted three and absorbed five close incident ten.", radiative_partition(10, 2, 3, 5, "infrared-band", "toward")["closes"]),),
    "005": (Witness("thermoelectric", "Seebeck two squared times temperature three over resistivity two and conductivity three is two.", thermoelectric_boundary(2, 3, 2, 3)["performance_part"] == 2),),
    "006": (Witness("phase-storage", "Sensible two, latent five and sensible three close stored carrier ten.", phase_storage(2, 5, 3, ("solid", "transition", "liquid"))["stored_total"] == 10),),
    "007": (Witness("shock", "The first retained crack occurs on the second complete thermal cycle.", thermal_shock_fatigue((2, 5, 3), ("heating", "cooling", "heating"), (None, 1, 2), 5)["first_crack_cycle"] == 2),),
}


@dataclass(frozen=True)
class ThermSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(witness.passed for witness in self.witnesses):
            raise ValueError("invalid THERM specification")
        for axis in self.axes:
            axis.survivor


class ThermProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


EXCLUSIONS = (
    "no imported continuum transport law, fitted constitutive equation, named mechanism or prior proof as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "absence and thermal orientation remain held labels",
    "no external outcome selects a survivor",
    "all favourable, adverse, absent, unavailable and boundary rows remain retained",
    "no failed attempt retires an obligation or changes protected authority",
)

SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    specification = ThermSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Complete literal product of eight THERM-{number} binary axes before target release.",
        grammar_boundary=f"Every positive finite THERM-{number} carrier with complete condition, path and observation distinctions.",
        axes=axes(RELATIONS[number]),
        exact_result=f"THERM-{number} uniquely retains {RELATIONS[number]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive thermal carrier retains every distinction.",
        induction_step="One lawful successor retains prior distinctions and adds no selector.",
        exclusions=EXCLUSIONS,
        witnesses=WITNESSES[number],
        number=number,
        obligation_id=f"SFT-MAT-OBL-THERM-{number}",
    )
    specification.validate()
    SPECS[claim_id] = specification

ORDER = tuple(row[1] for row in DEFINITIONS)

__all__ = (
    "ThermProgram", "ORDER", "SPECS", "diffusivity_relation", "boundary_resistance", "phonon_mean_path",
    "radiative_partition", "thermoelectric_boundary", "phase_storage", "thermal_shock_fatigue",
)

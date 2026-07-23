"""Tool routing for Physics groups; never part of a claim source manifest."""

from sft.physics.mechanics_laws import MECHANICS_SPECS
from sft.physics.field_laws import FIELD_SPECS
from sft.physics.wave_laws import WAVE_SPECS
from sft.physics.thermodynamics_laws import THERMODYNAMICS_SPECS
from sft.physics.measured_value_backfill_laws import BACKFILL_SPECS
from sft.physics.quantum_physics_laws import QUANTUM_PHYSICS_SPECS
from sft.physics.matter_nuclear_laws import MATTER_NUCLEAR_SPECS
from sft.physics.spacetime_gravity_laws import SPACETIME_GRAVITY_SPECS
from sft.physics.collective_matter_laws import COLLECTIVE_MATTER_SPECS
from sft.physics.cosmological_boundary_laws import COSMOLOGICAL_BOUNDARY_SPECS

GROUPS = {
    "mechanics": ("sft.physics.mechanics_laws", "MECHANICS_SPECS", MECHANICS_SPECS),
    "fields": ("sft.physics.field_laws", "FIELD_SPECS", FIELD_SPECS),
    "waves": ("sft.physics.wave_laws", "WAVE_SPECS", WAVE_SPECS),
    "thermodynamics": (
        "sft.physics.thermodynamics_laws",
        "THERMODYNAMICS_SPECS",
        THERMODYNAMICS_SPECS,
    ),
    "measured_backfill": (
        "sft.physics.measured_value_backfill_laws",
        "BACKFILL_SPECS",
        BACKFILL_SPECS,
    ),
    "quantum_physics": (
        "sft.physics.quantum_physics_laws",
        "QUANTUM_PHYSICS_SPECS",
        QUANTUM_PHYSICS_SPECS,
    ),
    "matter_nuclear": (
        "sft.physics.matter_nuclear_laws",
        "MATTER_NUCLEAR_SPECS",
        MATTER_NUCLEAR_SPECS,
    ),
    "spacetime_gravity": (
        "sft.physics.spacetime_gravity_laws",
        "SPACETIME_GRAVITY_SPECS",
        SPACETIME_GRAVITY_SPECS,
    ),
    "collective_matter": (
        "sft.physics.collective_matter_laws",
        "COLLECTIVE_MATTER_SPECS",
        COLLECTIVE_MATTER_SPECS,
    ),
    "cosmological_boundary": (
        "sft.physics.cosmological_boundary_laws",
        "COSMOLOGICAL_BOUNDARY_SPECS",
        COSMOLOGICAL_BOUNDARY_SPECS,
    ),
}

__all__ = ("GROUPS",)

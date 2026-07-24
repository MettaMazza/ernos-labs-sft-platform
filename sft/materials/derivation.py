"""Target-blind Fold derivation blueprints for Materials Science.

The complete question surface is generated before any Materials authority,
database, handbook or measured specimen record is selected.  Familiar names in
titles identify the question to reconcile; they are not premises and do not
select a survivor.  Each blueprint enumerates the literal product of eight
binary preservation choices and admits only the form that retains the complete
carrier, relation, organization, observation, proof record, root provenance,
finite-successor closure and absence of an extra rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.materials.obligations import MATERIALS_OBLIGATIONS, MaterialsObligation
from sft.materials.structural_counts import (
    acoustic_branch_census,
    allowed_crystallographic_orders,
    bravais_census,
    crystal_system_census,
    rotation_factor_certificate,
    simple_cubic_coordination,
)
from sft.physics.generated_empirical_law import LawDimension, dimension


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
)


SUBBRANCH_DEPENDENCIES = {
    "measurement_identity": (
        "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
        "SFT-CHEM-MEAS-SUBSTANCE-001",
    ),
    "crystal_quasicrystal": (
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-CONDENSED-LATTICE-001",
        "SFT-PHYS-WAVE-INTERFERENCE-001",
        "SFT-PHYS-WAVE-DIFFRACTION-001",
    ),
    "defects_microstructure": (
        "SFT-PHYS-CONDENSED-LATTICE-001",
        "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001",
        "SFT-PHYS-CONDENSED-PHASE-ORDER-001",
    ),
    "electronic_semiconductor": (
        "SFT-PHYS-QUANTUM-EXCLUSION-001",
        "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
        "SFT-PHYS-CONDENSED-BAND-001",
    ),
    "superconducting_superfluid_topological": (
        "SFT-PHYS-MATTER-FERMION-BOSON-001",
        "SFT-PHYS-CONDENSED-PHASE-ORDER-001",
        "SFT-PHYS-CONDENSED-SUPERCONDUCTIVITY-001",
        "SFT-PHYS-CONDENSED-TOPOLOGICAL-001",
    ),
    "mechanical": (
        "SFT-PHYS-CONDENSED-LATTICE-001",
        "SFT-PHYS-FLUID-PRESSURE-STRESS-001",
        "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
    ),
    "thermal_magnetic_optical": (
        "SFT-PHYS-THERMO-RESPONSE-001",
        "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001",
        "SFT-PHYS-WAVE-POLARIZATION-001",
        "SFT-PHYS-CONDENSED-PHASE-ORDER-001",
    ),
    "material_classes_bulk": (
        "SFT-CHEM-BOND-COVALENT-001",
        "SFT-CHEM-BOND-IONIC-001",
        "SFT-CHEM-BOND-METALLIC-001",
        "SFT-CHEM-POLYMER-CHAIN-001",
        "SFT-PHYS-THERMO-MICRO-MACRO-001",
    ),
    "processing_degradation": (
        "SFT-CHEM-RXN-IDENTITY-001",
        "SFT-CHEM-EQ-CHEMICAL-001",
        "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
        "SFT-PHYS-MATTER-SCATTERING-001",
    ),
    "advanced_functional_sustainable": (
        "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
        "SFT-PHYS-WAVE-PROPAGATION-001",
        "SFT-PHYS-CONDENSED-PHASE-ORDER-001",
        "SFT-CHEM-STOICH-CONSERVATION-001",
    ),
}


@dataclass(frozen=True)
class MaterialsBlueprint:
    claim_id: str
    title: str
    subbranch: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-MAT-"):
            raise ValueError("Materials blueprint claim identity is invalid")
        if not self.experiment_id.startswith("SFT-EXP-MAT-"):
            raise ValueError("Materials blueprint experiment identity is invalid")
        if self.subbranch not in SUBBRANCH_DEPENDENCIES:
            raise ValueError("Materials blueprint subbranch is unregistered")
        if not self.dependencies or len(self.dimensions) != 8:
            raise ValueError("Materials blueprint requires dependencies and eight dimensions")
        if len({row.key for row in self.dimensions}) != 8:
            raise ValueError("Materials blueprint dimensions repeat")
        for row in self.dimensions:
            if len(row.choices) != 2:
                raise ValueError("each Materials dimension must exhaust two registered forms")
            row.admitted_choice
        if self.exact_result != "__".join(row.admitted_choice.name for row in self.dimensions):
            raise ValueError("Materials exact result is not the unique preservation survivor")
        if not self.predicted_observation_label.strip() or not self.falsification_condition.strip():
            raise ValueError("Materials blueprint lacks prediction or falsification boundary")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("Materials operational witness failed")


def _dimensions(row: MaterialsObligation) -> tuple[LawDimension, ...]:
    return (
        dimension(
            "carrier",
            "carrier-erased-or-answer-only",
            "Erasing the material carrier prevents reconstruction of the observed distinction.",
            row.carrier,
            "The complete generated material carrier is retained.",
        ),
        dimension(
            "relation",
            "relation-imported-fitted-or-erased",
            "An imported, fitted or absent relation can select a familiar answer without forcing it.",
            row.relation,
            "Only the generated constituent, adjacency, transfer or response relation is admitted.",
        ),
        dimension(
            "organization",
            "organization-collapsed",
            "Collapsing organization merges materials states that the question requires to remain distinct.",
            row.organization,
            "Every organization, interface, history or boundary distinction required by the claim remains held.",
        ),
        dimension(
            "observation",
            "observation-boundary-unrecorded",
            "An unrecorded method, scale or condition cannot identify the Materials observation class.",
            row.observation,
            "The exact declared observation boundary is retained and cannot select the law.",
        ),
        dimension(
            "record",
            "result-without-state-transition-record",
            "A result label without its state, transition and boundary trace is not auditable.",
            "complete-state-transition-boundary-trace",
            "The complete initial state, transition, result and retained/lost distinctions are recorded.",
        ),
        dimension(
            "provenance",
            "authority-or-target-selected-law",
            "Authority, consensus, a handbook or target data may test but cannot select a Fold law.",
            "root-bound-forward-forcing",
            "Every decision is traced through admitted dependencies to the premise-free root theorem.",
        ),
        dimension(
            "generality",
            "single-specimen-or-instance-lookup",
            "One favorable specimen or instance does not close the generated class.",
            "positive-finite-successor-closure",
            "The base carrier and every positive finite successor preserve the relation at the declared boundary.",
        ),
        dimension(
            "extension",
            "free-fit-exception-or-extra-rule",
            "A free coefficient, fit, exception or added constitutive law can force a desired answer.",
            "no-extra-rule",
            "No rule beyond the admitted Fold dependencies and generated preservation conditions is present.",
        ),
    )


def _structural_witnesses(row: MaterialsObligation) -> tuple[tuple[str, str, bool], ...]:
    common = (
        ("carrier", "the generated carrier label is held and nonempty", bool(row.carrier)),
        ("relation", "the generated relation and organization are separately retained", row.relation != row.organization),
        ("observation", "the observation boundary is distinct from the material organization", row.observation != row.organization),
    )
    exact = {
        "SFT-MAT-CRYST-CUBIC-COORDINATION-001": (
            "coordination-six",
            "three directions times two held orientations generate six distinct neighbours",
            simple_cubic_coordination().value == 6,
        ),
        "SFT-MAT-CRYST-ROTATION-RESTRICTION-001": (
            "rotation-orders",
            "the depth-independent factor certificate retains exactly orders 1, 2, 3, 4 and 6",
            tuple(x.value for x in allowed_crystallographic_orders()) == (1, 2, 3, 4, 6)
            and rotation_factor_certificate()["least_excluded"].value == 5,
        ),
        "SFT-MAT-CRYST-SYSTEMS-001": (
            "seven-systems",
            "the complete rank-three length/angle quotient has seven survivors",
            len(crystal_system_census()) == 7,
        ),
        "SFT-MAT-CRYST-BRAVAIS-001": (
            "fourteen-bravais",
            "the complete system/centering quotient has fourteen survivors",
            len(bravais_census()) == 14,
        ),
        "SFT-MAT-CRYST-PHONON-001": (
            "three-acoustic-branches",
            "one longitudinal plus two transverse rank-three orientations are retained",
            len(acoustic_branch_census()) == 3,
        ),
    }
    return common + ((exact[row.claim_id],) if row.claim_id in exact else ())


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no V1/V2 result, handbook, named material, database row, measured property or application outcome may select a survivor",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "structural absence is a held empty form and opposed direction is a held orientation, never a prohibited scalar",
        "no axiom, free parameter, fit, learned coefficient, constitutive exception or target-derived rule",
        "no opaque prediction, selected favorable specimen, omitted failure, or unrecorded method/condition boundary",
        "external target content remains inaccessible until the complete prediction set is sealed",
        boundary,
    )


def _blueprint(row: MaterialsObligation) -> MaterialsBlueprint:
    dimensions = _dimensions(row)
    result = "__".join(item.admitted_choice.name for item in dimensions)
    dependencies = BASE_DEPENDENCIES + SUBBRANCH_DEPENDENCIES[row.subbranch]
    boundary = (
        "Every positive finite generated Materials carrier in the registered "
        f"{row.subbranch} grammar that preserves {row.carrier}, {row.relation}, "
        f"{row.organization} and {row.observation}."
    )
    slug = row.claim_id.removeprefix("SFT-MAT-").removesuffix("-001")
    return MaterialsBlueprint(
        claim_id=row.claim_id,
        title=row.title,
        subbranch=row.subbranch,
        statement=row.statement,
        dependencies=dependencies,
        generation_rule=(
            "Generate the literal Cartesian product of the registered content-specific carrier, relation, "
            "organization and observation choices with record, provenance, generality and extension choices."
        ),
        grammar_boundary=boundary,
        dimensions=dimensions,
        exact_result=result,
        induction_base=(
            "One complete material carrier retains its generated relation, organization, observation boundary "
            "and proof record."
        ),
        induction_step=(
            "Adding one generated constituent, cell, interface, transition or observation row preserves every "
            "earlier distinction and appends its exact source-bound relation without an extra rule."
        ),
        exclusions=_exclusions(boundary),
        operational_witnesses=_structural_witnesses(row),
        experiment_id=f"SFT-EXP-MAT-{slug}-001",
        predicted_observation_label=result,
        falsification_condition=(
            f"The claim fails if a complete registered {row.title.lower()} observation lacks any sealed "
            "carrier, relation, organization or boundary feature, any required row is omitted, or a tampered "
            "row is accepted."
        ),
    )


MATERIALS_BLUEPRINTS = tuple(_blueprint(row) for row in MATERIALS_OBLIGATIONS)

for _row in MATERIALS_BLUEPRINTS:
    _row.validate()


def blueprint_candidate_ids(blueprint: MaterialsBlueprint) -> tuple[str, ...]:
    """Enumerate the exact registered 2^8 grammar without an empirical target."""

    domains = tuple(tuple(choice.name for choice in row.choices) for row in blueprint.dimensions)
    return tuple("__".join(coordinates) for coordinates in product(*domains))


__all__ = (
    "BASE_DEPENDENCIES",
    "MATERIALS_BLUEPRINTS",
    "MaterialsBlueprint",
    "SUBBRANCH_DEPENDENCIES",
    "blueprint_candidate_ids",
)

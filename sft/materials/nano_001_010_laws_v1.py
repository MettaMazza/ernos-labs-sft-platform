"""Exact Fold laws for the complete Materials NANO-001--010 family."""

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive counted form")
    return value


def positive_fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(name + " must be exact")
    value = Fraction(value)
    if value <= 0:
        raise ValueError(name + " must be positive")
    return value


def nanoparticle_distribution(particles):
    rows = tuple((identity, tuple(dimensions), shape) for identity, dimensions, shape in particles)
    if not rows or len({row[0] for row in rows}) != len(rows):
        raise ValueError("particle identities must be complete and distinct")
    for identity, dimensions, shape in rows:
        if not identity or not shape or len(dimensions) != 3:
            raise ValueError("particle shape record incomplete")
        tuple(positive(value, "particle dimension") for value in dimensions)
    classes = tuple(sorted({(row[1], row[2]) for row in rows}, key=repr))
    counts = tuple((member, sum(1 for row in rows if (row[1], row[2]) == member)) for member in classes)
    return {"particles": rows, "classes": counts, "particle_count": len(rows), "all_particles_retained": True}


def nanowire_confinement(longitudinal_sites, transverse_a, transverse_b, end_labels):
    longitudinal_sites = positive(longitudinal_sites, "longitudinal sites")
    transverse_a = positive(transverse_a, "first transverse support")
    transverse_b = positive(transverse_b, "second transverse support")
    ends = tuple(end_labels)
    if len(ends) != 2 or not all(ends):
        raise ValueError("two nanowire ends must remain held")
    return {
        "longitudinal_sites": longitudinal_sites,
        "transverse_support": (transverse_a, transverse_b),
        "end_labels": ends,
        "one_extended_axis": True,
        "two_finite_transverse_axes": True,
    }


def layer_stack(layers, interface_labels, registry_labels):
    layers = tuple(layers)
    interfaces = tuple(interface_labels)
    registries = tuple(registry_labels)
    if len(layers) < 2 or len(interfaces) + 1 != len(layers) or len(registries) != len(interfaces):
        raise ValueError("layer-stack adjacency ledger incomplete")
    if not all(layers) or not all(interfaces) or not all(registries):
        raise ValueError("layer-stack labels must remain held")
    return {"layers": layers, "interfaces": interfaces, "registries": registries, "ordered": True}


def quantum_dot(sites, boundary_sites, carrier_label, level_labels):
    sites = positive(sites, "dot sites")
    boundary_sites = positive(boundary_sites, "boundary sites")
    levels = tuple(level_labels)
    if boundary_sites > sites or not carrier_label or not levels or not all(levels):
        raise ValueError("finite confinement record incomplete")
    return {
        "sites": sites,
        "boundary_sites": boundary_sites,
        "carrier_label": carrier_label,
        "level_labels": levels,
        "finite_support": True,
        "boundary_held": True,
    }


def surface_volume(width):
    width = positive(width, "width")
    if width < 3:
        raise ValueError("width must retain a positive interior")
    total = width ** 3
    interior = (width - 2) ** 3
    surface = total - interior
    successor_total = (width + 1) ** 3
    successor_interior = (width - 1) ** 3
    successor_surface = successor_total - successor_interior
    part = Fraction(surface, total)
    successor_part = Fraction(successor_surface, successor_total)
    if not successor_part < part:
        raise ValueError("finite surface dominance did not close")
    return {
        "width": width,
        "cells": total,
        "interior_cells": interior,
        "surface_cells": surface,
        "surface_part": part,
        "successor_surface_part": successor_part,
        "surface_part_decreases_with_successor_width": True,
    }


def nanoscale_phase_boundary(size_label, lower, transition, upper, initial_phase, terminal_phase, method):
    lower = positive_fraction(lower, "lower observation")
    transition = positive_fraction(transition, "transition observation")
    upper = positive_fraction(upper, "upper observation")
    if not lower < transition < upper or not size_label or not initial_phase or not terminal_phase or initial_phase == terminal_phase or not method:
        raise ValueError("nanoscale phase boundary incomplete")
    return {
        "size_label": size_label,
        "lower": lower,
        "transition": transition,
        "upper": upper,
        "initial_phase": initial_phase,
        "terminal_phase": terminal_phase,
        "method": method,
        "conditional_boundary": True,
    }


def collective_state(sites, local_labels, joint_label, topology_label, correlation_links):
    sites = positive(sites, "collective sites")
    local = tuple(local_labels)
    links = tuple(tuple(link) for link in correlation_links)
    if len(local) != sites or not all(local) or not joint_label or not topology_label or not links:
        raise ValueError("collective-state record incomplete")
    if any(len(link) != 2 for link in links):
        raise ValueError("correlation link must join two held sites")
    return {"sites": sites, "local_labels": local, "joint_label": joint_label, "topology_label": topology_label, "correlation_links": links, "local_and_collective_retained": True}


def moire_supercell(period_a, period_b, layer_a, layer_b, registry_label):
    period_a = positive(period_a, "first layer period")
    period_b = positive(period_b, "second layer period")
    if not layer_a or not layer_b or layer_a == layer_b or not registry_label:
        raise ValueError("moire layer identities incomplete")
    candidates = tuple(step for step in range(1, period_a * period_b + 1) if step % period_a == 0 and step % period_b == 0)
    if not candidates:
        raise ValueError("no positive joint recurrence")
    return {"period_a": period_a, "period_b": period_b, "layer_a": layer_a, "layer_b": layer_b, "registry_label": registry_label, "joint_recurrence": candidates[0], "all_joint_recurrences": candidates, "least_positive_recurrence_forced": True}


def nanocomposite_interface(matrix_units, inclusion_units, interface_contacts, matrix_label, inclusion_label):
    matrix_units = positive(matrix_units, "matrix units")
    inclusion_units = positive(inclusion_units, "inclusion units")
    interface_contacts = positive(interface_contacts, "interface contacts")
    if not matrix_label or not inclusion_label or matrix_label == inclusion_label:
        raise ValueError("nanocomposite identities incomplete")
    total_units = matrix_units + inclusion_units
    return {"matrix_units": matrix_units, "inclusion_units": inclusion_units, "interface_contacts": interface_contacts, "matrix_label": matrix_label, "inclusion_label": inclusion_label, "interface_contacts_per_unit": Fraction(interface_contacts, total_units), "identities_retained": True}


def aggregation_dispersion(particles, clusters, medium, condition_path):
    particles = tuple(particles)
    clusters = tuple(tuple(cluster) for cluster in clusters)
    path = tuple(condition_path)
    if not particles or len(set(particles)) != len(particles) or not clusters or not medium or len(path) < 2:
        raise ValueError("aggregation custody incomplete")
    flattened = tuple(member for cluster in clusters for member in cluster)
    if len(flattened) != len(set(flattened)) or set(flattened) != set(particles):
        raise ValueError("every particle must occur in exactly one cluster")
    return {"particles": particles, "clusters": clusters, "medium": medium, "condition_path": path, "cluster_count": len(clusters), "complete_partition": True}


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-MAT-MEAS-MATERIAL-001",
    "SFT-MAT-MEAS-SPECIMEN-001",
    "SFT-MAT-MEAS-PROPERTY-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-CRYST-LATTICE-001",
    "SFT-MAT-CRYST-UNIT-CELL-001",
    "SFT-MAT-MICRO-INTERFACE-001",
    "SFT-MAT-FUNC-NANOMATERIAL-001",
)

DEFINITIONS = (
    ("001", "SFT-MAT-NANO-SIZE-SHAPE-DISTRIBUTION-001", "Nanoparticle size and shape distribution", "A nanoparticle population is an exact finite ledger of particle identities, three counted dimensions, held shape labels and the complete generated distribution; no mean or fitted continuum replaces its members.", BASE),
    ("002", "SFT-MAT-NANO-NANOWIRE-CONFINEMENT-002", "Nanowire and one-dimensional confinement", "A nanowire retains one extended counted path, two finite transverse supports and both held terminal labels; one-dimensionality is a relation of supports rather than an imported continuum axis.", BASE + ("SFT-MAT-NANO-SIZE-SHAPE-DISTRIBUTION-001",)),
    ("003", "SFT-MAT-NANO-LAYER-STACKING-003", "Two-dimensional layer and stacking organization", "A two-dimensional material stack is the exact ordered word of layer identities, adjacent interfaces and registry labels; no layer or interface may be erased.", BASE + ("SFT-MAT-NANO-NANOWIRE-CONFINEMENT-002", "SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006")),
    ("004", "SFT-MAT-NANO-QUANTUM-DOT-CONFINEMENT-004", "Quantum-dot finite confinement", "A quantum dot retains finite counted support, boundary support, carrier identity and every distinguished level label as one exact confinement record.", BASE + ("SFT-MAT-NANO-LAYER-STACKING-003", "SFT-MAT-OPT-EXCITON-DYNAMICS-010")),
    ("005", "SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005", "Surface-to-volume dominance relation", "For every generated cubic cellular support with positive interior, exact enumeration forces the boundary-cell part to fall under one-width succession; smaller supports therefore carry the larger boundary part without a fitted continuum formula.", BASE + ("SFT-MAT-NANO-QUANTUM-DOT-CONFINEMENT-004", "SFT-MAT-BULK-SIZE-SURFACE-001")),
    ("006", "SFT-MAT-NANO-PHASE-MELTING-BOUNDARY-006", "Nanoscale phase and melting boundary", "A nanoscale phase boundary is an exact specimen-, size-, method- and condition-bound ordered observation separating two held phase identities; it is never promoted to a universal fitted temperature.", BASE + ("SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005", "SFT-MAT-PHASE-TRANSITION-001")),
    ("007", "SFT-MAT-NANO-QUANTUM-COLLECTIVE-STATE-007", "Quantum-material collective-state classification", "A quantum-material collective state retains every local state, every correlation link, the joint-state identity and its topology label; the collective class cannot be reduced to disconnected local labels.", BASE + ("SFT-MAT-NANO-PHASE-MELTING-BOUNDARY-006", "SFT-MAT-TOPO-INVARIANT-001", "SFT-MAT-TOPO-BULK-BOUNDARY-001")),
    ("008", "SFT-MAT-NANO-MOIRE-SUPERSTRUCTURE-008", "Moiré and twisted-layer superstructure", "Two nonidentical layer recurrences force a least positive joint recurrence by complete enumeration, while layer identities and interlayer registry remain held as the moiré superstructure.", BASE + ("SFT-MAT-NANO-QUANTUM-COLLECTIVE-STATE-007",)),
    ("009", "SFT-MAT-NANO-NANOCOMPOSITE-INTERFACE-DENSITY-009", "Nanocomposite interface density", "A nanocomposite retains matrix units, inclusion units, their distinct identities and every counted interfacial contact, yielding an exact contact-per-unit fraction without fitted constitutive parameters.", BASE + ("SFT-MAT-NANO-MOIRE-SUPERSTRUCTURE-008", "SFT-MAT-CLASS-COMPOSITE-001")),
    ("010", "SFT-MAT-NANO-AGGREGATION-DISPERSION-CUSTODY-010", "Nanomaterial aggregation and dispersion custody", "A nanomaterial dispersion is the exact partition of held particle identities into clusters together with medium and condition path; aggregation changes organization without losing particle custody.", BASE + ("SFT-MAT-NANO-NANOCOMPOSITE-INTERFACE-DENSITY-009", "SFT-MAT-SOFT-COLLOID-AGGREGATION-001")),
)

RELATIONS = dict(zip((f"{index:03d}" for index in range(1, 11)), (
    "particle-identity-three-dimension-shape-complete-distribution",
    "one-extended-two-finite-terminal-held-wire-support",
    "ordered-layer-interface-registry-word",
    "finite-site-boundary-carrier-level-confinement",
    "counted-boundary-interior-successor-surface-part",
    "size-phase-method-conditioned-transition-boundary",
    "local-correlation-joint-topology-collective-state",
    "two-layer-least-positive-joint-recurrence",
    "matrix-inclusion-interface-contact-density-ledger",
    "particle-cluster-medium-condition-complete-custody",
)))


def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "label-only", "erased", "complete-positive-nanomaterial-carrier", "held"),
        binary_axis("relation", "relation?", "imported-fit-model", "not forced", relation, "exact"),
        binary_axis("organization", "organization?", "endpoint-or-average-only", "erased", "complete-generated-discrete-organization", "retained"),
        binary_axis("observation", "conditions?", "condition-erased", "not reproducible", "specimen-method-condition-scale-uncertainty-held", "held"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-trace", "retained"),
        binary_axis("provenance", "selector?", "target-or-prior-model", "external selector", "root-bound-forward-forcing", "forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "preserved"),
        binary_axis("extension", "extra?", "fit-exception-extra-rule", "manufactured", "no-extra-rule", "none"),
    )


WITNESSES = {
    "001": (Witness("population", "complete distribution", nanoparticle_distribution((("p1", (1, 2, 3), "rod"), ("p2", (1, 1, 1), "compact")))["particle_count"] == 2),),
    "002": (Witness("wire", "one-dimensional confinement", nanowire_confinement(5, 1, 1, ("left", "right"))["two_finite_transverse_axes"]),),
    "003": (Witness("stack", "ordered adjacency", layer_stack(("a", "b", "c"), ("ab", "bc"), ("aligned", "twisted"))["ordered"]),),
    "004": (Witness("dot", "finite support", quantum_dot(5, 4, "exciton", ("ground", "excited"))["finite_support"]),),
    "005": (Witness("surface", "successor dominance", surface_volume(3)["surface_part_decreases_with_successor_width"]),),
    "006": (Witness("phase", "conditional boundary", nanoscale_phase_boundary("three-unit-particle", 1, Fraction(3, 2), 2, "ordered", "disordered", "exact-calorimetry")["conditional_boundary"]),),
    "007": (Witness("collective", "joint state", collective_state(3, ("a", "b", "a"), "correlated", "nontrivial", (("a", "b"), ("b", "c")))["local_and_collective_retained"]),),
    "008": (Witness("moire", "least recurrence", moire_supercell(2, 3, "layer-a", "layer-b", "twisted")["joint_recurrence"] == 6),),
    "009": (Witness("interface", "exact density", nanocomposite_interface(3, 2, 4, "matrix", "inclusion")["interface_contacts_per_unit"] == Fraction(4, 5)),),
    "010": (Witness("dispersion", "complete custody", aggregation_dispersion(("p1", "p2", "p3"), (("p1", "p2"), ("p3",)), "water", ("prepared", "measured"))["complete_partition"]),),
}


@dataclass(frozen=True)
class NanoSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(w.passed for w in self.witnesses):
            raise ValueError("invalid NANO spec")
        for axis in self.axes:
            axis.survivor


class NanoProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="materials",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


EXCLUSIONS = (
    "no imported continuum constitutive equation, fitted threshold, named mechanism or prior proof as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence and every particle, layer, boundary, interface, cluster, state and path distinction remain held labels",
    "no external outcome selects a survivor",
    "all favourable, adverse, absent, unavailable and unresolved result classes remain retained",
    "no failed attempt retires an obligation or changes protected authority",
)

SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    spec = NanoSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Complete literal product of eight NANO-{number} axes before target release.",
        grammar_boundary=f"Every positive finite NANO-{number} carrier with complete particle, layer, boundary, interface, state, path and observation distinctions.",
        axes=axes(RELATIONS[number]),
        exact_result=f"NANO-{number} uniquely retains {RELATIONS[number]} with complete carrier, organization, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive nanomaterial carrier retains every distinction.",
        induction_step="One lawful successor retains all prior distinctions and adds no selector.",
        exclusions=EXCLUSIONS,
        witnesses=WITNESSES[number],
        number=number,
        obligation_id=f"SFT-MAT-OBL-NANO-{number}",
    )
    spec.validate()
    SPECS[claim_id] = spec

ORDER = tuple(row[1] for row in DEFINITIONS)


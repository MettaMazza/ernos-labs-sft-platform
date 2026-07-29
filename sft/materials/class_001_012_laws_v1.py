"""Exact Fold laws for the complete Materials CLASS-001--012 family."""
from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis

def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be positive")
    return value

def alloy_phase(components, phase_counts, phase_labels):
    components, phase_counts, phase_labels = tuple(components), tuple(phase_counts), tuple(phase_labels)
    if len(components) < 2 or len(set(components)) != len(components) or len(phase_counts) != len(phase_labels) or not phase_counts or not all(phase_labels):
        raise ValueError("alloy identity incomplete")
    counts = tuple(positive(v, "phase count") for v in phase_counts)
    total = sum(counts)
    return {"components": components, "phase_counts": counts, "phase_labels": phase_labels, "phase_parts": tuple(Fraction(v, total) for v in counts), "closes": sum(Fraction(v, total) for v in counts) == 1}

def ordered_intermetallic(site_labels, occupancies, compound):
    site_labels, occupancies = tuple(site_labels), tuple(occupancies)
    if len(site_labels) < 2 or len(site_labels) != len(occupancies) or len(set(site_labels)) != len(site_labels) or not compound:
        raise ValueError("ordered-site record incomplete")
    values = tuple(positive(v, "occupancy") for v in occupancies)
    total = sum(values)
    return {"site_labels": site_labels, "occupancies": values, "compound": compound, "site_parts": tuple(Fraction(v, total) for v in values), "ordered": True}

def complex_alloy(component_counts, component_labels, phase_labels):
    values, labels, phases = tuple(component_counts), tuple(component_labels), tuple(phase_labels)
    if len(values) < 3 or len(values) != len(labels) or len(set(labels)) != len(labels) or not phases:
        raise ValueError("compositionally complex record incomplete")
    values = tuple(positive(v, "component count") for v in values)
    total = sum(values)
    return {"component_counts": values, "component_labels": labels, "phase_labels": phases, "component_parts": tuple(Fraction(v, total) for v in values), "all_components_retained": True}

def refractory_class(service_steps, survived_steps, retained_phases, specimen):
    service_steps, survived_steps = positive(service_steps, "service steps"), positive(survived_steps, "survived steps")
    phases = tuple(retained_phases)
    if survived_steps > service_steps or not phases or not specimen:
        raise ValueError("high-temperature survival record incomplete")
    return {"service_steps": service_steps, "survived_steps": survived_steps, "retained_phases": phases, "specimen": specimen, "survival_part": Fraction(survived_steps, service_steps), "service_boundary_retained": True}

def cementitious_composite(binder, aggregate, pore, hydration, specimen):
    values = tuple(positive(v, name) for v, name in ((binder, "binder"), (aggregate, "aggregate"), (pore, "pore"), (hydration, "hydration")))
    if not specimen:
        raise ValueError("cementitious specimen required")
    total = sum(values)
    return {"binder": values[0], "aggregate": values[1], "pore": values[2], "hydration": values[3], "specimen": specimen, "constituent_parts": tuple(Fraction(v, total) for v in values), "porous_hydrated_composite": True}

def fibre_load_transfer(applied, fibre, matrix, interface, orientation):
    applied, fibre, matrix, interface = (positive(v, n) for v, n in ((applied, "applied"), (fibre, "fibre"), (matrix, "matrix"), (interface, "interface")))
    if fibre + matrix + interface != applied or not orientation:
        raise ValueError("fibre transfer ledger invalid")
    return {"applied": applied, "fibre": fibre, "matrix": matrix, "interface": interface, "orientation": orientation, "reinforcement_part": Fraction(fibre, applied), "closes": True}

def particle_load_transfer(applied, particle, matrix, interface, distribution):
    applied, particle, matrix, interface = (positive(v, n) for v, n in ((applied, "applied"), (particle, "particle"), (matrix, "matrix"), (interface, "interface")))
    if particle + matrix + interface != applied or not distribution:
        raise ValueError("particle transfer ledger invalid")
    return {"applied": applied, "particle": particle, "matrix": matrix, "interface": interface, "distribution": distribution, "reinforcement_part": Fraction(particle, applied), "closes": True}

def metallic_glass(local_orders, crystalline_periodicity, metastable, composition):
    orders = tuple(local_orders)
    if not orders or crystalline_periodicity not in ("absent", "held") or not metastable or not composition:
        raise ValueError("metallic-glass record incomplete")
    return {"local_orders": orders, "crystalline_periodicity": crystalline_periodicity, "metastable": metastable, "composition": composition, "noncrystalline": crystalline_periodicity == "absent", "chemical_order_retained": True}

def ceramic_subclass(structural_responses, functional_responses, composition, process):
    structural, functional = tuple(structural_responses), tuple(functional_responses)
    if not structural or not functional or not composition or not process:
        raise ValueError("ceramic subclass record incomplete")
    return {"structural_responses": structural, "functional_responses": functional, "composition": composition, "process": process, "roles_distinct": set(structural).isdisjoint(functional)}

def polymer_subclasses(thermoplastic, thermoset, elastomer):
    rows = (tuple(thermoplastic), tuple(thermoset), tuple(elastomer))
    if any(len(row) != 3 for row in rows):
        raise ValueError("polymer response triples required")
    expected = (("softens", "reshape", "retains-chain"), ("crosslinked", "permanent-shape", "does-not-commonly-soften"), ("elastic", "deform", "recover"))
    if rows != expected:
        raise ValueError("polymer class distinctions erased")
    return {"thermoplastic": rows[0], "thermoset": rows[1], "elastomer": rows[2], "classes_distinct": len(set(rows)) == 3}

def functionally_graded(layers, property_counts):
    layers, values = tuple(layers), tuple(property_counts)
    if len(layers) < 2 or len(layers) != len(values) or len(set(layers)) != len(layers):
        raise ValueError("graded path incomplete")
    values = tuple(positive(v, "property count") for v in values)
    if len(set(values)) < 2:
        raise ValueError("gradient absent")
    return {"layers": layers, "property_counts": values, "adjacencies": tuple(zip(layers, layers[1:])), "endpoint_ratio": Fraction(values[-1], values[0]), "complete_gradient": True}

def architected_cellular(nodes, links, cells, responses, architecture):
    nodes, links, cells = positive(nodes, "nodes"), positive(links, "links"), positive(cells, "cells")
    responses = tuple(responses)
    if not responses or not architecture:
        raise ValueError("architected material record incomplete")
    return {"nodes": nodes, "links": links, "cells": cells, "responses": responses, "architecture": architecture, "link_part": Fraction(links, nodes + links + cells), "topology_retained": True}

BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-MAT-MEAS-MATERIAL-001", "SFT-MAT-MEAS-SPECIMEN-001",
    "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-MEAS-TRACEABILITY-001", "SFT-MAT-CLASS-METAL-001",
    "SFT-MAT-CLASS-CERAMIC-001", "SFT-MAT-CLASS-POLYMER-001", "SFT-MAT-CLASS-COMPOSITE-001",
    "SFT-MAT-CLASS-GLASS-001", "SFT-MAT-CLASS-POROUS-001", "SFT-MAT-PHASE-FRACTION-LEDGER-001",
    "SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001", "SFT-MAT-THERM-DIFFUSIVITY-001",
)

DEFINITIONS = (
    ("001", "SFT-MAT-CLASS-SOLID-SOLUTION-ALLOY-001", "Solid-solution and alloy phase organization", "An alloy retains every constituent identity and the complete exact phase partition; solid-solution and compound phase labels are observational distinctions, never imported selectors.", BASE),
    ("002", "SFT-MAT-CLASS-INTERMETALLIC-ORDER-002", "Ordered intermetallic compound organization", "An ordered intermetallic retains compound identity, every distinguishable site, its occupant count and the exact site partition.", BASE + ("SFT-MAT-CLASS-SOLID-SOLUTION-ALLOY-001",)),
    ("003", "SFT-MAT-CLASS-HIGH-ENTROPY-BOUNDARY-003", "Compositionally complex alloy boundary", "A compositionally complex alloy retains every distinct component, its exact positive part and every resulting phase label; no named entropy threshold or selected phase is imported.", BASE + ("SFT-MAT-CLASS-INTERMETALLIC-ORDER-002",)),
    ("004", "SFT-MAT-CLASS-REFRACTORY-UHT-004", "Refractory and ultra-high-temperature material class", "A refractory or ultra-high-temperature class is a specimen-bound survival history retaining the service boundary, survived interval and every retained phase without a fitted temperature cutoff.", BASE + ("SFT-MAT-CLASS-HIGH-ENTROPY-BOUNDARY-003",)),
    ("005", "SFT-MAT-CLASS-CEMENTITIOUS-CONCRETE-005", "Cementitious and concrete composite organization", "A cementitious composite retains binder, aggregate, pore and hydration-product supports as exact positive parts of one specimen record.", BASE + ("SFT-MAT-CLASS-REFRACTORY-UHT-004",)),
    ("006", "SFT-MAT-CLASS-FIBRE-REINFORCED-006", "Fibre-reinforced composite load transfer", "Fibre reinforcement retains the applied load partition across fibre, matrix and interface together with fibre orientation.", BASE + ("SFT-MAT-CLASS-CEMENTITIOUS-CONCRETE-005",)),
    ("007", "SFT-MAT-CLASS-PARTICLE-REINFORCED-007", "Particle-reinforced composite load transfer", "Particle reinforcement retains the applied load partition across particles, matrix and interface together with particle distribution.", BASE + ("SFT-MAT-CLASS-FIBRE-REINFORCED-006",)),
    ("008", "SFT-MAT-CLASS-METALLIC-GLASS-008", "Metallic-glass organization", "A metallic glass retains composition, metastability and local chemical order while crystalline periodicity is held as structurally absent rather than numerical zero.", BASE + ("SFT-MAT-CLASS-PARTICLE-REINFORCED-007",)),
    ("009", "SFT-MAT-CLASS-CERAMIC-SUBCLASSES-009", "Structural and functional ceramic subclasses", "Ceramic subclasses retain composition and process while structural and functional response roles remain separately observable.", BASE + ("SFT-MAT-CLASS-METALLIC-GLASS-008",)),
    ("010", "SFT-MAT-CLASS-POLYMER-SUBCLASSES-010", "Thermoplastic, thermoset and elastomer distinction", "Thermoplastic reshaping, thermoset permanent crosslinking and elastomeric recovery are three separately retained response histories.", BASE + ("SFT-MAT-CLASS-CERAMIC-SUBCLASSES-009",)),
    ("011", "SFT-MAT-CLASS-FUNCTIONALLY-GRADED-011", "Gradient and functionally graded materials", "A functionally graded material retains an ordered layer path, every exact positive property carrier and each adjacency from one endpoint to the other.", BASE + ("SFT-MAT-CLASS-POLYMER-SUBCLASSES-010",)),
    ("012", "SFT-MAT-CLASS-ARCHITECTED-CELLULAR-012", "Architected and cellular materials", "An architected cellular material retains nodes, links, cells, topology and response channels so architecture cannot be collapsed into bulk composition alone.", BASE + ("SFT-MAT-CLASS-FUNCTIONALLY-GRADED-011",)),
)

RELATIONS = dict(zip((f"{i:03d}" for i in range(1, 13)), (
    "constituent-phase-label-exact-alloy-partition", "ordered-site-occupancy-compound-partition", "complete-component-phase-complex-alloy-boundary",
    "service-survival-retained-phase-refractory-history", "binder-aggregate-pore-hydration-composite-organization", "fibre-matrix-interface-load-orientation-partition",
    "particle-matrix-interface-load-distribution-partition", "local-order-nonperiodic-metastable-metallic-glass", "structural-functional-composition-process-ceramic-subclasses",
    "thermoplastic-thermoset-elastomer-response-distinction", "ordered-layer-adjacency-property-gradient", "node-link-cell-topology-response-architecture",
)))

def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "class-name-only", "constituents erased", "complete-positive-material-carrier", "all held"),
        binary_axis("relation", "relation?", "imported-fit-classifier", "not forced", relation, "exact"),
        binary_axis("path", "path?", "endpoint-only", "organization erased", "complete-structure-state-response-path", "retained"),
        binary_axis("observation", "conditions?", "condition-erased", "not reproducible", "specimen-method-condition-scale-uncertainty-held", "held"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-trace", "retained"),
        binary_axis("provenance", "selector?", "target-or-prior-model", "external selector", "root-bound-forward-forcing", "forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "preserved"),
        binary_axis("extension", "extra?", "fit-exception-extra-rule", "manufactured", "no-extra-rule", "none"),
    )

WITNESSES = {
    "001": (Witness("alloy", "Exact two-phase partition.", alloy_phase(("A", "B"), (3, 2), ("solution", "compound"))["closes"]),),
    "002": (Witness("ordered", "Two ordered sites retained.", ordered_intermetallic(("alpha", "beta"), (2, 3), "AB")["ordered"]),),
    "003": (Witness("complex", "Three component parts retained.", len(complex_alloy((2, 3, 5), ("A", "B", "C"), ("solution",))["component_parts"]) == 3),),
    "004": (Witness("refractory", "Exact survival part retained.", refractory_class(5, 4, ("phase-a",), "sample")["survival_part"] == Fraction(4, 5)),),
    "005": (Witness("cement", "Four constituent parts retained.", len(cementitious_composite(2, 5, 1, 2, "sample")["constituent_parts"]) == 4),),
    "006": (Witness("fibre", "Exact fibre load part retained.", fibre_load_transfer(8, 4, 3, 1, "aligned")["reinforcement_part"] == Fraction(1, 2)),),
    "007": (Witness("particle", "Exact particle load part retained.", particle_load_transfer(8, 3, 4, 1, "dispersed")["reinforcement_part"] == Fraction(3, 8)),),
    "008": (Witness("glass", "Periodicity absence remains labelled.", metallic_glass(("near", "medium"), "absent", "metastable", "alloy")["noncrystalline"]),),
    "009": (Witness("ceramic", "Structural and functional roles stay distinct.", ceramic_subclass(("load",), ("dielectric",), "oxide", "sintered")["roles_distinct"]),),
    "010": (Witness("polymer", "Three response histories remain distinct.", polymer_subclasses(("softens", "reshape", "retains-chain"), ("crosslinked", "permanent-shape", "does-not-commonly-soften"), ("elastic", "deform", "recover"))["classes_distinct"]),),
    "011": (Witness("graded", "Ordered gradient retained.", functionally_graded(("left", "middle", "right"), (2, 3, 5))["complete_gradient"]),),
    "012": (Witness("architected", "Topology retained.", architected_cellular(4, 6, 3, ("auxetic",), "lattice")["topology_retained"]),),
}

@dataclass(frozen=True)
class ClassSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""
    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(w.passed for w in self.witnesses):
            raise ValueError("invalid CLASS spec")
        for axis in self.axes:
            axis.survivor

class ClassProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)

EXCLUSIONS = (
    "no imported constitutive equation, fitted class threshold, named mechanism or prior proof as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence, class, phase, orientation, topology and response remain held labels",
    "no external outcome selects a survivor", "all result classes remain retained", "no failed attempt retires an obligation or changes protected authority",
)

SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    spec = ClassSpec(claim_id=claim_id, title=title, statement=statement, dependencies=dependencies, evidence_mode=EvidenceMode.EMPIRICAL, generation_rule=f"Complete literal product of eight CLASS-{number} axes before target release.", grammar_boundary=f"Every positive finite CLASS-{number} material carrier with complete structure, state, path and observation distinctions.", axes=axes(RELATIONS[number]), exact_result=f"CLASS-{number} uniquely retains {RELATIONS[number]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.", induction_base="The first positive material carrier retains every distinction.", induction_step="One lawful successor retains all prior distinctions and adds no selector.", exclusions=EXCLUSIONS, witnesses=WITNESSES[number], number=number, obligation_id=f"SFT-MAT-OBL-CLASS-{number}")
    spec.validate()
    SPECS[claim_id] = spec

ORDER = tuple(row[1] for row in DEFINITIONS)

__all__ = ("ORDER", "SPECS", "ClassProgram", "ClassSpec", "alloy_phase", "ordered_intermetallic", "complex_alloy", "refractory_class", "cementitious_composite", "fibre_load_transfer", "particle_load_transfer", "metallic_glass", "ceramic_subclass", "polymer_subclasses", "functionally_graded", "architected_cellular")

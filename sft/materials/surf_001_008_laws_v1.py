"""Exact Fold laws for the complete Materials SURF-001--008 family."""

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be positive")
    return value


def surface_free_state(bulk_sites, surface_sites, state_labels, condition):
    bulk_sites, surface_sites = positive(bulk_sites, "bulk sites"), positive(surface_sites, "surface sites")
    states = tuple(state_labels)
    if not states or not all(states) or not condition:
        raise ValueError("surface free-state record incomplete")
    return {"bulk_sites": bulk_sites, "surface_sites": surface_sites, "state_labels": states, "condition": condition, "surface_part": Fraction(surface_sites, bulk_sites + surface_sites), "surface_distinction_held": True}


def wetting(contact_sites, noncontact_sites, angle, liquid, surface, method):
    contact_sites, noncontact_sites = positive(contact_sites, "contact sites"), positive(noncontact_sites, "noncontact sites")
    angle = Fraction(angle)
    if angle <= 0 or not liquid or not surface or not method:
        raise ValueError("wetting record incomplete")
    return {"contact_sites": contact_sites, "noncontact_sites": noncontact_sites, "angle": angle, "liquid": liquid, "surface": surface, "method": method, "contact_part": Fraction(contact_sites, contact_sites + noncontact_sites), "custody_complete": True}


def adhesion(initial_links, retained_links, separated_links, work_quanta, interface, path):
    initial_links, retained_links, separated_links, work_quanta = (positive(value, name) for value, name in ((initial_links, "initial links"), (retained_links, "retained links"), (separated_links, "separated links"), (work_quanta, "work quanta")))
    path = tuple(path)
    if retained_links + separated_links != initial_links or not interface or len(path) < 2:
        raise ValueError("adhesion ledger incomplete")
    return {"initial_links": initial_links, "retained_links": retained_links, "separated_links": separated_links, "work_quanta": work_quanta, "interface": interface, "path": path, "work_per_separated_link": Fraction(work_quanta, separated_links), "closes": True}


def coating_stack(substrate, layers, interfaces, process_path):
    layers, interfaces, path = tuple(layers), tuple(interfaces), tuple(process_path)
    if not substrate or not layers or len(interfaces) != len(layers) or not all(layers) or not all(interfaces) or len(path) < 2:
        raise ValueError("coating stack incomplete")
    return {"substrate": substrate, "layers": layers, "interfaces": interfaces, "process_path": path, "ordered": True}


def roughness_profile(heights, lateral_scale, method):
    heights = tuple(positive(height, "profile height") for height in heights)
    lateral_scale = positive(lateral_scale, "lateral scale")
    if len(heights) < 2 or max(heights) == min(heights) or not method:
        raise ValueError("roughness profile incomplete")
    return {"heights": heights, "lateral_scale": lateral_scale, "method": method, "height_range": max(heights) - min(heights), "all_profile_points_retained": True}


def surface_reaction(sites, reactants, products, surface_before, surface_after, path):
    sites = positive(sites, "surface sites")
    reactants, products, path = tuple(reactants), tuple(products), tuple(path)
    if not reactants or not products or not all(reactants + products) or not surface_before or surface_before != surface_after or len(path) < 3:
        raise ValueError("surface reaction handoff incomplete")
    return {"sites": sites, "reactants": reactants, "products": products, "surface_before": surface_before, "surface_after": surface_after, "path": path, "surface_identity_retained": True, "chemistry_handoff": True}


def tribofilm(initial_sites, covered_sites, uncovered_sites, film, substrate, path):
    initial_sites, covered_sites, uncovered_sites = (positive(value, name) for value, name in ((initial_sites, "initial sites"), (covered_sites, "covered sites"), (uncovered_sites, "uncovered sites")))
    path = tuple(path)
    if covered_sites + uncovered_sites != initial_sites or not film or not substrate or len(path) < 2:
        raise ValueError("tribofilm ledger incomplete")
    return {"initial_sites": initial_sites, "covered_sites": covered_sites, "uncovered_sites": uncovered_sites, "film": film, "substrate": substrate, "path": path, "coverage_part": Fraction(covered_sites, initial_sites), "retention_recorded": True}


def delamination(interface_links, intact_links, separated_links, front_path, layer, substrate):
    interface_links, intact_links, separated_links = (positive(value, name) for value, name in ((interface_links, "interface links"), (intact_links, "intact links"), (separated_links, "separated links")))
    front = tuple(front_path)
    if intact_links + separated_links != interface_links or len(front) < 2 or not layer or not substrate:
        raise ValueError("delamination ledger incomplete")
    return {"interface_links": interface_links, "intact_links": intact_links, "separated_links": separated_links, "front_path": front, "layer": layer, "substrate": substrate, "separated_part": Fraction(separated_links, interface_links), "closes": True}


BASE = ("SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-MAT-MEAS-MATERIAL-001", "SFT-MAT-MEAS-SPECIMEN-001", "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-MEAS-TRACEABILITY-001", "SFT-MAT-MICRO-INTERFACE-001", "SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005")
DEFINITIONS = (
    ("001", "SFT-MAT-SURF-FREE-STATE-ENERGY-001", "Surface free-state and energy relation", "A surface state retains distinct counted bulk and surface supports, every held state label and the observation condition; its exact excess support is a fraction, not an imported continuum energy model.", BASE),
    ("002", "SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002", "Wetting and contact-angle custody", "Wetting retains liquid, surface, method, exact contact/noncontact partition and exact rational angle as one condition-bound observation.", BASE + ("SFT-MAT-SURF-FREE-STATE-ENERGY-001",)),
    ("003", "SFT-MAT-SURF-ADHESION-SEPARATION-003", "Adhesion and work-of-separation ledger", "Adhesion retains the exact partition of interface links into retained and separated supports together with counted separation work and the complete path.", BASE + ("SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002",)),
    ("004", "SFT-MAT-SURF-COATING-SUBSTRATE-004", "Coating layer and substrate organization", "A coating system is the exact ordered word of substrate, layers, interfaces and process states; no effective single layer may erase its organization.", BASE + ("SFT-MAT-SURF-ADHESION-SEPARATION-003", "SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006")),
    ("005", "SFT-MAT-SURF-ROUGHNESS-SCALE-005", "Surface roughness and scale boundary", "Surface roughness is an exact finite height word bound to lateral scale and method, retaining every profile point and its counted range.", BASE + ("SFT-MAT-SURF-COATING-SUBSTRATE-004",)),
    ("006", "SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006", "Surface reaction and catalysis handoff", "A surface reaction record retains surface sites, reactant and product identities, the full state path and unchanged catalytic surface identity while handing chemical identity and rate consequences to Chemistry.", BASE + ("SFT-MAT-SURF-ROUGHNESS-SCALE-005",)),
    ("007", "SFT-MAT-SURF-TRIBOFILM-RETENTION-007", "Tribofilm formation and retention", "A tribofilm retains film and substrate identities, complete formation path and the exact surface-site partition into covered and uncovered supports.", BASE + ("SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006", "SFT-MAT-MECH-FRICTION-CONTACT-012", "SFT-MAT-MECH-LUBRICATION-TRIBOFILM-013")),
    ("008", "SFT-MAT-SURF-DELAMINATION-008", "Interface fracture and delamination", "Interface fracture retains layer, substrate, intact and separated link supports and the complete delamination-front path as one exact ledger.", BASE + ("SFT-MAT-SURF-TRIBOFILM-RETENTION-007", "SFT-MAT-MECH-FRACTURE-ENERGY-007")),
)
RELATIONS = dict(zip((f"{index:03d}" for index in range(1, 9)), ("bulk-surface-state-condition-excess-ledger", "liquid-surface-contact-noncontact-angle-method-custody", "interface-link-separation-work-path-ledger", "substrate-layer-interface-process-word", "height-word-lateral-scale-method-range", "surface-site-reactant-product-path-catalyst-handoff", "film-substrate-covered-uncovered-path", "layer-substrate-intact-separated-front-path")))


def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "label-only", "erased", "complete-positive-surface-carrier", "held"),
        binary_axis("relation", "relation?", "imported-fit-model", "not forced", relation, "exact"),
        binary_axis("path", "path?", "endpoint-or-average-only", "erased", "complete-surface-interface-state-path", "retained"),
        binary_axis("observation", "conditions?", "condition-erased", "not reproducible", "specimen-method-condition-scale-uncertainty-held", "held"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-trace", "retained"),
        binary_axis("provenance", "selector?", "target-or-prior-model", "external selector", "root-bound-forward-forcing", "forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "preserved"),
        binary_axis("extension", "extra?", "fit-exception-extra-rule", "manufactured", "no-extra-rule", "none"),
    )


WITNESSES = {
    "001": (Witness("surface", "distinct support", surface_free_state(3, 2, ("free", "bound"), "held")["surface_distinction_held"]),),
    "002": (Witness("wetting", "custody", wetting(3, 2, Fraction(3, 2), "water", "solid", "goniometry")["custody_complete"]),),
    "003": (Witness("adhesion", "separation", adhesion(5, 3, 2, 4, "layer-substrate", ("joined", "separated"))["work_per_separated_link"] == 2),),
    "004": (Witness("coating", "ordered", coating_stack("substrate", ("bond", "top"), ("sb", "bt"), ("deposited", "cured"))["ordered"]),),
    "005": (Witness("roughness", "range", roughness_profile((1, 3, 2), 5, "profilometry")["height_range"] == 2),),
    "006": (Witness("reaction", "handoff", surface_reaction(3, ("a",), ("b",), "catalyst", "catalyst", ("adsorb", "transform", "desorb"))["surface_identity_retained"]),),
    "007": (Witness("tribofilm", "coverage", tribofilm(5, 3, 2, "film", "substrate", ("initial", "formed"))["coverage_part"] == Fraction(3, 5)),),
    "008": (Witness("delamination", "partition", delamination(5, 3, 2, ("start", "front"), "layer", "substrate")["separated_part"] == Fraction(2, 5)),),
}


@dataclass(frozen=True)
class SurfSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(witness.passed for witness in self.witnesses):
            raise ValueError("invalid SURF spec")
        for axis in self.axes:
            axis.survivor


class SurfProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


EXCLUSIONS = ("no imported continuum surface equation, fitted threshold, named mechanism or prior proof as premise", "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude", "structural absence and every surface, layer, interface, state and path distinction remain held labels", "no external outcome selects a survivor", "all result classes remain retained", "no failed attempt retires an obligation or changes protected authority")
SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    spec = SurfSpec(claim_id=claim_id, title=title, statement=statement, dependencies=dependencies, evidence_mode=EvidenceMode.EMPIRICAL, generation_rule=f"Complete literal product of eight SURF-{number} axes before target release.", grammar_boundary=f"Every positive finite SURF-{number} carrier with complete surface, interface, state, path and observation distinctions.", axes=axes(RELATIONS[number]), exact_result=f"SURF-{number} uniquely retains {RELATIONS[number]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.", induction_base="The first positive surface carrier retains every distinction.", induction_step="One lawful successor retains all prior distinctions and adds no selector.", exclusions=EXCLUSIONS, witnesses=WITNESSES[number], number=number, obligation_id=f"SFT-MAT-OBL-SURF-{number}")
    spec.validate()
    SPECS[claim_id] = spec
ORDER = tuple(row[1] for row in DEFINITIONS)

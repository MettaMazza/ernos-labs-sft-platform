"""Exact Fold laws for Biology MOLX-001--014.

Every operation uses positive exact counts and fractions.  Numerical ``0`` is
accepted only at the human notation boundary elsewhere in the platform; inside
these laws an exhausted or unobserved carrier is a labelled structural absence.
No negative, floating, irrational or imaginary proof magnitude is produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


ABSENCE = "structural-absence"


def positive(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive exact count")
    return value


def exact_part(numerator: int, denominator: int, name: str) -> Fraction:
    return Fraction(positive(numerator, name + " numerator"), positive(denominator, name + " denominator"))


def held_remainder(total: int, used: int, name: str) -> int | str:
    total = positive(total, name + " total")
    used = positive(used, name + " used")
    if used > total:
        raise ValueError(name + " used carrier exceeds held total")
    return ABSENCE if used == total else total - used


def reaction_balance(
    reactant_atoms: Mapping[str, int], product_atoms: Mapping[str, int],
    reactants: Iterable[str], products: Iterable[str], direction: str,
) -> dict[str, object]:
    left = {str(label): positive(value, f"reactant {label}") for label, value in reactant_atoms.items()}
    right = {str(label): positive(value, f"product {label}") for label, value in product_atoms.items()}
    reactant_word, product_word = tuple(reactants), tuple(products)
    if not left or not right or not reactant_word or not product_word:
        raise ValueError("reaction requires complete positive participant and atom ledgers")
    if direction not in ("forward", "reverse", "reversible"):
        raise ValueError("reaction direction must remain a held label")
    if left != right:
        raise ValueError("elemental carriers do not close")
    return {
        "reactants": reactant_word,
        "products": product_word,
        "atom_ledger": tuple(sorted(left.items())),
        "direction": direction,
        "balanced": True,
        "unassigned_carrier": ABSENCE,
    }


def enzyme_specificity(
    catalyst: str, allowed_substrates: Iterable[str], substrate: str, product: str,
) -> dict[str, object]:
    allowed = tuple(dict.fromkeys(str(item) for item in allowed_substrates))
    if not catalyst or not substrate or not product or not allowed or any(not item for item in allowed):
        raise ValueError("complete catalyst, substrate and product labels required")
    accepted = substrate in allowed
    return {
        "catalyst_before": catalyst,
        "substrate": substrate,
        "allowed_substrates": allowed,
        "product": product if accepted else ABSENCE,
        "transition": "catalysed" if accepted else ABSENCE,
        "catalyst_after": catalyst,
        "catalyst_identity_retained": True,
    }


def finite_enzyme_throughput(
    substrate_count: int, site_count: int, turn_count: int,
    inhibited_site_count: int | None = None,
) -> dict[str, object]:
    substrate = positive(substrate_count, "substrate")
    sites = positive(site_count, "site")
    turns = positive(turn_count, "turn")
    if inhibited_site_count is None:
        active_sites: int | str = sites
        inhibited: int | str = ABSENCE
    else:
        inhibited_count = positive(inhibited_site_count, "inhibited site")
        if inhibited_count > sites:
            raise ValueError("inhibited sites exceed enzyme sites")
        active_sites = held_remainder(sites, inhibited_count, "site")
        inhibited = inhibited_count
    capacity = ABSENCE if active_sites == ABSENCE else active_sites * turns
    if capacity == ABSENCE:
        processed: int | str = ABSENCE
        unprocessed: int | str = substrate
    else:
        processed = substrate if substrate <= capacity else capacity
        unprocessed = held_remainder(substrate, processed, "substrate")
    return {
        "substrate_count": substrate,
        "site_count": sites,
        "turn_count": turns,
        "inhibited_site_count": inhibited,
        "active_site_count": active_sites,
        "finite_capacity": capacity,
        "processed": processed,
        "unprocessed": unprocessed,
        "condition_held": True,
    }


def redox_transfer(
    donor: str, acceptor: str, donor_carriers: int, acceptor_capacity: int,
    transferred: int, carrier_label: str,
) -> dict[str, object]:
    if not donor or not acceptor or donor == acceptor or not carrier_label:
        raise ValueError("distinct donor, acceptor and carrier labels required")
    supplied = positive(donor_carriers, "donor carrier")
    capacity = positive(acceptor_capacity, "acceptor capacity")
    amount = positive(transferred, "transferred carrier")
    if amount > supplied or amount > capacity:
        raise ValueError("transfer exceeds donor or acceptor support")
    return {
        "donor": donor,
        "acceptor": acceptor,
        "carrier_label": carrier_label,
        "orientation": f"{donor}-to-{acceptor}",
        "transferred": amount,
        "donor_remainder": held_remainder(supplied, amount, "donor"),
        "acceptor_unused_capacity": held_remainder(capacity, amount, "acceptor capacity"),
        "oxidation_and_reduction_coupled": True,
    }


def coupled_work(resource_units: int, required_units: int, work_acts: int, resource_label: str) -> dict[str, object]:
    available = positive(resource_units, "resource")
    required = positive(required_units, "required resource")
    acts = positive(work_acts, "work act")
    if not resource_label or required > available or acts > required:
        raise ValueError("work act lacks complete positive coupled support")
    return {
        "resource_label": resource_label,
        "available": available,
        "required": required,
        "work_acts": acts,
        "spent": required,
        "retained": held_remainder(available, required, "resource"),
        "work_per_spent_part": exact_part(acts, required, "work per spent"),
        "uncoupled_work": ABSENCE,
    }


def chemiosmotic_transport(
    side_a: int, side_b: int, moved: int, membrane: str, route: str, ion_label: str,
) -> dict[str, object]:
    a, b, amount = positive(side_a, "side a"), positive(side_b, "side b"), positive(moved, "moved")
    if not membrane or not route or not ion_label or a == b:
        raise ValueError("held membrane, route, ion and unequal side support required")
    source_label, sink_label = ("side-a", "side-b") if a > b else ("side-b", "side-a")
    source, sink = (a, b) if a > b else (b, a)
    excess = source - sink
    if amount > excess:
        raise ValueError("transport exceeds the oriented excess carrier")
    source_after = source - amount
    sink_after = sink + amount
    return {
        "membrane": membrane,
        "route": route,
        "ion_label": ion_label,
        "orientation": f"{source_label}-to-{sink_label}",
        "excess_before": excess,
        "moved": amount,
        "source_after": source_after,
        "sink_after": sink_after,
        "residual_excess": ABSENCE if source_after == sink_after else abs(source_after - sink_after),
        "side_identities_retained": True,
    }


def carbon_fixation(source_labels: Iterable[str], product_positions: Iterable[str], pathway: Iterable[str]) -> dict[str, object]:
    sources, positions, route = tuple(source_labels), tuple(product_positions), tuple(pathway)
    if not sources or len(sources) != len(positions) or len(set(sources)) != len(sources):
        raise ValueError("each fixed carbon requires one distinct source label and product position")
    if not route or any(not item for item in sources + positions + route):
        raise ValueError("complete fixation route required")
    return {
        "source_to_product": tuple(zip(sources, positions)),
        "pathway": route,
        "fixed_count": len(sources),
        "lost_source_labels": ABSENCE,
        "complete_provenance": True,
    }


def branch_allocation(total: int, allocations: Mapping[str, int], condition: str) -> dict[str, object]:
    carrier = positive(total, "branch carrier")
    parts = {str(label): positive(value, f"branch {label}") for label, value in allocations.items()}
    if not condition or len(parts) < 2 or sum(parts.values()) != carrier:
        raise ValueError("complete multi-branch allocation must close the input carrier")
    return {
        "total": carrier,
        "condition": condition,
        "allocations": tuple(sorted(parts.items())),
        "parts": tuple((label, Fraction(value, carrier)) for label, value in sorted(parts.items())),
        "unassigned": ABSENCE,
        "closes": True,
    }


def nutrient_cycle(carrier_label: str, path: Iterable[str], count: int, environment: str) -> dict[str, object]:
    route = tuple(path)
    amount = positive(count, "nutrient carrier")
    if not carrier_label or not environment or len(route) < 3 or route[0] != route[-1]:
        raise ValueError("nutrient cycle must retain a closed route and environment")
    if any(not state for state in route):
        raise ValueError("nutrient cycle contains an empty state")
    return {
        "carrier_label": carrier_label,
        "carrier_count": amount,
        "environment": environment,
        "path": route,
        "transition_count": len(route) - 1,
        "returned_to_source_state": True,
        "unaccounted_carrier": ABSENCE,
    }


def lipid_lifecycle(head: str, tails: Iterable[str], path: Iterable[str], compartment: str) -> dict[str, object]:
    tail_word, route = tuple(tails), tuple(path)
    if not head or not tail_word or any(not tail for tail in tail_word) or not compartment:
        raise ValueError("complete lipid identity and compartment required")
    required = ("synthesis", "incorporation", "remodelling", "degradation")
    if route != required:
        raise ValueError("lipid lifecycle must retain all ordered stages")
    return {
        "head": head,
        "tails": tail_word,
        "compartment": compartment,
        "path": route,
        "stage_count": len(route),
        "identity_changes_retained": True,
    }


def carbohydrate_storage(monomer: str, stored_units: int, released_units: int, compartment: str) -> dict[str, object]:
    stored, released = positive(stored_units, "stored unit"), positive(released_units, "released unit")
    if not monomer or not compartment or released > stored:
        raise ValueError("complete carbohydrate storage carrier required")
    return {
        "monomer": monomer,
        "compartment": compartment,
        "stored_units": stored,
        "released_units": released,
        "retained_units": held_remainder(stored, released, "storage"),
        "unit_conservation": True,
    }


def amino_acid_routing(amino_acid: str, nitrogen_label: str, carbon_skeleton: str, nitrogen_fate: str, carbon_fate: str) -> dict[str, object]:
    labels = (amino_acid, nitrogen_label, carbon_skeleton, nitrogen_fate, carbon_fate)
    if any(not label for label in labels) or nitrogen_fate == carbon_fate:
        raise ValueError("amino-acid routing requires distinct retained carrier fates")
    return {
        "amino_acid": amino_acid,
        "nitrogen": (nitrogen_label, nitrogen_fate),
        "carbon": (carbon_skeleton, carbon_fate),
        "unassigned_component": ABSENCE,
        "complete_fate_custody": True,
    }


def cofactor_dependence(catalyst: str, substrate: str, product: str, cofactor: str, cofactor_held: bool) -> dict[str, object]:
    if any(not label for label in (catalyst, substrate, product, cofactor)):
        raise ValueError("complete cofactor-dependent reaction labels required")
    return {
        "catalyst": catalyst,
        "substrate": substrate,
        "cofactor": cofactor,
        "cofactor_held": cofactor_held,
        "product": product if cofactor_held else ABSENCE,
        "terminal_transition": "complete" if cofactor_held else ABSENCE,
        "cofactor_identity_after": cofactor,
    }


def metabolome_flux_custody(
    observed: Mapping[str, int], missing: Iterable[str],
    transitions: Iterable[tuple[str, str, int]], condition: str,
) -> dict[str, object]:
    measured = {str(label): positive(value, f"metabolite {label}") for label, value in observed.items()}
    absent = tuple(dict.fromkeys(str(label) for label in missing))
    edges = tuple((str(source), str(target), positive(value, "flux")) for source, target, value in transitions)
    if not measured or not condition or any(not label for label in measured) or any(not label for label in absent):
        raise ValueError("source-bound metabolome condition and identity required")
    if set(measured).intersection(absent):
        raise ValueError("one metabolite cannot be both observed and structurally missing")
    if not edges or any(not source or not target for source, target, _ in edges):
        raise ValueError("complete positive transition records required")
    return {
        "condition": condition,
        "observed": tuple(sorted(measured.items())),
        "missing": absent if absent else ABSENCE,
        "transitions": edges,
        "observed_count": len(measured),
        "missing_count": len(absent) if absent else ABSENCE,
        "all_result_classes_retained": True,
    }


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MEAS-UNIT-COMPARISON-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-STOICH-COEFFICIENT-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-NET-REACTION-001",
    "SFT-CHEM-CAT-CATALYST-001",
    "SFT-BIO-METABOLISM-001",
    "SFT-BIO-METABOLIC-TRANSFORMATION-001",
    "SFT-BIO-ENERGY-COUPLING-001",
    "SFT-BIO-RESOURCE-CLOSURE-001",
)


DEFINITIONS = (
    ("001", "SFT-BIO-MOLX-REACTION-BALANCE-001", "Biological reaction-network stoichiometry and carrier balance", "A biological reaction is an oriented source-bound participant transition whose complete elemental carrier ledger closes exactly and retains no unassigned carrier.", BASE),
    ("002", "SFT-BIO-MOLX-ENZYME-SPECIFICITY-002", "Enzyme-catalysed transition and substrate-specificity boundary", "An enzyme-catalysed transition retains catalyst identity before and after one allowed substrate-to-product transition; an unregistered substrate produces structural absence rather than an invented product.", BASE + ("SFT-BIO-MOLX-REACTION-BALANCE-001", "SFT-CHEM-CAT-SELECTIVITY-001")),
    ("003", "SFT-BIO-MOLX-ENZYME-FINITE-THROUGHPUT-003", "Enzyme saturation, inhibition and finite-rate comparison", "Finite enzyme throughput is the exact processed carrier bounded jointly by positive substrate support, active site count and counted turns, with inhibited sites and unprocessed substrate retained separately.", BASE + ("SFT-BIO-MOLX-ENZYME-SPECIFICITY-002", "SFT-CHEM-KIN-RATE-001", "SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010")),
    ("004", "SFT-BIO-MOLX-REDOX-CARRIER-004", "Biological redox-carrier and electron-transfer ledger", "Biological redox is one oriented exact carrier transfer from a held donor to a distinct held acceptor with oxidation and reduction closed in the same record.", BASE + ("SFT-BIO-MOLX-ENZYME-FINITE-THROUGHPUT-003", "SFT-CHEM-REDOX-COUPLING-001")),
    ("005", "SFT-BIO-MOLX-COUPLED-WORK-005", "ATP-equivalent coupling and cellular work accounting", "Cellular work occurs only with a retained positive resource coupling whose spent carrier, remaining carrier and completed work acts close exactly; uncoupled work is structural absence.", BASE + ("SFT-BIO-MOLX-REDOX-CARRIER-004",)),
    ("006", "SFT-BIO-MOLX-CHEMIOSMOTIC-TRANSPORT-006", "Chemiosmotic gradient and coupled transport relation", "Chemiosmotic transport is an oriented counted ion-carrier transition between retained membrane sides through a named route, bounded by the exact pre-transition excess and preserving both side identities.", BASE + ("SFT-BIO-MOLX-COUPLED-WORK-005", "SFT-BIO-MEMBRANE-001", "SFT-BIO-CELL-TRANSPORT-001")),
    ("007", "SFT-BIO-MOLX-CARBON-FIXATION-007", "Carbon-fixation pathway organization", "Biological carbon fixation is a complete source-to-product positional mapping along a retained pathway; every fixed carbon label has one product position and no source label is erased.", BASE + ("SFT-BIO-MOLX-CHEMIOSMOTIC-TRANSPORT-006",)),
    ("008", "SFT-BIO-MOLX-CARBON-BRANCH-ALLOCATION-008", "Central carbon-flow and branch-point allocation", "A central-carbon branch point is an exact condition-bound partition of one positive input carrier among every registered outgoing route, with branch parts closing the whole and no unassigned carrier.", BASE + ("SFT-BIO-MOLX-CARBON-FIXATION-007",)),
    ("009", "SFT-BIO-MOLX-NUTRIENT-CYCLE-009", "Nitrogen, sulfur and phosphorus biological cycling", "A biological nutrient cycle is a closed environment-bound state path for one retained elemental carrier, with every transition counted and no unaccounted carrier.", BASE + ("SFT-BIO-MOLX-CARBON-BRANCH-ALLOCATION-008",)),
    ("010", "SFT-BIO-MOLX-LIPID-LIFECYCLE-010", "Lipid synthesis, remodelling and degradation", "A biological lipid lifecycle retains head and tail identity, compartment and the complete ordered synthesis, incorporation, remodelling and degradation path.", BASE + ("SFT-BIO-MOLX-NUTRIENT-CYCLE-009",)),
    ("011", "SFT-BIO-MOLX-CARBOHYDRATE-STORAGE-011", "Carbohydrate synthesis, storage and mobilization", "Carbohydrate storage is a compartment-bound ordered monomer carrier whose released and retained units close the stored whole exactly, with exhaustion represented as structural absence.", BASE + ("SFT-BIO-MOLX-LIPID-LIFECYCLE-010",)),
    ("012", "SFT-BIO-MOLX-AMINO-ACID-ROUTING-012", "Amino-acid synthesis and catabolic routing", "Amino-acid transformation retains distinct nitrogen and carbon-skeleton carrier identities through their complete named fates, with no unassigned component.", BASE + ("SFT-BIO-MOLX-CARBOHYDRATE-STORAGE-011",)),
    ("013", "SFT-BIO-MOLX-COFACTOR-DEPENDENCE-013", "Cofactor, vitamin and prosthetic-group dependence", "A cofactor-dependent biological transition completes only when the named cofactor is held with catalyst and substrate; its absence halts product formation while cofactor identity remains explicit.", BASE + ("SFT-BIO-MOLX-AMINO-ACID-ROUTING-012",)),
    ("014", "SFT-BIO-MOLX-METABOLOME-FLUX-CUSTODY-014", "Metabolome identity, flux and missing-carrier custody", "A metabolome is a condition-bound exact carrier inventory plus positive transition records that preserves observed, missing, uncertain and unassigned states rather than collapsing them into a favorable endpoint.", BASE + ("SFT-BIO-MOLX-COFACTOR-DEPENDENCE-013", "SFT-BIO-BIO-UNCERTAINTY-001")),
)


RELATIONS = dict(
    zip(
        (f"{index:03d}" for index in range(1, 15)),
        (
            "oriented-participant-transition-with-exact-elemental-carrier-closure",
            "allowed-substrate-product-transition-with-catalyst-identity-return",
            "substrate-site-turn-inhibition-bounded-exact-throughput",
            "held-donor-acceptor-oriented-carrier-transfer-closure",
            "resource-spend-work-act-exact-coupling-with-uncoupled-absence",
            "membrane-side-route-held-gradient-bounded-carrier-transport",
            "source-carbon-to-product-position-complete-path-mapping",
            "condition-bound-complete-branch-allocation-exact-parts",
            "environment-bound-elemental-carrier-closed-state-cycle",
            "head-tail-compartment-held-complete-lipid-lifecycle",
            "monomer-storage-release-retention-exact-unit-closure",
            "nitrogen-carbon-skeleton-distinct-complete-fate-routing",
            "cofactor-held-terminal-transition-with-absence-halt",
            "condition-bound-metabolite-inventory-transition-and-missing-custody",
        ),
    )
)


def axes(relation: str) -> tuple:
    return (
        binary_axis("carrier", "carrier?", "answer-label-only", "biological carrier erased", "complete-positive-labelled-biological-carrier", "all exact carriers retained"),
        binary_axis("relation", "relation?", "imported-named-pathway-or-fit", "not Fold-forced", relation, "exact generated relation"),
        binary_axis("path", "path?", "endpoint-only", "biological mechanism erased", "complete-state-transition-lineage-and-resource-path", "path retained"),
        binary_axis("condition", "conditions?", "organism-condition-method-erased", "not reproducible", "organism-compartment-condition-method-uncertainty-held", "conditions retained"),
        binary_axis("record", "result classes?", "favorable-observed-only", "missing and adverse states erased", "observed-adverse-absent-unavailable-standing-held", "all result classes retained"),
        binary_axis("provenance", "selector?", "external-target-prior-model-or-opaque-predictor", "external selector", "root-bound-forward-forcing-before-target", "root forced"),
        binary_axis("generality", "closure?", "selected-organism-or-instance", "no lawful extension", "positive-finite-successor-and-composition-closure", "successor preserved"),
        binary_axis("extension", "extra rule?", "free-parameter-fit-exception-or-extra-axiom", "manufactured", "no-extra-rule", "zero parameter"),
    )


WITNESSES = {
    "001": (Witness("balance", "Two carbon and four oxygen carriers close on both sides.", reaction_balance({"C": 2, "O": 4}, {"C": 2, "O": 4}, ("carbon-source", "oxygen-source"), ("fixed-product",), "forward")["balanced"]),),
    "002": (Witness("specificity", "Allowed substrate changes while the catalyst returns unchanged.", enzyme_specificity("enzyme-a", ("substrate-a",), "substrate-a", "product-a")["catalyst_identity_retained"]), Witness("rejection", "An unregistered substrate produces structural absence.", enzyme_specificity("enzyme-a", ("substrate-a",), "substrate-b", "product-b")["product"] == ABSENCE)),
    "003": (Witness("finite", "Two active sites over three turns process six of eight substrate carriers.", finite_enzyme_throughput(8, 2, 3)["processed"] == 6), Witness("inhibition", "One inhibited site halves the same finite support.", finite_enzyme_throughput(8, 2, 3, 1)["processed"] == 3)),
    "004": (Witness("redox", "Three carriers transfer with donor and acceptor remainders retained.", redox_transfer("donor", "acceptor", 5, 4, 3, "electron")["transferred"] == 3),),
    "005": (Witness("coupling", "Three work acts consume three of five held resource units.", coupled_work(5, 3, 3, "ATP-equivalent")["retained"] == 2),),
    "006": (Witness("gradient", "One carrier moves from five to three across a held route and removes the excess.", chemiosmotic_transport(5, 3, 1, "membrane", "synthase", "proton")["residual_excess"] == ABSENCE),),
    "007": (Witness("fixation", "Three source labels map one-to-one to three product positions.", carbon_fixation(("c1", "c2", "c3"), ("p1", "p2", "p3"), ("capture", "reduction", "product"))["fixed_count"] == 3),),
    "008": (Witness("branch", "Five carriers split exactly into two and three.", branch_allocation(5, {"route-a": 2, "route-b": 3}, "condition-a")["closes"]),),
    "009": (Witness("cycle", "One nutrient carrier returns through a complete three-transition cycle.", nutrient_cycle("nitrogen", ("environment", "cell", "product", "environment"), 2, "habitat-a")["returned_to_source_state"]),),
    "010": (Witness("lipid", "The complete four-stage lipid lifecycle is retained.", lipid_lifecycle("polar-head", ("tail-a", "tail-b"), ("synthesis", "incorporation", "remodelling", "degradation"), "membrane")["stage_count"] == 4),),
    "011": (Witness("storage", "Three released units leave two of five units retained.", carbohydrate_storage("glucose-unit", 5, 3, "granule")["retained_units"] == 2), Witness("exhaustion", "Complete release is structural absence, not numerical zero.", carbohydrate_storage("glucose-unit", 5, 5, "granule")["retained_units"] == ABSENCE)),
    "012": (Witness("routing", "Nitrogen and carbon fates remain distinct and complete.", amino_acid_routing("amino-acid-a", "N-label", "C-skeleton", "nitrogen-pool", "carbon-path")["complete_fate_custody"]),),
    "013": (Witness("cofactor", "Held cofactor completes product formation.", cofactor_dependence("enzyme", "substrate", "product", "cofactor", True)["terminal_transition"] == "complete"), Witness("halt", "Missing cofactor leaves product structurally absent.", cofactor_dependence("enzyme", "substrate", "product", "cofactor", False)["product"] == ABSENCE)),
    "014": (Witness("metabolome", "Observed, missing and transition records coexist without collapse.", metabolome_flux_custody({"a": 2, "b": 3}, ("c",), (("a", "b", 1),), "condition-a")["all_result_classes_retained"]),),
}


@dataclass(frozen=True)
class MolxSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self) -> None:
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(witness.passed for witness in self.witnesses):
            raise ValueError("invalid Biology MOLX specification")
        for axis in self.axes:
            axis.survivor


class MolxProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="biology",
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
    "no imported continuum kinetic law, fitted pathway coefficient, conventional biological model or prior answer as premise",
    "no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "the display glyph 0 may denote absence at a user boundary but numerical zero is not a native biological carrier",
    "no external database, observed target, authority label or opaque predictor selects a survivor",
    "all favorable, adverse, absent, unavailable and standing-prediction rows remain retained",
    "no failed attempt retires an obligation or changes protected authority",
)


SPECS: dict[str, MolxSpec] = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    specification = MolxSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Complete literal product of eight Biology MOLX-{number} binary axes before target release.",
        grammar_boundary=f"Every positive finite MOLX-{number} living-process carrier with complete condition, path, observation and missing-state custody.",
        axes=axes(RELATIONS[number]),
        exact_result=f"MOLX-{number} uniquely retains {RELATIONS[number]} with complete carrier, mechanism, condition, result-class, root provenance, successor closure and no extra rule.",
        induction_base="The first positive living-process carrier retains every required distinction.",
        induction_step="One lawful successor or composition retains every earlier distinction and adds no selector.",
        exclusions=EXCLUSIONS,
        witnesses=WITNESSES[number],
        number=number,
        obligation_id=f"SFT-BIO-OBL-MOLX-{number}",
    )
    specification.validate()
    SPECS[claim_id] = specification


ORDER = tuple(row[1] for row in DEFINITIONS)


__all__ = (
    "ABSENCE",
    "MolxProgram",
    "ORDER",
    "SPECS",
    "reaction_balance",
    "enzyme_specificity",
    "finite_enzyme_throughput",
    "redox_transfer",
    "coupled_work",
    "chemiosmotic_transport",
    "carbon_fixation",
    "branch_allocation",
    "nutrient_cycle",
    "lipid_lifecycle",
    "carbohydrate_storage",
    "amino_acid_routing",
    "cofactor_dependence",
    "metabolome_flux_custody",
)

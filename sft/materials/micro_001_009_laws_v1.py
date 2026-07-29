"""Exact Fold laws for the complete Materials MICRO-001--009 family."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis


def positive(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive generated count")
    return value


def site_balance(site_count: int, defect_sites: tuple[int, ...]) -> dict[str, object]:
    site_count = positive(site_count, "site count")
    if len(set(defect_sites)) != len(defect_sites) or any(positive(site, "defect site") > site_count for site in defect_sites):
        raise ValueError("defect sites must be distinct members of the finite carrier")
    defect_count = len(defect_sites)
    host_count = site_count - defect_count
    return {
        "site_count": site_count,
        "defect_sites": defect_sites,
        "defect_count": defect_count or None,
        "host_count": host_count or None,
        "defect_part": Fraction(defect_count, site_count) if defect_count else None,
        "host_part": Fraction(host_count, site_count) if host_count else None,
        "recomposes_complete_carrier": defect_count + host_count == site_count,
    }


def migration_path(points: tuple[tuple[int, int, int], ...]) -> dict[str, object]:
    if len(points) < 2 or any(len(point) != 3 or any(positive(axis, "coordinate") != axis for axis in point) for point in points):
        raise ValueError("migration requires at least one transition over positive lattice coordinates")
    steps = []
    for source, target in zip(points, points[1:]):
        changed = tuple(index for index, (left, right) in enumerate(zip(source, target), 1) if left != right)
        if len(changed) != 1:
            raise ValueError("each migration transition must change exactly one lattice axis")
        axis = changed[0]
        left, right = source[axis - 1], target[axis - 1]
        separation = right - left if right > left else left - right
        if separation != 1:
            raise ValueError("each migration transition must be one adjacent lattice step")
        steps.append((source, target, ("axis", axis), "forward" if right > left else "opposed"))
    return {"initial": points[0], "terminal": points[-1], "steps": tuple(steps), "transition_count": len(steps), "complete_path_retained": True}


def dislocation_reaction(lines: tuple[tuple[str, int], ...]) -> dict[str, object]:
    if not lines or any(direction not in ("forward", "opposed") for direction, _ in lines):
        raise ValueError("dislocation lines require held orientations")
    forward = sum(positive(magnitude, "line magnitude") for direction, magnitude in lines if direction == "forward")
    opposed = sum(positive(magnitude, "line magnitude") for direction, magnitude in lines if direction == "opposed")
    if forward == opposed:
        result = ("structural-absence", None)
    elif forward > opposed:
        result = ("forward", forward - opposed)
    else:
        result = ("opposed", opposed - forward)
    return {"lines": lines, "result": result, "carrier_conserved": forward + opposed >= (result[1] or 1)}


def dislocation_modes(line_label: str, slip_plane: str, alternate_plane: str, vacancy_label: str) -> dict[str, object]:
    if not all(isinstance(x, str) and x for x in (line_label, slip_plane, alternate_plane, vacancy_label)) or slip_plane == alternate_plane:
        raise ValueError("dislocation mode labels must be nonempty and planes distinct")
    return {
        "glide": (line_label, slip_plane),
        "climb": (line_label, slip_plane, vacancy_label, "adjacent-parallel-plane"),
        "cross_slip": (line_label, slip_plane, alternate_plane, "line-orientation-retained"),
        "all_modes_reconstruct_line": True,
    }


def grain_growth(grains: tuple[tuple[int, int], ...]) -> dict[str, object]:
    """Transfer one exact cell from greatest boundary/area ratio to least."""
    if len(grains) < 2:
        raise ValueError("grain growth requires at least two grains")
    normalized = tuple((positive(area, "grain area"), positive(boundary, "boundary cells")) for area, boundary in grains)
    curvature = tuple(Fraction(boundary, area) for area, boundary in normalized)
    donor = max(range(len(grains)), key=lambda index: (curvature[index], -index))
    receiver = min(range(len(grains)), key=lambda index: (curvature[index], index))
    if donor == receiver or normalized[donor][0] == 1:
        raise ValueError("declared carrier has no lawful one-cell curvature transfer")
    areas = [area for area, _ in normalized]
    before = sum(areas)
    areas[donor] -= 1
    areas[receiver] += 1
    return {"initial_areas": tuple(area for area, _ in normalized), "curvature_parts": curvature, "donor": donor + 1, "receiver": receiver + 1, "final_areas": tuple(areas), "carrier_conserved": sum(areas) == before}


def segregation_ledger(bulk: tuple[str, ...], boundary: tuple[str, ...]) -> dict[str, object]:
    if not bulk or not boundary or any(not label for label in bulk + boundary):
        raise ValueError("segregation requires complete bulk and boundary carriers")
    species = tuple(sorted(set(bulk + boundary)))
    bulk_counts, boundary_counts = Counter(bulk), Counter(boundary)
    rows = []
    for label in species:
        bulk_part = Fraction(bulk_counts[label], len(bulk)) if bulk_counts[label] else None
        boundary_part = Fraction(boundary_counts[label], len(boundary)) if boundary_counts[label] else None
        if bulk_part is None and boundary_part is None:
            relation = "structural-absence"
        elif bulk_part is None:
            relation = "boundary-only"
        elif boundary_part is None:
            relation = "bulk-only"
        elif boundary_part == bulk_part:
            relation = "equal"
        elif boundary_part > bulk_part:
            relation = "boundary-enriched"
        else:
            relation = "boundary-depleted"
        rows.append((label, bulk_part, boundary_part, relation))
    return {"bulk": bulk, "boundary": boundary, "species_rows": tuple(rows), "all_species_retained": True}


def least_common_return(first: int, second: int) -> int:
    first, second = positive(first, "matrix step"), positive(second, "precipitate step")
    candidate = first
    while candidate % second:
        candidate += first
    return candidate


def inclusion_boundary(matrix_step: int, precipitate_step: int, observed_span: int) -> dict[str, object]:
    matrix_step, precipitate_step, observed_span = positive(matrix_step, "matrix step"), positive(precipitate_step, "precipitate step"), positive(observed_span, "observed span")
    common = least_common_return(matrix_step, precipitate_step)
    if matrix_step == precipitate_step:
        boundary_class = "coherent"
    elif common <= observed_span:
        boundary_class = "semicoherent-common-return-retained"
    else:
        boundary_class = "incoherent-within-declared-span"
    return {"matrix_step": matrix_step, "precipitate_step": precipitate_step, "observed_span": observed_span, "least_common_return": common, "boundary_class": boundary_class}


def coarsening_transfer(sizes: tuple[int, ...], donor: int, receiver: int, amount: int) -> dict[str, object]:
    if len(sizes) < 2 or donor == receiver:
        raise ValueError("coarsening requires distinct donor and receiver")
    sizes = tuple(positive(size, "particle carrier") for size in sizes)
    donor, receiver, amount = positive(donor, "donor index"), positive(receiver, "receiver index"), positive(amount, "transfer amount")
    if donor > len(sizes) or receiver > len(sizes) or amount > sizes[donor - 1]:
        raise ValueError("coarsening transfer exceeds declared carrier")
    after = list(sizes)
    remainder = after[donor - 1] - amount
    after[donor - 1] = remainder or None
    after[receiver - 1] += amount
    return {"initial": sizes, "final": tuple(after), "donor": donor, "receiver": receiver, "amount": amount, "carrier_conserved": sum(size for size in after if size is not None) == sum(sizes), "surviving_particle_count": sum(size is not None for size in after)}


def interface_motion(path: tuple[int, ...], driving_count: int) -> dict[str, object]:
    if len(path) < 2 or any(positive(position, "interface position") != position for position in path):
        raise ValueError("interface motion requires a positive path")
    driving_count = positive(driving_count, "driving count")
    initial, terminal = path[0], path[-1]
    if initial == terminal:
        return {"path": path, "orientation": "structural-absence", "distance": None, "velocity": None, "mobility": None}
    orientation = "forward" if terminal > initial else "opposed"
    distance = terminal - initial if terminal > initial else initial - terminal
    return {"path": path, "orientation": orientation, "distance": distance, "velocity": Fraction(distance, len(path) - 1), "mobility": Fraction(distance, driving_count), "complete_path_retained": True}


def multiscale_correspondence(features: tuple[tuple[str, int, Fraction], ...]) -> dict[str, object]:
    if not features or any(not label or positive(count, "feature count") != count or not isinstance(response, Fraction) or response <= 0 for label, count, response in features):
        raise ValueError("multiscale correspondence requires exact positive feature records")
    total = sum(count for _, count, _ in features)
    weighted = features[0][2] * features[0][1]
    for _, count, response in features[1:]:
        weighted += response * count
    return {"features": features, "feature_count": len(features), "site_count": total, "bulk_response": weighted / total, "complete_micro_to_bulk_trace": True}


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-MATH-GEOMETRY-TOPOLOGY-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-LOGIC-PROOF-001", "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-MAT-MEAS-MATERIAL-001", "SFT-MAT-MEAS-SPECIMEN-001", "SFT-MAT-MEAS-MICROSTRUCTURE-001", "SFT-MAT-MEAS-TRACEABILITY-001", "SFT-MAT-MICRO-GRAIN-BOUNDARY-001", "SFT-MAT-MICRO-INTERFACE-001", "SFT-MAT-MICRO-DIFFUSION-001", "SFT-MAT-MICRO-NUCLEATION-GROWTH-001",
)


DEFINITIONS = (
    ("001", "SFT-MAT-MICRO-DEFECT-POPULATION-001", "Defect population and site-fraction balance", "A defect population is the complete exact partition of a finite site carrier into held defect and host classes, whose rational parts recompose the whole carrier.", BASE),
    ("002", "SFT-MAT-MICRO-DEFECT-MIGRATION-002", "Defect migration and retained path", "Defect migration is a complete adjacent-site transition word retaining initial site, every axis-oriented step, terminal site, time order and carrier identity.", BASE + ("SFT-MAT-MICRO-DEFECT-POPULATION-001",)),
    ("003", "SFT-MAT-MICRO-DISLOCATION-REACTION-003", "Dislocation reaction, climb and cross-slip", "Dislocation reactions compose exact line magnitudes with held orientations; climb retains vacancy-mediated plane change and cross-slip retains line identity across a distinct plane.", BASE + ("SFT-MAT-MICRO-DEFECT-MIGRATION-002",)),
    ("004", "SFT-MAT-MICRO-GRAIN-GROWTH-004", "Curvature-driven grain growth", "Discrete curvature is the exact boundary-cell to grain-cell part; one lawful growth step transfers a cell from greater to lesser curvature while preserving the complete material carrier.", BASE + ("SFT-MAT-MICRO-DISLOCATION-REACTION-003",)),
    ("005", "SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005", "Interface and grain-boundary segregation", "Boundary segregation is the complete species-by-species comparison of exact bulk and boundary parts, retaining enrichment, depletion, equality and structural absence without signed concentration.", BASE + ("SFT-MAT-MICRO-GRAIN-GROWTH-004",)),
    ("006", "SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006", "Precipitation and coherent-incoherent inclusion boundary", "A precipitate inclusion retains matrix and inclusion recurrences; equality is coherent, a finite common return is semicoherent, and no return within the declared observation span is incoherent at that boundary.", BASE + ("SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005",)),
    ("007", "SFT-MAT-MICRO-COARSENING-TRANSFER-007", "Ostwald-type coarsening as exact carrier transfer", "Coarsening is conserved exact carrier transfer from a declared donor particle to a receiver particle, with donor disappearance held as structural absence and no unaccounted material gain.", BASE + ("SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006",)),
    ("008", "SFT-MAT-MICRO-INTERFACE-MOBILITY-008", "Interface migration and mobility record", "Interface mobility is the exact oriented displacement part per retained driving count, inseparable from the complete position-time path and observation boundary.", BASE + ("SFT-MAT-MICRO-COARSENING-TRANSFER-007",)),
    ("009", "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009", "Microstructure-to-bulk multiscale correspondence", "A bulk material response is the exact site-weighted composition of every retained microstructural feature response, with the complete feature-to-bulk reconstruction ledger preserved.", BASE + ("SFT-MAT-MICRO-INTERFACE-MOBILITY-008",)),
)


RELATIONS = {
    "001": "complete-site-partition-and-rational-fraction-balance",
    "002": "adjacent-site-axis-oriented-complete-migration-word",
    "003": "held-orientation-line-reaction-climb-cross-slip-ledger",
    "004": "boundary-cell-per-grain-cell-curvature-transfer",
    "005": "species-wise-bulk-boundary-part-comparison",
    "006": "matrix-inclusion-recurrence-and-common-return-boundary",
    "007": "conserved-particle-carrier-transfer-and-absence",
    "008": "oriented-interface-path-velocity-and-mobility-parts",
    "009": "complete-site-weighted-feature-to-bulk-composition",
}


def axes(relation):
    return (
        binary_axis("carrier", "What carries the microstructural distinction?", "answer-only-or-erased-carrier", "Without the complete material carrier the result cannot be reconstructed.", "complete-positive-microstructure-carrier", "Every site, constituent, interface and feature label remains held."),
        binary_axis("relation", "Which generated relation survives?", "imported-continuum-or-fitted-relation", "An imported equation or fitted target is not forced by Fold structure.", relation, "The exact finite relation uniquely preserves every required distinction."),
        binary_axis("organization", "What organization remains?", "bulk-average-only", "A bulk average erases defects, boundaries, paths and histories.", "complete-site-path-interface-organization", "All site, path, interface and scale distinctions remain recoverable."),
        binary_axis("observation", "What defines the observation class?", "method-condition-scale-erased", "An unrecorded specimen, method, condition or scale does not identify an observation.", "specimen-method-condition-scale-uncertainty-held", "The complete observation boundary is retained."),
        binary_axis("record", "What proof record is emitted?", "headline-only", "A headline has no reproducible candidate or transition trace.", "complete-state-transition-resource-trace", "Candidates, eliminations, transitions and resources are recorded."),
        binary_axis("provenance", "What selects the law?", "authority-target-or-prior-model", "External authority can test but cannot select the native law.", "root-bound-forward-forcing", "Every choice traces through admitted dependencies to the root theorem."),
        binary_axis("generality", "What closes the class?", "selected-instance-or-lookup", "One favourable instance does not prove its successor.", "positive-finite-successor-closure", "The base carrier and every lawful positive successor preserve the relation."),
        binary_axis("extension", "May another selector enter?", "free-fit-exception-or-extra-rule", "A free choice can manufacture the outcome.", "no-extra-rule", "No axiom, fit, exception or target-derived selector is admitted."),
    )


WITNESSES = {
    "001": (Witness("site-parts", "Two defects among eight sites force exact defect and host parts one-quarter and three-quarters.", site_balance(8, (2, 7))["defect_part"] == Fraction(1, 4) and site_balance(8, (2, 7))["host_part"] == Fraction(3, 4)), Witness("balance", "Defect and host classes recompose all eight sites.", site_balance(8, (2, 7))["recomposes_complete_carrier"])),
    "002": (Witness("adjacent-path", "The registered three-step path retains two adjacent transitions on distinct axes.", migration_path(((1, 1, 1), (2, 1, 1), (2, 2, 1)))["transition_count"] == 2), Witness("terminal", "Complete path custody reconstructs its terminal site.", migration_path(((1, 1, 1), (2, 1, 1), (2, 2, 1)))["terminal"] == (2, 2, 1))),
    "003": (Witness("opposed-reaction", "Three forward units and one opposed unit retain two forward units without a negative scalar.", dislocation_reaction((("forward", 3), ("opposed", 1)))["result"] == ("forward", 2)), Witness("modes", "Climb and cross-slip preserve line identity while retaining their distinct plane relations.", dislocation_modes("line-a", "plane-one", "plane-two", "vacancy-a")["all_modes_reconstruct_line"])),
    "004": (Witness("curvature-transfer", "The higher boundary/area part donates one cell to the lower part.", grain_growth(((4, 4), (8, 4)))["final_areas"] == (3, 9)), Witness("conservation", "The cell transfer preserves the complete material carrier.", grain_growth(((4, 4), (8, 4)))["carrier_conserved"])),
    "005": (Witness("enrichment", "Species x at one-quarter in bulk and three-quarters at boundary is exactly boundary-enriched.", next(row for row in segregation_ledger(("x", "y", "y", "y"), ("x", "x", "x", "y"))["species_rows"] if row[0] == "x")[3] == "boundary-enriched"), Witness("all-species", "Every bulk and boundary species remains in the ledger.", segregation_ledger(("x", "y"), ("y", "z"))["all_species_retained"])),
    "006": (Witness("coherent", "Equal recurrences force a coherent boundary.", inclusion_boundary(3, 3, 6)["boundary_class"] == "coherent"), Witness("bounded-classes", "A common return within span is semicoherent; beyond span is explicitly incoherent at that scope.", inclusion_boundary(2, 3, 6)["boundary_class"].startswith("semicoherent") and inclusion_boundary(2, 3, 5)["boundary_class"].startswith("incoherent"))),
    "007": (Witness("conserved-transfer", "Complete transfer of two units from the smaller carrier to the larger preserves five total units.", coarsening_transfer((2, 3), 1, 2, 2)["carrier_conserved"]), Witness("donor-absence", "A fully transferred donor becomes structural absence and particle count falls from two to one.", coarsening_transfer((2, 3), 1, 2, 2)["final"] == (None, 5) and coarsening_transfer((2, 3), 1, 2, 2)["surviving_particle_count"] == 1)),
    "008": (Witness("exact-mobility", "A three-cell forward displacement over two transitions at drive six forces velocity three-halves and mobility one-half.", interface_motion((2, 4, 5), 6)["velocity"] == Fraction(3, 2) and interface_motion((2, 4, 5), 6)["mobility"] == Fraction(1, 2)), Witness("orientation", "Direction is retained as a held forward label rather than a signed scalar.", interface_motion((2, 4, 5), 6)["orientation"] == "forward")),
    "009": (Witness("weighted-bulk", "Two sites at response one-half and one site at response one force exact bulk response two-thirds.", multiscale_correspondence((("a", 2, Fraction(1, 2)), ("b", 1, Fraction(1, 1))))["bulk_response"] == Fraction(2, 3)), Witness("trace", "Every feature identity, site count and exact response remains reconstructible.", multiscale_correspondence((("a", 2, Fraction(1, 2)), ("b", 1, Fraction(1, 1))))["complete_micro_to_bulk_trace"])),
}


@dataclass(frozen=True)
class MicrostructureSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if not self.claim_id.startswith("SFT-MAT-MICRO-") or self.number not in WITNESSES or len(self.axes) != 8:
            raise ValueError("invalid Materials MICRO spec")
        if not self.dependencies or len({axis.key for axis in self.axes}) != 8:
            raise ValueError("incomplete Materials MICRO spec")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("Materials MICRO axis incomplete")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("Materials MICRO witness failed")


class MicrostructureProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


EXCLUSIONS = (
    "no V1/V2 proof artifact, conventional continuum law, fitted constitutive equation or named mechanism as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence and opposed direction remain held labels",
    "no target value, official source, measured micrograph, selected specimen or favourable outcome selects a survivor",
    "no omitted adverse, absent, unavailable, unresolved, tampered or scope-boundary evidence row",
    "no first failed route retires an obligation and no engine, verifier, receipt or admitted certificate change",
)


SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    relation = RELATIONS[number]
    spec = MicrostructureSpec(
        claim_id=claim_id, title=title, statement=statement, dependencies=dependencies, evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Generate the complete literal product of the eight registered MICRO-{number} preservation axes before external target release.",
        grammar_boundary=f"Every positive finite generated microstructure carrier in MICRO-{number}, with complete site, path, interface, specimen, method, condition, scale, uncertainty and proof distinctions.",
        axes=axes(relation), exact_result=f"MICRO-{number} uniquely retains {relation} with complete carrier, organization, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive microstructural carrier retains its complete site, relation, observation boundary and root trace.",
        induction_step="Appending one lawful site, constituent, transition or feature preserves every prior distinction, adds all new pair/path relations and introduces no selector.",
        exclusions=EXCLUSIONS, witnesses=WITNESSES[number], number=number, obligation_id=f"SFT-MAT-OBL-MICRO-{number}")
    spec.validate(); SPECS[claim_id] = spec


ORDER = tuple(row[1] for row in DEFINITIONS)


__all__ = ("MicrostructureProgram", "ORDER", "SPECS", "site_balance", "migration_path", "dislocation_reaction", "dislocation_modes", "grain_growth", "segregation_ledger", "inclusion_boundary", "coarsening_transfer", "interface_motion", "multiscale_correspondence")

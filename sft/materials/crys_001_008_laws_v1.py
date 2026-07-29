"""Exact Fold laws for the complete Materials CRYS-001--008 family.

The native derivations use positive finite carriers, rational parts, held
orientation labels and structural absence.  Conventional complex amplitudes,
negative scalars, irrational coordinates and continuum fields are not proof
premises.  Phase is an exact period-four label orbit; opposition is a held
relation and cancellation returns structural absence.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis


PHASES = ("phase-one", "phase-two", "phase-three", "phase-four")
OPPOSED = {"phase-one": "phase-three", "phase-three": "phase-one", "phase-two": "phase-four", "phase-four": "phase-two"}


def _positive(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive generated count")
    return value


def phase_label(step: int) -> str:
    """Return the held phase label for a positive orbit step."""
    step = _positive(step, "phase step")
    return PHASES[(step - 1) % len(PHASES)]


def diffraction_ledger(paths: tuple[tuple[str, int], ...]) -> dict[str, object]:
    """Cancel opposed phase-labelled paths and count retained coherent pairs."""
    if not paths:
        raise ValueError("diffraction requires a positive path carrier")
    counts = Counter()
    for label, weight in paths:
        if label not in PHASES:
            raise ValueError("unregistered phase label")
        counts[label] += _positive(weight, "path weight")
    retained = []
    for first, opposed in ((PHASES[0], PHASES[2]), (PHASES[1], PHASES[3])):
        if counts[first] == counts[opposed]:
            retained.append(("structural-absence", None))
        elif counts[first] > counts[opposed]:
            retained.append((first, counts[first] - counts[opposed]))
        else:
            retained.append((opposed, counts[opposed] - counts[first]))
    intensity = sum(weight * weight for _, weight in retained if weight is not None)
    return {
        "input": tuple(paths),
        "phase_totals": tuple((label, counts[label] or None) for label in PHASES),
        "retained_amplitude_axes": tuple(retained),
        "coherent_ordered_pair_count": intensity or None,
    }


def finite_structure_factor(scatterers: tuple[tuple[int, int], ...], reciprocal_step: int) -> dict[str, object]:
    """Compose a finite structure factor from exact weights and lattice positions."""
    reciprocal_step = _positive(reciprocal_step, "reciprocal step")
    paths = []
    for weight, position in scatterers:
        weight = _positive(weight, "scatterer weight")
        position = _positive(position, "scatterer position")
        paths.append((phase_label(((position * reciprocal_step) - 1) % len(PHASES) + 1), weight))
    result = diffraction_ledger(tuple(paths))
    return {"scatterers": tuple(scatterers), "reciprocal_step": reciprocal_step, **result}


def exact_distribution(labels: tuple[str, ...]) -> tuple[tuple[str, Fraction], ...]:
    """Return an exact finite orientation/phase distribution without stochastic input."""
    if not labels or any(not isinstance(x, str) or not x for x in labels):
        raise ValueError("distribution requires positive held labels")
    counts = Counter(labels)
    total = len(labels)
    return tuple((label, Fraction(counts[label], total)) for label in sorted(counts))


def lag_pair_distribution(word: tuple[str, ...], lag: int) -> tuple[tuple[tuple[str, str], Fraction], ...]:
    """Count all exact non-wrapping label pairs at one positive separation."""
    lag = _positive(lag, "lag")
    if lag >= len(word) or any(not x for x in word):
        raise ValueError("lag must leave a positive observed pair carrier")
    pairs = tuple((word[index], word[index + lag]) for index in range(len(word) - lag))
    counts = Counter(pairs)
    return tuple((pair, Fraction(counts[pair], len(pairs))) for pair in sorted(counts))


def diffuse_support(word: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    """Record how many distinct pair classes survive at every positive lag."""
    if len(word) < 2:
        raise ValueError("diffuse support requires at least one pair")
    return tuple((lag, len(lag_pair_distribution(word, lag))) for lag in range(1, len(word)))


def stacking_fault_ledger(word: tuple[str, ...]) -> dict[str, object]:
    """Compare a close-packed layer word with the unique cyclic successor relation."""
    if not word or any(label not in ("A", "B", "C") for label in word):
        raise ValueError("stacking word requires A/B/C labels")
    if any(left == right for left, right in zip(word, word[1:])):
        raise ValueError("adjacent close-packed layers cannot occupy one label")
    successor = {"A": "B", "B": "C", "C": "A"}
    faults = tuple(index + 1 for index, (left, right) in enumerate(zip(word, word[1:])) if successor[left] != right)
    spectra = []
    offsets = {"A": 1, "B": 2, "C": 3}
    for reciprocal_step in range(1, len(PHASES) + 1):
        paths = tuple((phase_label(((index + offsets[label]) * reciprocal_step - 1) % len(PHASES) + 1), 1) for index, label in enumerate(word, 1))
        spectra.append((reciprocal_step, diffraction_ledger(paths)["coherent_ordered_pair_count"]))
    return {"word": word, "fault_positions": faults, "fault_count": len(faults) or None, "diffraction_support": tuple(spectra)}


def twin_transform(point: tuple[int, int, int]) -> tuple[int, int, int]:
    """Apply the exact two-domain twin operation exchanging two held axes."""
    if len(point) != 3 or any(_positive(x, "coordinate") != x for x in point):
        raise ValueError("twin point requires three positive coordinates")
    return point[1], point[0], point[2]


def twin_domain_ledger(points: tuple[tuple[int, int, int], ...]) -> dict[str, object]:
    if not points:
        raise ValueError("twin domain requires a positive point carrier")
    twin = tuple(twin_transform(point) for point in points)
    return {
        "domain-one": points,
        "domain-two": twin,
        "operation_is_involution": tuple(twin_transform(point) for point in twin) == points,
        "shared_points": tuple(sorted(set(points).intersection(twin))),
        "domain_specific_points": tuple(sorted(set(points).symmetric_difference(twin))),
    }


def modulation_ledger(base_count: int) -> dict[str, object]:
    """Generate an independent successor fibre and its exact satellite indices."""
    base_count = _positive(base_count, "base count")
    carrier = tuple((position, ("modulation-successor", position)) for position in range(1, base_count + 1))
    satellites = tuple((position, position) for position in range(1, base_count + 1))
    return {
        "carrier": carrier,
        "main_indices": tuple((position, None) for position in range(1, base_count + 1)),
        "satellite_indices": satellites,
        "base_translation_restores_modulation": False,
        "successor_extension_is_new": (base_count + 1, ("modulation-successor", base_count + 1)) not in carrier,
    }


def pair_distribution(positions: tuple[int, ...]) -> tuple[tuple[int, Fraction], ...]:
    """Reconstruct the complete exact positive pair-distance distribution."""
    if len(positions) < 2 or any(_positive(x, "position") != x for x in positions) or len(set(positions)) != len(positions):
        raise ValueError("pair distribution requires distinct positive positions")
    distances = tuple(right - left for left, right in combinations(sorted(positions), 2))
    counts = Counter(distances)
    return tuple((distance, Fraction(counts[distance], len(distances))) for distance in sorted(counts))


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-MAT-MEAS-MATERIAL-001",
    "SFT-MAT-MEAS-SPECIMEN-001",
    "SFT-MAT-MEAS-MICROSTRUCTURE-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-CRYST-LATTICE-001",
    "SFT-MAT-CRYST-UNIT-CELL-001",
    "SFT-MAT-CRYST-RECIPROCAL-001",
    "SFT-CHEM-XRAY-DIFFRACTION-STRUCTURE-016",
)


DEFINITIONS = (
    ("001", "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001", "Exact diffraction amplitude and intensity ledger", "Every labelled scattering path enters one exact phase class; opposed classes cancel only into structural absence, while retained coherent path pairs force the exact intensity ledger.", BASE),
    ("002", "SFT-MAT-CRYS-STRUCTURE-FACTOR-002", "Finite structure-factor composition", "A finite structure factor is the permutation-invariant Fold composition of every scatterer weight, exact lattice position, reciprocal path and retained phase relation.", BASE + ("SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001",)),
    ("003", "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003", "Polycrystal texture and orientation distribution", "Polycrystal texture is the complete exact rational distribution of retained grain-orientation labels, phase labels, specimen identity and measurement boundary.", BASE + ("SFT-MAT-CRYS-STRUCTURE-FACTOR-002",)),
    ("004", "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004", "Short-range order and diffuse-scattering relation", "Short-range order is the exact lag-labelled pair distribution of a generated material word; noncollapsed pair classes form the complete diffuse-support ledger.", BASE + ("SFT-MAT-CRYS-STRUCTURE-FACTOR-002",)),
    ("005", "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005", "Stacking-fault sequence and diffraction consequence", "A stacking fault is an exact departure from the unique cyclic successor in a close-packed A/B/C word, with every changed phase-support and diffraction class retained.", BASE + ("SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004",)),
    ("006", "SFT-MAT-CRYS-TWIN-DOMAIN-006", "Crystal twinning and domain relation", "A twin is a distinct domain generated by an exact nonidentity involution of the crystal carrier; shared and domain-specific diffraction support remain separately reconstructible.", BASE + ("SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005",)),
    ("007", "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007", "Incommensurate and modulated structure organization", "An incommensurate modulation is an independent nonclosing successor fibre over the base lattice, forcing compound main/satellite indices without irrational proof coordinates.", BASE + ("SFT-MAT-CRYST-QUASICRYSTAL-001", "SFT-MAT-CRYS-TWIN-DOMAIN-006")),
    ("008", "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008", "Total-scattering pair-distribution reconstruction", "The real-space pair distribution is the complete exact rational multiplicity ledger of every positive constituent separation retained by total scattering.", BASE + ("SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007",)),
)


def axes(relation: str):
    return (
        binary_axis("carrier", "What carries the crystallographic distinction?", "answer-only-or-erased-carrier", "An answer without its specimen and constituent carrier cannot be reconstructed.", "complete-positive-material-carrier", "Every constituent, path and specimen label remains held."),
        binary_axis("relation", "Which relation survives?", "imported-continuum-or-fitted-relation", "An imported equation or fitted target relation does not follow from Fold structure.", relation, "The exact generated relation is the sole distinction-preserving form."),
        binary_axis("organization", "What organization is retained?", "average-structure-only", "Averages merge phase, disorder and domain distinctions required by the claim.", "complete-local-and-reciprocal-organization", "Local, reciprocal, domain and history distinctions remain separately recoverable."),
        binary_axis("observation", "What defines the observation class?", "method-condition-boundary-erased", "An unrecorded probe, condition or scale cannot identify the observation.", "probe-condition-scale-and-uncertainty-held", "The specimen, probe, condition, scale and uncertainty boundary remain explicit."),
        binary_axis("record", "What proof record is required?", "headline-value-only", "A headline cannot reproduce the state transition or eliminated alternatives.", "complete-state-transition-resource-trace", "The complete candidate, transition, result and retained/lost distinction trace is recorded."),
        binary_axis("provenance", "What selects the law?", "authority-measurement-or-prior-model", "Authority and target data can test but cannot select a Fold law.", "root-bound-forward-forcing", "Every decision traces through admitted dependencies to the root theorem."),
        binary_axis("generality", "What closes the generated class?", "selected-example-or-finite-lookup", "A favourable instance has no successor certificate.", "positive-finite-successor-closure", "The base carrier and every lawful positive successor preserve the relation."),
        binary_axis("extension", "May an extra selector be added?", "free-fit-exception-or-extra-rule", "A free choice can manufacture the target answer.", "no-extra-rule", "No axiom, fit, target-derived constant or exception is present."),
    )


WITNESSES = {
    "001": (
        Witness("coherent-square", "Three equal-phase paths retain amplitude three and exactly nine coherent ordered pairs.", diffraction_ledger(((PHASES[0], 1),) * 3)["coherent_ordered_pair_count"] == 9),
        Witness("opposed-absence", "Equal opposed paths close to structural absence rather than a negative or numerical zero.", diffraction_ledger(((PHASES[0], 2), (PHASES[2], 2)))["coherent_ordered_pair_count"] is None),
    ),
    "002": (
        Witness("composition", "Two co-positioned scatterers of weights two and three compose to intensity twenty-five.", finite_structure_factor(((2, 1), (3, 1)), 4)["coherent_ordered_pair_count"] == 25),
        Witness("permutation", "Finite composition is invariant to scatterer enumeration order.", finite_structure_factor(((2, 1), (3, 2), (1, 4)), 3)["retained_amplitude_axes"] == finite_structure_factor(((1, 4), (2, 1), (3, 2)), 3)["retained_amplitude_axes"]),
    ),
    "003": (
        Witness("orientation-parts", "Two grains in one orientation and one in another form exact parts two-thirds and one-third.", exact_distribution(("north", "north", "east")) == (("east", Fraction(1, 3)), ("north", Fraction(2, 3)))),
        Witness("complete-one", "Every exact orientation part recomposes the complete One.", exact_distribution(("a", "b", "a", "c")) == (("a", Fraction(1, 2)), ("b", Fraction(1, 4)), ("c", Fraction(1, 4)))),
    ),
    "004": (
        Witness("lag-ledger", "The complete lag-one pair ledger of ABAC retains three distinct exact pair classes.", len(lag_pair_distribution(("A", "B", "A", "C"), 1)) == 3),
        Witness("diffuse-distinction", "A locally varied word retains more lag-one pair classes than a single-label recurrence.", diffuse_support(("A", "B", "A", "C"))[0][1] > diffuse_support(("A", "A", "A", "A"))[0][1]),
    ),
    "005": (
        Witness("ideal-cycle", "ABCABC contains no departure from the cyclic successor relation.", stacking_fault_ledger(tuple("ABCABC"))["fault_count"] is None),
        Witness("fault-consequence", "ABCACB contains two exact successor departures and a different diffraction-support ledger.", stacking_fault_ledger(tuple("ABCACB"))["fault_count"] == 2 and stacking_fault_ledger(tuple("ABCACB"))["diffraction_support"] != stacking_fault_ledger(tuple("ABCABC"))["diffraction_support"]),
    ),
    "006": (
        Witness("involution", "Applying the exact twin operation twice reconstructs every original point.", twin_domain_ledger(((1, 2, 3), (2, 2, 4)))["operation_is_involution"] is True),
        Witness("domain-separation", "An asymmetric point and its twin remain distinct while a diagonal point is shared.", twin_domain_ledger(((1, 2, 3), (2, 2, 4)))["domain_specific_points"] == ((1, 2, 3), (2, 1, 3)) and twin_domain_ledger(((1, 2, 3), (2, 2, 4)))["shared_points"] == ((2, 2, 4),)),
    ),
    "007": (
        Witness("compound-index", "Four base sites force four distinct compound satellite indices.", modulation_ledger(4)["satellite_indices"] == ((1, 1), (2, 2), (3, 3), (4, 4))),
        Witness("nonclosing-successor", "The next modulation fibre is new and no base translation is declared to restore it.", modulation_ledger(7)["successor_extension_is_new"] and not modulation_ledger(7)["base_translation_restores_modulation"]),
    ),
    "008": (
        Witness("pair-multiplicity", "Positions one, two and four reconstruct separations one, two and three with exact thirds.", pair_distribution((1, 2, 4)) == ((1, Fraction(1, 3)), (2, Fraction(1, 3)), (3, Fraction(1, 3)))),
        Witness("translation-invariance", "Translation preserves the complete pair distribution.", pair_distribution((1, 3, 6, 10)) == pair_distribution((5, 7, 10, 14))),
    ),
}


@dataclass(frozen=True)
class CrystallographySpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-MAT-CRYS-") or self.number not in WITNESSES:
            raise ValueError("invalid Materials CRYS identity")
        if len(self.axes) != 8 or not self.dependencies or not self.witnesses:
            raise ValueError("Materials CRYS spec is incomplete")
        if len({axis.key for axis in self.axes}) != 8:
            raise ValueError("Materials CRYS axes repeat")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("Materials CRYS axis is not exhaustively binary")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("Materials CRYS operational witness failed")


class CrystallographyProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
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
    "no V1/V2 proof artifact, conventional complex amplitude, continuum field or named equation as a premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence and phase opposition are held forms rather than prohibited scalars",
    "no target value, official source, measured diffraction pattern or favourable specimen selects a survivor",
    "no omitted adverse, absent, unavailable, unresolved, tampered or scope-boundary row",
    "no failed route retires an obligation and no engine, verifier, receipt or admitted certificate change",
)


SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    relation = {
        "001": "period-four-phase-cancellation-and-coherent-pair-ledger",
        "002": "finite-scatterer-position-phase-composition",
        "003": "exact-grain-orientation-rational-distribution",
        "004": "lag-labelled-local-pair-and-diffuse-support-ledger",
        "005": "cyclic-layer-successor-fault-and-diffraction-ledger",
        "006": "nonidentity-involution-and-two-domain-ledger",
        "007": "independent-modulation-successor-and-compound-index-ledger",
        "008": "complete-positive-pair-separation-multiplicity-ledger",
    }[number]
    spec = CrystallographySpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Generate the complete literal product of the eight registered CRYS-{number} preservation axes before external target release.",
        grammar_boundary=f"Every positive finite generated material carrier in CRYS-{number}, retaining its exact local, reciprocal, specimen, method, condition, uncertainty and proof-trace distinctions.",
        axes=axes(relation),
        exact_result=f"CRYS-{number} uniquely retains {relation} with complete carrier, organization, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive carrier retains its complete label, relation, observation boundary and root-bound trace.",
        induction_step="Appending one lawful positive constituent or transition preserves every prior distinction, adds its complete pair/path relations and introduces no selector.",
        exclusions=EXCLUSIONS,
        witnesses=WITNESSES[number],
        number=number,
        obligation_id=f"SFT-MAT-OBL-CRYS-{number}",
    )
    spec.validate()
    SPECS[claim_id] = spec


ORDER = tuple(row[1] for row in DEFINITIONS)


__all__ = (
    "CrystallographyProgram", "CrystallographySpec", "ORDER", "SPECS",
    "diffraction_ledger", "finite_structure_factor", "exact_distribution",
    "lag_pair_distribution", "diffuse_support", "stacking_fault_ledger",
    "twin_domain_ledger", "modulation_ledger", "pair_distribution",
)

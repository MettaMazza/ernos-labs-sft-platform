"""Fold-native ANAL-012--022 laws developed as one coordinated family.

The eleven laws share only exact structural primitives.  Each retains its own
eight-decision grammar, unique survivor statement, dependencies and operational
witnesses.  No external spectrum, diffraction pattern, separation trace,
response curve, identity outcome or validation result is imported here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class ExactAnalyticalCoordinate:
    carrier: HeldLabel
    coordinate_kind: HeldLabel
    coordinate: Fraction | EmptyOne
    response_kind: HeldLabel
    response: Fraction | EmptyOne
    side: HeldLabel
    condition: HeldLabel
    position: PositiveCount

    def __post_init__(self) -> None:
        expected = (
            (self.carrier, "analytical-carrier"), (self.coordinate_kind, "analytical-coordinate-kind"),
            (self.response_kind, "analytical-response-kind"), (self.side, "held-side"),
            (self.condition, "analytical-condition"),
        )
        if any(value.family != family for value, family in expected):
            raise InadmissibleExactValue("complete held analytical coordinate identity required")
        if self.coordinate != EMPTY_ONE and (not isinstance(self.coordinate, Fraction) or self.coordinate <= 0):
            raise InadmissibleExactValue("analytical coordinate must be exact positive support or structural absence")
        if self.response != EMPTY_ONE and (not isinstance(self.response, Fraction) or self.response <= 0):
            raise InadmissibleExactValue("analytical response must be exact positive support or structural absence")
        if self.side.label not in {"higher", "lower", "preserving", "alternating", "coincident", "unresolved"}:
            raise InadmissibleExactValue("analytical held side was not generated")
        if self.side.label == "coincident" and self.coordinate != EMPTY_ONE:
            raise InadmissibleExactValue("coincident coordinate requires structural EmptyOne")


def exact_side_relation(source: Fraction, terminal: Fraction):
    if source <= 0 or terminal <= 0:
        raise InadmissibleExactValue("relation endpoints require exact positive support")
    if source == terminal:
        return HeldLabel("held-side", "coincident"), EMPTY_ONE
    return HeldLabel("held-side", "higher" if terminal > source else "lower"), abs(terminal - source)


def complete_vector(rows: tuple[ExactAnalyticalCoordinate, ...]) -> tuple[ExactAnalyticalCoordinate, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("analytical vector must be complete and ordered")
    if len({(row.carrier, row.condition) for row in rows}) != 1:
        raise InadmissibleExactValue("analytical vector crossed its retained carrier/condition boundary")
    keys = {(row.coordinate_kind, row.coordinate, row.response_kind, row.side) for row in rows}
    if len(keys) != len(rows):
        raise InadmissibleExactValue("analytical vector duplicated a coordinate-response identity")
    return rows


def dims(labels):
    return tuple(
        dimension(name, rejected, rejection, survivor, witness)
        for name, rejected, rejection, survivor, witness in labels
    )


COMMON_DEPS = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001",
)

LAW_ROWS = {
    "012": {
        "claim_id": "SFT-CHEM-INFRARED-LINE-INTENSITY-012",
        "title": "Fold infrared line-position and intensity law",
        "statement": "Held vibrational state pairs force exact positive infrared line coordinates and counted responses with complete condition, uncertainty and absent-line custody.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-SPEC-INFRARED-001", "SFT-CHEM-VIBRATIONAL-FREQUENCY-009", "SFT-CHEM-RAMAN-TRANSITION-INTENSITY-009"),
        "labels": (
            ("carrier", "detached-ir-number", "A number does not identify its molecule.", "held-molecule-and-phase", "Molecular identity and phase remain."),
            ("states", "peak-without-vibrational-states", "A peak alone loses both state endpoints.", "held-initial-final-vibrational-states", "Both vibrational states remain."),
            ("coordinate", "signed-floating-wavenumber", "A signed float is not a native coordinate.", "exact-positive-line-coordinate-or-EmptyOne", "Line position is positive exact support or absence."),
            ("response", "arbitrary-absorbance-height", "An arbitrary height loses counted comparison support.", "exact-counted-transmission-response-or-EmptyOne", "Response is an exact count ratio or absence."),
            ("selection", "imported-ir-selection-rule", "A named convention cannot replace the derived state distinction.", "held-dipole-state-transformation", "The held transformation remains."),
            ("condition", "unconditioned-spectrum", "Phase, temperature and instrument boundary affect observation.", "held-complete-measurement-condition", "Complete conditions remain."),
            ("custody", "selected-strong-bands", "Peak selection erases weak and adverse rows.", "complete-line-error-bound-absence-custody", "Every row and status remains."),
            ("extension", "refitted-added-spectrum", "Refitting can change prior evidence.", "successor-appends-without-changing-prior-lines", "Extension is append-only."),
        ),
        "result": "held-molecule-and-phase__held-initial-final-vibrational-states__exact-positive-line-coordinate-or-EmptyOne__exact-counted-transmission-response-or-EmptyOne__held-dipole-state-transformation__held-complete-measurement-condition__complete-line-error-bound-absence-custody__successor-appends-without-changing-prior-lines",
    },
    "013": {
        "claim_id": "SFT-CHEM-UVVISIBLE-LINE-INTENSITY-013",
        "title": "Fold UV-visible line-position and intensity law",
        "statement": "Held electronic state pairs force exact positive absorption coordinates and counted response support with complete solvent, condition and uncertainty custody.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-SPEC-UVVIS-001", "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009", "SFT-CHEM-FLUORESCENCE-YIELD-LIFETIME-010"),
        "labels": (
            ("carrier", "detached-uvvis-number", "A number does not identify its molecule.", "held-molecule-and-electronic-carrier", "Molecule and electronic carrier remain."),
            ("states", "band-without-electronic-states", "A band alone loses its state endpoints.", "held-initial-final-electronic-states", "Both electronic states remain."),
            ("coordinate", "signed-floating-wavelength", "A signed float is not native support.", "exact-positive-absorption-coordinate-or-EmptyOne", "Absorption coordinate is exact or absent."),
            ("response", "fitted-extinction-scalar", "A fitted scalar can hide source counts.", "exact-counted-absorption-response-or-EmptyOne", "Response retains exact comparison support."),
            ("partition", "bright-transition-only", "Selecting bright transitions erases the remaining support.", "complete-electronic-transition-support", "All transitions remain."),
            ("condition", "solvent-free-universal-band", "Solvent and condition alter observation.", "held-solvent-phase-temperature-condition", "All conditions remain."),
            ("custody", "selected-favorable-bands", "Selection erases shoulders, errors and absent rows.", "complete-band-error-bound-absence-custody", "Every status remains."),
            ("extension", "renormalized-added-band", "Renormalization changes prior responses.", "successor-retains-and-appends-complete-bands", "Extension preserves prior bands."),
        ),
        "result": "held-molecule-and-electronic-carrier__held-initial-final-electronic-states__exact-positive-absorption-coordinate-or-EmptyOne__exact-counted-absorption-response-or-EmptyOne__complete-electronic-transition-support__held-solvent-phase-temperature-condition__complete-band-error-bound-absence-custody__successor-retains-and-appends-complete-bands",
    },
    "014": {
        "claim_id": "SFT-CHEM-MASS-ISOTOPE-FRAGMENT-VECTOR-014",
        "title": "Fold mass, isotope and fragmentation spectrum law",
        "statement": "Held molecular and ionic carriers force a complete exact mass-to-charge, isotope and fragmentation event vector without weak-peak selection.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-SPEC-MASS-001", "SFT-CHEM-ELEM-ISOTOPE-001", "SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012"),
        "labels": (
            ("carrier", "mass-peaks-without-molecule", "Peaks alone lose molecular identity.", "held-molecular-parent-and-ion-carriers", "Parent and ion carriers remain."),
            ("composition", "nominal-mass-only", "Nominal mass loses isotope composition.", "held-isotope-and-charge-composition", "Isotope and charge remain."),
            ("coordinate", "floating-mass-to-charge", "A float is not native exact support.", "exact-positive-mass-charge-ratio", "Mass/charge is exact positive support."),
            ("fragmentation", "peak-without-fragment-path", "A peak alone loses its parent path.", "held-parent-fragment-transition-path", "Fragment paths remain."),
            ("response", "normalized-major-peak-only", "Major-only normalization erases weak events.", "exact-event-over-reference-event-ratio", "Response is an exact event ratio."),
            ("condition", "unconditioned-ionization", "Ionization and instrument boundary affect fragmentation.", "held-ionization-and-acquisition-condition", "Complete conditions remain."),
            ("custody", "selected-diagnostic-peaks", "Selection erases weak, isotope and unresolved rows.", "complete-peak-isotope-error-absence-custody", "Every peak and status remains."),
            ("extension", "refitted-added-fragment", "Refitting changes prior event ratios.", "successor-retains-and-appends-complete-fragments", "Extension preserves prior fragments."),
        ),
        "result": "held-molecular-parent-and-ion-carriers__held-isotope-and-charge-composition__exact-positive-mass-charge-ratio__held-parent-fragment-transition-path__exact-event-over-reference-event-ratio__held-ionization-and-acquisition-condition__complete-peak-isotope-error-absence-custody__successor-retains-and-appends-complete-fragments",
    },
    "015": {
        "claim_id": "SFT-CHEM-ROTATIONAL-SPECTRUM-LINE-015",
        "title": "Fold rotational spectrum line law",
        "statement": "Held geometry, axis, isotopologue and rotational-state pairs force a complete exact frequency/intensity/error line vector.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-SPEC-ROT-VIB-001", "SFT-CHEM-ROTATIONAL-CONSTANT-010", "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005"),
        "labels": (
            ("carrier", "detached-microwave-line", "A line does not identify its molecule.", "held-molecule-geometry-isotopologue", "Molecule, geometry and isotopologue remain."),
            ("states", "line-without-rotational-states", "A line alone loses quantum-state endpoints.", "held-initial-final-rotational-states", "Both rotational states remain."),
            ("axis", "axis-free-rotational-number", "Geometry-dependent rotation needs a held axis.", "held-molecular-axis-and-symmetry", "Axis and symmetry remain."),
            ("coordinate", "floating-frequency", "A float is not native exact support.", "exact-positive-frequency-or-EmptyOne", "Frequency is exact or absent."),
            ("response", "arbitrary-line-strength", "An arbitrary strength loses event support.", "exact-positive-line-response-or-EmptyOne", "Response is exact or absent."),
            ("condition", "unconditioned-catalog-line", "Temperature and state-energy boundary matter.", "held-energy-temperature-unit-condition", "All conditions remain."),
            ("custody", "selected-detected-lines", "Selection erases errors and predicted/unresolved rows.", "complete-frequency-error-intensity-state-custody", "Every catalog row remains."),
            ("extension", "refitted-catalog-extension", "Refitting can change earlier lines.", "successor-appends-without-changing-prior-lines", "Extension is append-only."),
        ),
        "result": "held-molecule-geometry-isotopologue__held-initial-final-rotational-states__held-molecular-axis-and-symmetry__exact-positive-frequency-or-EmptyOne__exact-positive-line-response-or-EmptyOne__held-energy-temperature-unit-condition__complete-frequency-error-intensity-state-custody__successor-appends-without-changing-prior-lines",
    },
    "016": {
        "claim_id": "SFT-CHEM-XRAY-DIFFRACTION-STRUCTURE-016",
        "title": "Fold X-ray diffraction chemical-structure law",
        "statement": "A held crystal carrier and reciprocal support force exact diffraction coordinates, responses and a chemistry-owned structure correspondence.",
        "dependencies": COMMON_DEPS + ("SFT-PHYS-WAVE-DIFFRACTION-001", "SFT-MAT-CRYST-UNIT-CELL-001", "SFT-MAT-CRYST-RECIPROCAL-001"),
        "labels": (
            ("carrier", "pattern-without-crystal", "A pattern alone loses crystal identity.", "held-crystal-phase-and-composition", "Crystal phase and composition remain."),
            ("probe", "chemistry-owned-xray-probe", "Probe production belongs to Physics.", "explicit-physics-xray-scattering-handoff", "Physics handoff remains explicit."),
            ("support", "line-list-without-reciprocal-support", "Lines alone lose the generated lattice relation.", "held-direct-and-reciprocal-support", "Both supports remain."),
            ("coordinate", "floating-two-theta", "A float is not native exact support.", "exact-positive-spacing-or-held-angle", "Spacing/angle relation is exact and held."),
            ("response", "arbitrary-diffraction-intensity", "An arbitrary height loses comparison support.", "exact-counted-relative-intensity-or-EmptyOne", "Intensity is exact or absent."),
            ("structure", "database-structure-label-only", "A label cannot establish structure correspondence.", "complete-cell-symmetry-site-correspondence", "Cell, symmetry and sites remain."),
            ("custody", "selected-major-reflections", "Selection erases weak and adverse reflections.", "complete-reflection-error-condition-custody", "Every reflection/status remains."),
            ("extension", "refined-added-pattern", "Refinement can change prior evidence.", "successor-retains-prior-reflections-and-structure", "Extension preserves prior evidence."),
        ),
        "result": "held-crystal-phase-and-composition__explicit-physics-xray-scattering-handoff__held-direct-and-reciprocal-support__exact-positive-spacing-or-held-angle__exact-counted-relative-intensity-or-EmptyOne__complete-cell-symmetry-site-correspondence__complete-reflection-error-condition-custody__successor-retains-prior-reflections-and-structure",
    },
    "017": {
        "claim_id": "SFT-CHEM-ELECTRON-NEUTRON-DIFFRACTION-017",
        "title": "Fold electron/neutron diffraction correspondence law",
        "statement": "Held probe identity and one held chemical structure force separately retained electron and neutron diffraction correspondences without probe conflation.",
        "dependencies": COMMON_DEPS + ("SFT-PHYS-MATTER-SCATTERING-001", "SFT-MAT-CRYST-RECIPROCAL-001", "SFT-CHEM-XRAY-DIFFRACTION-STRUCTURE-016"),
        "labels": (
            ("carrier", "diffraction-without-material", "A pattern alone loses material identity.", "held-material-phase-and-composition", "Material identity remains."),
            ("probe", "probe-agnostic-pattern", "Electron and neutron interactions cannot be conflated.", "held-electron-or-neutron-probe", "Probe identity remains."),
            ("handoff", "chemistry-invents-probe-law", "Probe scattering belongs to Physics.", "explicit-physics-scattering-handoff", "Physics dependency remains."),
            ("support", "peaks-without-reciprocal-state", "Peaks alone lose structural support.", "held-reciprocal-and-site-support", "Reciprocal and site support remain."),
            ("coordinate", "floating-diffraction-coordinate", "A float is not native exact support.", "exact-positive-diffraction-coordinate-or-EmptyOne", "Coordinate is exact or absent."),
            ("correspondence", "same-response-for-both-probes", "Different probes retain different response relations.", "probe-specific-structure-response-correspondence", "Probe-specific correspondence remains."),
            ("custody", "selected-agreeing-reflections", "Agreement selection erases adverse rows.", "complete-probe-reflection-error-custody", "Every row remains."),
            ("extension", "refitted-mixed-probe-pattern", "Refitting can change prior evidence.", "successor-appends-probe-records-without-conflation", "Probe records append separately."),
        ),
        "result": "held-material-phase-and-composition__held-electron-or-neutron-probe__explicit-physics-scattering-handoff__held-reciprocal-and-site-support__exact-positive-diffraction-coordinate-or-EmptyOne__probe-specific-structure-response-correspondence__complete-probe-reflection-error-custody__successor-appends-probe-records-without-conflation",
    },
    "018": {
        "claim_id": "SFT-CHEM-CHROMATOGRAPHIC-RETENTION-RESOLUTION-018",
        "title": "Fold chromatographic retention and resolution law",
        "statement": "Held analyte, matrix and mobile/stationary phases force complete exact retention, peak and pairwise resolution custody at fixed conditions.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-ANALYTICAL-SAMPLE-001", "SFT-CHEM-ANALYTICAL-SELECTIVITY-INTERFERENCE-005", "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019"),
        "labels": (
            ("analyte", "retention-number-without-analyte", "A time/index alone loses analyte identity.", "held-analyte-and-matrix", "Analyte and matrix remain."),
            ("phases", "phase-free-retention", "Retention depends on both phase identities.", "held-mobile-and-stationary-phases", "Both phases remain."),
            ("coordinate", "floating-retention-value", "A float is not native exact support.", "exact-positive-retention-coordinate-or-EmptyOne", "Retention is exact or absent."),
            ("peak", "apex-only-peak", "An apex alone loses complete peak support.", "complete-positive-peak-support", "Complete peak support remains."),
            ("resolution", "named-separated-or-not", "A category hides pairwise distances and widths.", "exact-pairwise-resolution-relation", "Resolution is exact and pairwise."),
            ("condition", "unconditioned-retention-index", "Temperature, flow and phase conditions matter.", "held-temperature-flow-column-condition", "All conditions remain."),
            ("custody", "selected-resolved-analytes", "Selection erases coelution and unresolved rows.", "complete-coelution-error-absence-custody", "Every status remains."),
            ("extension", "refitted-added-analyte", "Refitting can change earlier peaks.", "successor-retains-and-appends-complete-peaks", "Extension preserves prior peaks."),
        ),
        "result": "held-analyte-and-matrix__held-mobile-and-stationary-phases__exact-positive-retention-coordinate-or-EmptyOne__complete-positive-peak-support__exact-pairwise-resolution-relation__held-temperature-flow-column-condition__complete-coelution-error-absence-custody__successor-retains-and-appends-complete-peaks",
    },
    "019": {
        "claim_id": "SFT-CHEM-ELECTROPHORETIC-MOBILITY-SEPARATION-019",
        "title": "Fold electrophoretic mobility and separation law",
        "statement": "Held species, charge orientation and medium force exact positive mobility magnitude, trajectory and separation custody.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008", "SFT-CHEM-ANALYTICAL-SELECTIVITY-INTERFERENCE-005"),
        "labels": (
            ("species", "mobility-without-species", "A mobility value loses species identity.", "held-species-and-particle-identity", "Species identity remains."),
            ("charge", "signed-negative-mobility", "A signed number conflates orientation and magnitude.", "held-charge-motion-side", "Orientation is held separately."),
            ("medium", "medium-free-mobility", "Medium and pH affect motion.", "held-medium-pH-temperature-condition", "Complete medium conditions remain."),
            ("field", "unrecorded-field", "Motion needs a retained applied-field boundary.", "held-field-direction-and-resource", "Field direction/resource remain."),
            ("mobility", "floating-mobility", "A float is not native exact support.", "exact-positive-mobility-magnitude-or-EmptyOne", "Magnitude is exact or absent."),
            ("separation", "named-separated-or-not", "A category loses trajectories and distances.", "exact-trajectory-and-pairwise-separation", "Trajectory/separation remain exact."),
            ("custody", "selected-mobile-fraction", "Selection erases immobile and adverse rows.", "complete-mobility-error-absence-custody", "Every status remains."),
            ("extension", "refitted-added-species", "Refitting changes earlier mobilities.", "successor-retains-and-appends-species", "Extension preserves prior species."),
        ),
        "result": "held-species-and-particle-identity__held-charge-motion-side__held-medium-pH-temperature-condition__held-field-direction-and-resource__exact-positive-mobility-magnitude-or-EmptyOne__exact-trajectory-and-pairwise-separation__complete-mobility-error-absence-custody__successor-retains-and-appends-species",
    },
    "020": {
        "claim_id": "SFT-CHEM-ELECTROANALYTICAL-RESPONSE-020",
        "title": "Fold electroanalytical response law",
        "statement": "Held analyte/electrode/cell identities and an ordered applied-potential path force a complete exact current-response trace with reaction and adverse custody.",
        "dependencies": COMMON_DEPS + ("SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002", "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003", "SFT-CHEM-ELECTRODE-REACTION-RATE-009"),
        "labels": (
            ("system", "current-curve-without-system", "A curve alone loses analyte and cell identity.", "held-analyte-electrode-cell-identity", "Complete system identity remains."),
            ("path", "unordered-potential-points", "An unordered set loses scan causality.", "held-ordered-applied-potential-path", "Potential order remains."),
            ("orientation", "signed-current-as-native-number", "A signed number conflates direction and magnitude.", "held-oxidation-reduction-current-side", "Current direction is held."),
            ("response", "floating-current", "A float is not native exact support.", "exact-positive-current-magnitude-or-EmptyOne", "Current magnitude is exact or absent."),
            ("reaction", "peak-without-electrode-reaction", "A peak alone loses chemical transition identity.", "held-electrode-reaction-correspondence", "Reaction correspondence remains."),
            ("condition", "scan-rate-free-curve", "Scan rate, medium and reference affect response.", "held-scan-medium-reference-condition", "All conditions remain."),
            ("custody", "selected-peak-values", "Peak selection erases baseline and adverse trace rows.", "complete-trace-error-background-custody", "Every trace row remains."),
            ("extension", "refitted-longer-scan", "Refitting changes prior trace points.", "successor-appends-path-without-changing-prior-response", "Extension is append-only."),
        ),
        "result": "held-analyte-electrode-cell-identity__held-ordered-applied-potential-path__held-oxidation-reduction-current-side__exact-positive-current-magnitude-or-EmptyOne__held-electrode-reaction-correspondence__held-scan-medium-reference-condition__complete-trace-error-background-custody__successor-appends-path-without-changing-prior-response",
    },
    "021": {
        "claim_id": "SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021",
        "title": "Fold multimodal molecular identity reconstruction law",
        "statement": "Complete orthogonal analytical records force the unique common molecular carrier or halt without identity inflation.",
        "dependencies": COMMON_DEPS + tuple(f"SFT-CHEM-{name}" for name in (
            "NMR-CHEMICAL-SHIFT-006", "RAMAN-TRANSITION-INTENSITY-009", "INFRARED-LINE-INTENSITY-012",
            "UVVISIBLE-LINE-INTENSITY-013", "MASS-ISOTOPE-FRAGMENT-VECTOR-014", "ROTATIONAL-SPECTRUM-LINE-015",
        )),
        "labels": (
            ("carrier", "independent-modality-identities", "Separate names do not establish one carrier.", "one-held-molecular-carrier", "One carrier is required."),
            ("records", "selected-diagnostic-modalities", "Selection can manufacture identity.", "complete-orthogonal-record-family", "Every registered modality remains."),
            ("candidates", "database-first-answer", "A first answer is not exhaustive.", "complete-generated-carrier-candidate-set", "All candidates are generated."),
            ("comparison", "fitted-similarity-score", "A fitted score imports a threshold.", "exact-record-candidate-incidence", "Incidence is exact."),
            ("intersection", "majority-vote-identity", "A vote can ignore contradiction.", "exact-complete-support-intersection", "All supports intersect exactly."),
            ("uniqueness", "best-ranked-candidate", "Ranking does not force uniqueness.", "one-unique-common-carrier-or-halt", "Only one carrier survives or execution halts."),
            ("adversity", "discarded-conflicting-modality", "Discarding conflict invalidates reconstruction.", "complete-conflict-absence-unresolved-custody", "Conflicts and absences remain."),
            ("extension", "refitted-new-modality", "Refitting can change earlier evidence.", "successor-intersects-without-changing-prior-records", "New records only restrict support."),
        ),
        "result": "one-held-molecular-carrier__complete-orthogonal-record-family__complete-generated-carrier-candidate-set__exact-record-candidate-incidence__exact-complete-support-intersection__one-unique-common-carrier-or-halt__complete-conflict-absence-unresolved-custody__successor-intersects-without-changing-prior-records",
    },
    "022": {
        "claim_id": "SFT-CHEM-ANALYTICAL-PERFORMANCE-BUDGET-022",
        "title": "Fold complete analytical performance and uncertainty budget",
        "statement": "One analytical result is admissible only with jointly retained traceability, trueness, precision, sensitivity, selectivity, detection/quantification and uncertainty custody.",
        "dependencies": COMMON_DEPS + (
            "SFT-CHEM-ANALYTICAL-ACCURACY-TRUENESS-001", "SFT-CHEM-ANALYTICAL-PRECISION-REPEATABILITY-002",
            "SFT-CHEM-ANALYTICAL-SENSITIVITY-003", "SFT-CHEM-ANALYTICAL-DETECTION-QUANTIFICATION-004",
            "SFT-CHEM-ANALYTICAL-SELECTIVITY-INTERFERENCE-005", "SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021",
        ),
        "labels": (
            ("result", "detached-final-number", "A final number loses its analytical carrier.", "held-result-sample-measurand-method", "Complete result identity remains."),
            ("traceability", "untraced-reference", "An untraced result has no comparison chain.", "complete-reference-traceability-chain", "Traceability remains."),
            ("trueness", "precision-as-trueness", "Repeatability cannot establish reference agreement.", "exact-trueness-relation-or-EmptyOne", "Trueness remains separate."),
            ("precision", "single-observation-precision", "One observation cannot establish repeatability.", "complete-replicate-precision-relation", "Replicate structure remains."),
            ("response", "sensitivity-without-domain", "A slope without support/domain is incomplete.", "exact-sensitivity-selectivity-domain", "Response and interference domain remain."),
            ("decision", "single-detection-threshold", "Detection cannot substitute for quantification.", "separate-detection-quantification-custody", "Decision classes remain separate."),
            ("uncertainty", "single-combined-error-number", "One scalar hides components and alternatives.", "complete-component-dependency-uncertainty-budget", "Every uncertainty component remains."),
            ("extension", "replaced-validation-study", "Replacement loses prior evidence.", "successor-retains-and-appends-validation-records", "Validation evidence appends."),
        ),
        "result": "held-result-sample-measurand-method__complete-reference-traceability-chain__exact-trueness-relation-or-EmptyOne__complete-replicate-precision-relation__exact-sensitivity-selectivity-domain__separate-detection-quantification-custody__complete-component-dependency-uncertainty-budget__successor-retains-and-appends-validation-records",
    },
}


def _vector_witnesses(key: str):
    carrier = HeldLabel("analytical-carrier", f"carrier-{key}")
    condition = HeldLabel("analytical-condition", f"condition-{key}")
    side, coordinate = exact_side_relation(Fraction(3), Fraction(5))
    rows = complete_vector((
        ExactAnalyticalCoordinate(carrier, HeldLabel("analytical-coordinate-kind", "coordinate-a"), coordinate, HeldLabel("analytical-response-kind", "response-a"), Fraction(2, 3), side, condition, PositiveCount(1)),
        ExactAnalyticalCoordinate(carrier, HeldLabel("analytical-coordinate-kind", "coordinate-b"), Fraction(7, 2), HeldLabel("analytical-response-kind", "response-b"), EMPTY_ONE, HeldLabel("held-side", "unresolved"), condition, PositiveCount(2)),
    ))
    return rows


for key, law in LAW_ROWS.items():
    law["dimensions"] = dims(law.pop("labels"))
    if key == "021":
        modalities = ({"carrier-a", "carrier-b"}, {"carrier-a", "carrier-c"}, {"carrier-a"})
        intersection = set.intersection(*(set(item) for item in modalities))
        booleans = (len(intersection) == 1, len(modalities) == 3, len(set.union(*(set(item) for item in modalities))) == 3, all(isinstance(item, set) for item in modalities), intersection == {"carrier-a"}, next(iter(intersection)) == "carrier-a", "carrier-b" not in intersection, set.intersection(intersection, {"carrier-a", "carrier-d"}) == {"carrier-a"})
    elif key == "022":
        budget = {name: Fraction(index + 1, index + 2) for index, name in enumerate(("traceability", "trueness", "precision", "sensitivity-selectivity", "detection-quantification", "uncertainty"))}
        booleans = (len(budget) == 6, "traceability" in budget, budget["trueness"] == Fraction(2, 3), budget["precision"] == Fraction(3, 4), "sensitivity-selectivity" in budget, "detection-quantification" in budget, all(value > 0 for value in budget.values()), dict(budget) == budget)
    else:
        rows = _vector_witnesses(key)
        booleans = (all(row.carrier == rows[0].carrier for row in rows), rows[0].coordinate != EMPTY_ONE, rows[0].response == Fraction(2, 3), rows[0].side.label == "higher", rows[1].response == EMPTY_ONE, all(row.condition == rows[0].condition for row in rows), len(rows) == 2, complete_vector(rows) == rows)
    law["operational_witnesses"] = tuple(
        (dimension_row.key, next(choice.reason for choice in dimension_row.choices if choice.admitted), passed)
        for dimension_row, passed in zip(law["dimensions"], booleans)
    )
    if len(law["dimensions"]) != 8 or len(law["operational_witnesses"]) != 8 or not all(item[2] for item in law["operational_witnesses"]):
        raise InadmissibleExactValue(f"ANAL-{key} native witness family failed")


__all__ = ("ExactAnalyticalCoordinate", "LAW_ROWS", "complete_vector", "exact_side_relation")

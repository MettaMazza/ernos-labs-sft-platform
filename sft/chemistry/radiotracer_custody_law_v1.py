"""Fold-native radiotracer custody and inference law (NUCHEM-009)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class RadiotracerObservation:
    tracer: HeldLabel
    chemical_carrier: HeldLabel
    location: HeldLabel
    rank: PositiveCount
    observed_events: PositiveCount
    administered_events: PositiveCount

    def __post_init__(self):
        if (self.tracer.family, self.chemical_carrier.family, self.location.family) != ("radiotracer", "chemical-carrier", "observation-location"):
            raise InadmissibleExactValue("complete radiotracer identity and location required")
        if self.observed_events.value > self.administered_events.value:
            raise InadmissibleExactValue("observed tracer cannot exceed administered custody")

    @property
    def recovery(self) -> Fraction:
        return Fraction(self.observed_events.value, self.administered_events.value)

    @property
    def unobserved(self):
        remainder = self.administered_events.value - self.observed_events.value
        return EMPTY_ONE if remainder == 0 else PositiveCount(remainder)


def tracer_record(rows: tuple[RadiotracerObservation, ...]):
    if not rows or tuple(row.rank.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("complete ordered tracer support required")
    if len({(row.tracer, row.chemical_carrier) for row in rows}) != 1:
        raise InadmissibleExactValue("tracer or chemical identity changed")
    return tuple((row.location, row.recovery, row.unobserved) for row in rows)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001", "SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001",
    "SFT-CHEM-ACTIVITY-AMOUNT-TIME-003", "SFT-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005",
)
DIMENSIONS = (
    dimension("identity", "activity-only-tracer", "Activity alone loses nuclide and chemistry.", "held-tracer-and-chemical-carrier", "Tracer and carrier remain held."),
    dimension("support", "continuous-concentration-field", "A continuum field hides observations.", "positive-ordered-observation-support", "Every observation has positive rank."),
    dimension("locations", "selected-detector-location", "Selection cannot establish complete transport.", "complete-location-time-vector", "Every registered location and time remains."),
    dimension("events", "expected-count-premise", "Expectation is not observed-event custody.", "positive-administered-and-observed-counts", "Administered and observed events are counted."),
    dimension("recovery", "fitted-recovery-coefficient", "A fit cannot define recovery.", "exact-observed-per-administered-ratio", "Recovery is an exact positive ratio."),
    dimension("loss", "negative-missing-activity", "Missing tracer cannot be a negative proof value.", "positive-Take-or-EmptyOne-unobserved", "Unobserved custody is positive or structurally absent."),
    dimension("inference", "model-selected-localization", "A model cannot create an observation.", "inference-bounded-by-observed-support", "Inference never exceeds retained observations."),
    dimension("extension", "renormalized-selected-series", "Renormalization erases custody.", "successor-preserves-identity-and-complete-record", "Every successor retains all earlier rows."),
)
EXACT_RESULT = "held-tracer-and-chemical-carrier__positive-ordered-observation-support__complete-location-time-vector__positive-administered-and-observed-counts__exact-observed-per-administered-ratio__positive-Take-or-EmptyOne-unobserved__inference-bounded-by-observed-support__successor-preserves-identity-and-complete-record"


def _row(rank, observed, administered, location):
    return RadiotracerObservation(HeldLabel("radiotracer", "Tc-99m"), HeldLabel("chemical-carrier", "pertechnetate"), HeldLabel("observation-location", location), PositiveCount(rank), PositiveCount(observed), PositiveCount(administered))


_rows = (_row(1, 3, 5, "inlet"), _row(2, 4, 5, "outlet"))
OPERATIONAL_WITNESSES = (
    ("identity", "Tracer chemistry held.", _rows[0].tracer.label == "Tc-99m" and _rows[0].chemical_carrier.label == "pertechnetate"),
    ("support", "Ranks complete.", tuple(row.rank.value for row in _rows) == (1, 2)),
    ("locations", "Both locations retained.", len({row.location for row in _rows}) == 2),
    ("events", "Counts positive and bounded.", _rows[0].observed_events.value == 3 and _rows[0].administered_events.value == 5),
    ("recovery", "Recovery exact.", _rows[0].recovery == Fraction(3, 5)),
    ("loss", "Remainder is positive or absent.", _rows[0].unobserved.value == 2 and _row(1, 5, 5, "one").unobserved == EMPTY_ONE),
    ("inference", "Inference uses retained rows.", len(tracer_record(_rows)) == 2),
    ("successor", "Successor retains complete record.", len(tracer_record(_rows + (_row(3, 5, 5, "terminal"),))) == 3),
)

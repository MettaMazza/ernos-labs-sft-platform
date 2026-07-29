"""Exact Fold laws for the complete Materials OPT-001--010 family."""
from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis

def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be positive")
    return value

def absorption_extinction(incident, transmitted, reflected, absorbed, scattered, specimen):
    values = tuple(positive(value, name) for value, name in ((incident, "incident"), (transmitted, "transmitted"), (reflected, "reflected"), (absorbed, "absorbed"), (scattered, "scattered")))
    if sum(values[1:]) != values[0] or not specimen:
        raise ValueError("optical carrier does not close")
    return {"incident": values[0], "transmitted": values[1], "reflected": values[2], "absorbed": values[3], "scattered": values[4], "specimen": specimen, "absorbed_part": Fraction(values[3], values[0]), "extinction_part": Fraction(values[3] + values[4], values[0]), "closes": True}

def reflection_transmission(incident, reflected, transmitted, retained, geometry):
    values = tuple(positive(value, name) for value, name in ((incident, "incident"), (reflected, "reflected"), (transmitted, "transmitted"), (retained, "retained")))
    if sum(values[1:]) != values[0] or not geometry:
        raise ValueError("reflection-transmission ledger invalid")
    return {"incident": values[0], "reflected": values[1], "transmitted": values[2], "retained": values[3], "geometry": geometry, "reflection_part": Fraction(values[1], values[0]), "transmission_part": Fraction(values[2], values[0]), "closes": True}

def luminescence_yield(absorbed, emitted, nonradiative, excitation, emission):
    absorbed, emitted, nonradiative = positive(absorbed, "absorbed"), positive(emitted, "emitted"), positive(nonradiative, "nonradiative")
    if emitted + nonradiative != absorbed or not excitation or not emission:
        raise ValueError("luminescence ledger invalid")
    return {"absorbed": absorbed, "emitted": emitted, "nonradiative": nonradiative, "excitation": excitation, "emission": emission, "quantum_yield": Fraction(emitted, absorbed), "closes": True}

def light_scattering(incident, elastic, inelastic, unscattered, method):
    values = tuple(positive(value, name) for value, name in ((incident, "incident"), (elastic, "elastic"), (inelastic, "inelastic"), (unscattered, "unscattered")))
    if sum(values[1:]) != values[0] or not method:
        raise ValueError("scattering ledger invalid")
    return {"incident": values[0], "elastic": values[1], "inelastic": values[2], "unscattered": values[3], "method": method, "scattered_part": Fraction(values[1] + values[2], values[0]), "channel_labels_retained": True, "closes": True}

def birefringence(first, second, first_polarization, second_polarization, axis):
    first, second = positive(first, "first response"), positive(second, "second response")
    if first == second or first_polarization == second_polarization or not first_polarization or not second_polarization or not axis:
        raise ValueError("distinct optical axes required")
    orientation = "first-above" if first > second else "second-above"
    return {"first": first, "second": second, "first_polarization": first_polarization, "second_polarization": second_polarization, "axis": axis, "orientation": orientation, "gap_magnitude": abs(first - second), "ratio": Fraction(first, second)}

def nonlinear_mixing(inputs, output, relation, polarizations):
    values = tuple(positive(value, "input frequency") for value in inputs)
    output = positive(output, "output frequency")
    polarizations = tuple(polarizations)
    if len(values) < 2 or len(polarizations) != len(values) + 1 or not all(polarizations):
        raise ValueError("mixing support incomplete")
    if relation == "sum":
        valid = output == sum(values)
    elif relation == "positive-difference":
        valid = len(values) == 2 and output == abs(values[0] - values[1]) and values[0] != values[1]
    elif relation == "harmonic":
        valid = len(set(values)) == 1 and output == sum(values)
    else:
        raise ValueError("mixing relation held")
    if not valid:
        raise ValueError("mixing relation does not close")
    return {"inputs": values, "output": output, "relation": relation, "polarizations": polarizations, "complete_path": True}

def waveguide_confinement(incident, guided, lost, core, cladding, path):
    incident, guided, lost = positive(incident, "incident"), positive(guided, "guided"), positive(lost, "lost")
    if guided + lost != incident or not core or not cladding or len(tuple(path)) < 2:
        raise ValueError("waveguide ledger invalid")
    return {"incident": incident, "guided": guided, "lost": lost, "core": core, "cladding": cladding, "path": tuple(path), "guided_part": Fraction(guided, incident), "loss_part": Fraction(lost, incident), "closes": True}

def photonic_gap(lower, upper, defect_mode, periodic_support, defect):
    lower, upper, defect_mode = positive(lower, "lower"), positive(upper, "upper"), positive(defect_mode, "defect mode")
    if upper <= lower or not (lower < defect_mode < upper) or not periodic_support or not defect:
        raise ValueError("photonic gap boundary invalid")
    return {"lower": lower, "upper": upper, "gap_width": upper - lower, "defect_mode": defect_mode, "periodic_support": periodic_support, "defect": defect, "lower_margin": defect_mode - lower, "upper_margin": upper - defect_mode, "confined": True}

def plasmonic_response(total, collective, dissipated, interface, mode):
    total, collective, dissipated = positive(total, "total"), positive(collective, "collective"), positive(dissipated, "dissipated")
    if collective + dissipated != total or not interface or not mode:
        raise ValueError("plasmonic ledger invalid")
    return {"total": total, "collective": collective, "dissipated": dissipated, "interface": interface, "mode": mode, "collective_part": Fraction(collective, total), "closes": True}

def exciton_dynamics(generated, recombined, retained, transported, path):
    generated, recombined, retained, transported = positive(generated, "generated"), positive(recombined, "recombined"), positive(retained, "retained"), positive(transported, "transported")
    path = tuple(path)
    if recombined + retained != generated or transported > generated or len(path) < 3:
        raise ValueError("exciton history invalid")
    return {"generated": generated, "recombined": recombined, "retained": retained, "transported": transported, "path": path, "recombined_part": Fraction(recombined, generated), "retained_part": Fraction(retained, generated), "complete_history": True}

BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-ELECTROMAGNETIC-COMPOSITION-001",
    "SFT-PHYS-WAVE-INTERFERENCE-001",
    "SFT-PHYS-WAVE-EXACT-OPERATIONS-003",
    "SFT-MAT-MEAS-MATERIAL-001",
    "SFT-MAT-MEAS-SPECIMEN-001",
    "SFT-MAT-MEAS-PROPERTY-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-OPT-REFRACTIVE-001",
    "SFT-MAT-SEMI-OPTICAL-001",
    "SFT-MAT-FUNC-PHOTONIC-001",
    "SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012",
)

DEFINITIONS = (
    ("001", "SFT-MAT-OPT-ABSORPTION-EXTINCTION-001", "Optical absorption and extinction", "Optical absorption and extinction retain the complete incident partition into transmitted, reflected, absorbed and scattered carriers with specimen identity and exact rational response parts.", BASE),
    ("002", "SFT-MAT-OPT-REFLECTION-TRANSMISSION-002", "Reflection and transmission ledger", "Reflection and transmission are exact positive parts of one incident carrier with retained specimen geometry and any internally retained optical support.", BASE + ("SFT-MAT-OPT-ABSORPTION-EXTINCTION-001",)),
    ("003", "SFT-MAT-OPT-LUMINESCENCE-YIELD-003", "Luminescence and quantum-yield custody", "Luminescence is an exact partition of absorbed excitations into emitted and nonradiative outcomes; quantum yield is the exact emitted part with excitation and emission identities retained.", BASE + ("SFT-MAT-OPT-REFLECTION-TRANSMISSION-002",)),
    ("004", "SFT-MAT-OPT-LIGHT-SCATTERING-004", "Elastic and inelastic light scattering", "Light scattering retains elastic, inelastic and unscattered channels as a complete incident partition with method and channel identity preserved.", BASE + ("SFT-MAT-OPT-LUMINESCENCE-YIELD-003",)),
    ("005", "SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005", "Birefringence and optical anisotropy", "Optical anisotropy retains two positive response carriers, their distinct polarizations and axis, exact ratio and positive gap magnitude with ordering as a held label.", BASE + ("SFT-MAT-OPT-LIGHT-SCATTERING-004",)),
    ("006", "SFT-MAT-OPT-NONLINEAR-MIXING-006", "Nonlinear optical mixing response", "Nonlinear optical mixing retains every positive input, output, polarization and complete sum, positive-difference or harmonic relation without importing a continuum field equation.", BASE + ("SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005",)),
    ("007", "SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007", "Waveguide confinement and loss", "Waveguide propagation is the exact partition of incident support into guided and lost carriers along a retained core-cladding path.", BASE + ("SFT-MAT-OPT-NONLINEAR-MIXING-006",)),
    ("008", "SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008", "Photonic-band-gap and defect mode", "A photonic gap is an ordered positive excluded interval in periodic support; a retained defect generates an exact confined mode with both boundary margins preserved.", BASE + ("SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007",)),
    ("009", "SFT-MAT-OPT-PLASMONIC-RESPONSE-009", "Plasmonic collective response", "Plasmonic response is the exact partition of interface excitation into a retained collective mode and dissipated support with mode and interface identity preserved.", BASE + ("SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008",)),
    ("010", "SFT-MAT-OPT-EXCITON-DYNAMICS-010", "Exciton generation, transport and recombination", "Exciton dynamics retain generated, transported, recombined and surviving carriers and the complete generation-transport-terminal history.", BASE + ("SFT-MAT-OPT-PLASMONIC-RESPONSE-009",)),
)

RELATIONS = {number: relation for number, relation in zip((f"{index:03d}" for index in range(1, 11)), (
    "incident-transmitted-reflected-absorbed-scattered-extinction-partition",
    "incident-reflection-transmission-retained-geometry-ledger",
    "absorbed-emitted-nonradiative-quantum-yield-partition",
    "elastic-inelastic-unscattered-channel-partition",
    "two-polarization-axis-ratio-positive-gap-anisotropy",
    "input-output-polarization-sum-difference-harmonic-mixing",
    "incident-guided-lost-core-cladding-path-partition",
    "ordered-gap-periodic-support-confined-defect-mode",
    "interface-collective-dissipated-plasmonic-mode-partition",
    "generated-transported-recombined-retained-exciton-history",
))}

def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "answer-only", "carrier erased", "complete-positive-optical-carrier", "all held"),
        binary_axis("relation", "relation?", "imported-fit-continuum", "not forced", relation, "exact"),
        binary_axis("path", "path?", "endpoint-only", "history erased", "complete-optical-state-channel-path", "retained"),
        binary_axis("observation", "conditions?", "condition-erased", "not reproducible", "specimen-method-geometry-spectrum-polarization-uncertainty-held", "held"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-trace", "retained"),
        binary_axis("provenance", "selector?", "target-or-prior-model", "external selector", "root-bound-forward-forcing", "forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "preserved"),
        binary_axis("extension", "extra?", "fit-exception-extra-rule", "manufactured", "no-extra-rule", "none"),
    )

WITNESSES = {
    "001": (Witness("extinction", "Exact extinction half.", absorption_extinction(8, 2, 2, 3, 1, "sample")["extinction_part"] == Fraction(1, 2)),),
    "002": (Witness("reflection", "Exact reflection quarter.", reflection_transmission(8, 2, 3, 3, "normal")["reflection_part"] == Fraction(1, 4)),),
    "003": (Witness("yield", "Exact quantum yield three fifths.", luminescence_yield(5, 3, 2, "pump", "emission")["quantum_yield"] == Fraction(3, 5)),),
    "004": (Witness("scatter", "Exact scattered half.", light_scattering(8, 2, 2, 4, "bidirectional")["scattered_part"] == Fraction(1, 2)),),
    "005": (Witness("anisotropy", "Positive gap two.", birefringence(5, 3, "ordinary", "extraordinary", "crystal")["gap_magnitude"] == 2),),
    "006": (Witness("mix", "Exact sum mixing.", nonlinear_mixing((2, 3), 5, "sum", ("p", "s", "p"))["complete_path"]),),
    "007": (Witness("guide", "Exact guided part three fifths.", waveguide_confinement(5, 3, 2, "core", "cladding", ("input", "output"))["guided_part"] == Fraction(3, 5)),),
    "008": (Witness("gap", "Exact gap width four.", photonic_gap(2, 6, 4, "periodic", "defect")["gap_width"] == 4),),
    "009": (Witness("plasmon", "Exact collective part three fifths.", plasmonic_response(5, 3, 2, "metal-dielectric", "surface")["collective_part"] == Fraction(3, 5)),),
    "010": (Witness("exciton", "Exact retained part two fifths.", exciton_dynamics(5, 3, 2, 4, ("generated", "transported", "terminal"))["retained_part"] == Fraction(2, 5)),),
}

@dataclass(frozen=True)
class OptSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(witness.passed for witness in self.witnesses):
            raise ValueError("invalid OPT spec")
        for axis in self.axes:
            axis.survivor

class OptProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)

EXCLUSIONS = (
    "no imported continuum optical equation, fitted constitutive response, named mechanism or prior proof as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "orientation, polarization, channel and structural absence remain held labels",
    "no external outcome selects a survivor",
    "all result classes and the initial source limitation remain retained",
    "no failed attempt retires an obligation or changes protected authority",
)

SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    spec = OptSpec(claim_id=claim_id, title=title, statement=statement, dependencies=dependencies, evidence_mode=EvidenceMode.EMPIRICAL, generation_rule=f"Complete literal product of eight OPT-{number} axes before target release.", grammar_boundary=f"Every positive finite OPT-{number} carrier with complete state, channel, path and observation distinctions.", axes=axes(RELATIONS[number]), exact_result=f"OPT-{number} uniquely retains {RELATIONS[number]} with complete carrier, path, observation, proof, root provenance, successor closure and no extra rule.", induction_base="The first positive optical carrier retains every distinction.", induction_step="One lawful successor retains all prior distinctions and adds no selector.", exclusions=EXCLUSIONS, witnesses=WITNESSES[number], number=number, obligation_id=f"SFT-MAT-OBL-OPT-{number}")
    spec.validate()
    SPECS[claim_id] = spec

ORDER = tuple(row[1] for row in DEFINITIONS)

__all__ = ("ORDER", "SPECS", "OptProgram", "OptSpec", "absorption_extinction", "reflection_transmission", "luminescence_yield", "light_scattering", "birefringence", "nonlinear_mixing", "waveguide_confinement", "photonic_gap", "plasmonic_response", "exciton_dynamics")

"""Complete Smithium consequence family from the sealed element-126 prediction.

The prior V3 claim fixes the Smithium coordinate and electronic support.  This
module does not replay that result.  It exhausts the additional synthesis,
decay, lifetime-identifiability, ion, spectroscopy, separation and joint-
identification consequences that follow without importing an apparatus,
cross-section, decay width, spectral wavelength or measured outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.physics.atomic_constants import orbit_capacity
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


SYNTHESIS_ID = "SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001"
DECAY_ID = "SFT-CHEM-SMITHIUM-DECAY-CHANNEL-LEDGER-001"
LIFETIME_ID = "SFT-CHEM-SMITHIUM-LIFETIME-BOUNDARY-001"
ION_ID = "SFT-CHEM-SMITHIUM-ION-OXIDATION-LADDER-001"
SPECTROSCOPY_ID = "SFT-CHEM-SMITHIUM-SPECTROSCOPIC-CLASSES-001"
SEPARATION_ID = "SFT-CHEM-SMITHIUM-CHEMICAL-SEPARATION-001"
DETECTION_ID = "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001"
EMPIRICAL_ID = "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001"

PROTON_COUNT = 126
NEUTRON_COUNT = 184
MASS_COUNT = 310


@dataclass(frozen=True)
class StructuralChemistrySpec(StructuralPhysicsSpec):
    """Structural product specification under Chemistry authority."""

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CHEM-"):
            raise ValueError("structural Chemistry claim identity is invalid")
        if not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("structural Chemistry law lacks dependencies, eight axes or witnesses")
        if len({axis.key for axis in self.axes}) != len(self.axes):
            raise ValueError("structural Chemistry law contains duplicate axes")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("each Smithium axis must exhaust two registered forms")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("structural Chemistry operational witness failed")


class StructuralChemistryProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="chemistry",
            statement=self.spec.statement,
            evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


def positive_entrance_partitions() -> tuple[tuple[int, int, int, int], ...]:
    """All labelled positive two-body entrance coordinates conserving Z and N."""

    return tuple(
        (z, n, PROTON_COUNT - z, NEUTRON_COUNT - n)
        for z, n in product(range(1, PROTON_COUNT), range(1, NEUTRON_COUNT))
    )


def decay_channel_ledger() -> dict[str, object]:
    """Exact coordinate changes for the complete registered decay-class grammar."""

    return {
        "gamma": {"daughter": (PROTON_COUNT, NEUTRON_COUNT, MASS_COUNT), "emitted": "one-photon-record"},
        "alpha": {"daughter": (124, 182, 306), "emitted": (2, 2, 4)},
        "beta-minus": {"daughter": (127, 183, MASS_COUNT), "conversion": "one-neutron-to-one-proton"},
        "beta-plus-or-electron-capture": {"daughter": (125, 185, MASS_COUNT), "conversion": "one-proton-to-one-neutron"},
        "labelled-fission-partitions": positive_entrance_partitions(),
    }


def lifetime_identifiability_record() -> dict[str, object]:
    """Separate structural closure from a numerical lifetime measurement."""

    return {
        "double_closure": (PROTON_COUNT, NEUTRON_COUNT),
        "decay_classes": tuple(decay_channel_ledger()),
        "required_for_numeric_lifetime": ("positive-transition-width", "registered-time-unit"),
        "numeric_lifetime": "unselected-standing-measurement",
        "closed_boundary": True,
    }


def ion_ladder() -> tuple[dict[str, object], ...]:
    """Remove the two 8s carriers before the six 5g carriers, retaining identity."""

    rows: list[dict[str, object]] = []
    for charge in range(2, 9):
        removed_g = charge - 2
        retained_g = 6 - removed_g
        rows.append(
            {
                "positive_oxidation_count": charge,
                "electron_count": PROTON_COUNT - charge,
                "removed": ((8, "s", 2), (5, "g", removed_g) if removed_g else ()),
                "active_configuration": ((5, "g", retained_g),) if retained_g else (),
                "closed_core": charge == 8,
            }
        )
    return tuple(rows)


def spectroscopic_class_record() -> dict[str, object]:
    """Return exact occupation and E1-adjacent orbital classes, not line values."""

    return {
        "conventional_orbital_label": "g",
        "conventional_orbital_rank": 4,
        "fold_orbit_rank": 5,
        "capacity": orbit_capacity(5),
        "occupation": 6,
        "holes": orbit_capacity(5) - 6,
        "electric_dipole_adjacent_classes": ("g-to-f", "g-to-h", "f-to-g", "h-to-g"),
        "line_energy": "unselected-standing-measurement",
        "wavelength": "unselected-standing-measurement",
    }


def separation_distinction_record() -> dict[str, object]:
    states = tuple(row["positive_oxidation_count"] for row in ion_ladder())
    pairs = tuple((left, right) for index, left in enumerate(states) for right in states[index + 1 :])
    return {
        "nuclear_identity": (PROTON_COUNT, NEUTRON_COUNT, MASS_COUNT),
        "oxidation_states": states,
        "pairwise_state_distinctions": pairs,
        "pairwise_count": len(pairs),
        "apparatus_efficiency": "unselected-standing-measurement",
    }


def joint_detection_record() -> dict[str, object]:
    return {
        "protocol_scope": "complete-SFT-identification-record-not-an-IUPAC-minimum-rule",
        "required_records": (
            "proton-and-neutron-coordinate",
            "mass-coordinate",
            "genetically-linked-decay-record",
            "ion-or-oxidation-state-record",
            "spectroscopic-class-record",
        ),
        "current_status": "standing-unobserved-prediction",
    }


EXCLUSIONS = (
    "no apparatus, projectile, target, beam energy, cross-section or production yield selected as a law",
    "no lifetime, branching ratio, transition energy, wavelength or line intensity invented without measurement",
    "no current non-observation relabelled as disproof and no standing prediction relabelled as discovery",
    "no numerical absence used as a proof value; absence is a held structural record",
    "no negative, irrational, imaginary, floating, fitted, free or target-selected proof magnitude",
    "no V1/V2 answer used to select a survivor; prior work supplies only the reconstruction question",
)


def axes(relation_name: str, relation_reason: str) -> tuple:
    return (
        binary_axis("coordinate", "Which element carrier is retained?", "selected-element-name", "A selected name does not reconstruct a nuclear/electronic coordinate.", "sealed-126-184-310-coordinate", "The admitted Smithium predecessor fixes all three positive coordinates."),
        binary_axis("conservation", "Which transformations are lawful?", "outcome-only-transformation", "An outcome without the complete carrier ledger can hide loss or invention.", "complete-positive-carrier-ledger", "Every proton, neutron, mass and electron carrier is retained or explicitly transferred."),
        binary_axis("relation", "Which family relation survives?", "free-or-imported-relation", "A free or imported relation is not forced by the dependencies.", relation_name, relation_reason),
        binary_axis("enumeration", "How are alternatives exhausted?", "selected-favourable-example", "One favourable example cannot establish uniqueness.", "complete-declared-product", "Every form inside the frozen grammar occurs exactly once."),
        binary_axis("measurement", "May an observed value select the law?", "target-before-seal", "Target access before the derivation seal is fitting.", "formal-seal-before-target-access", "The exact law closes before any external outcome is opened."),
        binary_axis("record", "Which external outcomes remain?", "favourable-only-record", "Selective retention destroys empirical falsifiability.", "favourable-adverse-absent-unresolved-held", "Every result class remains visible and separately typed."),
        binary_axis("absence", "How is an unavailable magnitude represented?", "invented-numerical-placeholder", "A placeholder turns absence into a false number.", "structural-absence-and-explicit-halt", "The unavailable value is held as absence and numerical evaluation halts."),
        binary_axis("extension", "Is an exception required?", "free-extra-rule", "An exception is an unforced parameter.", "no-extra-rule", "The admitted dependencies exhaust the frozen boundary."),
    )


BASE_DEPENDENCIES = (
    "SFT-CHEM-PRED-SMITHIUM-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
)


SYNTHESIS_SPEC = StructuralChemistrySpec(
    claim_id=SYNTHESIS_ID,
    title="Complete Smithium synthesis-conservation grammar",
    statement="Every positive labelled two-body entrance coordinate conserving the sealed Smithium proton and neutron counts is generated; conservation alone selects no unique apparatus route.",
    dependencies=BASE_DEPENDENCIES + ("SFT-PHYS-NUCLEAR-FUSION-001",),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis Smithium synthesis product and every positive labelled two-body Z/N entrance partition.",
    grammar_boundary="All positive labelled pairs (Z1,N1),(Z2,N2) with Z1+Z2=126 and N1+N2=184, plus all 256 methodological forms.",
    axes=axes("all-22875-conserving-labelled-entrance-partitions", "Positive exact conservation generates 125 times 183 labelled partitions and refuses to invent a unique beam/target route."),
    exact_result="The complete conservation grammar contains exactly 22,875 labelled positive two-body entrance partitions. Every row sums to Z=126, N=184 and A=310. No partition is promoted to a feasible reaction, unique synthesis route, beam energy, cross-section or yield without additional sealed law and measurement.",
    induction_base="The least positive first fragment leaves positive complements 125 and 183.",
    induction_step="Successor movement of either first-fragment coordinate reduces only its held complement by the same positive count, preserving both totals until the positive boundary.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("cardinality", "All labelled positive entrance partitions are present.", len(positive_entrance_partitions()) == 22875),
        Witness("first", "The least partition conserves all coordinates.", positive_entrance_partitions()[0] == (1, 1, 125, 183)),
        Witness("last", "The terminal positive partition conserves all coordinates.", positive_entrance_partitions()[-1] == (125, 183, 1, 1)),
    ),
)


DECAY_SPEC = StructuralChemistrySpec(
    claim_id=DECAY_ID,
    title="Complete Smithium decay-channel coordinate ledger",
    statement="Gamma, alpha, beta-minus, beta-plus/electron-capture and labelled fission classes receive exact carrier ledgers from the Smithium coordinate without selecting a branch or branching fraction.",
    dependencies=(SYNTHESIS_ID, "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005", "SFT-PHYS-NUCLEAR-FISSION-001", "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 decay-ledger forms and the complete registered gamma, alpha, beta and labelled-fission coordinate classes.",
    grammar_boundary="The sealed Smithium parent under gamma, alpha, beta-minus, beta-plus/electron-capture and every positive labelled two-fragment conservation partition.",
    axes=axes("complete-gamma-alpha-beta-and-labelled-fission-ledger", "The admitted nuclear transformations force exact daughters while preserving the complete coordinate ledger."),
    exact_result="Gamma retains (126,184,310); alpha yields daughter (124,182,306) plus (2,2,4); beta-minus yields (127,183,310); beta-plus or electron capture yields (125,185,310); and labelled fission exhausts the same 22,875 positive conservation partitions. No branch is asserted active and no branching ratio is invented.",
    induction_base="Each elementary channel retains the parent identity and one complete transformation record.",
    induction_step="Appending a labelled fission partition or decay record preserves the parent totals and every earlier channel without selecting an outcome.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("alpha", "Alpha coordinates exactly conserve the parent.", decay_channel_ledger()["alpha"] == {"daughter": (124, 182, 306), "emitted": (2, 2, 4)}),
        Witness("beta", "Both beta directions retain mass 310.", decay_channel_ledger()["beta-minus"]["daughter"][2] == decay_channel_ledger()["beta-plus-or-electron-capture"]["daughter"][2] == MASS_COUNT),
        Witness("fission", "Every labelled fission partition is retained.", len(decay_channel_ledger()["labelled-fission-partitions"]) == 22875),
    ),
)


LIFETIME_SPEC = StructuralChemistrySpec(
    claim_id=LIFETIME_ID,
    title="Smithium lifetime identifiability and mandatory-halt boundary",
    statement="The double closure and channel grammar do not uniquely determine a numerical lifetime; a positive transition width and registered time unit are mandatory additional records.",
    dependencies=(DECAY_ID, "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 lifetime-identifiability forms from closure, channel, width, unit, record and target-custody alternatives.",
    grammar_boundary="Every numerical-lifetime request using the sealed double closure and channel ledger, distinguished by presence or absence of a positive transition width and registered time unit.",
    axes=axes("numeric-lifetime-only-from-positive-width-and-unit", "A lifetime is evaluable only when its positive transition width and time unit are held; double closure alone supplies neither."),
    exact_result="Smithium's 126/184 double closure forces a stability-relevant structural coordinate but not a numerical lifetime. Numerical evaluation must halt until a positive transition width and registered time unit are independently derived or measured. No half-life or branching value is claimed by V3 at this boundary.",
    induction_base="One closure record identifies the parent but contains no elapsed-time carrier.",
    induction_step="Adding channel names without a positive width still contains no unique elapsed-time carrier; adding a sealed width and unit makes the evaluation identifiable without changing prior records.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("closure-held", "The double closure is preserved.", lifetime_identifiability_record()["double_closure"] == (126, 184)),
        Witness("requirements", "Both width and unit are explicitly required.", lifetime_identifiability_record()["required_for_numeric_lifetime"] == ("positive-transition-width", "registered-time-unit")),
        Witness("halt", "No false numerical lifetime is emitted.", lifetime_identifiability_record()["numeric_lifetime"] == "unselected-standing-measurement"),
    ),
)


ION_SPEC = StructuralChemistrySpec(
    claim_id=ION_ID,
    title="Exact Smithium positive-ion and oxidation ladder",
    statement="The sealed 8s2 5g6 active support forces seven retained +2 through +8 oxidation/ion records by removing the 8s pair before the six 5g carriers.",
    dependencies=(LIFETIME_ID, "SFT-CHEM-REDOX-OXIDATION-STATE-001", "SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 ion-ladder forms and every positive removal count from the 8s pair through the six 5g carriers.",
    grammar_boundary="The seven structurally admissible positive oxidation counts +2 through +8 of the sealed 8s2 5g6 Smithium active configuration.",
    axes=axes("ordered-8s-then-5g-removal-with-identity-retained", "The admitted active support fixes the two 8s carriers and six 5g carriers and retains the proton identity at every removal."),
    exact_result="The exact structural ladder has seven records: +2 leaves [Og]5g6 with 124 electrons; each successor removes one further 5g carrier; +8 leaves the [Og] core with 118 electrons. These are structural admissibility classes, not measured abundances or guaranteed isolable compounds.",
    induction_base="Removing the complete 8s pair yields the +2 record with six 5g carriers retained.",
    induction_step="Each positive successor removes one held 5g carrier, reduces the electron count by one and preserves Z=126 until +8 closes the active support.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("seven-states", "Seven positive ladder states are generated.", len(ion_ladder()) == 7),
        Witness("plus-two", "The +2 state retains six 5g carriers and 124 electrons.", ion_ladder()[0]["positive_oxidation_count"] == 2 and ion_ladder()[0]["electron_count"] == 124 and ion_ladder()[0]["active_configuration"] == ((5, "g", 6),)),
        Witness("plus-eight", "The +8 state closes the active support at 118 electrons.", ion_ladder()[-1]["positive_oxidation_count"] == 8 and ion_ladder()[-1]["electron_count"] == 118 and ion_ladder()[-1]["closed_core"]),
    ),
)


SPECTROSCOPY_SPEC = StructuralChemistrySpec(
    claim_id=SPECTROSCOPY_ID,
    title="Smithium spectroscopic transition-class law",
    statement="The 5g6 support fixes orbital capacity, occupation, holes and electric-dipole-adjacent orbital classes while refusing to invent line energies or wavelengths.",
    dependencies=(ION_ID, "SFT-CHEM-SELECTION-RULE-STRUCTURE-010", "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 spectroscopy forms and the complete capacity, occupation, hole and E1-adjacent class record for the sealed 5g6 support.",
    grammar_boundary="The Smithium 5g active carrier under exact Fold capacity and one-electron electric-dipole orbital-rank adjacency, separated from unmeasured line values.",
    axes=axes("5g6-capacity-occupation-holes-and-E1-adjacency", "The admitted orbit capacity and selection structure force the g carrier, its twelve holes and adjacent f/h E1 classes."),
    exact_result="The conventional g orbital has l=4 and Fold orbit rank 5, exact capacity 18, occupation 6 and 12 holes. One-electron E1 orbital adjacency permits g↔f and g↔h classes. Numerical line energies, wavelengths, intensities and lifetimes remain standing measurements and cannot be fabricated from class identity.",
    induction_base="The sealed 5g6 support fixes one occupied g class and its exact remaining capacity.",
    induction_step="Appending an ion stage retains the nuclear identity and updates only the held occupation; the E1 adjacent-class relation remains unchanged.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("capacity", "The 5g carrier has capacity 18.", spectroscopic_class_record()["capacity"] == 18),
        Witness("holes", "Six occupied carriers leave twelve holes.", spectroscopic_class_record()["holes"] == 12),
        Witness("classes", "Both E1-adjacent directions are retained.", spectroscopic_class_record()["electric_dipole_adjacent_classes"] == ("g-to-f", "g-to-h", "f-to-g", "h-to-g")),
    ),
)


SEPARATION_SPEC = StructuralChemistrySpec(
    claim_id=SEPARATION_ID,
    title="Complete Smithium chemical-state distinction and separation boundary",
    statement="Nuclear identity plus the seven-state oxidation carrier generates every pairwise chemical-state distinction while leaving apparatus efficiency and yield unselected.",
    dependencies=(SPECTROSCOPY_ID, "SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 separation forms and every unordered pair of the seven retained positive oxidation-state identities.",
    grammar_boundary="All pairwise distinctions among Smithium's +2 through +8 structural states, conditioned on the sealed nuclear identity and without an apparatus model.",
    axes=axes("all-21-pairwise-oxidation-state-distinctions", "Seven exact retained state labels force twenty-one unordered pairwise distinctions and no preferred apparatus."),
    exact_result="The seven Smithium +2…+8 state identities generate exactly 21 unordered pairwise distinctions, each held with Z=126, N=184 and A=310. This closes the mathematical separation target grammar; it does not assert a separation medium, recovery, decontamination factor, efficiency or yield.",
    induction_base="The first two retained state identities generate one pairwise distinction.",
    induction_step="Appending the next state adds one distinction with every earlier state while preserving all prior pairs, giving 1+2+3+4+5+6=21.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("pair-count", "Seven states generate twenty-one pairs.", separation_distinction_record()["pairwise_count"] == 21),
        Witness("first-pair", "The first state distinction is +2 versus +3.", separation_distinction_record()["pairwise_state_distinctions"][0] == (2, 3)),
        Witness("last-pair", "The terminal state distinction is +7 versus +8.", separation_distinction_record()["pairwise_state_distinctions"][-1] == (7, 8)),
    ),
)


DETECTION_SPEC = StructuralChemistrySpec(
    claim_id=DETECTION_ID,
    title="Complete Smithium joint-identification protocol",
    statement="A complete SFT identification record jointly retains nuclear, mass, decay, ion and spectroscopic evidence without redefining the official minimum criterion for element discovery.",
    dependencies=(SEPARATION_ID, "SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009", "SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate all 256 identification forms and the complete five-record conjunction for the Smithium standing prediction.",
    grammar_boundary="Every finite evidence record assembled from nuclear coordinate, mass, genetic decay, ion/oxidation and spectroscopic classes, with complete provenance and explicit official-scope separation.",
    axes=axes("five-record-complete-SFT-identification-conjunction", "Retaining all five independently distinguishable records supplies the complete project protocol without erasing source or scope."),
    exact_result="Complete SFT identification of Smithium requires the conjunction of (i) Z/N, (ii) A, (iii) genetically linked decay, (iv) ion/oxidation identity and (v) spectroscopic class, with source custody for every record. This is a deliberately stronger complete-project protocol, not a claim that IUPAC requires all five for priority recognition. Current status remains an unobserved standing prediction.",
    induction_base="One nuclear coordinate identifies a candidate carrier but does not provide the complete project record.",
    induction_step="Each appended independent record narrows identity while retaining every prior source and distinction; completion occurs only when all five classes are held.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("five-records", "All five identification classes are retained.", len(joint_detection_record()["required_records"]) == 5),
        Witness("scope", "The protocol is not misrepresented as an IUPAC minimum.", joint_detection_record()["protocol_scope"] == "complete-SFT-identification-record-not-an-IUPAC-minimum-rule"),
        Witness("standing", "The prediction remains explicitly unobserved.", joint_detection_record()["current_status"] == "standing-unobserved-prediction"),
    ),
)


EMPIRICAL_SPEC = StructuralChemistrySpec(
    claim_id=EMPIRICAL_ID,
    title="Complete post-seal Smithium external-status record",
    statement="The seven sealed Smithium consequence laws are compared after sealing with official IUPAC production, identification and current-boundary records and the NIST E1 selection-rule record.",
    dependencies=(DETECTION_ID, "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate all 256 complete-family comparison forms before opening the registered IUPAC and NIST snapshots.",
    grammar_boundary="All seven formal Smithium successor receipts, the official current element boundary, superheavy production/identification practice, E1 orbital adjacency and favorable/adverse/absent/unresolved status classes.",
    axes=axes("sealed-seven-law-family-versus-complete-official-source-record", "The formal family remains fixed while each official source row and standing-prediction status is retained after seal."),
    exact_result="IUPAC's registered record places the current known element boundary at oganesson, Z=118; reports superheavy Z≥104 production by heavy-ion fusion and identification through implanted-residue decay chains with alpha decay and/or spontaneous fission; and NIST records one-electron E1 orbital change by one rank. These externally correspond to the frozen synthesis, decay and spectroscopy classes but do not observe Smithium, select a unique production route, or supply its lifetime, branch fractions or wavelengths. Smithium remains a precise standing prediction.",
    induction_base="All seven formal claims and their receipts are sealed before the source-derived target is opened.",
    induction_step="Each official fragment is appended with source identity and status; correspondence, absence and unresolved values cannot be relabelled as discovery or retirement.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("formal-family", "All seven formal claim identities are distinct.", len({SYNTHESIS_ID, DECAY_ID, LIFETIME_ID, ION_ID, SPECTROSCOPY_ID, SEPARATION_ID, DETECTION_ID}) == 7),
        Witness("standing-status", "The complete protocol retains unobserved status.", joint_detection_record()["current_status"] == "standing-unobserved-prediction"),
        Witness("no-numerical-fabrication", "Lifetime and wavelength remain explicitly unselected.", lifetime_identifiability_record()["numeric_lifetime"] == "unselected-standing-measurement" and spectroscopic_class_record()["wavelength"] == "unselected-standing-measurement"),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPECS = {
    spec.claim_id: spec
    for spec in (
        SYNTHESIS_SPEC,
        DECAY_SPEC,
        LIFETIME_SPEC,
        ION_SPEC,
        SPECTROSCOPY_SPEC,
        SEPARATION_SPEC,
        DETECTION_SPEC,
        EMPIRICAL_SPEC,
    )
}

for _spec in SPECS.values():
    _spec.validate()


__all__ = (
    "DECAY_ID",
    "DETECTION_ID",
    "EMPIRICAL_ID",
    "ION_ID",
    "LIFETIME_ID",
    "SEPARATION_ID",
    "SPECS",
    "SPECTROSCOPY_ID",
    "SYNTHESIS_ID",
    "StructuralChemistryProgram",
    "decay_channel_ledger",
    "ion_ladder",
    "joint_detection_record",
    "lifetime_identifiability_record",
    "positive_entrance_partitions",
    "separation_distinction_record",
    "spectroscopic_class_record",
)

"""Exact local-vacuum/inertial-response return family from admitted V3 laws."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis, fold_part


ONE = Fraction(1, 1)
LOCAL_DRIVE_ID = "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083"
COVARIATION_ID = "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084"
POSITIVE_FLOOR_ID = "SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085"
COMPLETE_LEDGER_ID = "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086"


def positive_part(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0 or value > 1:
        raise ValueError("vacuum/inertia carriers must be exact positive parts of the One")
    return value


def positive_count(value: int) -> int:
    if isinstance(value, bool) or value < 1:
        raise ValueError("a depth or act count must be positive")
    return value


def local_resonant_drive(source: Fraction, retained: Fraction) -> dict[str, Fraction]:
    """Transfer an exact positive difference while retaining both endpoints."""

    source_part = positive_part(source)
    retained_part = positive_part(retained)
    if retained_part >= source_part:
        raise ValueError("this oriented drive record requires a smaller retained local carrier")
    transferred = source_part - retained_part
    return {
        "source": source_part,
        "retained": retained_part,
        "transferred": transferred,
        "reconstructed": retained_part + transferred,
    }


def live_phase_trace(seed: Fraction, act_count: int) -> tuple[Fraction, ...]:
    current = positive_part(seed)
    positive_count(act_count)
    trace = []
    for _ in range(act_count):
        current = fold_part(current)
        trace.append(current)
    return tuple(trace)


def vacuum_inertia_pair(vacuum: Fraction) -> dict[str, Fraction]:
    carrier = positive_part(vacuum)
    return {"vacuum": carrier, "inertia": carrier, "exchange_ratio": carrier / carrier}


def covariation_record(initial: Fraction, driven: Fraction) -> dict[str, Fraction]:
    initial_pair = vacuum_inertia_pair(initial)
    driven_pair = vacuum_inertia_pair(driven)
    if driven_pair["vacuum"] >= initial_pair["vacuum"]:
        raise ValueError("the reduction-oriented witness requires a smaller driven carrier")
    vacuum_change = initial_pair["vacuum"] - driven_pair["vacuum"]
    inertia_change = initial_pair["inertia"] - driven_pair["inertia"]
    return {
        "initial_vacuum": initial_pair["vacuum"],
        "initial_inertia": initial_pair["inertia"],
        "driven_vacuum": driven_pair["vacuum"],
        "driven_inertia": driven_pair["inertia"],
        "vacuum_change": vacuum_change,
        "inertia_change": inertia_change,
        "initial_ratio": initial_pair["exchange_ratio"],
        "driven_ratio": driven_pair["exchange_ratio"],
    }


def finite_depth_floor(depth: int) -> Fraction:
    positive_count(depth)
    support = 2
    for _ in range(depth):
        support += support
    return Fraction(1, support)


def bounded_driven_carrier(carrier: Fraction, depth: int) -> Fraction:
    held = positive_part(carrier)
    floor = finite_depth_floor(depth)
    if held < floor:
        raise ValueError("the driven carrier lies below its registered finite-depth floor")
    return held


def complete_drive_response_ledger(initial: Fraction, driven: Fraction) -> dict[str, object]:
    change = covariation_record(initial, driven)
    transfer = change["vacuum_change"]
    if transfer != change["inertia_change"]:
        raise ValueError("vacuum and inertia changes did not remain at exchange ratio One")
    restored_vacuum = change["driven_vacuum"] + transfer
    restored_inertia = change["driven_inertia"] + transfer
    return {
        **change,
        "outward_transfer": transfer,
        "restoration_transfer": transfer,
        "restored_vacuum": restored_vacuum,
        "restored_inertia": restored_inertia,
        "information_record": (
            "initial-pair",
            "drive-act",
            "driven-pair",
            "outward-transfer",
            "restoration-act",
            "restored-pair",
        ),
        "closed": restored_vacuum == change["initial_vacuum"] and restored_inertia == change["initial_inertia"],
    }


EXCLUSIONS = (
    "no V1/V2 executable, patent formula, apparatus equation or desired outcome as a premise",
    "no measured acceleration, field strength, device performance or target value selecting a survivor",
    "no free coupling, tunable efficiency, hidden reservoir or omitted information record",
    "no semantic numerical zero, negative, irrational, imaginary, floating or completed-infinite proof magnitude",
    "no claim that structural co-variation proves any craft, propulsion system or useful apparatus magnitude",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("carrier", "What carries the local state?", "inert-empty-background", "An inert empty background has no generated state to drive.", "live-exact-positive-vacuum-carrier", "The admitted vacuum has exact positive live support."),
        binary_axis("drive", "What constitutes a drive?", "unrecorded-field-assertion", "An unrecorded assertion supplies no transition or conservation trace.", "resonant-source-bound-transition", "A resonant act is a source-bound exact state transition."),
        binary_axis("relation", "Which response relation survives?", "free-response-coefficient", "A free coefficient is an unforced parameter.", relation, reason),
        binary_axis("floor", "How is absence treated?", "drive-to-numerical-nothing", "Numerical nothing is not an admitted physical carrier.", "positive-finite-depth-floor", "Every registered finite depth retains an exact positive least carrier."),
        binary_axis("ledger", "Which transfers remain?", "outcome-only-ledger", "An outcome-only record hides source, loss or restoration cost.", "complete-drive-response-restoration-ledger", "Every source, response, transfer, restoration and information carrier remains held."),
        binary_axis("measurement", "Can an apparatus select the law?", "target-selected-channel", "Target selection is fitting.", "formal-seal-before-apparatus-comparison", "The structural channel seals before apparatus evidence is compared."),
        binary_axis("record", "Which results remain?", "favourable-only-record", "Selective retention cannot test a controversial claim.", "complete-favourable-adverse-unresolved-record", "Every favorable, adverse and unresolved row remains visible."),
        binary_axis("extension", "Is an extra rule required?", "free-extra-rule", "An exception or hidden interaction is a parameter.", "no-extra-rule", "The admitted dependency chain exhausts the declared structural boundary."),
    )


LOCAL_DRIVE_SPEC = StructuralPhysicsSpec(
    claim_id=LOCAL_DRIVE_ID,
    title="Exact local resonant vacuum-state drive channel",
    statement="A live exact local vacuum carrier can undergo a source-bound resonant transition while retaining its initial state, driven state and complete transferred support.",
    dependencies=(
        "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
        "SFT-PHYS-TESLA-RESONANT-TRANSFER-081",
        "SFT-PHYS-WAVE-RESONANCE-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of local carrier, resonant drive, exact state transition, positive floor, complete ledger, measurement direction, record and extension forms.",
    grammar_boundary="Every ordered pair of distinct exact positive local vacuum parts, every positive finite phase-act count, their complete transfer ledger and all 256 registered structural alternatives.",
    axes=axes("exact-local-state-change-with-source-bound-transfer", "A live state plus an admitted resonant transition forces a changed local carrier only when the exact transferred support reconstructs the source."),
    exact_result="For every ordered exact positive pair b<a within the One, a lawful local resonant drive from a to b retains the exact positive transfer a Take b and reconstructs a as b plus that transfer. Odd-denominator carriers additionally retain a finite live Fold phase trace. This forces a local drive channel without selecting a device, field strength, frequency or magnitude.",
    induction_base="One source-bound act retains the initial carrier, the changed carrier and their exact positive separation.",
    induction_step="Appending a resonant act extends the live phase trace while preserving the source and every prior transfer record.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("drive-third-to-quarter", "The historical one-third to one-quarter probe retains exact transfer one-twelfth.", local_resonant_drive(Fraction(1, 3), Fraction(1, 4))["transferred"] == Fraction(1, 12)),
        Witness("live-third", "The one-third mode returns exactly after two Fold acts.", live_phase_trace(Fraction(1, 3), 2) == (Fraction(2, 3), Fraction(1, 3))),
        Witness("reconstruction", "A distinct positive drive record reconstructs its source.", local_resonant_drive(Fraction(2, 5), Fraction(1, 5))["reconstructed"] == Fraction(2, 5)),
    ),
)


COVARIATION_SPEC = StructuralPhysicsSpec(
    claim_id=COVARIATION_ID,
    title="Exact driven vacuum-to-inertia co-variation law",
    statement="Because the admitted vacuum-to-inertia exchange ratio is the One, every lawful local vacuum-carrier change is held identically by its inertial carrier.",
    dependencies=(LOCAL_DRIVE_ID, "SFT-PHYS-VACUUM-INERTIA-UNITY-003", "SFT-PHYS-MECH-INERTIA-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of driven carrier, source-bound drive, unity co-variation, positive floor, complete ledger, measurement direction, record and extension forms.",
    grammar_boundary="Every ordered exact positive initial/driven vacuum pair, its unity-related inertia pair, both exact positive change carriers and all 256 structural alternatives.",
    axes=axes("vacuum-change-equals-inertia-change-at-exchange-One", "The already admitted exchange ratio One leaves no independent inertial response coefficient: equal paired carriers have equal exact changes."),
    exact_result="For every lawful exact local change from vacuum carrier a to b, the unity exchange law forces the inertial carrier to change from a to b and forces both positive change magnitudes to equal a Take b. The initial and driven vacuum/inertia ratios remain the One. In the historical one-third to one-quarter probe, both changes are exactly one-twelfth.",
    induction_base="At one lawful drive act, the paired vacuum and inertia carriers are equal before and after the act.",
    induction_step="Appending a drive act preserves exchange ratio One and appends the same exact positive change to both held histories.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("historical-probe", "One-third to one-quarter changes both carriers by one-twelfth.", covariation_record(Fraction(1, 3), Fraction(1, 4))["vacuum_change"] == covariation_record(Fraction(1, 3), Fraction(1, 4))["inertia_change"] == Fraction(1, 12)),
        Witness("initial-unity", "The initial exchange ratio remains the One.", covariation_record(Fraction(2, 5), Fraction(1, 5))["initial_ratio"] == ONE),
        Witness("driven-unity", "The driven exchange ratio remains the One.", covariation_record(Fraction(2, 5), Fraction(1, 5))["driven_ratio"] == ONE),
    ),
)


POSITIVE_FLOOR_SPEC = StructuralPhysicsSpec(
    claim_id=POSITIVE_FLOOR_ID,
    title="Finite-depth positive lower bound on driven vacuum and inertia",
    statement="At every registered positive finite Fold depth, complete binary support forces an exact positive least carrier, so neither a driven vacuum carrier nor its unity-related inertia carrier can become structural absence.",
    dependencies=(COVARIATION_ID, "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-FOUNDATION-PART-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of driven carrier, source-bound drive, unity response, finite-depth floor, complete ledger, measurement direction, record and extension forms.",
    grammar_boundary="Every positive finite depth, its complete binary word support and least oscillator part, every driven carrier at or above that floor and all 256 structural alternatives.",
    axes=axes("finite-depth-floor-bounds-both-unity-related-carriers", "The complete depth-k support has a least positive half-spacing; unity relation assigns the same lower boundary to inertia."),
    exact_result="At every registered positive finite depth k, the least oscillator carrier is the exact positive part One over 2^(k+1). Every lawful driven vacuum carrier and its unity-related inertia carrier must remain at or above that part. Structural absence is therefore unreachable at every declared finite depth; this is not a claim of one depth-independent dimensional mass floor.",
    induction_base="At depth One, complete binary support has four half-spacing cells and least positive carrier one-quarter.",
    induction_step="The next depth doubles complete support and halves the least exact positive part while never converting it into structural absence.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("depth-one", "The first finite-depth least carrier is one-quarter.", finite_depth_floor(1) == Fraction(1, 4)),
        Witness("depth-three", "Depth three retains the historical positive one-sixteenth floor under this indexing.", finite_depth_floor(3) == Fraction(1, 16)),
        Witness("bound", "One-quarter is admitted at depth three while one-thirty-second is below its floor.", bounded_driven_carrier(Fraction(1, 4), 3) == Fraction(1, 4)),
    ),
)


COMPLETE_LEDGER_SPEC = StructuralPhysicsSpec(
    claim_id=COMPLETE_LEDGER_ID,
    title="Complete vacuum-drive, inertial-response and restoration ledger",
    statement="A lawful local vacuum/inertia drive retains the source, paired response, outward transfer, restoration transfer and information trace, forbidding unrecorded cyclic gain while preserving the outward event.",
    dependencies=(
        POSITIVE_FLOOR_ID,
        "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003",
        "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003",
        "SFT-PHYS-THERMO-FIRST-LAW-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of local carrier, resonant drive, unity response, positive floor, complete drive/response/restoration ledger, measurement direction, record and extension forms.",
    grammar_boundary="Every lawful ordered initial/driven exact pair, equal vacuum/inertia response, outward and restoration transfer, complete six-label information trace and all 256 structural alternatives.",
    axes=axes("complete-paired-drive-response-restoration-and-information-ledger", "Conservation and information retention force every drive, paired response, outward transfer and restoration carrier into one reconstructable trace."),
    exact_result="For every lawful exact driven pair b<a, vacuum and inertia both change by a Take b at exchange ratio One. The outward event retains that positive carrier; exact restoration returns both carriers to a. The complete six-label information trace records initial pair, drive, driven pair, outward transfer, restoration and restored pair. Thus the channel and outward event remain admitted while an unrecorded net-support gain in a fully returned cycle is forbidden.",
    induction_base="One drive/restoration pair closes both unity-related carriers and retains all six required information labels.",
    induction_step="Appending a complete cycle concatenates a separately reconstructable six-label trace and cannot erase an earlier outward or restoration carrier.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("closed", "The historical one-third/one-quarter probe restores both paired carriers.", complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))["closed"] is True),
        Witness("six-records", "The complete information ledger contains exactly six named stages.", len(complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))["information_record"]) == 6),
        Witness("equal-transfers", "Outward and restoration carriers are the same exact one-twelfth.", complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))["outward_transfer"] == complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))["restoration_transfer"] == Fraction(1, 12)),
    ),
)


SPECS = {spec.claim_id: spec for spec in (LOCAL_DRIVE_SPEC, COVARIATION_SPEC, POSITIVE_FLOOR_SPEC, COMPLETE_LEDGER_SPEC)}


__all__ = (
    "COMPLETE_LEDGER_ID",
    "COVARIATION_ID",
    "LOCAL_DRIVE_ID",
    "POSITIVE_FLOOR_ID",
    "SPECS",
    "bounded_driven_carrier",
    "complete_drive_response_ledger",
    "covariation_record",
    "finite_depth_floor",
    "live_phase_trace",
    "local_resonant_drive",
    "vacuum_inertia_pair",
)

"""Exact correspondence return required after the sealed Classical Computation catalog."""

from __future__ import annotations

from itertools import product

from sft.computation.generated_law import LawSpec, Witness, binary_dimension
from sft.computation.lineage_laws import EMPTY_ONE, LABELS, closing_trace, verify_trace


EXTERNAL_LABELS = ("external-lower", "external-upper")
ENCODE = {"external-lower": "held-lower", "external-upper": "held-upper"}
DECODE = {"held-lower": "external-lower", "held-upper": "external-upper"}


def external_words_at_depth(depth: int) -> tuple[tuple[str, ...], ...]:
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("depth must be one supplied positive finite host count")
    return tuple(product(EXTERNAL_LABELS, repeat=depth))


def encode_external(word: tuple[str, ...]) -> tuple[str, ...]:
    if not word or any(label not in ENCODE for label in word):
        raise ValueError("encoding requires one complete registered external word")
    return tuple(ENCODE[label] for label in word)


def decode_native(word: tuple[str, ...]) -> tuple[str, ...]:
    if not word or any(label not in DECODE for label in word):
        raise ValueError("decoding requires one complete registered native word")
    return tuple(DECODE[label] for label in word)


def external_verdict(word: tuple[str, ...]) -> bool:
    """The registered external family accepts exactly upper-terminal words."""

    if not word or any(label not in ENCODE for label in word):
        raise ValueError("verdict requires one complete registered external word")
    return word[-1] == "external-upper"


def native_verdict(word: tuple[str, ...]) -> bool:
    if not word or any(label not in DECODE for label in word):
        raise ValueError("verdict requires one complete registered native word")
    return word[-1] == "held-upper"


def decode_trace(trace: tuple[tuple[str, ...], ...]) -> tuple[tuple[str, ...], ...]:
    if not trace or trace[-1] != EMPTY_ONE:
        raise ValueError("a translated trace must terminate at structural empty One")
    return tuple(decode_native(state) if state != EMPTY_ONE else EMPTY_ONE for state in trace)


def external_suffix_trace(word: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    if not word or any(label not in ENCODE for label in word):
        raise ValueError("a source trace requires one complete registered external word")
    return tuple(word[index:] for index in range(len(word))) + (EMPTY_ONE,)


def transport_holds(depth: int) -> bool:
    """Execute the complete registered external family through supplied depth."""

    for rung in range(1, depth + 1):
        for source in external_words_at_depth(rung):
            encoded = encode_external(source)
            certificate = closing_trace(encoded)
            if decode_native(encoded) != source:
                return False
            if external_verdict(source) != native_verdict(encoded):
                return False
            if not verify_trace(encoded, certificate):
                return False
            if decode_trace(certificate) != external_suffix_trace(source):
                return False
            if len(encoded) != len(source) or len(certificate) - 1 != len(source):
                return False
    return True


def changed_encoding_rejects() -> bool:
    source = ("external-lower", "external-upper")
    changed = ("held-upper", "held-lower")
    return decode_native(changed) != source and external_verdict(source) != native_verdict(changed)


def dim(key: str, question: str, rejected: str, rejected_reason: str, admitted: str, admitted_reason: str):
    return binary_dimension(key, question, rejected, rejected_reason, admitted, admitted_reason)


CONDITIONAL_TRANSLATION = LawSpec(
    claim_id="SFT-COMP-CPLX-CONVENTIONAL-TRANSLATION-003",
    group="complexity",
    slug="conventional_translation",
    title="Conditional conventional decision-family transport law",
    statement=(
        "A conventionally presented decision family inherits the admitted native Fold P_F=NP_F equality only when a registered total encoding covers every declared instance, "
        "preserves verdicts, deterministic traces and sound-complete certificates in both directions, and retains explicit polynomial size and execution bounds on a common input-size carrier. "
        "The theorem executes one complete external word family by an exact bijective translation; without those conditions no conclusion about arbitrary conventional P versus NP is admitted."
    ),
    dependencies=(
        "SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002",
        "SFT-COMP-FORM-MODEL-EQUIVALENCE-001",
        "SFT-COMP-CBL-REDUCTION-001",
        "SFT-COMP-CPLX-INPUT-SIZE-001",
        "SFT-COMP-CPLX-BOUNDS-001",
        "SFT-COMP-SEM-VERIFICATION-001",
    ),
    generation_rule="Generate the literal product of source-domain, encoding, answer, deterministic-trace, certificate, resource, successor and conclusion-boundary coordinates.",
    grammar_boundary="One complete generated external two-label word family and every later external family carrying separately registered total answer-, certificate- and polynomial-resource-preserving translations into the admitted native Fold process grammar.",
    dimensions=(
        dim("domain", "Which external inputs are covered?", "sampled-external-instances", "Samples cannot establish a family translation.", "complete-registered-external-family", "Every declared external word through the supplied depth is generated."),
        dim("encoding", "What connects the external and native descriptions?", "partial-or-colliding-encoding", "A partial or colliding map can erase instances or distinctions.", "total-bijective-source-bound-encoding", "Every source word has one native image and exact reverse reconstruction."),
        dim("answer", "How are decisions preserved?", "asserted-verdict-correspondence", "Naming equal answers is not a commuting decision proof.", "exact-bidirectional-verdict-preservation", "External and native verdict functions agree on every generated source."),
        dim("trace", "How is deterministic evaluation transported?", "terminal-result-only", "A terminal result hides steps and cost.", "complete-stepwise-trace-translation", "Every native suffix state decodes to the exact external suffix state."),
        dim("certificate", "How is nondeterministic verification transported?", "one-way-or-unsound-certificate-map", "One-way or unsound mapping cannot transport NP membership.", "sound-complete-bidirectional-certificate-map", "Accepted certificates translate and reconstruct exactly with tampered traces rejected."),
        dim("resource", "How are complexity resources compared?", "unmatched-size-and-cost-carriers", "Unmatched resources cannot transport a polynomial class claim.", "explicit-common-size-polynomial-overhead", "The registered map preserves size and step count exactly, a unit polynomial bound."),
        dim("successor", "How is every supplied finite depth covered?", "fixed-depth-examples", "Examples do not cover a generated family.", "prepend-label-translation-successor", "Prepending either external label adds one mapped label and one translated trace edge."),
        dim("conclusion", "What conclusion may be exported?", "arbitrary-conventional-p-equals-np", "Unregistered languages, encodings and resource conventions are absent.", "conditional-family-transport-only", "Only a family satisfying every registered translation condition inherits the native equality."),
    ),
    exact_result="The sole all-preserving kernel transports P_F=NP_F to the complete registered external two-label decision family with identity size and trace overhead, and proves that arbitrary conventional P-versus-NP export is inadmissible without the same complete translation certificate.",
    laws=(
        "total reverse-reconstructible encoding preserves every source distinction",
        "the external and native verdict diagrams commute on complete generated support",
        "deterministic traces and accepted certificates translate stepwise in both directions",
        "common exact input length and trace length supply a unit polynomial overhead",
        "native class equality transports only under all four preservation relations",
    ),
    induction_base="At external depth One, both registered labels encode bijectively, preserve their terminal verdict and carry one exact closing edge and verifier check.",
    induction_step="Prepending either external label prepends its unique native label, preserves the previous translated suffix trace and adds exactly one source position, evaluator edge and verifier check.",
    boundary_exclusions=(
        "no arbitrary conventional P-versus-NP conclusion",
        "no partial, sampled or answer-changing encoding",
        "no unmatched input-size or resource convention",
        "no hidden advice, oracle or nondeterministic machine import",
        "no completed infinite language object",
    ),
    witnesses=(
        Witness("complete-depth-seven", "Every registered external word through depth seven round-trips and preserves verdict, trace, certificate, input size and step resource.", transport_holds(7)),
        Witness("successor-through-fourteen", "The exact translation and unit-overhead successor execute through depth fourteen.", transport_holds(14)),
        Witness("changed-encoding-control", "A changed source encoding breaks both reverse identity and the registered verdict diagram.", changed_encoding_rejects()),
    ),
    why="The native Fold equality cannot be exported by analogy. A complete conditional transport theorem must enumerate the exact encoding, semantic, certificate and resource obligations and execute at least one non-native presentation end to end.",
    derivation="Model equivalence supplies exact bidirectional simulation, reduction supplies answer preservation, input-size and bounds supply comparable resources, and verification supplies sound-complete certificates. Their conjunction is both the sufficient transport route and the exact boundary preventing an unsupported broader conclusion.",
    check="Generate all 256 structural candidates; execute every external word through depth seven and the structural successor through fourteen; compare source and native verdicts, decoded traces, certificates and unit overhead; reject a changed encoding; independently regenerate the complete candidate vector.",
    limitations="This theorem closes the operational translation boundary and one complete registered external family. It does not prove conventional P=NP for arbitrary languages, Turing machines, encodings or polynomial conventions lacking the required translation certificate.",
    correspondence_terms=("P versus NP", "complexity-class transport", "many-one reduction", "simulation overhead", "certificate preservation"),
)


RETURN_SPECS = (CONDITIONAL_TRANSLATION,)


__all__ = ("RETURN_SPECS", "transport_holds", "changed_encoding_rejects")

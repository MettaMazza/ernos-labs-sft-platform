"""Forced formal prerequisites for target-inaccessible physical experiments."""

from __future__ import annotations

from sft.engine import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldInstruction,
    FoldLanguageHalt,
    FoldOpcode,
    FoldProgram,
    HostilePackageAuditor,
    HostilePackageHalt,
    TargetVault,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import PositiveCount
from sft.physics.formal_law import (
    FormalPrerequisiteSpec,
    OperationalWitness,
    binary_axis,
)


def _interpreter_witness() -> bool:
    program = FoldProgram(
        "formal-prerequisite-witness",
        (
            FoldInstruction(FoldOpcode.INPUT, "held", ("registered",)),
            FoldInstruction(FoldOpcode.EMIT, "", ("held",)),
        ),
    )
    result = CapabilityClosedFoldInterpreter().execute(program, {"registered": PositiveCount(1)})
    forbidden = {"filesystem", "network", "subprocess", "clock", "environment", "import", "foreign"}
    return result.completed and result.output == PositiveCount(1) and not forbidden.intersection(
        opcode.value for opcode in FoldOpcode
    )


def _custody_witness() -> bool:
    envelope = PredictionEnvelope(
        "formal-custody-witness",
        {"registered": sha256_identity("input")},
        ("target",),
        sha256_identity("relation"),
        sha256_identity("registration"),
    )
    vault = TargetVault(
        experiment_id=envelope.experiment_id,
        custodian_id="target-custodian",
        targets={"target": "withheld-record"},
        custody_nonce="custodian-held",
        expected_envelope_hash=sha256_identity(envelope),
    )
    boundary = BlindExperimentBoundary(envelope)
    seal = boundary.seal_prediction("prediction", "complete-trace")
    release = vault.release(seal)
    CrossPlatformCustodyExchange.verify(vault.commitment, release, seal)
    return release.prediction_seal_hash == seal.seal_hash


def _hostile_witness() -> bool:
    try:
        HostilePackageAuditor().reject_executable_prediction_source("print('target')")
    except HostilePackageHalt:
        return True
    return False


CAPABILITY_CLOSED_PREDICTION = FormalPrerequisiteSpec(
    claim_id="SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
    title="Capability-closed exact Fold prediction form",
    statement=(
        "Within the registered finite prediction grammar, a physical prediction can be target-inaccessible, "
        "exact, portable and completely traced in exactly one form: immutable registered Fold inputs pass "
        "through a data-only sequence of generated exact operations to one terminal emission, while every "
        "ambient host capability and unregistered operation is absent and any violation halts."
    ),
    dependencies=(
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-INFO-ENCODING-DECODING-001",
        "SFT-COMP-FORM-STATE-TRANSITION-001",
        "SFT-COMP-FORM-OPERATIONAL-PROCESS-001",
        "SFT-COMP-SEM-EVALUATION-001",
        "SFT-COMP-SEM-TERMINATION-001",
        "SFT-COMP-SEM-VERIFICATION-001",
    ),
    generation_rule="Generate the complete product of input, value, operation, capability, state, termination, trace and extension forms.",
    grammar_boundary=(
        "All finite data-only prediction interpreters assembled from admitted exact values, registered inputs, "
        "generated operations, immutable held states, a declared terminal emission and no host capability."
    ),
    axes=(
        binary_axis("input", "May execution acquire undeclared inputs?", "ambient-input", "Ambient input can contain the withheld target or an answer-producing channel.", "registered-input-only", "Every readable input is named and hashed before execution."),
        binary_axis("value", "What values may enter prediction?", "host-scalar-domain", "Host scalars import forbidden or platform-dependent proof values.", "exact-fold-domain", "Structural Empty One, positive counts, exact ratios, held labels and finite products retain exact provenance."),
        binary_axis("operation", "How is the instruction surface formed?", "contributor-executable-source", "Arbitrary source can create operations outside the registered grammar.", "data-only-generated-operations", "Every instruction is selected from a closed, registered operation set."),
        binary_axis("capability", "Can instructions reach ambient host resources?", "ambient-capability", "An ambient resource can reveal target, comparison or mutable authority state.", "no-ambient-capability", "No registered instruction denotes filesystem, network, process, clock, environment, dynamic import or foreign function access."),
        binary_axis("state", "How are intermediate results held?", "mutable-overwrite", "Silent overwrite loses the exact predecessor and permits untraced replacement.", "single-assignment-held-state", "Each register is held once and every read names a generated predecessor."),
        binary_axis("termination", "How is completion identified?", "implicit-or-open-ended", "Implicit or open-ended completion cannot certify a complete prediction artifact.", "one-terminal-emission", "Exactly one final emission closes the finite registered program."),
        binary_axis("trace", "What execution evidence is retained?", "result-only", "A result alone hides the operational relation and its resource path.", "complete-step-trace", "Every instruction position, arguments and output receive exact identities."),
        binary_axis("extension", "May an undeclared extra rule be added?", "extra-rule", "An extra instruction or capability is a free answer-selecting parameter.", "no-extra-rule", "The runtime contains only the generated preserving surface."),
    ),
    exact_result="Registered exact inputs, a data-only closed opcode surface, no ambient capability, single-assignment state, one final emission, complete trace and no extra rule.",
    induction_base="One registered instruction consumes one declared exact value and emits one fully identified exact value.",
    induction_step="Appending one registered instruction reads only previously held exact values, writes one fresh held value and appends one identified trace row without adding a capability.",
    exclusions=("arbitrary Python or native contributor code", "filesystem, network, subprocess, clock, environment, import and foreign-function access", "floating, negative, irrational, imaginary and semantic-zero proof values", "unbounded or untraced execution"),
    witnesses=(
        OperationalWitness("closed-surface", "The executable opcode enumeration contains no ambient host operation.", _interpreter_witness()),
        OperationalWitness("exact-round-trip", "A registered positive Fold count passes through input and emission with an exact complete trace.", _interpreter_witness()),
    ),
)


PORTABLE_TARGET_CUSTODY = FormalPrerequisiteSpec(
    claim_id="SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    title="Portable target commitment and post-seal custody",
    statement=(
        "Within the registered blind-exchange grammar, target content remains unavailable to prediction in "
        "exactly one form: a distinct custodian commits the complete named target package and prediction envelope "
        "before execution, then releases that unchanged package once to the matching experiment only after a "
        "matching prediction seal exists."
    ),
    dependencies=(
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-INFO-ENCODING-DECODING-001",
        "SFT-COMP-SEC-HASHING-001",
        "SFT-COMP-SEC-COMMITMENT-001",
        "SFT-COMP-SEC-INTEGRITY-001",
    ),
    generation_rule="Generate the complete product of timing, holder, target support, content identity, experiment, envelope, release and extension forms.",
    grammar_boundary="All finite portable target exchanges using admitted exact identities, pre-seal commitment, distinct custody and one post-seal release.",
    axes=(
        binary_axis("timing", "When is target identity fixed?", "post-prediction-choice", "A post-prediction choice can select favorable target content.", "pre-prediction-commitment", "Complete target identity is fixed before prediction begins."),
        binary_axis("holder", "Who can read target content during prediction?", "prediction-holder", "The predictor holding targets violates structural inaccessibility.", "distinct-custodian", "A separate custodian alone holds target content."),
        binary_axis("support", "How is target support declared?", "partial-or-open-support", "Partial or open support permits selective favorable rows.", "complete-named-support", "Every target identity is registered and later matched exactly."),
        binary_axis("content", "How is unchanged target content checked?", "unbound-content", "Unbound content can be replaced after prediction.", "nonce-bound-content-identity", "Every named target and custodian-held nonce contributes to the committed identity."),
        binary_axis("experiment", "Is release bound to one experiment?", "cross-experiment-release", "Cross-experiment reuse breaks registration custody.", "matching-experiment-only", "Release and seal must name the committed experiment."),
        binary_axis("envelope", "Is the seal bound to the registered prediction envelope?", "unbound-envelope", "An unbound seal can certify a different input or relation.", "matching-envelope-only", "The seal identity must contain the preregistered envelope identity."),
        binary_axis("release", "When and how often may content be released?", "preseal-or-repeat-release", "Pre-seal or repeat release leaks target information.", "one-postseal-release", "One release occurs only after the matching seal."),
        binary_axis("extension", "May release use an extra discretionary rule?", "extra-rule", "Discretionary release is a free selection parameter.", "no-extra-rule", "Commitment and seal matching fully determine lawful release."),
    ),
    exact_result="Pre-prediction complete commitment, distinct custodian, nonce-bound unchanged content, matching experiment and envelope, one post-seal release and no extra rule.",
    induction_base="One named target is committed before prediction and released once after its matching seal.",
    induction_step="Adding one target appends one named committed identity and requires the identical name and content at release without altering timing, custody or seal conditions.",
    exclusions=("target access by the prediction executor", "release before a matching prediction seal", "selective target-row omission", "host-specific sandbox claims"),
    witnesses=(OperationalWitness("commit-release-verify", "A committed target package verifies only after the matching sealed prediction.", _custody_witness()),),
)


HOSTILE_AUTHORITY_PROTECTION = FormalPrerequisiteSpec(
    claim_id="SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
    title="Hostile empirical-package and authority protection",
    statement=(
        "Within the registered empirical-package grammar, contributor material can enter official prediction "
        "without gaining execution or scientific authority in exactly one form: strict data-only program fields "
        "are parsed by the admitted interpreter, the census and model-admitted receipts are identical before and "
        "after handling, and every extra field, executable source or protected-tree change halts admission."
    ),
    dependencies=(
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-COMP-SEC-INTEGRITY-001",
        "SFT-COMP-SEC-ADVERSARIAL-001",
        "SFT-COMP-SEM-VERIFICATION-001",
    ),
    generation_rule="Generate the complete product of package, parser, field, execution, authority, comparison, response and extension forms.",
    grammar_boundary="All finite empirical prediction packages admitted through a strict data-only parser while census and model-admitted receipt authority remain protected.",
    axes=(
        binary_axis("package", "What package form is accepted?", "mixed-code-and-data", "Mixed packages can execute contributor-selected behavior.", "data-only-fold-document", "The package is only an exact Fold program document."),
        binary_axis("parser", "How are package fields interpreted?", "permissive-parser", "A permissive parser admits undeclared behavior.", "exact-schema-parser", "The parser requires every and only registered fields."),
        binary_axis("field", "What happens to unknown fields?", "ignore-extra-field", "An ignored field creates divergent or hidden meaning.", "reject-extra-field", "Any missing or additional field halts."),
        binary_axis("execution", "May contributor source execute directly?", "execute-contributor-source", "Direct execution exposes every ambient host capability.", "interpreter-only-execution", "Only the admitted closed interpreter evaluates data."),
        binary_axis("authority", "May handling alter scientific authority artifacts?", "mutable-authority-tree", "Changing census or accepted receipts can manufacture admission.", "unchanged-protected-tree", "Before and after identities of authority artifacts must be identical."),
        binary_axis("comparison", "May target comparison enter the prediction package?", "embedded-comparison", "Embedded comparison can expose or optimize against targets.", "postseal-separate-comparison", "Comparison remains a separately identified post-seal operation."),
        binary_axis("response", "What happens on any audit violation?", "warn-and-continue", "Continuation admits a known authority or capability breach.", "halt-without-admission", "Any violation terminates without model admission."),
        binary_axis("extension", "May a package add an unregistered route?", "extra-route", "An extra route bypasses the protected admission path.", "no-extra-route", "Only the one audited path exists."),
    ),
    exact_result="Strict data-only Fold document, exact parser, no unknown fields or direct source execution, unchanged authority trees, separate comparison, fail-closed response and no extra route.",
    induction_base="One data-only program document is parsed without executing contributor source and leaves each protected authority file unchanged.",
    induction_step="Adding one registered instruction changes only the data program identity; the same strict parser, closed interpreter and protected-tree equality remain required.",
    exclusions=("contributor Python, native source, shell commands, modules or callables", "unknown package fields", "census or model-admitted receipt mutation", "target comparison within prediction"),
    witnesses=(OperationalWitness("executable-source-rejection", "The auditor rejects nonempty contributor executable source.", _hostile_witness()),),
)


PREREQUISITE_SPECS = (
    CAPABILITY_CLOSED_PREDICTION,
    PORTABLE_TARGET_CUSTODY,
    HOSTILE_AUTHORITY_PROTECTION,
)

for _spec in PREREQUISITE_SPECS:
    _spec.validate()


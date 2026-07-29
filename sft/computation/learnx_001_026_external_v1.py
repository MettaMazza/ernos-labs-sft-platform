"""Post-registry exact execution validator for LEARNX-001 through LEARNX-026."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_learnx_001_026_target_registry_v1.json"
REGISTRY_HASH = "sha256:19e34ff63a50c72aa97a08754c9c4593dfeb67ecfb5e58f2fe9cbd1865be7326"
VECTOR = "experiments/external_sources/computation/learnx_001_026_observation_vector_v1.json"
VECTOR_HASH = "sha256:d7e326483d08141806b1df2e3c7bc2d6326e9e1085a1c73a3624463f4c2627b3"
FALSIFICATION = "Reject if the value-free registry, example or target identity, hypothesis support, update, held-out or adverse row, shift or application boundary, exact trace, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def LearningObservationValidator(root, spec):
    return CompleteFieldObservationValidator(root, spec, "LEARNX", REGISTRY, REGISTRY_HASH, VECTOR, VECTOR_HASH, "classical-computation-learnx-observer-v1", FALSIFICATION)

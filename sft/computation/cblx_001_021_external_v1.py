"""Post-registry exact execution validator for CBLX-001 through CBLX-021."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_cblx_001_021_target_registry_v1.json"
REGISTRY_HASH = "sha256:b981e1e4bbb339bd056b68531b0b8975e6d470e8051ad810b494e93e460dbcf1"
VECTOR = "experiments/external_sources/computation/cblx_001_021_observation_vector_v1.json"
VECTOR_HASH = "sha256:0407601e028c69a46a2c9ee00508dcf08a1b710f5111bad74052bbfc7b6d356c"
FALSIFICATION = "Reject if the value-free registry, complete description grammar, exact execution, self-application record, finite boundary, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def ComputabilityObservationValidator(root, spec):
    return CompleteFieldObservationValidator(root, spec, "CBLX", REGISTRY, REGISTRY_HASH, VECTOR, VECTOR_HASH, "classical-computation-cblx-observer-v1", FALSIFICATION)

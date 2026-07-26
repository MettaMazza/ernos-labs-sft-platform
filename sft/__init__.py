"""Accessible host package for the third SFT clean-room reconstruction.

Scientific modules enter only through registered claim packages and the
repository constitution. The current programme is reconciling every registered
V1/V2 result against independently admitted V3 evidence.
"""

from sft.engine_seal import ENGINE_SEAL_ID, require_engine_seal


# This executes before Python can import ``sft.engine``.  It hashes the actual
# runtime files, not merely HEAD, and halts the whole SFT package on any drift.
ENGINE_SEAL_ATTESTATION = require_engine_seal()

__all__ = [
    "BUILD_GENERATION",
    "BUILD_PHASE",
    "ENGINE_SEAL_ATTESTATION",
    "ENGINE_SEAL_ID",
]

BUILD_GENERATION = "v3-python-accessible"
BUILD_PHASE = "global-lineage-and-categorical-ownership-reconciliation"

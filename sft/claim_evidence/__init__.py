"""Claim-side evidence helpers consumed by the frozen admission engine.

This package has no authority to admit claims, write the model census, or
alter engine receipts.  It supplies exact prediction, custody, and hostile-
package evidence objects to the byte-frozen ``sft.engine`` validation kernel.
"""

from sft.claim_evidence.custody import (
    CrossPlatformCustodyExchange,
    CustodyHalt,
    TargetCommitment,
    TargetRelease,
    TargetVault,
    target_identity_from_release,
)
from sft.claim_evidence.fold_language import (
    EMPTY_ONE,
    CapabilityClosedFoldInterpreter,
    EmptyOne,
    FoldExecution,
    FoldInstruction,
    FoldLanguageHalt,
    FoldOpcode,
    FoldPair,
    FoldProgram,
    FoldTable,
    FoldTraceRow,
    FoldWord,
    PositiveRatio,
    fold_program_from_mapping,
    fold_value_from_mapping,
)
from sft.claim_evidence.hostile import (
    HostilePackageAuditor,
    HostilePackageHalt,
    PackageAuditCertificate,
    ProtectedTreeSnapshot,
    snapshot_protected_tree,
)

__all__ = [
    "EMPTY_ONE",
    "CapabilityClosedFoldInterpreter",
    "CrossPlatformCustodyExchange",
    "CustodyHalt",
    "EmptyOne",
    "FoldExecution",
    "FoldInstruction",
    "FoldLanguageHalt",
    "FoldOpcode",
    "FoldPair",
    "FoldProgram",
    "FoldTable",
    "FoldTraceRow",
    "FoldWord",
    "HostilePackageAuditor",
    "HostilePackageHalt",
    "PackageAuditCertificate",
    "PositiveRatio",
    "ProtectedTreeSnapshot",
    "TargetCommitment",
    "TargetRelease",
    "TargetVault",
    "fold_program_from_mapping",
    "fold_value_from_mapping",
    "snapshot_protected_tree",
    "target_identity_from_release",
]

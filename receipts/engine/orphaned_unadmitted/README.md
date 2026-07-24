# Orphaned engine executions

Files in this directory are preserved byte-for-byte execution records that did
not enter `census/claims.json`. They are not model dependencies.

`SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003-20fd69edc390c001.json` was emitted
by a second execution while the already admitted 4,096-form execution was still
materializing. The repository correctly rejected the second census admission
because the claim already had receipt
`sha256:ee6b271f050a867fbe8d5ddcd10e7dba7f7ccba227b4094efbd5c6e2b48741fb`.
The temporary second grammar was not admitted, was not used as a dependency,
and its record is retained here rather than deleted or represented as current.
The current source is restored to the admitted 4,096-form grammar.

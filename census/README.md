# Fundamental knowledge census

`claims.json` is the machine-readable global index. It begins empty because
earlier-corpus claims are not automatically admitted into v3.

Every future row must identify its claim package, status, exact boundary and
dependencies.

Do not edit admitted rows manually. `EngineRepository` writes them only from a
closed, externally validated `SFTAdmissionEngine` receipt. Rejected and
conditional receipts remain outside the authoritative claim list.

# Engine receipts

Only a receipt referenced by `census/claims.json` carries current dependency
authority. The provisional root receipt under `prebaseline/` is retained as
migration evidence: it predates the addition of independently validated
implementation and certificate identities to the engine receipt. It is
intentionally absent from the census and cannot become a dependency.

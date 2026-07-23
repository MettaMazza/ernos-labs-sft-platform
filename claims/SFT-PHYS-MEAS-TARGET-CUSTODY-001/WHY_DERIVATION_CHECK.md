# Portable target commitment and post-seal custody

Claim: `SFT-PHYS-MEAS-TARGET-CUSTODY-001`

## Exact statement

Within the registered blind-exchange grammar, target content remains unavailable to prediction in exactly one form: a distinct custodian commits the complete named target package and prediction envelope before execution, then releases that unchanged package once to the matching experiment only after a matching prediction seal exists.

## Generated grammar and uniqueness

All finite portable target exchanges using admitted exact identities, pre-seal commitment, distinct custody and one post-seal release.

The registered product exhausts every combination of the eight declared binary
axes, giving exactly 256 named forms. A form survives only when every axis
retains target inaccessibility, exact provenance, complete evidence and
fail-closed authority. Therefore the sole survivor is:

`pre-prediction-commitment__distinct-custodian__complete-named-support__nonce-bound-content-identity__matching-experiment-only__matching-envelope-only__one-postseal-release__no-extra-rule`

- `timing`: `pre-prediction-commitment` is the only preserving choice; `post-prediction-choice` — A post-prediction choice can select favorable target content.; `pre-prediction-commitment` — Complete target identity is fixed before prediction begins.
- `holder`: `distinct-custodian` is the only preserving choice; `prediction-holder` — The predictor holding targets violates structural inaccessibility.; `distinct-custodian` — A separate custodian alone holds target content.
- `support`: `complete-named-support` is the only preserving choice; `partial-or-open-support` — Partial or open support permits selective favorable rows.; `complete-named-support` — Every target identity is registered and later matched exactly.
- `content`: `nonce-bound-content-identity` is the only preserving choice; `unbound-content` — Unbound content can be replaced after prediction.; `nonce-bound-content-identity` — Every named target and custodian-held nonce contributes to the committed identity.
- `experiment`: `matching-experiment-only` is the only preserving choice; `cross-experiment-release` — Cross-experiment reuse breaks registration custody.; `matching-experiment-only` — Release and seal must name the committed experiment.
- `envelope`: `matching-envelope-only` is the only preserving choice; `unbound-envelope` — An unbound seal can certify a different input or relation.; `matching-envelope-only` — The seal identity must contain the preregistered envelope identity.
- `release`: `one-postseal-release` is the only preserving choice; `preseal-or-repeat-release` — Pre-seal or repeat release leaks target information.; `one-postseal-release` — One release occurs only after the matching seal.
- `extension`: `no-extra-rule` is the only preserving choice; `extra-rule` — Discretionary release is a free selection parameter.; `no-extra-rule` — Commitment and seal matching fully determine lawful release.

No axis is a fitted parameter: both alternatives are generated before
execution and the dependencies reject the non-preserving alternative.

## Operational witnesses

- `commit-release-verify`: A committed target package verifies only after the matching sealed prediction.

The One base is: One named target is committed before prediction and released once after its matching seal.

The successor certificate is: Adding one target appends one named committed identity and requires the identical name and content at release without altering timing, custody or seal conditions.

## Boundary

- target access by the prediction executor
- release before a matching prediction seal
- selective target-row omission
- host-specific sandbox claims

This is a formal prerequisite for empirical work. It is not itself a claim that
nature follows any physical relation. Four adverse controls and a separate
standard-library validator regenerate the full product and its sole survivor.

# Engine-backed claim implementation

A claim package supplies a `DerivationProgram`, a separate
`IndependentValidator`, and—when registered as empirical—an
`EmpiricalValidator`.

The engine itself calls the generator, decides every generated candidate, runs
all four mandatory control classes, seals the result and passes that exact seal
to the independent validator. Claim code never writes itself into the census.

Use `program_template.py` as an interface reminder. Replace every placeholder;
an unimplemented method must halt rather than return a desired answer.

This Python interface is appropriate for authored formal claim packages. Do not
execute an untrusted contributed Python package. An official empirical
prediction additionally requires the portable capability-closed interpreter
and separate target custody described in `docs/ENGINE_AUTHORITY.md`.

# One portable host system

## Supported systems

The v3 baseline supports macOS, Windows and Linux through one Python-standard-
library interface. These are hosts for the reconstruction, not three scientific
implementations. Host identity may appear in a receipt as implementation
metadata but cannot change a generator, candidate, proof, control, result or
admission decision.

The common validation command is:

```text
python -m sft verify-all
```

Use the command name that launches Python 3 on the local machine. No POSIX shell,
PowerShell script, Docker runtime, notebook or third-party Python package is
part of the baseline route.

## Unified boundaries

- Paths use `pathlib` and repository-relative portable identities.
- Child processes receive argument vectors, never host-shell expressions.
- Only launch-essential environment variables are copied to independent
  validators; arbitrary variables and credentials are excluded.
- Atomic receipt and census writes use standard-library temporary files followed
  by same-directory replacement.
- Canonical JSON and SHA-256 identities are identical across hosts.
- Exact mathematical values never depend on machine floats or native word size.
- Official blind prediction uses capability closure and separate target custody,
  not a host-specific sandbox.

## What the baseline does not claim

Python cannot certify identical system-wide network or filesystem isolation for
arbitrary native programs on all supported systems. The engine therefore does
not use a boolean promise as proof of such isolation. Official prediction code
must run in the registered capability-closed Fold interpreter, whose language
has no operation for those resources. The current interpreter implementation
remains infrastructure until its form is separately derived and admitted
through the engine.

The repository includes a continuous-validation matrix for the three host
families. A passing matrix establishes implementation portability of the tested
engine version; it does not establish a scientific derivation.

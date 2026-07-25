# Smithian Fold Calculator completion audit

Date: 2026-07-25
Scope: calculator only; Physics and all later branches remain paused.

## Immutable admitted baseline

`SFT-MATH-SCIENTIFIC-CALCULATOR-005` is an independently replicated,
depth-independent admission over its declared 8,192-form grammar. Its source,
receipt and materialized evidence are retained unchanged.

That admission does not by itself satisfy the later, stricter instruction that
the calculator be fully realised as a general-user application and 100% tested.
The first measured branch-coverage run over the complete calculator package was
65%, despite all 23 focused tests passing. Therefore 005 is a valid baseline,
not the completion claim.

## Completion contract for the next version

The completion version must pass all of the following without editing the
frozen admission engine or any 005 source.

1. Ordinary arithmetic interaction
   - digits, exact decimals and scientific notation;
   - parentheses, four arithmetic operations, powers, postfix factorial and
     percent;
   - terminal equals, answer chaining, unary result application, clear-entry,
     all-clear and backspace.
2. Scientific operation surface
   - powers and roots;
   - circular, inverse-circular, hyperbolic and inverse-hyperbolic functions;
   - exponential and all declared logarithms;
   - combinatorics, exact aggregate statistics and whole-count utilities;
   - typed orthogonal-fibre construction and conjugation.
3. Exact SFT value discipline
   - empty-One rather than a stored numerical zero;
   - held orientation rather than negative proof magnitudes;
   - positive rational proof scalars only;
   - certified rational enclosures rather than irrational or imaginary proof
     scalars;
   - mandatory halt on invalid domains, exhausted resources or unclosed output.
4. Familiar application behavior
   - keyboard and button entry share one evaluator;
   - RAD, DEG and GRAD are explicit;
   - Ans, MC, MR, MS, M+ and M- preserve typed state;
   - ordered history can be restored and cleared;
   - readable result, exact value, certificate, proof trace and resources are
     all visible;
   - every declared function is discoverable in the app;
   - embedded learning guidance explains the notation and evidence.
5. Accessibility and portability
   - Python standard library runtime only;
   - macOS, Windows and Linux launch paths;
   - terminal interface remains available when the graphical library is absent;
   - installable `sft-calculator` command plus repository launchers.
6. Safety and scale
   - extreme counted input is checked before expensive construction;
   - large circular arguments use certified periodic reduction;
   - no NaN, infinity, floating transcendental or host random answer can enter
     an admitted result;
   - all limits halt explicitly and retain the attempted expression.
7. Verification
   - unit tests for every exact value and operation branch;
   - parser and expression-machine integration tests;
   - session and pure UI-controller state tests;
   - headless graphical-adapter tests plus an available-display smoke test;
   - terminal and launcher end-to-end tests;
   - unfavorable/tampered/boundary controls;
   - 100% statement and branch coverage over the declared active calculator
     implementation, with the exact measured file set recorded;
   - fresh frozen-engine admission, complete enumeration, independent replay
     and immutable receipt.

## Gaps found after 005 admission

- Result chaining was available through typed `Ans`, but ordinary button
  presses did not automatically use the displayed answer.
- Clear-entry was not separate from all-clear.
- Several parser-supported functions were documented but not directly
  discoverable from the visible app controls.
- Extreme numeric exponents and counted operations needed earlier fail-closed
  resource checks.
- Large circular inputs needed certified periodic reduction rather than relying
  only on a direct power series.
- Repository users had one terminal command but no dedicated Windows, macOS and
  Linux click/launch files or installed calculator command.
- The focused passing test suite did not provide complete statement and branch
  coverage.

These gaps require a new versioned claim. They must not be repaired by changing
the admitted 005 files in place.

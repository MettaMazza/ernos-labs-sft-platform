# Smithian Fold Scientific Calculator

This is the complete, accessible calculator application for the current
Smithian Fold Theory Mathematics branch. The first screen behaves like a
familiar scientific calculator. Exact Fold evidence, the complete function
library and the registered Mathematics law explorer remain one click away.

The application has no runtime dependency outside Python's standard library.
It runs on macOS, Windows and Linux.

## Open the app

From the repository folder:

```text
python3 -m sft.mathematics.calculator_complete --gui
```

After installing the repository, the shorter command is:

```text
sft-calculator
```

Repository launchers are also supplied:

- macOS: `launchers/Launch Smithian Calculator.command`
- Windows: `launchers/Launch Smithian Calculator.bat`
- Linux: `launchers/launch-smithian-calculator.sh`

## Ordinary use first

Type or press `1 + 1 =`. The large screen returns `2`.

The default window contains the controls people expect: numbers, decimal
point, parentheses, four arithmetic operations, powers, roots, percent,
factorial, sign, equals, backspace, clear-entry, all-clear, memory, previous
answer and RAD/DEG/GRAD selection. Results automatically chain through `Ans`.

`Show SFT proof` opens history, exact evidence, the complete function list and
the Mathematics explorer. `Learn SFT` gives a plain-language guide. Those
panels are hidden during ordinary use so the proof system never makes the
calculator intimidating.

## Scientific expression language

The parser accepts exact integers, decimal notation, scientific notation,
parentheses, `+`, `-`, `*`, `/`, `^`, `!`, `%`, and optional terminal `=`.

Functions:

```text
abs recip sqrt cbrt root pow
sin cos tan asin acos atan
sinh cosh tanh asinh acosh atanh
exp ln log log10 log2
ncr npr complex conj
sum prod mean variance stddev
floor ceil gcd lcm mod hypot
```

Constants and retained state:

```text
pi tau e phi empty ans mem
```

Examples:

```text
0.1 + 0.2 =
2^(1/3)
2^pi
sqrt(pi)
sin(30)             # DEG mode
log(8, 2)
mean(1, 2, 3, 4)
stddev(1, 2, 3)
complex(2,3) * complex(2,-3)
```

Large circular arguments are reduced by an exact whole number of certified
turns before their rational recurrence executes. No host sine, cosine or
tangent routine supplies a proof value.

## The SFT value boundary

The screen accepts conventional notation because it is a human interface. The
proof value behind the screen obeys the SFT Mathematics law:

- displayed `0` translates to the structural empty-One form; a numerical zero
  is not stored as a proof scalar;
- conventional negative notation translates to a held orientation and an
  exact positive magnitude;
- every scalar magnitude is an exact positive `Fraction`;
- typed real and orthogonal Fold fibres replace an imaginary proof scalar;
- non-rational roots, circle values, exponentials, logarithms and circular or
  hyperbolic functions remain exact rational lower/upper enclosures with a
  replayable certificate;
- no NaN, infinity, floating transcendental or host-random value enters an
  answer;
- invalid domains, unclosed enclosures and exhausted counted resources raise a
  mandatory `CalculatorHalt` and return no value.

Projection precision and operation limits are counted interface/resource
boundaries, not fitted scientific parameters. They cannot change a law or
select an answer.

## Proof output

Request a machine-readable exact evaluation:

```text
python3 -m sft.mathematics.calculator_complete "sqrt(2)" --proof
```

The JSON reports:

- the exact expression and typed result form;
- exact fraction or rational enclosure;
- recurrence/enclosure certificate;
- complete operation trace;
- token and operation resources;
- runtime-inspected SFT value constraints;
- calculator claim and admitted dependency;
- official receipt hash when the completion claim is present in the census.

The output explicitly says that a calculation is not a new engine admission.
The calculator evaluates admitted laws. Only the frozen engine can decide that
a proposed new law is fully enumerated, uniquely forced, controlled,
independently validated and admissible.

## Every current Mathematics family

The advanced `Mathematics` tab exposes every registered predecessor in the
current Mathematics branch. A user can read its statement, dependencies,
grammar boundary, exact result, laws, limitations, candidate count and official
receipt, then locally replay its complete generated census and witnesses.

The expression census is one-to-one across all 24 predecessor claims:

- the twelve foundational Mathematics domains retain their structured exact
  operation libraries and a law replay;
- exact relations, number theory, continuum boundaries, algebraic balance,
  finite many-body recurrence, floored fluid regularity, prime-pair censuses,
  the Riemann mirror boundary, bounded Collatz results and self-similar
  convergence retain scalar/certificate evaluation and law replay;
- calculator claims 004 and 005 remain immutable admitted dependencies.

This means all currently registered SFT Mathematics expression families are
reachable without pretending a desktop expression is itself a theorem. A
future lawful Mathematics addition requires a new versioned translation and
cannot silently enter this census.

Terminal exploration is also available:

```text
python3 -m sft.mathematics.calculator_complete --law SFT-MATH-EXACT-ARITHMETIC-001
python3 -m sft.mathematics.calculator_complete --replay-law SFT-MATH-EXACT-ARITHMETIC-001
```

## Verification boundary

The declared active calculator file set includes all inherited exact value,
operation and parser kernels plus every completion application file. Its test
gate requires 100% statement and 100% branch coverage, not just a passing
example suite. It also requires:

- exact unit and property checks;
- expression-machine and session integration;
- pure interaction-controller state checks;
- headless graphical-adapter execution;
- CLI and all three operating-system launcher checks;
- every declared scientific function and domain failure;
- every current Mathematics law summary and local replay;
- adverse controls and complete frozen-engine admission evidence.

The authoritative admission status and receipt are always the rows in
`census/claims.json` and `receipts/engine/`; documentation never overrides
those records.

# Smithian Fold Scientific Calculator

This is a familiar scientific calculator translated into the exact Smithian
Fold Theory value law. It has a clean cross-platform desktop app, an interactive
terminal, exact evidence, memory, history and an embedded learning guide. It
uses only Python's standard library.

## Open the calculator app

From the repository folder, run:

```text
python3 -m sft.mathematics.calculator --gui
```

The app provides:

- an editable expression display and large result display;
- digit, arithmetic, bracket, percent and terminal `=` keys;
- powers, square/cube roots, reciprocal, factorial, permutations and combinations;
- `sin`, `cos`, `tan`, inverse circular and hyperbolic functions;
- RAD, DEG and GRAD modes;
- `ln`, common log, base-two log, arbitrary-base log and exponential functions;
- exact sum, product, mean, population variance and population standard deviation;
- `gcd`, `lcm`, modulo, floor, ceiling and hypotenuse;
- certified `pi`, `tau`, `e` and golden-ratio constants;
- typed real/orthogonal-fibre arithmetic through `complex` and `conj`;
- MC, MR, M+, M-, MS, previous-answer and ordered history controls;
- a readable projected answer, full exact detail, complete proof trace and resource counts;
- an embedded guide explaining how ordinary notation maps to SFT structures.

Keyboard input works as expected. `1+1=` returns `2`; pressing Enter performs
the same terminal action.

## Terminal use

Evaluate one expression:

```text
python3 -m sft.mathematics.calculator "sin(30)=" --angle deg --trace
```

Omit the expression for an interactive session. Type `:help` to see angle,
memory and history commands.

## Expression reference

The parser accepts exact integers, decimals, fractions, scientific notation,
parentheses, `+`, `-`, `*`, `/`, `^`, `!`, `%`, and an optional terminal `=`.

Named functions:

```text
abs recip sqrt cbrt root pow
sin cos tan asin acos atan
sinh cosh tanh asinh acosh atanh
exp ln log log10 log2
ncr npr complex conj
sum prod mean variance stddev
floor ceil gcd lcm mod hypot
```

`log(value)` is base ten and `log(value, base)` accepts an explicit base.
Constants are `pi`, `tau`, `e`, `phi`, `empty`, `ans` and `mem` where the
last two are session values.

Examples:

```text
0.1 + 0.2 =
2^(1/3)
2^pi
sqrt(pi)
sin(30)          # with --angle deg or DEG selected in the app
atan(1)
log(8, 2)
mean(1, 2, 3, 4)
stddev(1, 2, 3)
complex(2,3) * complex(2,-3)
```

## SFT value law

- Displayed `0` is structural `empty-One`, not a numerical proof scalar.
- A conventional negative is a positive exact magnitude with the
  `counter-held` orientation.
- Entered decimal and scientific notation becomes an exact rational part
  before an operation executes.
- Rational powers are counted roots followed by counted composition.
- Non-rational powers, roots, circular constants and transcendental functions
  are exact rational lower/upper enclosures with replayable finite recurrences
  and positive remainder bounds.
- Conventional complex notation becomes a typed pair of real and orthogonal
  Fold fibres; no imaginary proof scalar enters the model.
- Division by empty-One, singular intervals, invalid domains, unsupported
  types and exhausted resource bounds halt explicitly. No NaN or infinity is
  silently returned.
- Memory and history retain typed values but cannot change an operation law.
- Decimal output is a human-readable projection only. Exact fractions,
  enclosure endpoints and certificates remain the evidence.

## Exact scope

The active expanded law is `SFT-MATH-SCIENTIFIC-CALCULATOR-005`. It depends on
the independently admitted corrected exact core `004` and is run separately
through the frozen admission engine. Claim `003` remains retained as adverse
evidence for its corrected alternating-series parity; it is not an active law.

The explicit feature manifest above is closed. Proprietary calculator-specific
buttons, empirical physical-unit conversion tables and opaque host random
generators are outside this version. They require a separately registered exact
law or empirical source rather than a hidden library shortcut.

# Exact positive finite count

## WHY

The structural One supplies exact self-wholeness, but later partitions and
parts require a lawful way to say how many generated occurrences are present.
Importing conventional natural-number axioms would violate the clean-room
boundary. This claim therefore asks what representation is forced by a
registered nonempty finite generation trace itself.

## DERIVATION

A proposed representation is classified by whether it retains none, a proper
collection, or all generated occurrences; whether every retained occurrence
appears once or at least one is duplicated; and whether material outside the
registered trace is added. The grammar generates all meaningful combinations:
two no-coverage forms and four forms for each of proper and complete coverage.

No coverage does not represent the registered nonempty trace. Proper coverage
omits a generated occurrence. Duplication changes the trace. Extra material is
ungenerated. Only `complete-coverage__once__no-extra` retains the entire trace
exactly.

The depth-independent certificate has a base and successor form. The structural
One is the nonempty base. Appending one newly generated occurrence makes the
prior trace proper coverage of the extension; retaining the new terminal once
restores completeness. The same classification therefore holds after every
finite generated extension without forming a completed infinite object.

## CHECK

The declared grammar contains ten generated representation classes. Every class
receives a decision and proof identity. The controls reject absent coverage,
source drift, duplicated occurrences and attempts to cross the positive finite
boundary. A standalone implementation independently regenerates the grammar and
must reject any altered second survivor.

This result establishes count identity only. Equal partitions, exact parts and
Fold operations remain separate downstream obligations.

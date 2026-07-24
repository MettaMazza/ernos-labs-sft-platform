# Unrestricted native Fold Busy-Beaver law

Claim: `SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002`

## WHY

V2 Step 404 asserts an unrestricted theorem over the native Fold grammar; a bounded table or generic halting law does not close that same-strength value.

## DERIVATION

The admitted machine has only the unique depth-lowering edge on a closing path. Complete word generation supplies the upper bound; any depth-k word supplies the equal lower witness; the label-prepending successor makes the equality depth-independent.

Boundary:

> Every positive finite native Fold description built only from generated fibre-label words, lawful depth-lowering Fold edges and separately registered recurrent period-b processes.

The complete grammar contains 256 candidates across eight binary axes. Exactly one retains every requirement.

- `grammar` -> `complete-native-fold-descriptions`: Every generated native word through the supplied depth occurs.
- `transition` -> `one-lawful-depth-lowering-edge`: One Fold edge closes exactly one word position.
- `halting` -> `exact-empty-one-terminal-trace`: The complete suffix trace reaches structural empty One.
- `maximum` -> `complete-upper-and-attaining-lower-witness`: All runs give the upper bound and a depth-k word attains it.
- `recurrence` -> `separate-exact-nonhalting-certificate`: The period-b return is classified outside the closing maximum.
- `successor` -> `prepend-one-label-successor`: Prepending one label adds exactly one lawful transition and one maximum unit.
- `evidence` -> `all-process-traces-and-attainment`: Every closing description retains its exact trace and the longest witness.
- `addition` -> `no-extra-machine-premise`: The result is internal to the already-derived native Fold machine.

Forced result:

> The unique complete kernel forces BB_F(k)=k for every supplied positive finite k in the admitted native Fold closing grammar, with recurrent processes separately certified nonhalting.

Operational laws:

- every closing edge lowers exact word depth once
- every native closing word of depth at most k halts within k
- a depth-k word attains k
- prepending one fibre label increments the maximum by one
- recurrent period-b processes never enter the closing maximum

Base:

> At the first positive depth, either fibre label reaches structural empty One in one lawful edge, so BB_F(One)=One.

Successor:

> Prepending one generated fibre label to every depth-k word creates all depth-(k+1) words and adds exactly one mandatory closing edge; no shallower word exceeds that trace.

## CHECK

Enumerate every native closing word through depth fourteen, retain every suffix trace, prove the upper and attaining lower bounds, test the recurrent exclusion, exhaust 256 structural candidates and independently regenerate the decision vector.

- `depths-through-fourteen`: Complete native populations through depth fourteen attain their exact depth and no run exceeds it.
- `first-attains`: The first depth-k word supplies an exact k-edge lower witness.
- `recurrence-boundary`: A two-label recurrent alternation returns after its period without structural empty-One termination.

The false-premise, changed-source, changed-survivor and excluded-boundary controls must all reject. The independent validator regenerates the literal product without importing this scientific module.

## Exact limitation

This theorem is unrestricted over positive finite depth in the admitted native Fold process grammar. It makes no statement about arbitrary external Turing-machine tables.

- no external Turing transition table
- no numerical-zero description depth
- no completed infinite description
- no recurrent process counted as halting
- no claim about conventional Busy Beaver

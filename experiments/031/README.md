# Experiment 031 — Reusable Operator Schema Induction

## Question

Can MORPH induce a reusable, parameterized operator schema from labeled traces without being handed named derived-operator families?

This is deliberately harder than 030:

- 030 selected concrete derived operators from a supplied arithmetic meta-substrate.
- 031 removes those named derived families.
- The learner searches a generic typed AST grammar and must discover reusable schemas whose variable bindings change across independent episodes.

## Protocol

`black-box labeled traces → generic AST search → cross-episode binding → blind holdout → transfer → composite reuse → adversarial gate`

The learner sees states and labels only. It does not receive the hidden semantic rule or the name of the mechanism being learned.

The generic grammar contains only constructors:

`VAR, CONST, ABS, ADD, SUB, EQ, LE`

No family called `near`, `sum`, `absdiff`, or similar is enumerated for selection.

A candidate schema is accepted only when a single parameterized AST shape can be rebound to multiple independent episodes and then survive unseen bindings.

## Verified result

Local deterministic execution produced:

- generic predicate candidates: 11,511
- induced near schema: `abs((s0-s1)) <= 1`
- induced sum schema: `s2 == (s1+s0)`
- near holdout: 1.0
- near transfer: 1.0
- sum holdout: 1.0
- sum transfer: 1.0
- composite transfer: 1.0
- adversarial gate: 1.0
- decoy cross-fit: false

## What changed from 030

031 does not merely choose an instance such as `abs(x1-x2) <= 1`.

It induces a parameterized form such as:

`abs(s0-s1) <= 1`

and later rebinds `s0,s1` to new feature positions.

Likewise, the sum relation is retained as a reusable three-slot schema rather than a fixed `x3+x4==x5` instance.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator with black-box labeled traces.

This does **not** establish unrestricted invention of new primitive mathematical operators. The constructive AST vocabulary is still supplied by the experiment. The stronger claim supported here is reusable operator-schema induction and rebinding from evidence.

## Research value

031 closes an important loophole exposed by 030: the learner is no longer handed a menu of named derived-operator families.

The next pressure point is deeper: can MORPH change the **constructor language itself**, rather than merely synthesize reusable expressions from a fixed constructor set?

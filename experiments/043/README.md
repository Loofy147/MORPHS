# Experiment 043 — Real External Runtime Transfer

## Corrected research question

Can the read-only protocol require explicit capability, authority, provenance, freshness, cross-surface binding, and independent postcondition verification across an external boundary?

## Critical epistemic boundary

043 has two distinct evidence surfaces:

1. A deterministic MORPHS protocol model executed by CI.
2. A host-captured GitHub read observation.

The second is real external evidence, but the 043 experiment module does not invoke GitHub.

Therefore:

- deterministic protocol semantics: EXPERIMENTALLY_SUPPORTED
- MORPHS runtime integration with GitHub read: OPEN
- provider-independent verification: OPEN

## Protocol

DISCOVER -> CLASSIFY -> BIND -> AUTHORIZE -> EXECUTE -> OBSERVE -> INDEPENDENT_READ -> VERIFY_POSTCONDITION -> RECORD

The model protects:

- explicit capability descriptor
- read-only authority
- provenance
- freshness
- repository/path/ref binding
- independent postcondition requirement
- DEFER on disagreement or stale evidence

## Host-captured live observation

A real GitHub read was captured separately using two GitHub surfaces:

- repository contents
- raw content

They matched for the same repository/path/ref and were tied to the recorded commit/blob identity.

This is evidence about the external provider boundary.

It is not evidence that the MORPHS runtime invoked GitHub.

## What 043 establishes

EXPERIMENTALLY_SUPPORTED, within the deterministic protocol-model scope.

## What 043 does not establish

- MORPHS runtime -> GitHub adapter execution
- provider-independent verification
- external mutation safety
- unknown mutation outcome handling in a live provider
- irreversible-effect safety
- real rollback
- provider substitution under contract equivalence

These remain OPEN.

## Preserved audit rule

A live observation may support a claim only at its actual execution surface.

CI success for a deterministic simulator cannot silently upgrade a host-side observation into MORPHS runtime evidence.

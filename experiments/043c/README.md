# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same resource through a second provider surface, and verify content plus provider identity before classifying the observation?

## Why this follows the audit

043 and 043b exposed an important distinction:

host-side GitHub tooling performing an action is not the same evidence as the MORPHS runtime performing that action.

043c tests only that missing bridge.

It deliberately remains read-only.

## Runtime boundary

Provider: GitHub

Operation: read \`README.md\` from \`Loofy147/MORPHS@main\`

Primary surface:
\`api.github.com/repos/.../contents/README.md?ref=main\`

Independent surface:
\`raw.githubusercontent.com/Loofy147/MORPHS/main/README.md\`

The Python experiment invokes both surfaces itself.

## Receipt

Every live invocation records:

- provider
- operation
- HTTP method
- exact API URL
- status
- timestamp
- provider request id when available
- response SHA-256
- derived invocation id

The observation additionally records:

- provider Git blob SHA
- locally computed Git blob SHA
- content SHA-256 from both surfaces

## Verification rule

The live observation is VERIFIED only when:

1. the runtime invocation returns successfully,
2. the API response is a file,
3. the API content decodes successfully,
4. raw content matches byte-for-byte,
5. Git blob identity computed from the observed content matches the provider blob SHA,
6. the receipt is internally complete and hash-bound,
7. repository/path/ref binding remains exact.

Otherwise the experiment fails instead of upgrading the evidence state.

## Epistemic limits

This establishes a stronger claim than 043:

\`MORPHS runtime -> real GitHub read\`

It still does not establish:

- provider-independent verification
- mutation through the MORPHS runtime
- ambiguous network outcome handling
- irreversible effects
- rollback
- distributed transaction semantics
- general capability-registry integration

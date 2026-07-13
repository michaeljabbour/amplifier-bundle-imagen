# Experiment Journal

## 2026-07-13 — Deterministic high-risk behavioral policy gate

**Question:** Can the release gate execute meaningful policy behavior without
paid provider calls or circularly grading scripted assistant prose?

**Method:** Reviewed Amplifier core's `MockTool` and scripted test-provider
patterns plus the local evaluation bundle. Implemented a typed policy executor
for five high-risk facts, an independent event/tool-trace grader, and one unsafe
mutation per policy rule. Bound the rules to production context composition,
semantic anchors, and source hashes.

**Result:** 5/5 baseline cases passed; 5/5 unsafe mutations were rejected; 12
production policy anchors and 4 behavior-composition checks passed. Network and
provider call counts were zero. Evidence is archived at
`evals/results/2026-07-13.json`.

**Limit:** This establishes deterministic reference-policy behavior and grader
sensitivity. It does not establish that every stochastic orchestration model
will comply, and it does not replace credentialed OpenAI/Gemini canaries.

## 2026-07-13 — Credentialed provider canaries and artifact truth

**Question:** Do both independently configured providers still generate a
usable image through the real MCP boundary, and do persisted file facts match
the contract?

**Method:** Initialized `imagen_mcp` 0.4.0 over stdio and sent one bounded,
non-sensitive successful request to each provider. Recorded request IDs,
dimensions, byte counts, SHA-256 digests, usage/cost where available, actual
decoded formats, file modes, and human visual observations without retaining
API keys or full prompt bodies. A Gemini 400 for an unsupported option
combination was treated as non-retryable; the corrected request used only
documented baseline controls.

**Result:** OpenAI request `c20d05083e7c` returned a 1024x1024 JPEG through
`gpt-image-2` and passed visual review. Gemini request `684fa1218f60` returned a
1024x1024 RGB image through `gemini-3.1-flash-image` and passed visual review.
The Gemini bytes were JPEG despite a `.png` path, and both canary files exposed
an inherited `0644` mode. Before release, imagen-mcp was changed to validate
actual response bytes, normalize supported non-PNG Gemini output to genuine
PNG, create files with `0600`, and create new private output directories with
`0700`; mocked real-JPEG and permission regressions pass.

**Limit:** The successful calls establish point-in-time API/MCP compatibility
and bounded visual sanity, not provider uptime or broad aesthetic quality. No
second paid request was made solely to retest deterministic local transforms.

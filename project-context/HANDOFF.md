# Handoff

*Last updated: 2026-07-13 — 2.0.0 release completed*

## Accomplished

- Released the standalone provider server independently as `imagen-mcp`
  `v0.4.0`, with canonical packaging, current OpenAI/Gemini contracts,
  fail-closed routing, private retained state and artifacts, structured errors,
  clean wheel/sdist installation, and Python 3.10–3.14 CI.
- Released this bundle as `v2.0.0` with adaptive Fast, Guided, and Studio
  routes; rights/consent/privacy gates; cost and draft approval; exact-artifact
  refinement; accessibility; lineage; and capability-gated visual QA.
- Replaced the handwritten image transport with an official MCP SDK adapter
  that validates `imagen-mcp >=0.4,<0.5`, discovers a reviewed eight-tool
  allowlist, bounds model-visible output, redacts binary payloads, and owns a
  single initialized lifecycle.
- Kept the repositories strictly independent. The adapter declares no
  imagen-mcp distribution dependency, imports no server implementation, and
  never searches sibling development directories; imagen-mcp has no Amplifier
  dependency. Their only integration boundary is MCP.
- Pinned the remaining skill self-source and all release examples to immutable
  `v2.0.0`; pre-composed variants still use relative namespaced composition so
  they cannot fetch a second drifting copy of this repository.
- Added deterministic schema/static checks, clean adapter-wheel installation,
  cross-repo protocol tests, production policy/hash binding, and a high-risk
  behavioral gate with adversarial mutation checks.
- Ran bounded credentialed OpenAI and Gemini canaries. Both providers returned
  valid, visually inspected images through the real MCP boundary. The canaries
  exposed and drove fixes for private output modes and Gemini JPEG bytes being
  mislabeled as PNG.

## Verification Results

- Bundle static validation passed for 5 YAML files, 2 skills, and 12 workflow
  specifications; Ruff formatting and linting passed.
- Adapter tests: 36 passed, 1 opt-in external-contract test skipped in the
  ordinary suite, and 85.33% line coverage.
- High-risk behavior: 5/5 mock-backed cases passed, 5/5 unsafe mutations were
  rejected, and all 12 policy anchors plus 4 composition checks passed. Dated
  evidence is in `evals/results/2026-07-13.json`.
- Real composition: the official Amplifier validator passed 43/43 checks; the
  loader resolved 14 tools and 43 agents; the explicit cross-repo MCP contract
  passed against the independently initialized server.
- Standalone: 321/321 tests passed locally at 84.35% coverage. GitHub Actions
  run 29259873511 passed Ruff, mypy, tests, coverage, builds, and clean
  wheel/sdist stdio smokes on Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- Live canaries: OpenAI request `c20d05083e7c` and corrected Gemini request
  `684fa1218f60` both returned HTTP 200 and visually matched their bounded safe
  requests. No additional paid call was used to retest deterministic local
  byte normalization or permission changes.

## Remaining Follow-up

- P2 resilience: migrate Gemini's synchronous SDK calls away from a shared
  non-cancellable thread pool so repeated provider hangs cannot exhaust workers
  after local timeouts. This is not a cross-repository dependency.

## Start Here Next Session

1. Verify the tagged release CI remains green and reproduce any reported issue
   from the immutable tag before changing `main`.
2. Preserve the MCP-only boundary when reviewing imagen-mcp 0.5 or later; a
   0.x minor schema change requires an explicit adapter compatibility review.
3. Address the Gemini executor follow-up with cancellation/load tests before
   changing the documented timeout guarantees.

## Non-Obvious Context

- `imagen-mcp/run.sh` contains a user-owned macOS Keychain credential-loading
  change. It was preserved, never staged, and is not part of `v0.4.0`.
- Visual QA cannot be truthfully completed from a path or base64 text. Attach
  exact pixels through a vision-capable client or keep QA pending and obtain
  human approval.
- Google Search grounding is opt-in and must return/display the provider's
  Search Suggestions and source links; unsupported output paths fail closed.

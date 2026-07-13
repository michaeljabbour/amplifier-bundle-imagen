# Changelog

## 2.0.0 — 2026-07-13

### Added

- Adaptive Fast, Guided, and Studio routes.
- User approval and concrete-draft selection gates for Studio work.
- Rights, consent, privacy, moderation, provenance, metadata, and accessibility guidance.
- Machine-readable artifact manifest schema and versioned workflow evaluation specifications.
- Deterministic bundle validator and CI workflow.
- Discovery registration for both bundled skills.
- Cost estimation and batch-generation guidance for the eight-tool live contract.
- Provider-free MCP lifecycle tests, Amplifier protocol validation, an 80%
  coverage gate, and clean-wheel smoke installation.

### Changed

- Both à-la-carte behaviors now mount the native image adapter themselves.
- `tool-imagen` now uses the official MCP SDK for initialization, paginated
  discovery, correlated calls, timeouts, and cleanup; server identity/version,
  tool names, and secret-free schemas fail closed.
- The image server is an independent runtime reached only through MCP. The
  adapter declares no imagen-mcp package dependency, imports no implementation
  modules, and never searches sibling development directories.
- Binary MCP payloads and binary-shaped structured fields are omitted from
  model context, and textual tool output is capped at 128 KiB.
- GPT Image 2 guidance now reflects arbitrary constrained dimensions up to a
  3840px edge, opaque-only output, automatic high-fidelity inputs, and the
  official scene → subject → details → constraints prompt order.
- Gemini guidance uses GA IDs, model-specific reference limits, 1K defaults,
  current size tiers, and SynthID/C2PA provenance facts.
- Refinement branches from a user-selected artifact; every production rerender
  is treated as a new artifact and re-QA'd before delivery.
- Foundation and tool-skills dependencies are pinned where a stable release or
  commit exists. The skill self-source is pinned to this `v2.0.0` release.
- Pre-composed variants compose the pinned foundation and this checkout's
  namespaced image behavior directly instead of fetching a second mutable copy
  of the repository.

### Removed

- Claims that GPT Image 2 supports transparent backgrounds, configurable
  `input_fidelity`, a roughly 1792px ceiling, or pixel-perfect edit isolation.
- Guidance to retry/rephrase blocked requests or remove watermarks.
- Documentation that described only six tools or an unpublished v1.2.0 tag.
- The unsupported direct-provider adapter and implicit sibling-checkout lookup.

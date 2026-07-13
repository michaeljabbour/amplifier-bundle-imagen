# Decision Provenance

## D001 — Adaptive routing

**Decision:** Fast, Guided, and Studio modes replace mandatory delegation.
**Why:** A clear one-shot request should stay fast, while expensive, ambiguous,
identity-sensitive, or public-facing work needs explicit specialist and user gates.

## D002 — Artifacts, not prompts, are approved

**Decision:** Studio users select concrete drafts; refinement branches from the
selected file; every final rerender is a new artifact and is re-QA'd.
**Why:** Reusing a prompt does not reproduce approved pixels.

## D003 — Live MCP schema is authoritative

**Decision:** Prose explains intent, while `tools/list` and mounted schemas own
tool arguments. Static validation rejects known stale claims.
**Why:** Hand-copied schemas caused transport and documentation drift.

## D004 — Current provider facts

**Decision:** GPT Image 2 guidance follows official OpenAI docs; Gemini guidance
uses GA IDs, current limits/defaults, and documented provenance signals.
**Why:** Prior size, transparency, fidelity, model-ID, and reference-limit claims
were obsolete or unsupported.

## D005 — Policy is a workflow gate

**Decision:** Rights, consent, privacy, moderation, accessibility, and provenance
checks run before provider calls and before delivery.
**Why:** Safety and trust cannot be recovered by a disclaimer after generation.

## D006 — Reproducible composition

**Decision:** Use relative sources for bundle-owned modules and pin external
dependencies where a stable release/commit exists. Pin the skill self-source to
the same immutable `v2.0.0` tag as the consuming behavior.
**Why:** A shared immutable tag keeps installed skill discovery reproducible;
the temporary `main` pin was required only before the 2.0.0 tag existed.
Pre-composed variants include the pinned foundation and the local
`imagen:behaviors/imagegen` namespace directly, so they cannot fetch a second,
independently drifting copy of this repository.

## D007 — Protocol-only image-server boundary

**Decision:** `tool-imagen` declares no imagen-mcp package dependency, imports
no server implementation, and never searches sibling development directories.
It launches an independently installed executable or an explicitly configured
checkout and validates the MCP server identity, compatible `>=0.4,<0.5`
version, and reviewed tool allowlist before mounting anything. Because a 0.x
minor release may change model-visible schemas, a new minor requires explicit
adapter review rather than being trusted by name alone.
**Why:** Either repository must be buildable, testable, and releasable without
the other repository's source tree or Python modules.

## D008 — Bounded textual tool results

**Decision:** Binary image/audio content and binary-shaped structured fields are
redacted before entering Amplifier tool output, and each result is capped at
128 KiB. Visual QA remains pending unless exact pixels arrive through a real
vision-capable channel.
**Why:** Base64 in model context is expensive and is not equivalent to visual
access; unbounded MCP output is also a context-exhaustion risk.

## D009 — Deterministic high-risk policy gate

**Decision:** Execute moderation shopping, watermark removal, sensitive child
references, exact-artifact refinement, and visual-QA honesty through a typed
policy executor backed by Amplifier `MockTool` instances. Grade structured
events and tool arguments independently, and inject one unsafe mutation per
rule to prove the grader rejects violations.
**Why:** Amplifier's local mock provider returns scripted model responses, so
grading that prose would be circular. The executable reference policy provides
reproducible release evidence without pretending to prove stochastic-model
compliance or calling paid image providers.

# Project Context

## Current State

**Phase:** Released
**Milestone:** 2.0.0
**Active work:** Maintain the released protocol contract and address the
documented P2 Gemini executor-resilience follow-up without coupling the two
repositories.

## Team

| Person | Role |
|--------|------|
| Repository maintainers | Product and release ownership |
| Codex agents | Implementation, contract tests, provider-fact review, and adversarial QA |

## Recent Milestones

- 2026-07-13 — Replaced the broken handwritten transport with an official MCP
  SDK client and a reviewed eight-tool allowlist.
- 2026-07-13 — Added Fast/Guided/Studio workflows, policy and approval gates,
  artifact lineage, capability-gated visual QA, CI, and workflow fixtures.
- 2026-07-13 — Established a protocol-only boundary: this bundle and
  imagen-mcp can be built, tested, and released independently.
- 2026-07-13 — Executed and archived the deterministic high-risk policy gate:
  five cases passed and five unsafe trace mutations were rejected.
- 2026-07-13 — Released independent `imagen-mcp` v0.4.0, pinned all bundle
  self-sources to `v2.0.0`, and completed bounded OpenAI/Gemini live canaries.

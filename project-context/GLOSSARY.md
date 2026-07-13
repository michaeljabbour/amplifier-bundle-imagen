# Glossary

| Term | Means | Does NOT Mean |
|------|-------|---------------|
| Fast mode | One clear, low-risk request with policy preflight and final-file QA | Skipping safety or delivery checks |
| Guided mode | A focused specialist route for a meaningful ambiguity | Mandatory full-pipeline delegation |
| Studio mode | Approval-gated work with cost preview, drafts, user selection, refinement, and final QA | Silently selecting a draft for the user |
| Artifact | A concrete image file with stable ID, hash, metadata, and lineage | A prompt or an unverified path |
| Artifact manifest | Machine-readable record conforming to `schemas/artifact-manifest.schema.json` | A claim of cryptographic authenticity by itself |
| Approval gate | Explicit user acceptance of a plan or concrete artifact | Agent inference from prompt quality |
| Production candidate | Exact file proposed for final delivery and subject to final QA | A promise that a rerun will match an approved draft |
| Last accepted artifact | Most recent concrete file that passed the relevant review | Most recently generated output |
| Protocol-only boundary | Integration through MCP initialize, discovery, and tool calls with no package imports or sibling-repo discovery | A package dependency between the bundle and imagen-mcp |
| Capability-gated visual QA | Pixel-level review only when the exact artifact is present in a vision-capable context | Inferring image content from a path, hash, or successful write |
| Deterministic policy evaluation | Typed high-risk scenario execution with mock tools, independent trace predicates, and adversarial grader mutations | A canned assistant response or proof that every stochastic model complies |

# amplifier-bundle-imagen

An adaptive Amplifier image studio: OpenAI/Gemini generation and editing,
specialist creative direction, human approval gates, capability-gated visual QA, accessibility,
and artifact provenance. Provider calls are supplied by
[`imagen-mcp`](https://github.com/michaeljabbour/imagen-mcp) through the native
`tool-imagen` adapter.

> **Release status:** 2.0.0 is published as the immutable `v2.0.0` Git tag.
> Pin that tag for reproducible use; reserve a local checkout for development.

## What it provides

| Component | Inventory |
|---|---|
| Native tool adapter | Live `imagen-mcp` contract, currently 8 tools: single/batch generation, conversation, edit, cost estimate, and provider/model discovery |
| Specialist agents | `image-director`, `image-prompt-engineer`, `image-editor`, `image-researcher` |
| Discoverable skills | `design-visual-asset`, `image-ascii-art` |
| Behaviors | Full `imagegen` plus self-contained `image-generation` and `image-editing` à-la-carte behaviors |
| Always-on guidance | Adaptive routing plus rights, consent, privacy, safety, provenance, and accessibility gates |
| Verification | Static contract validator, versioned workflow eval specifications, module tests, and CI |

The adapter discovers argument schemas from `tools/list` for a reviewed
eight-name allowlist. Missing or additional names fail closed by default;
documentation does not override the live schemas of allowed tools.

## Prerequisites

1. Independently install `imagen-mcp` from its immutable `v0.4.0` tag or
   initialize a compatible local checkout according to its repository instructions.
2. Set at least one provider credential:

```bash
export OPENAI_API_KEY="..."
export GEMINI_API_KEY="..."
```

3. Include an orchestration provider (the pre-composed Anthropic bundle does
   this) and verify the mounted tools with `list_providers`.

The two projects are intentionally independent: this bundle neither installs
nor imports imagen-mcp, and imagen-mcp has no Amplifier dependency. At runtime,
configure an explicit checkout/executable or put the separately installed
`imagen-mcp` console script on `PATH`; the adapter communicates only over MCP.

Reference images leave the local machine for the selected provider. Review
`context/image-production-policy.md` before using private or identity-sensitive
sources.

## Use the full bundle

### Local checkout (development)

```bash
amplifier run -B "file:///path/to/amplifier-bundle-imagen/bundles/standalone-local.yaml"
```

### Tagged release

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@v2.1.2
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@v2.0.0
```

The full behavior registers both skills through `tool-skills`. The configured
git self-source is necessary because current `tool-skills` resolves plain local
paths from the runtime working directory rather than the contributing bundle.
The source is pinned to the same immutable `v2.0.0` release.

## Use an à-la-carte behavior

Both behaviors mount `tool-imagen` themselves; consumers no longer need to copy
a separate tool declaration.

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@v2.1.2
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@v2.0.0#subdirectory=behaviors/image-generation.yaml
```

Use `behaviors/image-editing.yaml` instead for the editor-only surface. Include
the full `imagegen` behavior when you also want bundled skill discovery.

## Adaptive workflow

The router chooses the smallest useful path unless the user explicitly selects
a mode:

- **Fast:** one clear, low-risk request → policy preflight → tool → file QA and, when pixels are available to vision, visual QA.
- **Guided:** one meaningful ambiguity → relevant specialist → tool → capability-gated visual review.
- **Studio:** brief → cost/capability preview → user approval → drafts → user
  selection → artifact-anchored refinement → final-file QA → artifact pack.

Studio mode never silently picks a draft. Rerunning an accepted prompt creates a
new artifact, not a higher-quality copy of the approved image, so it must be
shown and QA'd again.

A local path is not itself a vision input. If the active client cannot expose
the exact candidate's pixels to the model, Imagen verifies file facts, shows the
artifact for human review, and records visual QA as pending. It never claims to
have inspected pixels from a filename or base64 serialized as tool-result text.

### Example requests

```text
Fast: Create a 1536x1024 opaque PNG of a cobalt ceramic mug on warm grey.

Guided: Make a website hero for a privacy-first developer tool; help me choose
the visual direction, then generate one draft.

Studio: Develop a three-image launch campaign. Estimate the cost, show a
labeled contact sheet, wait for my selections, refine those exact files, and
deliver manifests plus alt text.

Edit: On ~/Downloads/images/openai/product.png, change only the accent from red to navy. Preserve
the authorized label, geometry, lighting, and camera angle.
```

## Current provider notes

### OpenAI GPT Image 2

- Prompt order: background/scene → subject → key details → constraints, with
  intended use stated.
- Size is constrained rather than limited to five presets: both dimensions
  must be multiples of 16, each edge ≤3840px, ratio ≤3:1, and total pixels
  655,360–8,294,400 inclusive.
- Transparent backgrounds are unsupported.
- Image inputs are always processed at high fidelity; omit `input_fidelity`.
- Any final rerender/edit must be inspected as a new artifact.

### Google Gemini 3 image

| Model | Sizes | Reference limits | Search | Signal |
|---|---|---|---|---|
| `gemini-3.1-flash-image` | 0.5K/1K/2K/4K; default 1K | 10 objects / 4 characters | Yes | SynthID |
| `gemini-3-pro-image` | 1K/2K/4K; default 1K | 6 objects / 5 characters / 3 style refs, 14 total | Yes | SynthID |
| `gemini-3.1-flash-lite-image` | 1K only | validate live | No | SynthID + C2PA |

Preview IDs shut down June 25, 2026. Use the GA IDs above.
Gemini 3.1 Flash and Flash Lite additionally support `1:4`, `4:1`, `1:8`,
and `8:1`; validate ratios against the selected model rather than assuming
family-wide support.

## Safety, rights, and privacy

- Confirm rights and consent before uploading unclear, private, biometric,
  child, medical, intimate, trademarked, or identity-sensitive sources.
- Never remove watermarks, signatures, provenance marks, or safety labels.
- Do not retry a moderation-blocked/user error unchanged, euphemize it, or
  switch providers for safeguard shopping. Retry only after a substantive,
  policy-compliant user/input change.
- Do not promise metadata removal, C2PA, invisible watermarks, or authenticity
  verification unless the final file was actually processed and checked.
- Deliver alt text and a transcript of literal on-image text.

See [`context/image-production-policy.md`](context/image-production-policy.md).

## Configuration

`behaviors/image-generation.yaml` and `behaviors/image-editing.yaml` provide the
default adapter configuration. Common overrides include `imagen_mcp_path`,
provider API keys, output directory, default provider, and provider-specific
default size. Validate supported keys against the adapter documentation and
mounted schemas; do not pass undocumented direct-mode or provider fields.

The 2.0 behavior default for Gemini is 1K, matching Gemini 3 image defaults.
Draft/final size should still be selected intentionally for the use case.

## Verify a checkout

```bash
python3 scripts/validate_bundle.py
PYTHONPATH=. python3 scripts/run_behavioral_evals.py \
  --verify evals/results/2026-07-13.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p pytest_asyncio.plugin modules/tool-imagen/tests
```

Live-provider canaries are intentionally opt-in because they spend quota and
send data externally. CI runs deterministic schema/static/module checks without
provider keys. The high-risk workflow gate under `evals/` executes against
Amplifier mock tools and independently grades structured decisions and tool
traces. Its dated result is deterministic policy evidence, not a claim of
universal compliance by every stochastic orchestration model.

## Repository map

```text
agents/                 specialist instructions
behaviors/              full and à-la-carte composition
bundles/                local and pre-composed entry points
context/                adaptive router and production policy
docs/                   provider, prompt, edit, direction, and analysis guides
evals/                  routing and workflow scenarios
modules/tool-imagen/     native Amplifier adapter
schemas/                 artifact manifest contract
scripts/                 deterministic bundle validation
skills/                  design workflow and ASCII-art pipeline
project-context/         persistent project coordination
```

## Release

See [`CHANGELOG.md`](CHANGELOG.md). The 2.0.0 release passed deterministic CI,
clean adapter packaging, real MCP initialize/`tools/list` compatibility against
independently released `imagen-mcp` v0.4.0, and bounded live provider canaries.

## License

MIT — see [`LICENSE`](LICENSE).

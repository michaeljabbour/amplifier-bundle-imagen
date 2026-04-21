# amplifier-bundle-imagen

An Amplifier bundle that adds specialist image generation and editing agents to any session. Powered by the `imagegen` MCP server, which exposes OpenAI **gpt-image-2** and **Gemini Nano Banana Pro** (gemini-3-pro-image-preview).

---

## What This Bundle Provides

| Component | Description |
|-----------|-------------|
| **4 specialist agents** | Creative director, prompt engineer, sequential editor, visual analyst |
| **1 compound skill** | `design-visual-asset` — end-to-end pipeline from brief to delivered image |
| **3 behavior bundles** | `imagegen` (full), `image-generation`, `image-editing` (à-la-carte) |
| **1 awareness context** | Thin root-session pointer that enforces delegation without bloating context |
| **6 documentation guides** | Prompt engineering, provider comparison, creative direction, edit workflow, visual analysis, tool reference |

The bundle namespace is `imagen`. The underlying MCP server is registered separately (see Prerequisites).

---

## Prerequisites — Register the imagegen MCP Server

> **This bundle does NOT register the MCP server.** The `imagegen` MCP server must be present in your session before this bundle's agents can call any image tools.

### 1. Clone or install the server

```bash
git clone https://github.com/michaeljabbour/imagen-mcp.git
cd imagen-mcp
uv sync
```

### 2. Register it in your Amplifier settings

Add the following to `~/.amplifier/settings.yaml`:

```yaml
mcp_servers:
  - name: imagegen
    command: uv
    args:
      - run
      - --directory
      - /path/to/imagen-mcp
      - imagen-mcp
    env:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
```

Set your API keys in your environment:

```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AIza..."
```

### 3. Verify

In an Amplifier session, call `list_providers` — you should see both OpenAI and Gemini listed.

**Full server documentation**: https://github.com/michaeljabbour/imagen-mcp

---

## Including This Bundle

### Option A — Add to a consumer bundle's `bundle.md`

```yaml
---
bundle:
  name: my-bundle
  version: 1.0.0

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main
---

@foundation:context/shared/common-system-base.md
```

### Option B — Include just the behavior (à-la-carte)

For generation only (no editor):

```yaml
includes:
  - bundle: foundation
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main#subdirectory=behaviors/image-generation.yaml
```

For editing only:

```yaml
includes:
  - bundle: foundation
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main#subdirectory=behaviors/image-editing.yaml
```

### Option C — Use the full behavior in your own bundle

```yaml
includes:
  - bundle: foundation
  - bundle: imagen:behaviors/imagegen   # after loading the bundle above
```

---

## Quickstart

Once the bundle is loaded and the MCP server is registered:

### Generate an image (full pipeline)

```
"Create a product photo of a matte black mechanical keyboard on a dark slate surface — 
I want it to feel like an Apple product launch photo."
```

The session will:
1. Delegate to `imagen:image-director` to establish the brief (lighting, framing, style)
2. Delegate to `imagen:image-prompt-engineer` to craft a gpt-image-2 prompt with `quality=high, size=1536x1024`
3. Call `generate_image` and return the path

### Analyze a reference image

```
"Analyze the lighting and style of /tmp/reference.jpg so I can replicate it."
```

Delegates to `imagen:image-researcher`, which returns a structured visual analysis and prompt reconstruction.

### Multi-step editing

```
"Take /tmp/product.png. First remove the background to pure white. Then 
add a subtle drop shadow. Then add a small lifestyle plant in the upper right corner."
```

Delegates to `imagen:image-editor` which runs three sequential `edit_image` calls with `input_fidelity=high`.

### Run the design-visual-asset skill

```
"Run the design-visual-asset skill. I need a hero image for a SaaS landing page 
targeting enterprise developers."
```

Executes the full 6-step pipeline: brief → prompt → generate → critique → refine → deliver.

---

## Agent Roster

| Agent | `model_role` | Activation Triggers |
|-------|-------------|---------------------|
| `imagen:image-director` | creative, reasoning | Creative requests without clear spec; style ambiguity; multi-image series needing visual consistency |
| `imagen:image-prompt-engineer` | creative, coding | After a brief exists; "craft the prompt"; parameter selection; provider-specific encoding |
| `imagen:image-editor` | creative, vision | "Change X in this image"; multi-step edits; inpainting; iterative refinement of an existing file |
| `imagen:image-researcher` | vision, research | "Analyze this image"; "match this style"; reverse-prompt from reference; visual property extraction |

---

## Bundle Structure

```
amplifier-bundle-imagen/
├── bundle.md                          # Root bundle — includes foundation + imagegen behavior
├── README.md                          # This file
├── behaviors/
│   ├── imagegen.yaml                  # Full: composes image-generation + image-editing
│   ├── image-generation.yaml          # Director + prompt-engineer + researcher
│   └── image-editing.yaml             # Editor only
├── agents/
│   ├── image-director.md              # Creative authority
│   ├── image-prompt-engineer.md       # Technical translator
│   ├── image-editor.md                # Sequential edit operator
│   └── image-researcher.md            # Visual analyst
├── context/
│   └── imagen-awareness.md            # Thin root-session pointer (~30 lines)
├── docs/
│   ├── CREATIVE_DIRECTION_GUIDE.md
│   ├── PROMPT_ENGINEERING_GUIDE.md
│   ├── PROVIDER_COMPARISON.md
│   ├── EDIT_WORKFLOW_GUIDE.md
│   ├── VISUAL_ANALYSIS_GUIDE.md
│   └── TOOL_REFERENCE.md
└── skills/
    └── design-visual-asset/
        └── SKILL.md
```

---
---

## Pre-composed bundles

The `bundles/` directory ships two pre-wired variants so you can include the imagen suite with a single line rather than composing providers manually.

### `bundles/with-anthropic.yaml` — Turnkey variant

Includes this bundle plus an Anthropic Claude Opus provider. Use this when you want an out-of-the-box image-generation agent experience without hand-wiring a routing matrix.

**Requires:** `ANTHROPIC_API_KEY` in your environment.

```yaml
includes:
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@v1.1.0#subdirectory=bundles/with-anthropic.yaml
```

The `foundation` bundle comes in transitively via `amplifier-bundle-imagen` — do not re-include it. Agents' `model_role:` fields fall through to the provider's `default_model` automatically.

Cost-conscious users can swap the provider to Sonnet by editing one line:

```yaml
  - bundle: foundation:providers/anthropic-sonnet   # instead of anthropic-opus
```

### `bundles/standalone-local.yaml` — Dev variant (bundle authors only)

Points at the local bundle checkout (relative path `../bundle.md`) so you can test bundle changes without pushing to GitHub. **Not intended for end users.**

```yaml
includes:
  - bundle: /path/to/amplifier-bundle-imagen/bundles/standalone-local.yaml
```

> **Note:** The `imagegen` MCP server must still be configured separately in your `settings.yaml`. This variant only swaps the bundle source, not the MCP integration. See [Prerequisites](#prerequisites--register-the-imagegen-mcp-server) above.

## License

MIT License — see [LICENSE](LICENSE)

## Author

Michael Jabbour — https://github.com/michaeljabbour

# amplifier-bundle-imagen

An Amplifier bundle that adds specialist image generation and editing agents, plus a **self-contained Python tool adapter**, to any session. Powered by [imagen-mcp](https://github.com/michaeljabbour/imagen-mcp), which exposes OpenAI **gpt-image-2** and **Gemini Nano Banana Pro** (gemini-3-pro-image-preview).

No `settings.yaml` MCP registration required — the bundle ships its own `tool-imagen` module that spawns or imports `imagen-mcp` directly.

---

## What This Bundle Provides

| Component | Description |
|-----------|-------------|
| **1 tool module** | `tool-imagen` — canonical Amplifier tool module exposing 6 image tools (generate, conversational, edit, list) |
| **4 specialist agents** | Creative director, prompt engineer, sequential editor, visual analyst |
| **1 compound skill** | `design-visual-asset` — end-to-end pipeline from brief to delivered image |
| **3 behavior bundles** | `imagegen` (full), `image-generation`, `image-editing` (à-la-carte) |
| **1 awareness context** | Thin root-session pointer that enforces delegation without bloating context |
| **6 documentation guides** | Prompt engineering, provider comparison, creative direction, edit workflow, visual analysis, tool reference |

The bundle namespace is `imagen`. The tool module is loaded automatically when the bundle is included — no `mcp_servers:` registration needed.

---

## Prerequisites

### 1. Install imagen-mcp

The tool module uses [imagen-mcp](https://github.com/michaeljabbour/imagen-mcp) as its provider layer. It can be installed as a package or cloned locally:

```bash
# Option 1: package install
pip install git+https://github.com/michaeljabbour/imagen-mcp.git

# Option 2: local clone (useful if you want to point tool-imagen at a specific checkout)
git clone https://github.com/michaeljabbour/imagen-mcp.git ~/imagen-mcp
cd ~/imagen-mcp && uv sync
```

The `tool-imagen` module auto-discovers imagen-mcp in this order:
1. `imagen_mcp_path` config value (absolute path to a local clone)
2. `imagen_mcp` Python package on the current PATH
3. `~/imagen-mcp/src/server.py` (default local clone location)

### 2. Set API keys

At least one provider key is required; set both for auto-selection to work across all prompt types.

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

### Option B — Include just a behavior (à-la-carte)

Each à-la-carte behavior ships the tool module via the umbrella `imagegen` behavior. If you want to load `image-generation` or `image-editing` *without* loading `imagegen`, add the tool declaration yourself:

```yaml
includes:
  - bundle: foundation
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main#subdirectory=behaviors/image-generation.yaml

tools:
  - module: tool-imagen
    source: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main#subdirectory=modules/tool-imagen
```

### Option C — Use the full behavior in a downstream bundle

```yaml
includes:
  - bundle: foundation
  - bundle: imagen:behaviors/imagegen
```

---

## Configuring the tool module

The tool module accepts the following optional config under `tools[].config`:

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `"subprocess"` | `"subprocess"` (spawn imagen-mcp as a child) or `"direct"` (in-process import) |
| `imagen_mcp_path` | — | Absolute path to a local imagen-mcp clone |
| `openai_api_key` | env `OPENAI_API_KEY` | Override API key |
| `gemini_api_key` | env `GEMINI_API_KEY` | Override API key |
| `default_provider` | `"auto"` | `"auto"`, `"openai"`, `"gemini"` |
| `output_dir` | `~/Downloads/images` | Base directory for saved images |
| `default_openai_size` | `"1536x1024"` | |
| `default_gemini_size` | `"2K"` | |
| `enable_google_search` | `false` | Gemini Google Search grounding |
| `log_level` | `"WARNING"` | imagen-mcp log verbosity |

Overrides apply only to this bundle's `imagegen` behavior. See [modules/tool-imagen/README.md](modules/tool-imagen/README.md) for module internals.

---

## Quickstart

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
├── modules/
│   └── tool-imagen/                   # Native Amplifier tool module (6 tools)
│       ├── pyproject.toml
│       ├── amplifier_module_tool_imagen/__init__.py
│       └── tests/
├── behaviors/
│   ├── imagegen.yaml                  # Full: declares tool-imagen + composes generation + editing
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

## Pre-composed bundles

The `bundles/` directory ships two pre-wired variants so you can include the imagen suite with a single line rather than composing providers manually.

### `bundles/with-anthropic.yaml` — Turnkey variant

Includes this bundle plus an Anthropic Claude Opus provider. Use this when you want an out-of-the-box image-generation agent experience without hand-wiring a routing matrix.

**Requires:** `ANTHROPIC_API_KEY` in your environment.

```yaml
includes:
  - bundle: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@v1.2.0#subdirectory=bundles/with-anthropic.yaml
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

---

## License

MIT License — see [LICENSE](LICENSE)

## Author

Michael Jabbour — https://github.com/michaeljabbour

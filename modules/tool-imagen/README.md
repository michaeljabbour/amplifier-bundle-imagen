# amplifier-module-tool-imagen

Amplifier adapter for [imagen-mcp](https://github.com/michaeljabbour/imagen-mcp).
Version 2 uses the official MCP Python SDK and discovers reviewed tool schemas
from the running server during mount. Schemas are not copied into the adapter,
but tool names are fail-closed behind an explicit allowlist; contract changes
require review and a compatible adapter release.

The module ships inside `amplifier-bundle-imagen`; it is not published as a
standalone PyPI package. Bundle manifests reference its git subdirectory:

```yaml
tools:
  - module: tool-imagen
    source: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@v2.0.0#subdirectory=modules/tool-imagen
    config:
      mode: mcp
```

## Runtime contract

At mount time the adapter:

1. resolves an installed `imagen-mcp` console script or an explicitly configured checkout;
2. launches it over stdio without a shell;
3. performs the MCP initialize handshake;
4. discovers every tool with paginated `tools/list` calls;
5. validates the MCP server identity/version and exact reviewed tool contract;
6. mounts allowlisted tools under their native names; and
7. keeps one initialized session alive until bundle cleanup.

FastMCP represents Pydantic arguments as a required `params` object. The adapter
flattens that sole wrapper for Amplifier while retaining `$defs`, then restores
`{"params": ...}` on the MCP call. Zero-argument and ordinary multi-argument
tools are passed through unchanged.

The supported imagen-mcp `>=0.4,<0.5` contract currently advertises:

| Name | Purpose |
|------|---------|
| `generate_image` | Provider-routed image generation |
| `conversational_image` | Multi-turn generation and refinement |
| `edit_image` | Image editing |
| `list_providers` | Configured providers and capabilities |
| `list_conversations` | Saved conversation threads |
| `list_gemini_models` | Available Gemini image models |
| `estimate_cost` | Provider-free cost estimate |
| `generate_image_batch` | Bounded concurrent batch generation |

The live server owns schemas for these reviewed names. Missing or additional
names fail mount by default instead of silently expanding the agent's authority.

## Installation

The adapter depends on `amplifier-core>=1.6,<2` and `mcp>=1.26,<2`, and targets
imagen-mcp `>=0.4,<0.5`. The image server is a separate runtime and must either
be independently installed from the immutable v0.4.0 Git tag or initialized as
a local checkout. For a reproducible VCS installation:

```bash
python3 -m pip install \
  "imagen-mcp @ git+https://github.com/michaeljabbour/imagen-mcp.git@v0.4.0"
```

For source development, use a checkout:

```bash
git clone https://github.com/michaeljabbour/imagen-mcp ~/dev/imagen-mcp
cd ~/dev/imagen-mcp && uv sync
```

For a checkout, point the bundle at its root (the directory containing
`pyproject.toml` and `imagen_mcp/__main__.py`):

```yaml
config:
  imagen_mcp_path: ~/dev/imagen-mcp
```

For a checkout, the adapter requires a checkout-local `.venv` or `venv` Python
and launches the canonical `python -m imagen_mcp` entry point. Run `uv sync` in
the checkout first. It deliberately does not borrow the adapter's interpreter,
which may have the MCP SDK but not imagen-mcp's provider dependencies.

The adapter never searches sibling development directories. A checkout is used
only when `imagen_mcp_path` names it explicitly; otherwise the independently
installed `imagen-mcp` executable must be on `PATH`.

## Configuration

All keys are optional and belong under `tools[].config`.

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `"mcp"` | Preferred mode. Legacy `"subprocess"` is an alias. |
| `imagen_mcp_path` | installed executable | Local checkout root or executable path; no sibling directories are searched. |
| `timeout_seconds` | `600` | Per-tool MCP response timeout. |
| `startup_timeout_seconds` | `30` | Initialize and discovery timeout. |
| `shutdown_timeout_seconds` | `10` | Graceful cleanup timeout. |
| `allowed_tools` | reviewed eight-tool contract | Exact tools the server must expose and the adapter may mount. |
| `strict_tool_contract` | `true` | Reject unreviewed advertised tools; `false` ignores extras but never mounts them. |
| `openai_api_key` | env `OPENAI_API_KEY` | OpenAI credential override. |
| `gemini_api_key` | env `GEMINI_API_KEY` | Gemini credential override. |
| `default_provider` | `"auto"` | `auto`, `openai`, or `gemini`. |
| `output_dir` | server default | Base output directory. |
| `allowed_input_roots` | server output root | Non-empty list of local roots from which `edit_image` may read source/mask files. |
| `conversation_retention_days` | `30` | Delete inactive persisted conversation history after this many days; `0` disables cleanup. |
| `default_openai_size` | server default (`"1024x1024"`) | Default OpenAI size override. |
| `default_gemini_size` | server default (`"1K"`) | Default Gemini size override. |
| `default_gemini_aspect_ratio` | server default (`"1:1"`) | Default Gemini aspect ratio override. |
| `enable_prompt_enhancement` | server default (`false`) | Enable the optional prompt-refinement round trip. |
| `enable_google_search` | inherited/server default | Gemini grounding flag. |
| `log_level` | `"WARNING"` | imagen-mcp log level. |

Only environment variables consumed by imagen-mcp are inherited. Unrelated
parent credentials are not copied. The child transport is always forced to
`stdio`, and stderr is directed to the operating system null device so it
cannot block the protocol.

For edit safety, imagen-mcp reads source and mask files only from its output
root unless `IMAGEN_MCP_ALLOWED_INPUT_ROOTS` or `allowed_input_roots` explicitly
adds another root. Prefer passing a path returned by a prior generation.

Tool calls are serialized on the shared session. MCP request IDs still provide
protocol correlation, while serialization protects provider clients that do not
support overlapping operations. MCP `isError` becomes a failed Amplifier
`ToolResult`; safe `structuredContent` is preserved as structured output.
Binary fields and image/audio payloads are deliberately replaced with bounded
metadata instead of being JSON-serialized into the LLM context, and every
result has a 128 KiB context ceiling. The saved artifact path remains the
handoff until Amplifier exposes a native multimodal tool-result channel.
Credential-shaped input fields are stripped recursively from discovered schemas
as defense in depth for accidentally selected pre-0.4 servers; provider keys
belong in environment/configuration, never model-visible tool arguments.
The adapter imports no `imagen_mcp` or legacy `src` modules and declares no
package dependency on imagen-mcp; process launch and tool calls cross only the
standard MCP boundary.

## Migrating from 1.x

Version 2 removes `mode: direct` and the `[direct]` optional dependency. That
path called an unstable provider API, implemented only a subset of tools, and
could not match the MCP server contract. Use `mode: mcp` instead. Existing
`mode: subprocess` configurations continue to work as an alias, and existing
provider/configuration keys retain their meaning.

Mount now establishes the server connection immediately. A missing or
incompatible imagen-mcp installation therefore fails early instead of
registering tools that fail on first use.

## Verification

The test suite includes a provider-free MCP server and exercises initialization,
dynamic eight-tool discovery, schema flattening and nested refs, call argument
rewrapping, structured/error content, timeouts, recovery, and clean shutdown.
Set `IMAGEN_MCP_CONTRACT_PATH=/path/to/imagen-mcp` to opt into a live external
contract check without invoking an image provider. Normal unit/CI runs do not
assume a sibling repository exists.

```bash
python -m pytest
python -m pytest --cov=amplifier_module_tool_imagen --cov-report=term-missing
ruff check .
```

## License

MIT

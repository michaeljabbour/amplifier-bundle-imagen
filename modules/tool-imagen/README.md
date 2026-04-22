# amplifier-module-tool-imagen

Amplifier tool module that exposes [imagen-mcp](https://github.com/michaeljabbour/imagen-mcp) as six native Amplifier tools.

This module is shipped as part of the `amplifier-bundle-imagen` bundle — it is not published to PyPI. Bundles reference it by git subdirectory:

```yaml
tools:
  - module: tool-imagen
    source: git+https://github.com/michaeljabbour/amplifier-bundle-imagen@main#subdirectory=modules/tool-imagen
```

## Tools

| Name | Provider | Purpose |
|------|----------|---------|
| `generate_image` | auto / OpenAI / Gemini | Primary generation |
| `conversational_image` | auto / OpenAI / Gemini | Multi-turn refinement |
| `edit_image` | OpenAI gpt-image-2 | Sequential editing with `input_fidelity` |
| `list_providers` | — | Configured providers |
| `list_conversations` | — | Saved conversations |
| `list_gemini_models` | Gemini | Available image models |

## Execution modes

- **subprocess** (default) — spawns `imagen-mcp` as a child process and proxies calls over MCP JSON-RPC on stdio. No Python import needed; `imagen-mcp` must be importable as a Python module, installed on PATH, or located at `imagen_mcp_path`.
- **direct** — imports `imagen-mcp`'s provider layer in-process for lower latency. Requires `pip install -e ".[direct]"`.

## Configuration

All optional. Set under `tools[].config` in your bundle frontmatter.

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `"subprocess"` | `"subprocess"` or `"direct"` |
| `imagen_mcp_path` | — | Absolute path to a local imagen-mcp clone |
| `openai_api_key` | env `OPENAI_API_KEY` | Override API key |
| `gemini_api_key` | env `GEMINI_API_KEY` | Override API key |
| `default_provider` | `"auto"` | `"auto"`, `"openai"`, `"gemini"` |
| `output_dir` | `~/Downloads/images` | Base directory for saved images |
| `default_openai_size` | `"1536x1024"` | |
| `default_gemini_size` | `"2K"` | |
| `enable_google_search` | `false` | Gemini Google Search grounding |
| `log_level` | `"WARNING"` | imagen-mcp log verbosity |

## License

MIT

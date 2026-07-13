# Ways of Working

## Deterministic verification

Run these checks without provider credentials or paid API calls:

```bash
modules/tool-imagen/.venv/bin/python scripts/validate_bundle.py
PYTHONPATH=. modules/tool-imagen/.venv/bin/python scripts/run_behavioral_evals.py \
  --verify evals/results/2026-07-13.json
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  modules/tool-imagen/.venv/bin/python -m pytest -q evals/test_behavioral_harness.py
modules/tool-imagen/.venv/bin/ruff format --check modules/tool-imagen scripts evals
modules/tool-imagen/.venv/bin/ruff check modules/tool-imagen scripts evals
cd modules/tool-imagen
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q \
  -p pytest_asyncio.plugin -p pytest_cov.plugin \
  --cov=amplifier_module_tool_imagen --cov-fail-under=80
```

The test suite creates a provider-free MCP server and runs Amplifier's official
`ToolValidator` with an explicit external-runtime path. This verifies the real
initialize, discovery, mount, call, timeout, error, and cleanup lifecycle while
preserving repository independence.

The behavioral command binds five high-risk traces to the production policy
sources, executes permitted calls with Amplifier `MockTool`, grades structured
events and tool arguments separately, and rejects adversarial unsafe mutations.
Do not reinterpret it as stochastic-model or live-provider evidence.

## External contract check

After imagen-mcp is initialized independently, run:

```bash
cd modules/tool-imagen
IMAGEN_MCP_CONTRACT_PATH=/path/to/imagen-mcp \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q \
  -p pytest_asyncio.plugin tests/test_tool_imagen.py::test_external_imagen_mcp_contract_when_explicitly_requested
```

The Amplifier CLI validator calls `mount()` without module configuration. It
therefore needs an independently installed compatible `imagen-mcp` executable
on `PATH`; do not repair a missing executable by adding sibling-directory
auto-discovery. For a checkout-only local validation, prepend that checkout's
`.venv/bin` to `PATH`.

Run the opt-in external lifecycle check serially, not beside coverage and wheel
builds. Its 30-second startup timeout is intentionally strict; a machine-load
timeout must be rerun in isolation and must pass rather than being waived. The
release-candidate rerun passed in 5.97 seconds after a contention-only timeout.

Live provider canaries are separate, opt-in release checks because they consume
quota and send prompts or images to an external provider.

For a canary, HTTP 200 and a returned path are insufficient evidence. Inspect
the actual decoded format, dimensions, byte count, SHA-256 digest, file mode,
and exact pixels; compare format and mode with the result metadata and suffix.
Treat non-retryable 4xx responses as final, correct the request deliberately,
and do not spend quota repeating a successful provider call when a discovered
defect is entirely in deterministic local persistence or transformation code.

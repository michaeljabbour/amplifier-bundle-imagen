"""
Amplifier tool module for imagen-mcp multi-provider image generation.

Exposes six native Amplifier tools backed by OpenAI gpt-image-2 and Google
Gemini Nano Banana Pro (gemini-3-pro-image-preview) via the imagen-mcp server.

Tools:
  generate_image        Primary generation with auto provider selection
  conversational_image  Multi-turn refinement with dialogue history
  edit_image            Sequential editing via gpt-image-2 with input_fidelity
  list_providers        Report configured providers and capabilities
  list_conversations    List saved conversation threads
  list_gemini_models    List available Gemini image models

Two execution modes:
  subprocess (default)  Spawns imagen-mcp as a child process, proxies calls
                        over MCP JSON-RPC on stdio. No Python import needed.
  direct                Imports imagen-mcp's provider layer in-process. Faster
                        but requires the direct extra: pip install -e ".[direct]"

Configuration (all optional, set in bundle frontmatter under tools[].config):
  mode                  "subprocess" | "direct" (default: "subprocess")
  imagen_mcp_path       Absolute path to a local imagen-mcp clone
  openai_api_key        Override OPENAI_API_KEY
  gemini_api_key        Override GEMINI_API_KEY
  default_provider      "auto" | "openai" | "gemini" (default: "auto")
  output_dir            Base directory for saved images
  default_openai_size   Default OpenAI image size (default: "1536x1024")
  default_gemini_size   Default Gemini image size (default: "2K")
  enable_google_search  Enable Gemini Google Search grounding (default: false)
  log_level             imagen-mcp log level (default: "WARNING")
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from amplifier_core import ModuleCoordinator, ToolResult

__amplifier_module_type__ = "tool"

logger = logging.getLogger(__name__)


# ── Tool schemas ──────────────────────────────────────────────────────────────

_GENERATE_IMAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Text description of the image to generate.",
        },
        "provider": {
            "type": "string",
            "enum": ["auto", "openai", "gemini"],
            "description": "Force a specific provider. Default: auto (selected from prompt content).",
        },
        "size": {
            "type": "string",
            "description": (
                "Image size. OpenAI gpt-image-2: '1024x1024', '1024x1536', '1536x1024'. "
                "Gemini Nano Banana Pro: '1K', '2K', '4K'."
            ),
        },
        "quality": {
            "type": "string",
            "enum": ["auto", "low", "medium", "high"],
            "description": "Quality tier. OpenAI only.",
        },
        "n": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "description": "Number of images to generate. Default: 1.",
        },
        "output_path": {
            "type": "string",
            "description": (
                "Path to save the image. If a directory, auto-names the file. "
                "Defaults to ~/Downloads/images/{provider}/."
            ),
        },
        "enable_google_search": {
            "type": "boolean",
            "description": "Enable Google Search grounding for real-time data. Gemini only.",
        },
        "reference_images": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Base64-encoded reference images for style/character consistency. Gemini only, up to 14.",
        },
        "gemini_model": {
            "type": "string",
            "description": "Override the Gemini model. Default: gemini-3-pro-image-preview.",
        },
    },
    "required": ["prompt"],
}

_CONVERSATIONAL_IMAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Generation or refinement instruction.",
        },
        "conversation_id": {
            "type": "string",
            "description": "Resume an existing conversation. Omit to start a new one.",
        },
        "provider": {
            "type": "string",
            "enum": ["auto", "openai", "gemini"],
            "description": "Force a specific provider. Default: auto.",
        },
        "size": {"type": "string"},
        "output_path": {"type": "string"},
    },
    "required": ["prompt"],
}

_EDIT_IMAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Edit instruction, e.g. 'change the sky to sunset'.",
        },
        "image_path": {
            "type": "string",
            "description": "Absolute path to the source image (png/jpeg/webp).",
        },
        "mask_path": {
            "type": "string",
            "description": "Optional PNG mask. Transparent pixels mark the edit zone; opaque pixels are protected.",
        },
        "input_fidelity": {
            "type": "string",
            "enum": ["high", "low"],
            "description": (
                "Fidelity of unchanged pixels. 'high' (default) preserves pixels outside "
                "the described change, enabling safe multi-step edit chains. 'low' allows "
                "drift across the whole image."
            ),
        },
        "size": {"type": "string"},
        "quality": {
            "type": "string",
            "enum": ["auto", "low", "medium", "high"],
        },
        "n": {"type": "integer", "minimum": 1, "maximum": 10},
        "output_path": {"type": "string"},
    },
    "required": ["prompt", "image_path"],
}

_LIST_PROVIDERS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {},
}

_LIST_CONVERSATIONS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "description": "Max conversations to return. Default: 10.",
        },
        "provider": {
            "type": "string",
            "enum": ["openai", "gemini"],
            "description": "Filter by provider.",
        },
    },
}

_LIST_GEMINI_MODELS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {},
}


_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "generate_image",
        "description": (
            "Generate an image from a text prompt. Automatically selects the best provider "
            "based on prompt content (OpenAI gpt-image-2 for text/diagrams/infographics; "
            "Google Gemini Nano Banana Pro for photorealistic portraits, product photography, "
            "and 4K output). Override with provider='openai' or 'gemini' to force a choice."
        ),
        "input_schema": _GENERATE_IMAGE_SCHEMA,
    },
    {
        "name": "conversational_image",
        "description": (
            "Generate or refine an image through multi-turn dialogue. Maintains conversation "
            "history for iterative refinement. Resume an existing conversation by passing its "
            "conversation_id."
        ),
        "input_schema": _CONVERSATIONAL_IMAGE_SCHEMA,
    },
    {
        "name": "edit_image",
        "description": (
            "Edit an existing image using OpenAI gpt-image-2. With input_fidelity='high' "
            "(default), pixels outside the described change are preserved, enabling safe "
            "multi-step edit chains where each output becomes the next input. Supports "
            "inpainting via an optional PNG mask."
        ),
        "input_schema": _EDIT_IMAGE_SCHEMA,
    },
    {
        "name": "list_providers",
        "description": "List configured image generation providers and their capabilities.",
        "input_schema": _LIST_PROVIDERS_SCHEMA,
    },
    {
        "name": "list_conversations",
        "description": "List active image generation conversations and their history.",
        "input_schema": _LIST_CONVERSATIONS_SCHEMA,
    },
    {
        "name": "list_gemini_models",
        "description": "Query available Gemini image generation models.",
        "input_schema": _LIST_GEMINI_MODELS_SCHEMA,
    },
]


# ── Environment builder ──────────────────────────────────────────────────────

def _build_env(config: dict[str, Any]) -> dict[str, str]:
    """Build the subprocess environment from config + current env."""
    env = os.environ.copy()

    key_map = {
        "openai_api_key": "OPENAI_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
        "default_provider": "DEFAULT_PROVIDER",
        "output_dir": "OUTPUT_DIR",
        "default_openai_size": "DEFAULT_OPENAI_SIZE",
        "default_gemini_size": "DEFAULT_GEMINI_SIZE",
        "log_level": "IMAGEN_MCP_LOG_LEVEL",
    }
    for cfg_key, env_key in key_map.items():
        value = config.get(cfg_key)
        if value is not None:
            env[env_key] = str(value)

    if config.get("enable_google_search"):
        env["ENABLE_GOOGLE_SEARCH"] = "true"

    env.setdefault("IMAGEN_MCP_LOG_LEVEL", "WARNING")
    env.setdefault("DEFAULT_OPENAI_SIZE", "1536x1024")
    env.setdefault("DEFAULT_GEMINI_SIZE", "2K")

    return env


# ── Direct-import adapter ────────────────────────────────────────────────────

class _DirectAdapter:
    """Call imagen-mcp's provider registry directly in-process."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._registry: Any = None

    async def _get_registry(self) -> Any:
        if self._registry is not None:
            return self._registry
        try:
            from imagen_mcp.providers import get_provider_registry  # type: ignore
            self._registry = get_provider_registry()
            return self._registry
        except ImportError:
            pass

        mcp_path = self._config.get("imagen_mcp_path")
        if mcp_path and Path(mcp_path).expanduser().exists():
            sys.path.insert(0, str(Path(mcp_path).expanduser()))
            from src.providers import get_provider_registry  # type: ignore
            self._registry = get_provider_registry()
            return self._registry

        raise RuntimeError(
            "imagen-mcp is not installed and imagen_mcp_path is not set. "
            "Install with: pip install imagen-mcp  "
            "or set tools[].config.mode = 'subprocess' and install imagen-mcp on PATH."
        )

    async def call(self, tool_name: str, params: dict[str, Any]) -> str:
        registry = await self._get_registry()

        if tool_name == "list_providers":
            return json.dumps(registry.list_providers(), indent=2)

        if tool_name == "generate_image":
            result = await registry.generate(
                prompt=params["prompt"],
                provider=params.get("provider", "auto"),
                size=params.get("size"),
                n=params.get("n", 1),
                output_path=params.get("output_path"),
            )
            return (
                result.markdown
                if getattr(result, "success", False)
                else f"Error: {getattr(result, 'error', 'unknown')}"
            )

        return (
            f"Tool '{tool_name}' is not implemented in direct mode. "
            "Use mode: subprocess for full tool coverage."
        )

    async def close(self) -> None:
        return None


# ── Subprocess MCP bridge ────────────────────────────────────────────────────

class _SubprocessAdapter:
    """Proxy tool calls to imagen-mcp via MCP JSON-RPC on stdio."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._env = _build_env(config)
        self._proc: subprocess.Popen | None = None  # type: ignore[type-arg]
        self._lock = asyncio.Lock()
        self._call_id = 0

    def _find_mcp_command(self) -> list[str]:
        explicit = self._config.get("imagen_mcp_path")
        if explicit:
            p = Path(explicit).expanduser()
            if (p / "src" / "server.py").exists():
                return [sys.executable, str(p / "src" / "server.py")]

        try:
            import importlib.util
            spec = importlib.util.find_spec("imagen_mcp")
            if spec:
                return [sys.executable, "-m", "imagen_mcp"]
        except (ImportError, ValueError):
            pass

        local = Path.home() / "imagen-mcp"
        if (local / "src" / "server.py").exists():
            return [sys.executable, str(local / "src" / "server.py")]

        raise RuntimeError(
            "imagen-mcp server not found. Install with: "
            "pip install imagen-mcp  or clone https://github.com/michaeljabbour/imagen-mcp "
            "and set tools[].config.imagen_mcp_path."
        )

    async def _ensure_proc(self) -> None:
        async with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                cmd = self._find_mcp_command()
                logger.debug("Starting imagen-mcp subprocess: %s", cmd)
                self._proc = subprocess.Popen(  # type: ignore[assignment]
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=self._env,
                    text=True,
                    bufsize=1,
                )

    async def call(self, tool_name: str, params: dict[str, Any]) -> str:
        await self._ensure_proc()
        proc = self._proc
        assert proc and proc.stdin and proc.stdout

        self._call_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": params},
        }

        try:
            loop = asyncio.get_event_loop()
            line = json.dumps(request) + "\n"
            await loop.run_in_executor(None, proc.stdin.write, line)
            await loop.run_in_executor(None, proc.stdin.flush)

            response_line = await asyncio.wait_for(
                loop.run_in_executor(None, proc.stdout.readline),
                timeout=120.0,
            )
            if not response_line:
                return "Error: imagen-mcp subprocess returned an empty response."

            response = json.loads(response_line)
            if "error" in response:
                err = response["error"]
                return f"Error: {err.get('message', str(err))}"

            result = response.get("result", {})
            content = result.get("content", [])
            if isinstance(content, list) and content:
                parts = [
                    c.get("text", "")
                    for c in content
                    if isinstance(c, dict) and c.get("type") == "text"
                ]
                return "\n".join(parts) or str(content)
            return str(result)

        except asyncio.TimeoutError:
            return "Error: imagen-mcp timed out after 120 seconds."
        except Exception as exc:
            logger.exception("Error calling imagen-mcp tool %s", tool_name)
            return f"Error: {exc}"

    async def close(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()


# ── Tool class ───────────────────────────────────────────────────────────────

class ImagenTool:
    """One imagen-mcp tool, conforming to amplifier_core.interfaces.Tool."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        adapter: Any,
    ) -> None:
        self._name = name
        self._description = description
        self._input_schema = input_schema
        self._adapter = adapter

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        try:
            output = await self._adapter.call(self._name, input)
        except Exception as exc:
            logger.exception("imagen tool %s raised", self._name)
            message = f"{type(exc).__name__}: {exc}"
            return ToolResult(
                success=False,
                output=f"Error: {message}",
                error={"message": message},
            )

        if isinstance(output, str) and output.startswith("Error:"):
            return ToolResult(
                success=False,
                output=output,
                error={"message": output[len("Error:"):].strip()},
            )
        return ToolResult(success=True, output=output)


# ── Module entry point ───────────────────────────────────────────────────────

async def mount(
    coordinator: ModuleCoordinator,
    config: dict[str, Any] | None = None,
):
    """Mount all imagen tools into the Amplifier coordinator.

    Args:
        coordinator: Module coordinator.
        config: Tool configuration. See module docstring for keys.

    Returns:
        A cleanup coroutine that terminates the imagen-mcp subprocess.
    """
    cfg = config or {}
    mode = cfg.get("mode", "subprocess")

    adapter: Any
    if mode == "direct":
        adapter = _DirectAdapter(cfg)
    else:
        adapter = _SubprocessAdapter(cfg)

    registered: list[str] = []
    for definition in _TOOL_DEFINITIONS:
        tool = ImagenTool(
            name=definition["name"],
            description=definition["description"],
            input_schema=definition["input_schema"],
            adapter=adapter,
        )
        await coordinator.mount("tools", tool, name=tool.name)
        registered.append(tool.name)

    logger.info("imagen tools registered (%s mode): %s", mode, registered)

    async def cleanup() -> None:
        if hasattr(adapter, "close"):
            await adapter.close()

    return cleanup

"""Expose the reviewed ``imagen-mcp`` tool contract as native Amplifier tools.

The module uses the official MCP Python SDK for the complete stdio lifecycle:
server launch, initialization, paginated tool discovery, correlated tool calls,
and shutdown. Tool schemas are discovered live, while a fail-closed name
allowlist prevents server updates from silently expanding agent authority.

Configuration (all optional, under ``tools[].config``):

``mode``
    ``"mcp"`` (preferred) or the legacy alias ``"subprocess"``.
``imagen_mcp_path``
    Path to an initialized local ``imagen-mcp`` clone or executable.  When
    omitted, the installed ``imagen-mcp`` console script is preferred.
``timeout_seconds``
    Per-tool-call timeout (default: 600).
``startup_timeout_seconds`` / ``shutdown_timeout_seconds``
    Lifecycle timeouts (defaults: 30 and 10).

Provider settings may be supplied with the existing config keys documented in
the module README.  Relevant provider environment variables are inherited
explicitly; the complete parent environment is never copied into the server.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import sys
from contextlib import suppress
from copy import deepcopy
from datetime import timedelta
from importlib import metadata
from inspect import isawaitable
from pathlib import Path
from typing import Any, NamedTuple

from amplifier_core import ModuleCoordinator, ToolResult
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client
from mcp.shared.exceptions import McpError

__amplifier_module_type__ = "tool"
__version__ = "2.0.0"

logger = logging.getLogger(__name__)

_SUPPORTED_TOOL_NAMES = frozenset(
    {
        "generate_image",
        "conversational_image",
        "edit_image",
        "list_providers",
        "list_conversations",
        "list_gemini_models",
        "estimate_cost",
        "generate_image_batch",
    }
)
_SUPPORTED_SERVER_NAMES = frozenset({"imagen_mcp", "imagen-mcp"})
_SUPPORTED_SERVER_VERSION = (0, 4)
_MAX_TOOL_OUTPUT_BYTES = 128 * 1024
_BINARY_RESULT_FIELDS = frozenset(
    {
        "audio_data",
        "base64",
        "blob",
        "bytes",
        "content_bytes",
        "data",
        "image_data",
    }
)


# Only variables consumed by imagen-mcp are inherited.  This avoids forwarding
# unrelated credentials and shell state to the child process.
_INHERITED_IMAGEN_ENV = (
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "DEFAULT_PROVIDER",
    "DEFAULT_OPENAI_SIZE",
    "DEFAULT_GEMINI_SIZE",
    "DEFAULT_GEMINI_ASPECT_RATIO",
    "ENABLE_PROMPT_ENHANCEMENT",
    "ENABLE_GOOGLE_SEARCH",
    "REQUEST_TIMEOUT",
    "OPENAI_RPM",
    "OPENAI_MIN_INTERVAL_SECONDS",
    "OPENAI_BURST_LIMIT",
    "GEMINI_RPM",
    "GEMINI_MIN_INTERVAL_SECONDS",
    "GEMINI_BURST_LIMIT",
    "OUTPUT_DIR",
    "IMAGEN_MCP_ALLOWED_INPUT_ROOTS",
    "IMAGEN_MCP_CONVERSATION_RETENTION_DAYS",
    "IMAGEN_MCP_LOG_DIR",
    "IMAGEN_MCP_LOG_LEVEL",
    "IMAGEN_MCP_LOG_MAX_BYTES",
    "IMAGEN_MCP_LOG_BACKUP_COUNT",
    "IMAGEN_MCP_LOG_PROMPTS",
)

_CONFIG_ENV_MAP = {
    "openai_api_key": "OPENAI_API_KEY",
    "gemini_api_key": "GEMINI_API_KEY",
    "default_provider": "DEFAULT_PROVIDER",
    "output_dir": "OUTPUT_DIR",
    "default_openai_size": "DEFAULT_OPENAI_SIZE",
    "default_gemini_size": "DEFAULT_GEMINI_SIZE",
    "default_gemini_aspect_ratio": "DEFAULT_GEMINI_ASPECT_RATIO",
    "log_level": "IMAGEN_MCP_LOG_LEVEL",
}


def _build_env(config: dict[str, Any]) -> dict[str, str]:
    """Build a least-privilege environment for the MCP server."""

    env = get_default_environment()
    for name in _INHERITED_IMAGEN_ENV:
        if name in os.environ:
            env[name] = os.environ[name]

    for config_name, env_name in _CONFIG_ENV_MAP.items():
        value = config.get(config_name)
        if value is not None:
            env[env_name] = str(value)

    if "enable_google_search" in config:
        env["ENABLE_GOOGLE_SEARCH"] = (
            "true" if _boolean_config(config, "enable_google_search", False) else "false"
        )
    if "enable_prompt_enhancement" in config:
        env["ENABLE_PROMPT_ENHANCEMENT"] = (
            "true" if _boolean_config(config, "enable_prompt_enhancement", False) else "false"
        )
    if "allowed_input_roots" in config:
        roots = config["allowed_input_roots"]
        if (
            not isinstance(roots, list)
            or not roots
            or not all(isinstance(root, str) and root.strip() for root in roots)
        ):
            raise ValueError("allowed_input_roots must be a non-empty list of paths")
        env["IMAGEN_MCP_ALLOWED_INPUT_ROOTS"] = os.pathsep.join(
            str(Path(root).expanduser()) for root in roots
        )
    if "conversation_retention_days" in config:
        value = config["conversation_retention_days"]
        if isinstance(value, bool):
            raise ValueError("conversation_retention_days must be a non-negative integer")
        try:
            retention_days = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("conversation_retention_days must be a non-negative integer") from exc
        if retention_days < 0 or str(value).strip() != str(retention_days):
            raise ValueError("conversation_retention_days must be a non-negative integer")
        env["IMAGEN_MCP_CONVERSATION_RETENTION_DAYS"] = str(retention_days)

    # stdio is part of this adapter's contract, even if a parent process has a
    # different imagen-mcp transport configured.
    env["IMAGEN_MCP_TRANSPORT"] = "stdio"
    env.setdefault("IMAGEN_MCP_LOG_LEVEL", "WARNING")
    return env


def _boolean_config(config: dict[str, Any], key: str, default: bool) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    raise ValueError(f"{key} must be a boolean")


def _allowed_tools(config: dict[str, Any]) -> frozenset[str]:
    value = config.get("allowed_tools")
    if value is None:
        return _SUPPORTED_TOOL_NAMES
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        raise ValueError("allowed_tools must be a non-empty list of tool names")
    normalized = frozenset(item.strip() for item in value)
    if len(normalized) != len(value):
        raise ValueError("allowed_tools must not contain duplicates")
    return normalized


def _validate_server_identity(result: Any) -> None:
    info = getattr(result, "serverInfo", None) or getattr(result, "server_info", None)
    name = getattr(info, "name", None) if info is not None else None
    version = getattr(info, "version", None) if info is not None else None
    if name not in _SUPPORTED_SERVER_NAMES:
        raise RuntimeError(f"unexpected MCP server identity {name!r}; expected imagen-mcp")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:\+[A-Za-z0-9.-]+)?", str(version or ""))
    if match is None:
        raise RuntimeError(f"imagen-mcp returned an invalid server version: {version!r}")
    parsed = (int(match.group(1)), int(match.group(2)))
    if parsed != _SUPPORTED_SERVER_VERSION:
        raise RuntimeError(f"imagen-mcp {version} is incompatible; supported range is >=0.4,<0.5")


def _positive_timeout(config: dict[str, Any], key: str, default: float) -> float:
    value = config.get(key, default)
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a positive number, not a boolean")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a positive number") from exc
    if parsed <= 0:
        raise ValueError(f"{key} must be greater than zero")
    return parsed


class _ServerCommand(NamedTuple):
    command: str
    args: tuple[str, ...] = ()
    cwd: Path | None = None


class _ToolDefinition(NamedTuple):
    name: str
    description: str
    input_schema: dict[str, Any]
    wrap_params: bool = False


def _clone_command(path: Path) -> _ServerCommand | None:
    """Return a command for a verified imagen-mcp source checkout."""

    if (
        not (path / "pyproject.toml").is_file()
        or not (path / "imagen_mcp" / "__main__.py").is_file()
    ):
        return None

    python_names = (
        ".venv/bin/python",
        "venv/bin/python",
        ".venv/Scripts/python.exe",
        "venv/Scripts/python.exe",
    )
    for relative in python_names:
        candidate = path / relative
        if candidate.is_file() and os.access(candidate, os.X_OK):
            # Do not resolve the interpreter symlink: Python uses its path to
            # locate the checkout's pyvenv.cfg and site-packages.
            return _ServerCommand(str(candidate.absolute()), ("-m", "imagen_mcp"), cwd=path)

    raise RuntimeError(
        f"imagen-mcp checkout at {path} has no local Python environment; "
        "run 'uv sync' (imagen-mcp >=0.4) before mounting it"
    )


def _entry_point_command() -> _ServerCommand | None:
    """Resolve an installed console entry point without invoking a shell."""

    candidates = [
        shutil.which("imagen-mcp", path=str(Path(sys.executable).parent)),
        shutil.which("imagen-mcp"),
    ]
    for candidate in candidates:
        if candidate:
            return _ServerCommand(str(Path(candidate).resolve()))

    try:
        distribution = metadata.distribution("imagen-mcp")
        entry_point = next(
            ep
            for ep in distribution.entry_points
            if ep.group == "console_scripts" and ep.name == "imagen-mcp"
        )
    except (metadata.PackageNotFoundError, StopIteration):
        return None

    # Keep the bootstrap source constant.  The installed distribution controls
    # the entry point, just as it would through its generated console script.
    bootstrap = (
        "from importlib.metadata import distribution;"
        "next(e for e in distribution('imagen-mcp').entry_points "
        "if e.group == 'console_scripts' and e.name == 'imagen-mcp').load()()"
    )
    logger.debug("Using installed imagen-mcp entry point %s", entry_point.value)
    return _ServerCommand(sys.executable, ("-c", bootstrap))


def _resolve_server_command(config: dict[str, Any]) -> _ServerCommand:
    explicit = config.get("imagen_mcp_path")
    if explicit is not None:
        try:
            path = Path(str(explicit)).expanduser().resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise RuntimeError(f"imagen_mcp_path does not exist: {explicit}") from exc

        if path.is_dir():
            command = _clone_command(path)
            if command is None:
                raise RuntimeError(
                    "imagen_mcp_path is not a compatible imagen-mcp >=0.4 checkout "
                    "(expected pyproject.toml and imagen_mcp/__main__.py)"
                )
            return command
        if path.is_file() and os.access(path, os.X_OK):
            return _ServerCommand(str(path))
        raise RuntimeError("imagen_mcp_path must be a checkout directory or executable")

    installed = _entry_point_command()
    if installed is not None:
        return installed

    raise RuntimeError(
        "imagen-mcp was not found. Install it so the 'imagen-mcp' console script "
        "is available, or explicitly set imagen_mcp_path to an initialized checkout."
    )


def _resolve_local_ref(schema: dict[str, Any], ref: object) -> dict[str, Any] | None:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    current: object = schema
    for raw_segment in ref[2:].split("/"):
        segment = raw_segment.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current if isinstance(current, dict) else None


_SECRET_SCHEMA_FIELDS = frozenset({"openai_api_key", "gemini_api_key"})


def _strip_secret_schema_fields(node: Any) -> None:
    """Remove credential inputs recursively from a JSON Schema in place."""

    if isinstance(node, list):
        for item in node:
            _strip_secret_schema_fields(item)
        return
    if not isinstance(node, dict):
        return

    properties = node.get("properties")
    if isinstance(properties, dict):
        for field in _SECRET_SCHEMA_FIELDS:
            properties.pop(field, None)
        required = node.get("required")
        if isinstance(required, list):
            filtered = [field for field in required if field not in _SECRET_SCHEMA_FIELDS]
            if filtered:
                node["required"] = filtered
            else:
                node.pop("required", None)

    for value in node.values():
        _strip_secret_schema_fields(value)


def _flatten_params_schema(schema: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Flatten FastMCP's sole ``params`` model while retaining valid refs."""

    root = deepcopy(schema)
    _strip_secret_schema_fields(root)
    properties = root.get("properties")
    required = root.get("required")
    if (
        not isinstance(properties, dict)
        or set(properties) != {"params"}
        or required != ["params"]
        or not isinstance(properties.get("params"), dict)
    ):
        return root, False

    params_schema = properties["params"]
    resolved = _resolve_local_ref(root, params_schema.get("$ref"))
    if resolved is None and (
        params_schema.get("type") == "object" or "properties" in params_schema
    ):
        resolved = params_schema
    if resolved is None or (resolved.get("type") != "object" and "properties" not in resolved):
        return root, False

    flattened = deepcopy(resolved)
    # Siblings of a $ref can add useful descriptions/defaults in JSON Schema
    # 2020-12.  Apply them without retaining the wrapper's local ref.
    for key, value in params_schema.items():
        if key != "$ref":
            flattened[key] = deepcopy(value)

    outer_defs = root.get("$defs")
    inner_defs = flattened.get("$defs")
    if isinstance(outer_defs, dict):
        merged_defs = deepcopy(outer_defs)
        if isinstance(inner_defs, dict):
            merged_defs.update(deepcopy(inner_defs))
        flattened["$defs"] = merged_defs
    if "$schema" in root:
        flattened.setdefault("$schema", root["$schema"])
    return flattened, True


def _model_dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(value, dict):
        return deepcopy(value)
    return str(value)


def _result_field(result: Any, name: str, default: Any = None) -> Any:
    if isinstance(result, dict):
        return result.get(name, default)
    return getattr(result, name, default)


def _redact_binary_result_fields(value: Any) -> Any:
    """Copy protocol output while removing fields commonly used for binary payloads."""

    if isinstance(value, dict):
        redacted: dict[Any, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            if normalized_key in _BINARY_RESULT_FIELDS and isinstance(
                item, (bytes, bytearray, memoryview, str)
            ):
                redacted[key] = "[binary content omitted]"
            else:
                redacted[key] = _redact_binary_result_fields(item)
        return redacted
    if isinstance(value, list):
        return [_redact_binary_result_fields(item) for item in value]
    if isinstance(value, tuple):
        return [_redact_binary_result_fields(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "[binary content omitted]"
    return deepcopy(value)


def _bounded_result_output(value: Any) -> Any:
    """Redact binary fields and keep any single tool result within a safe bound."""

    redacted = _redact_binary_result_fields(value)
    if isinstance(redacted, str):
        encoded = redacted.encode("utf-8")
        if len(encoded) <= _MAX_TOOL_OUTPUT_BYTES:
            return redacted
        suffix = "\n[tool output truncated by tool-imagen]"
        budget = _MAX_TOOL_OUTPUT_BYTES - len(suffix.encode("utf-8"))
        prefix = encoded[:budget].decode("utf-8", errors="ignore")
        return prefix + suffix

    encoded = json.dumps(redacted, ensure_ascii=False, default=str).encode("utf-8")
    if len(encoded) <= _MAX_TOOL_OUTPUT_BYTES:
        return redacted
    return {
        "omitted": True,
        "bytes": len(encoded),
        "message": (
            "MCP tool output exceeded the tool-imagen context limit and was omitted; "
            "use the saved artifact path or inspect the server logs."
        ),
    }


def _result_output(result: Any) -> Any:
    """Convert MCP content without serializing binary payloads into LLM text."""

    structured = _result_field(result, "structuredContent")
    if structured is None:
        structured = _result_field(result, "structured_content")
    if structured is not None:
        # structuredContent is authoritative; text content is the protocol's
        # backwards-compatible rendering of the same result.
        return _bounded_result_output(_model_dump(structured))

    content = _result_field(result, "content", []) or []
    text_parts: list[str] = []
    serialized: list[Any] = []
    all_text = True
    for block in content:
        block_type = _result_field(block, "type")
        if block_type == "text":
            text = _result_field(block, "text", "")
            text_parts.append(str(text))
            serialized.append(_model_dump(block))
        elif block_type in {"image", "audio"}:
            all_text = False
            data = _result_field(block, "data", "")
            encoded_length = len(data) if isinstance(data, str) else 0
            approximate_bytes = (encoded_length * 3) // 4
            serialized.append(
                {
                    "type": block_type,
                    "mimeType": _result_field(block, "mimeType")
                    or _result_field(block, "mime_type"),
                    "bytes": approximate_bytes,
                    "omitted": True,
                    "message": (
                        "Binary MCP content was omitted from textual tool output; "
                        "use the saved artifact path or a vision-capable client."
                    ),
                }
            )
        else:
            all_text = False
            serialized.append(_model_dump(block))

    if all_text:
        return _bounded_result_output("\n".join(text_parts))
    return _bounded_result_output(serialized)


def _error_message(tool_name: str, output: Any) -> str:
    if isinstance(output, str) and output.strip():
        return output.strip()
    if output not in (None, "", [], {}):
        return json.dumps(output, ensure_ascii=False, default=str)
    return f"MCP tool '{tool_name}' reported an error without details"


class _MCPAdapter:
    """Own one initialized MCP SDK session for all discovered imagen tools."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._server = _resolve_server_command(config)
        self._env = _build_env(config)
        self._call_timeout = _positive_timeout(config, "timeout_seconds", 600.0)
        self._startup_timeout = _positive_timeout(config, "startup_timeout_seconds", 30.0)
        self._shutdown_timeout = _positive_timeout(config, "shutdown_timeout_seconds", 10.0)
        self._allowed_tools = _allowed_tools(config)
        self._strict_tool_contract = _boolean_config(config, "strict_tool_contract", True)
        self._session: ClientSession | None = None
        self._tools: tuple[_ToolDefinition, ...] = ()
        self._tool_names: frozenset[str] = frozenset()
        self._wrapped_tools: set[str] = set()
        self._connection_task: asyncio.Task[None] | None = None
        self._ready = asyncio.Event()
        self._shutdown = asyncio.Event()
        self._connect_lock = asyncio.Lock()
        self._call_lock = asyncio.Lock()
        self._connection_error: BaseException | None = None
        self._closing = False

    @property
    def tools(self) -> tuple[_ToolDefinition, ...]:
        return self._tools

    async def _list_tools(self, session: ClientSession) -> tuple[_ToolDefinition, ...]:
        definitions: list[_ToolDefinition] = []
        names: set[str] = set()
        cursor: str | None = None
        seen_cursors: set[str] = set()

        while True:
            page = await session.list_tools(cursor=cursor)
            for tool in page.tools:
                if not tool.name or tool.name in names:
                    raise RuntimeError(f"imagen-mcp returned duplicate/invalid tool: {tool.name!r}")
                schema = tool.inputSchema
                if not isinstance(schema, dict):
                    raise RuntimeError(f"imagen-mcp tool '{tool.name}' has an invalid schema")
                flat_schema, wrapped = _flatten_params_schema(schema)
                definitions.append(
                    _ToolDefinition(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=flat_schema,
                        wrap_params=wrapped,
                    )
                )
                names.add(tool.name)

            next_cursor = getattr(page, "nextCursor", None)
            if not next_cursor:
                break
            if next_cursor in seen_cursors:
                raise RuntimeError("imagen-mcp returned a repeated tools/list cursor")
            seen_cursors.add(next_cursor)
            cursor = next_cursor

        if not definitions:
            raise RuntimeError("imagen-mcp did not advertise any tools")
        advertised = {definition.name for definition in definitions}
        missing = self._allowed_tools - advertised
        unexpected = advertised - self._allowed_tools
        if missing:
            raise RuntimeError(
                "imagen-mcp is missing required tools: " + ", ".join(sorted(missing))
            )
        if unexpected and self._strict_tool_contract:
            raise RuntimeError(
                "imagen-mcp advertised unreviewed tools: "
                + ", ".join(sorted(unexpected))
                + "; update allowed_tools or set strict_tool_contract=false to ignore them"
            )
        if unexpected:
            logger.warning(
                "Ignoring imagen-mcp tools outside the allowlist: %s", sorted(unexpected)
            )
        return tuple(
            definition for definition in definitions if definition.name in self._allowed_tools
        )

    async def _connection_main(self) -> None:
        params = StdioServerParameters(
            command=self._server.command,
            args=list(self._server.args),
            env=self._env,
            cwd=self._server.cwd,
        )
        try:
            logger.debug(
                "Starting imagen-mcp via %s %s (cwd=%s)",
                self._server.command,
                list(self._server.args),
                self._server.cwd,
            )
            # The SDK passes this file descriptor directly to the child, so
            # stderr cannot fill a pipe and deadlock the protocol.
            with open(os.devnull, "w", encoding="utf-8") as errlog:
                async with stdio_client(params, errlog=errlog) as (read, write):
                    async with ClientSession(
                        read,
                        write,
                        read_timeout_seconds=timedelta(seconds=self._startup_timeout),
                    ) as session:
                        initialize_result = await session.initialize()
                        _validate_server_identity(initialize_result)
                        tools = await self._list_tools(session)
                        self._session = session
                        self._tools = tools
                        self._tool_names = frozenset(definition.name for definition in tools)
                        self._wrapped_tools = {
                            definition.name for definition in tools if definition.wrap_params
                        }
                        self._ready.set()
                        await self._shutdown.wait()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._connection_error = exc
            logger.exception("imagen-mcp connection failed")
        finally:
            self._session = None
            self._ready.set()

    async def connect(self) -> tuple[_ToolDefinition, ...]:
        async with self._connect_lock:
            if self._closing:
                raise RuntimeError("imagen-mcp adapter is closed")
            if self._session is not None:
                return self._tools
            if self._connection_task is None:
                self._connection_task = asyncio.create_task(
                    self._connection_main(), name="imagen-mcp-session"
                )

            try:
                async with asyncio.timeout(self._startup_timeout):
                    await self._ready.wait()
            except TimeoutError as exc:
                await self.close()
                raise TimeoutError(
                    f"imagen-mcp startup timed out after {self._startup_timeout:g} seconds"
                ) from exc

            if self._connection_error is not None:
                error = self._connection_error
                await self.close()
                raise RuntimeError(f"imagen-mcp startup failed: {error}") from error
            if self._session is None:
                await self.close()
                raise RuntimeError("imagen-mcp exited before completing startup")
            return self._tools

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if self._session is None:
            raise RuntimeError("imagen-mcp is not connected")
        if tool_name not in self._tool_names:
            raise RuntimeError(f"imagen-mcp did not advertise tool '{tool_name}'")

        wire_arguments = (
            {"params": deepcopy(arguments)}
            if tool_name in self._wrapped_tools
            else deepcopy(arguments)
        )
        # ClientSession correlates request IDs, and serialization additionally
        # protects servers/providers that are not safe for overlapping calls.
        async with self._call_lock:
            try:
                async with asyncio.timeout(self._call_timeout):
                    return await self._session.call_tool(
                        tool_name,
                        arguments=wire_arguments,
                        read_timeout_seconds=timedelta(seconds=self._call_timeout),
                    )
            except TimeoutError as exc:
                raise TimeoutError(
                    f"imagen-mcp tool '{tool_name}' timed out after {self._call_timeout:g} seconds"
                ) from exc
            except McpError as exc:
                if exc.error.code == 408:
                    raise TimeoutError(
                        f"imagen-mcp tool '{tool_name}' timed out after "
                        f"{self._call_timeout:g} seconds"
                    ) from exc
                raise

    async def close(self) -> None:
        if self._closing and self._connection_task is None:
            return
        self._closing = True
        task = self._connection_task
        if task is None:
            return

        self._shutdown.set()
        try:
            async with asyncio.timeout(self._shutdown_timeout):
                await asyncio.shield(task)
        except TimeoutError:
            logger.warning(
                "imagen-mcp shutdown exceeded %.1f seconds; cancelling", self._shutdown_timeout
            )
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        finally:
            self._connection_task = None


class ImagenTool:
    """An MCP tool presented through Amplifier's native Tool interface."""

    def __init__(self, definition: _ToolDefinition, adapter: _MCPAdapter) -> None:
        self._name = definition.name
        self._description = definition.description
        self._input_schema = definition.input_schema
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
            result = await self._adapter.call(self._name, input)
            output = _result_output(result)
            is_error = bool(_result_field(result, "isError", False))
            if is_error:
                message = _error_message(self._name, output)
                return ToolResult(
                    success=False,
                    output=output if output not in (None, "") else f"Error: {message}",
                    error={"message": message, "mcp_tool": self._name},
                )
            return ToolResult(success=True, output=output)
        except Exception as exc:
            logger.exception("imagen tool %s raised", self._name)
            message = f"{type(exc).__name__}: {exc}"
            return ToolResult(
                success=False,
                output=f"Error: {message}",
                error={"message": message, "mcp_tool": self._name},
            )


async def mount(
    coordinator: ModuleCoordinator,
    config: dict[str, Any] | None = None,
):
    """Initialize imagen-mcp, discover its tools, and mount them in Amplifier."""

    cfg = config or {}
    mode = cfg.get("mode", "mcp")
    if mode == "direct":
        raise ValueError(
            "tool-imagen 2.0 removed unsupported direct mode; use mode='mcp' "
            "(or legacy mode='subprocess') with an imagen-mcp server"
        )
    if mode not in {"mcp", "subprocess"}:
        raise ValueError("mode must be 'mcp' or the legacy alias 'subprocess'")

    adapter = _MCPAdapter(cfg)
    registered: list[str] = []
    try:
        definitions = await adapter.connect()
        coordinator_get = getattr(coordinator, "get", None)
        if callable(coordinator_get):
            collisions = [
                definition.name
                for definition in definitions
                if coordinator_get("tools", definition.name) is not None
            ]
            if collisions:
                raise RuntimeError(
                    "tool name collision while mounting imagen-mcp: "
                    + ", ".join(sorted(collisions))
                )
        for definition in definitions:
            tool = ImagenTool(definition, adapter)
            await coordinator.mount("tools", tool, name=tool.name)
            registered.append(tool.name)
    except BaseException:
        coordinator_unmount = getattr(coordinator, "unmount", None)
        if callable(coordinator_unmount):
            for name in reversed(registered):
                with suppress(Exception):
                    result = coordinator_unmount("tools", name)
                    if isawaitable(result):
                        await result
        await adapter.close()
        raise

    logger.info("imagen-mcp tools registered dynamically: %s", registered)

    async def cleanup() -> None:
        await adapter.close()

    return cleanup

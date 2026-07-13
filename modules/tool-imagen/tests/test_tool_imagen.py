"""Unit and provider-free MCP integration tests for tool-imagen."""

from __future__ import annotations

import os
import shlex
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from mcp.types import CallToolResult, ImageContent, TextContent, Tool

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from amplifier_core import ToolResult  # noqa: E402
from amplifier_core.validation import ToolValidator  # noqa: E402

import amplifier_module_tool_imagen as mod  # noqa: E402

EXPECTED_TOOLS = {
    "generate_image",
    "conversational_image",
    "edit_image",
    "list_providers",
    "list_conversations",
    "list_gemini_models",
    "estimate_cost",
    "generate_image_batch",
}


class _RecordingCoordinator:
    def __init__(self) -> None:
        self.mounted: list[tuple[str, object, str]] = []

    async def mount(self, namespace: str, obj: object, name: str) -> None:
        self.mounted.append((namespace, obj, name))

    @property
    def tools(self) -> dict[str, Any]:
        return {name: obj for _, obj, name in self.mounted}


class _FakeAdapter:
    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call(self, name: str, arguments: dict[str, Any]) -> Any:
        self.calls.append((name, arguments))
        if self.error:
            raise self.error
        return self.result


def _definition(name: str = "generate_image") -> mod._ToolDefinition:
    return mod._ToolDefinition(name, "description", {"type": "object", "properties": {}})


@pytest.fixture
def fake_checkout(tmp_path: Path) -> Path:
    checkout = tmp_path / "imagen-mcp"
    package = checkout / "imagen_mcp"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    shutil.copy(Path(__file__).with_name("fake_mcp_server.py"), package / "__main__.py")
    (checkout / "pyproject.toml").write_text(
        "[project]\nname='fake-imagen-mcp'\nversion='0.4.0'\n", encoding="utf-8"
    )
    venv_python = checkout / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text(
        f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n', encoding="utf-8"
    )
    venv_python.chmod(0o755)
    return checkout


def test_build_env_uses_allowlist_and_config_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "from-parent")
    monkeypatch.setenv("UNRELATED_SECRET", "do-not-forward")
    monkeypatch.delenv("DEFAULT_OPENAI_SIZE", raising=False)
    monkeypatch.delenv("DEFAULT_GEMINI_SIZE", raising=False)
    defaults = mod._build_env({})
    assert "DEFAULT_OPENAI_SIZE" not in defaults
    assert "DEFAULT_GEMINI_SIZE" not in defaults

    env = mod._build_env(
        {
            "openai_api_key": "from-config",
            "gemini_api_key": "gemini-config",
            "default_provider": "gemini",
            "default_openai_size": "1024x1536",
            "default_gemini_size": "4K",
            "default_gemini_aspect_ratio": "16:9",
            "enable_google_search": False,
            "enable_prompt_enhancement": "false",
            "allowed_input_roots": ["~/Pictures", "/tmp/authorized-images"],
            "conversation_retention_days": 14,
        }
    )

    assert env["OPENAI_API_KEY"] == "from-config"
    assert env["GEMINI_API_KEY"] == "gemini-config"
    assert env["DEFAULT_PROVIDER"] == "gemini"
    assert env["ENABLE_GOOGLE_SEARCH"] == "false"
    assert env["IMAGEN_MCP_TRANSPORT"] == "stdio"
    assert env["DEFAULT_OPENAI_SIZE"] == "1024x1536"
    assert env["DEFAULT_GEMINI_SIZE"] == "4K"
    assert env["DEFAULT_GEMINI_ASPECT_RATIO"] == "16:9"
    assert env["ENABLE_PROMPT_ENHANCEMENT"] == "false"
    assert env["IMAGEN_MCP_ALLOWED_INPUT_ROOTS"] == os.pathsep.join(
        [str(Path("~/Pictures").expanduser()), "/tmp/authorized-images"]
    )
    assert env["IMAGEN_MCP_CONVERSATION_RETENTION_DAYS"] == "14"
    assert "UNRELATED_SECRET" not in env


@pytest.mark.parametrize("key", ["enable_google_search", "enable_prompt_enhancement"])
def test_build_env_rejects_ambiguous_boolean_values(key: str) -> None:
    with pytest.raises(ValueError, match="must be a boolean"):
        mod._build_env({key: "definitely"})


@pytest.mark.parametrize("value", [[], "~/Pictures", [""], [1]])
def test_build_env_rejects_invalid_allowed_input_roots(value: object) -> None:
    with pytest.raises(ValueError, match="non-empty list of paths"):
        mod._build_env({"allowed_input_roots": value})


@pytest.mark.parametrize("value", [-1, True, 1.5, "1.5", "nope", None])
def test_build_env_rejects_invalid_conversation_retention(value: object) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        mod._build_env({"conversation_retention_days": value})


@pytest.mark.parametrize("value", [0, -1, True, "nope", None])
def test_timeout_validation_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError, match="positive|greater than zero|boolean"):
        mod._positive_timeout({"timeout": value}, "timeout", 1)


def test_flatten_params_schema_retains_nested_definitions() -> None:
    schema = {
        "$defs": {
            "Request": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "provider": {"$ref": "#/$defs/Provider"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/BatchItem"},
                    },
                },
                "required": ["prompt"],
            },
            "Provider": {"type": "string", "enum": ["auto", "openai", "gemini"]},
            "BatchItem": {
                "type": "object",
                "properties": {"prompt": {"type": "string"}},
                "required": ["prompt"],
            },
        },
        "type": "object",
        "properties": {"params": {"$ref": "#/$defs/Request"}},
        "required": ["params"],
    }

    flattened, wrapped = mod._flatten_params_schema(schema)

    assert wrapped is True
    assert "params" not in flattened["properties"]
    assert set(flattened["$defs"]) == {"Request", "Provider", "BatchItem"}
    Draft202012Validator.check_schema(flattened)
    Draft202012Validator(flattened).validate(
        {
            "prompt": "cat",
            "provider": "auto",
            "items": [{"prompt": "one"}],
        }
    )
    assert schema["properties"] == {"params": {"$ref": "#/$defs/Request"}}


def test_flatten_strips_credential_fields_recursively() -> None:
    schema = {
        "$defs": {
            "Request": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "openai_api_key": {"type": "string"},
                    "nested": {"$ref": "#/$defs/Nested"},
                },
                "required": ["prompt", "openai_api_key"],
            },
            "Nested": {
                "type": "object",
                "properties": {
                    "gemini_api_key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["gemini_api_key"],
            },
        },
        "type": "object",
        "properties": {"params": {"$ref": "#/$defs/Request"}},
        "required": ["params"],
    }

    flattened, wrapped = mod._flatten_params_schema(schema)

    assert wrapped is True
    assert "openai_api_key" not in flattened["properties"]
    assert flattened["required"] == ["prompt"]
    nested = flattened["$defs"]["Nested"]
    assert "gemini_api_key" not in nested["properties"]
    assert "required" not in nested
    assert "openai_api_key" in schema["$defs"]["Request"]["properties"]


def test_flatten_leaves_zero_arg_and_multi_arg_schemas_unchanged() -> None:
    empty = {"type": "object", "properties": {}}
    multi = {
        "type": "object",
        "properties": {"params": {"type": "object"}, "ctx": {"type": "object"}},
        "required": ["params"],
    }
    assert mod._flatten_params_schema(empty) == (empty, False)
    assert mod._flatten_params_schema(multi) == (multi, False)


def test_resolve_explicit_checkout_and_executable(fake_checkout: Path) -> None:
    checkout_command = mod._resolve_server_command({"imagen_mcp_path": str(fake_checkout)})
    assert checkout_command.command == str((fake_checkout / ".venv" / "bin" / "python").resolve())
    assert checkout_command.args == ("-m", "imagen_mcp")
    assert checkout_command.cwd == fake_checkout.resolve()

    executable_command = mod._resolve_server_command({"imagen_mcp_path": sys.executable})
    assert executable_command.command == str(Path(sys.executable).resolve())
    assert executable_command.args == ()


def test_resolve_rejects_missing_or_invalid_explicit_path(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="does not exist"):
        mod._resolve_server_command({"imagen_mcp_path": tmp_path / "missing"})
    with pytest.raises(RuntimeError, match="not a compatible imagen-mcp"):
        mod._resolve_server_command({"imagen_mcp_path": tmp_path})


def test_resolve_rejects_uninitialized_checkout(tmp_path: Path) -> None:
    checkout = tmp_path / "imagen-mcp"
    (checkout / "imagen_mcp").mkdir(parents=True)
    (checkout / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (checkout / "imagen_mcp" / "__main__.py").write_text("", encoding="utf-8")

    with pytest.raises(RuntimeError, match="uv sync"):
        mod._resolve_server_command({"imagen_mcp_path": checkout})


def test_result_output_prefers_structured_content_and_preserves_images() -> None:
    structured = CallToolResult(
        content=[TextContent(type="text", text='{"answer": 42}')],
        structuredContent={"answer": 42},
    )
    assert mod._result_output(structured) == {"answer": 42}

    image = CallToolResult(
        content=[
            TextContent(type="text", text="preview"),
            ImageContent(type="image", data="aGVsbG8=", mimeType="image/png"),
        ]
    )
    output = mod._result_output(image)
    assert output[0] == {"type": "text", "text": "preview"}
    assert output[1]["type"] == "image"
    assert output[1]["mimeType"] == "image/png"
    assert output[1]["omitted"] is True
    assert "data" not in output[1]


def test_result_output_redacts_nested_binary_structured_content() -> None:
    result = {
        "structuredContent": {
            "output_path": "/tmp/result.png",
            "preview": {
                "image-data": "aGVsbG8=",
                "nested": [{"blob": b"secret"}],
            },
        }
    }

    assert mod._result_output(result) == {
        "output_path": "/tmp/result.png",
        "preview": {
            "image-data": "[binary content omitted]",
            "nested": [{"blob": "[binary content omitted]"}],
        },
    }


def test_result_output_enforces_size_limit_for_text_and_structured_content() -> None:
    oversized_text = "x" * (mod._MAX_TOOL_OUTPUT_BYTES + 100)
    bounded_text = mod._result_output(
        CallToolResult(content=[TextContent(type="text", text=oversized_text)])
    )
    assert bounded_text.endswith("[tool output truncated by tool-imagen]")
    assert len(bounded_text.encode("utf-8")) <= mod._MAX_TOOL_OUTPUT_BYTES

    bounded_structured = mod._result_output(
        {"structuredContent": {"items": ["x" * mod._MAX_TOOL_OUTPUT_BYTES] * 2}}
    )
    assert bounded_structured["omitted"] is True
    assert bounded_structured["bytes"] > mod._MAX_TOOL_OUTPUT_BYTES


@pytest.mark.asyncio
async def test_imagen_tool_maps_success_mcp_error_and_exception() -> None:
    adapter = _FakeAdapter(CallToolResult(content=[TextContent(type="text", text="ok")]))
    tool = mod.ImagenTool(_definition(), adapter)
    success = await tool.execute({"prompt": "cat"})
    assert isinstance(success, ToolResult)
    assert success.success is True
    assert success.output == "ok"
    assert adapter.calls == [("generate_image", {"prompt": "cat"})]

    adapter.result = CallToolResult(
        content=[TextContent(type="text", text="provider unavailable")], isError=True
    )
    failure = await tool.execute({"prompt": "cat"})
    assert failure.success is False
    assert failure.output == "provider unavailable"
    assert failure.error == {
        "message": "provider unavailable",
        "mcp_tool": "generate_image",
    }

    adapter.error = RuntimeError("transport broke")
    exception = await tool.execute({"prompt": "cat"})
    assert exception.success is False
    assert "transport broke" in exception.error["message"]


class _PageSession:
    def __init__(self, repeat_cursor: bool = False) -> None:
        self.repeat_cursor = repeat_cursor

    async def list_tools(self, cursor: str | None = None) -> Any:
        if cursor is None:
            return SimpleNamespace(
                tools=[
                    Tool(
                        name="first",
                        description="one",
                        inputSchema={"type": "object", "properties": {}},
                    )
                ],
                nextCursor="next",
            )
        return SimpleNamespace(
            tools=[
                Tool(
                    name="second",
                    description="two",
                    inputSchema={"type": "object", "properties": {}},
                )
            ],
            nextCursor="next" if self.repeat_cursor else None,
        )


@pytest.mark.asyncio
async def test_list_tools_reads_all_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mod, "_resolve_server_command", lambda _config: mod._ServerCommand(sys.executable)
    )
    adapter = mod._MCPAdapter({"allowed_tools": ["first", "second"]})
    definitions = await adapter._list_tools(_PageSession())
    assert [definition.name for definition in definitions] == ["first", "second"]

    with pytest.raises(RuntimeError, match="repeated"):
        await adapter._list_tools(_PageSession(repeat_cursor=True))


@pytest.mark.asyncio
async def test_list_tools_rejects_missing_and_unreviewed_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mod, "_resolve_server_command", lambda _config: mod._ServerCommand(sys.executable)
    )
    with pytest.raises(RuntimeError, match="unreviewed"):
        await mod._MCPAdapter({"allowed_tools": ["first"]})._list_tools(_PageSession())

    with pytest.raises(RuntimeError, match="missing required"):
        await mod._MCPAdapter({"allowed_tools": ["first", "missing"]})._list_tools(
            _PageSession(),
        )

    definitions = await mod._MCPAdapter(
        {"allowed_tools": ["first"], "strict_tool_contract": False}
    )._list_tools(_PageSession())
    assert [definition.name for definition in definitions] == ["first"]


def test_server_identity_requires_imagen_mcp_0_4_or_newer() -> None:
    valid = SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="0.4.0"))
    mod._validate_server_identity(valid)

    with pytest.raises(RuntimeError, match="unexpected MCP server"):
        mod._validate_server_identity(
            SimpleNamespace(serverInfo=SimpleNamespace(name="other", version="0.4.0"))
        )
    with pytest.raises(RuntimeError, match=">=0.4,<0.5"):
        mod._validate_server_identity(
            SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="0.3.9"))
        )
    with pytest.raises(RuntimeError, match=">=0.4,<0.5"):
        mod._validate_server_identity(
            SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="1.0.0"))
        )
    with pytest.raises(RuntimeError, match=">=0.4,<0.5"):
        mod._validate_server_identity(
            SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="0.5.0"))
        )
    mod._validate_server_identity(
        SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="0.4.99"))
    )
    with pytest.raises(RuntimeError, match="invalid server version"):
        mod._validate_server_identity(
            SimpleNamespace(serverInfo=SimpleNamespace(name="imagen_mcp", version="0.5.0rc1"))
        )


@pytest.mark.asyncio
async def test_fake_server_mount_discovery_calls_errors_and_timeout_recovery(
    fake_checkout: Path,
) -> None:
    coordinator = _RecordingCoordinator()
    cleanup = await mod.mount(
        coordinator,
        {
            "mode": "mcp",
            "imagen_mcp_path": str(fake_checkout),
            "timeout_seconds": 0.1,
        },
    )
    try:
        assert {name for _, _, name in coordinator.mounted} == EXPECTED_TOOLS
        assert {namespace for namespace, _, _ in coordinator.mounted} == {"tools"}

        generate = coordinator.tools["generate_image"]
        assert "params" not in generate.input_schema["properties"]
        assert "Provider" in generate.input_schema["$defs"]
        Draft202012Validator(generate.input_schema).validate({"prompt": "cat", "provider": "auto"})
        generated = await generate.execute({"prompt": "cat", "provider": "openai"})
        assert generated.success is True
        assert generated.output == {"result": "generated:cat:openai"}

        cost = await coordinator.tools["estimate_cost"].execute({"prompt": "cat", "n": 2})
        assert cost.success is True
        assert cost.output == {"provider": "openai", "total_usd": 0.02}

        failed = await coordinator.tools["edit_image"].execute(
            {"prompt": "fail", "image_path": "/tmp/input.png"}
        )
        assert failed.success is False
        assert "synthetic edit failure" in failed.error["message"]

        timed_out = await coordinator.tools["conversational_image"].execute(
            {"prompt": "slow", "delay_seconds": 0.25}
        )
        assert timed_out.success is False
        assert "timed out" in timed_out.error["message"]

        recovered = await coordinator.tools["list_providers"].execute({})
        assert recovered.success is True
        assert recovered.output == {"result": "openai,gemini"}
    finally:
        await cleanup()
        await cleanup()


@pytest.mark.asyncio
async def test_official_amplifier_validator_with_external_runtime(
    fake_checkout: Path,
) -> None:
    """Exercise Amplifier's own module validator without coupling the packages."""

    validator = ToolValidator()
    result = await validator.validate(
        PACKAGE_ROOT / "amplifier_module_tool_imagen",
        config={"imagen_mcp_path": str(fake_checkout)},
    )

    assert result.passed, [check.message for check in result.checks if not check.passed]


@pytest.mark.asyncio
async def test_mount_rejects_removed_or_unknown_modes() -> None:
    coordinator = _RecordingCoordinator()
    with pytest.raises(ValueError, match="removed unsupported direct mode"):
        await mod.mount(coordinator, {"mode": "direct"})
    with pytest.raises(ValueError, match="mode must be"):
        await mod.mount(coordinator, {"mode": "magic"})


@pytest.mark.asyncio
async def test_mount_closes_adapter_when_registration_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = {"closed": False}

    class FakeMCPAdapter:
        def __init__(self, _config: dict[str, Any]) -> None:
            pass

        async def connect(self) -> tuple[mod._ToolDefinition, ...]:
            return (_definition(),)

        async def close(self) -> None:
            state["closed"] = True

    class BrokenCoordinator:
        async def mount(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("registration failed")

    monkeypatch.setattr(mod, "_MCPAdapter", FakeMCPAdapter)
    with pytest.raises(RuntimeError, match="registration failed"):
        await mod.mount(BrokenCoordinator())
    assert state["closed"] is True


@pytest.mark.asyncio
async def test_mount_rejects_existing_tool_name_and_closes_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = {"closed": False}

    class FakeMCPAdapter:
        def __init__(self, _config: dict[str, Any]) -> None:
            pass

        async def connect(self) -> tuple[mod._ToolDefinition, ...]:
            return (_definition(),)

        async def close(self) -> None:
            state["closed"] = True

    class CollisionCoordinator(_RecordingCoordinator):
        def get(self, namespace: str, name: str) -> object | None:
            assert namespace == "tools"
            return object() if name == "generate_image" else None

    monkeypatch.setattr(mod, "_MCPAdapter", FakeMCPAdapter)
    with pytest.raises(RuntimeError, match="tool name collision"):
        await mod.mount(CollisionCoordinator())
    assert state["closed"] is True


@pytest.mark.asyncio
async def test_external_imagen_mcp_contract_when_explicitly_requested() -> None:
    configured = os.getenv("IMAGEN_MCP_CONTRACT_PATH")
    if not configured:
        pytest.skip("set IMAGEN_MCP_CONTRACT_PATH for the opt-in external contract test")
    checkout = Path(configured).expanduser().resolve()
    if not (checkout / "imagen_mcp" / "__main__.py").is_file():
        pytest.skip("local imagen-mcp checkout is unavailable")
    try:
        mod._clone_command(checkout)
    except RuntimeError:
        pytest.skip("local imagen-mcp checkout has no initialized venv")

    coordinator = _RecordingCoordinator()
    cleanup = await mod.mount(
        coordinator,
        {
            "imagen_mcp_path": str(checkout),
            "startup_timeout_seconds": 30,
        },
    )
    try:
        assert set(coordinator.tools) == EXPECTED_TOOLS
        for name, tool in coordinator.tools.items():
            Draft202012Validator.check_schema(tool.input_schema)
            if name not in {"list_providers", "list_gemini_models"}:
                assert "params" not in tool.input_schema.get("properties", {})

        secret_names = {"openai_api_key", "gemini_api_key"}
        for tool in coordinator.tools.values():
            assert secret_names.isdisjoint(tool.input_schema.get("properties", {}))
            for definition in tool.input_schema.get("$defs", {}).values():
                if isinstance(definition, dict):
                    assert secret_names.isdisjoint(definition.get("properties", {}))
    finally:
        await cleanup()

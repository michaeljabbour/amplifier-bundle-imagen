"""Unit tests for amplifier-module-tool-imagen.

These tests exercise the pure-Python surface: schema shape, adapter fan-out,
ToolResult mapping, and mount() registering all six tools.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

import amplifier_module_tool_imagen as mod  # noqa: E402
from amplifier_core import ToolResult  # noqa: E402


class _RecordingCoordinator:
    """Minimal ModuleCoordinator stand-in that records mount calls."""

    def __init__(self):
        self.mounted: list[tuple[str, object, str]] = []

    async def mount(self, namespace, obj, name):
        self.mounted.append((namespace, obj, name))


# ── Tests ───────────────────────────────────────────────────────────────────

def test_tool_definitions_count_and_names():
    names = [t["name"] for t in mod._TOOL_DEFINITIONS]
    assert names == [
        "generate_image",
        "conversational_image",
        "edit_image",
        "list_providers",
        "list_conversations",
        "list_gemini_models",
    ]


def test_edit_image_schema_exposes_input_fidelity():
    edit = next(t for t in mod._TOOL_DEFINITIONS if t["name"] == "edit_image")
    assert "input_fidelity" in edit["input_schema"]["properties"]
    assert edit["input_schema"]["properties"]["input_fidelity"]["enum"] == ["high", "low"]


def test_all_schemas_are_well_formed_json_schema():
    for t in mod._TOOL_DEFINITIONS:
        schema = t["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema


def test_build_env_sets_api_keys_and_defaults():
    env = mod._build_env(
        {
            "openai_api_key": "sk-test",
            "gemini_api_key": "gk-test",
            "default_provider": "gemini",
            "enable_google_search": True,
        }
    )
    assert env["OPENAI_API_KEY"] == "sk-test"
    assert env["GEMINI_API_KEY"] == "gk-test"
    assert env["DEFAULT_PROVIDER"] == "gemini"
    assert env["ENABLE_GOOGLE_SEARCH"] == "true"
    assert env["IMAGEN_MCP_LOG_LEVEL"] == "WARNING"
    assert env["DEFAULT_OPENAI_SIZE"] == "1536x1024"
    assert env["DEFAULT_GEMINI_SIZE"] == "2K"


class _FakeAdapter:
    def __init__(self):
        self.calls = []
        self.next_result = "ok"
        self.should_raise = False

    async def call(self, name, params):
        self.calls.append((name, params))
        if self.should_raise:
            raise RuntimeError("boom")
        return self.next_result

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_execute_returns_successful_toolresult():
    adapter = _FakeAdapter()
    adapter.next_result = "https://example/x.png"
    tool = mod.ImagenTool(
        name="generate_image",
        description="",
        input_schema={"type": "object", "properties": {}},
        adapter=adapter,
    )
    result = await tool.execute({"prompt": "a cat"})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.output == "https://example/x.png"
    assert adapter.calls == [("generate_image", {"prompt": "a cat"})]


@pytest.mark.asyncio
async def test_execute_converts_error_string_to_failed_toolresult():
    adapter = _FakeAdapter()
    adapter.next_result = "Error: provider unavailable"
    tool = mod.ImagenTool(
        name="generate_image",
        description="",
        input_schema={"type": "object", "properties": {}},
        adapter=adapter,
    )
    result = await tool.execute({"prompt": "x"})
    assert result.success is False
    assert result.error == {"message": "provider unavailable"}


@pytest.mark.asyncio
async def test_execute_catches_exception():
    adapter = _FakeAdapter()
    adapter.should_raise = True
    tool = mod.ImagenTool(
        name="generate_image",
        description="",
        input_schema={"type": "object", "properties": {}},
        adapter=adapter,
    )
    result = await tool.execute({"prompt": "x"})
    assert result.success is False
    assert "boom" in result.error["message"]


@pytest.mark.asyncio
async def test_mount_registers_all_six_tools(monkeypatch):
    adapter = _FakeAdapter()
    monkeypatch.setattr(mod, "_SubprocessAdapter", lambda cfg: adapter)
    coordinator = _RecordingCoordinator()

    cleanup = await mod.mount(coordinator, {"mode": "subprocess"})

    assert len(coordinator.mounted) == 6
    registered_names = [name for _, _, name in coordinator.mounted]
    assert registered_names == [
        "generate_image",
        "conversational_image",
        "edit_image",
        "list_providers",
        "list_conversations",
        "list_gemini_models",
    ]
    namespaces = {ns for ns, _, _ in coordinator.mounted}
    assert namespaces == {"tools"}
    # cleanup is awaitable
    await cleanup()


@pytest.mark.asyncio
async def test_mount_direct_mode_uses_direct_adapter(monkeypatch):
    used = {}

    def _fake_direct(cfg):
        used["direct"] = True
        return _FakeAdapter()

    monkeypatch.setattr(mod, "_DirectAdapter", _fake_direct)
    coordinator = _RecordingCoordinator()
    await mod.mount(coordinator, {"mode": "direct"})
    assert used == {"direct": True}

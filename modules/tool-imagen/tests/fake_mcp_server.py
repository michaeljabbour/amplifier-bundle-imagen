"""Provider-free MCP server used by the tool-imagen integration tests."""

from __future__ import annotations

import asyncio
from enum import StrEnum

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


class Provider(StrEnum):
    AUTO = "auto"
    OPENAI = "openai"
    GEMINI = "gemini"


class GenerateInput(BaseModel):
    prompt: str = Field(min_length=1)
    provider: Provider = Provider.AUTO


class ConversationInput(BaseModel):
    prompt: str
    delay_seconds: float = Field(default=0, ge=0, le=2)


class EditInput(BaseModel):
    prompt: str
    image_path: str


class ListInput(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)


class EstimateInput(BaseModel):
    prompt: str
    n: int = Field(default=1, ge=1, le=10)


class EstimateOutput(BaseModel):
    provider: str
    total_usd: float


class BatchItem(BaseModel):
    prompt: str
    provider: Provider = Provider.AUTO


class BatchInput(BaseModel):
    items: list[BatchItem] = Field(min_length=1)


mcp = FastMCP("imagen_mcp")
mcp._mcp_server.version = "0.4.0"


@mcp.tool(name="generate_image")
async def generate_image(params: GenerateInput) -> str:
    """Return a deterministic generation result without calling a provider."""

    return f"generated:{params.prompt}:{params.provider.value}"


@mcp.tool(name="conversational_image")
async def conversational_image(params: ConversationInput) -> str:
    """Optionally wait so client timeout recovery can be tested."""

    await asyncio.sleep(params.delay_seconds)
    return f"conversation:{params.prompt}"


@mcp.tool(name="edit_image")
async def edit_image(params: EditInput) -> str:
    """Raise a synthetic MCP tool error when requested."""

    if params.prompt == "fail":
        raise ValueError("synthetic edit failure")
    return f"edited:{params.image_path}"


@mcp.tool(name="list_providers")
async def list_providers() -> str:
    """Return deterministic provider names."""

    return "openai,gemini"


@mcp.tool(name="list_conversations")
async def list_conversations(params: ListInput) -> str:
    """Echo the requested list limit."""

    return f"limit:{params.limit}"


@mcp.tool(name="list_gemini_models")
async def list_gemini_models() -> str:
    """Return a deterministic model name."""

    return "gemini-test"


@mcp.tool(name="estimate_cost")
async def estimate_cost(params: EstimateInput) -> EstimateOutput:
    """Return structured output to test MCP structuredContent mapping."""

    return EstimateOutput(provider="openai", total_usd=0.01 * params.n)


@mcp.tool(name="generate_image_batch")
async def generate_image_batch(params: BatchInput) -> str:
    """Return the number of provider-free batch items."""

    return f"batch:{len(params.items)}"


if __name__ == "__main__":
    mcp.run()

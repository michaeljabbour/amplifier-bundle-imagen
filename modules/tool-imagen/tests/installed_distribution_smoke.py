"""Smoke a cleanly installed tool-imagen wheel outside the source checkout."""

from __future__ import annotations

from importlib.metadata import distribution

import amplifier_module_tool_imagen as module


def main() -> None:
    installed = distribution("amplifier-module-tool-imagen")
    requirements = installed.metadata.get_all("Requires-Dist") or []

    assert installed.version == module.__version__ == "2.0.0"
    assert installed.metadata["License-Expression"] == "MIT"
    assert any(str(path).endswith("licenses/LICENSE") for path in (installed.files or ()))
    assert any(requirement.startswith("amplifier-core") for requirement in requirements)
    assert any(
        requirement.startswith("mcp") and "<2" in requirement for requirement in requirements
    )
    assert not any("imagen-mcp" in requirement.lower() for requirement in requirements)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deterministic static validation for the Imagen bundle."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def yaml_file(path: Path, failures: list[str]) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}", failures)
        return {}
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)}: expected a YAML mapping", failures)
        return {}
    return value


def frontmatter(path: Path, failures: list[str]) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)}: missing YAML frontmatter", failures)
        return {}
    try:
        header = text.split("---\n", 2)[1]
        value = yaml.safe_load(header)
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(f"{path.relative_to(ROOT)}: invalid frontmatter: {exc}", failures)
        return {}
    return value if isinstance(value, dict) else {}


def main() -> int:
    failures: list[str] = []

    required = [
        "LICENSE",
        "CHANGELOG.md",
        "context/image-production-policy.md",
        "schemas/artifact-manifest.schema.json",
        "evals/workflow-scenarios.yaml",
        "evals/deterministic-cases.yaml",
        "evals/results/2026-07-13.json",
        "evals/README.md",
        "modules/tool-imagen/LICENSE",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}", failures)

    yaml_paths = sorted((ROOT / "behaviors").glob("*.yaml")) + sorted(
        (ROOT / "bundles").glob("*.yaml")
    )
    parsed = {path: yaml_file(path, failures) for path in yaml_paths}

    root_meta = frontmatter(ROOT / "bundle.md", failures)
    if root_meta.get("bundle", {}).get("version") != "2.0.0":
        fail("bundle.md: expected version 2.0.0", failures)

    for path, data in parsed.items():
        if data.get("bundle", {}).get("version") != "2.0.0":
            fail(f"{path.relative_to(ROOT)}: expected version 2.0.0", failures)

    for relative in ("bundles/standalone-local.yaml", "bundles/with-anthropic.yaml"):
        variant = parsed[ROOT / relative]
        includes = [item.get("bundle") for item in variant.get("includes", [])]
        if (
            "git+https://github.com/microsoft/amplifier-foundation@v2.1.2"
            not in includes
        ):
            fail(f"{relative}: must pin the foundation release", failures)
        if "imagen:behaviors/imagegen" not in includes:
            fail(
                f"{relative}: must compose the local namespaced image behavior",
                failures,
            )

    for path in sorted((ROOT / "agents").glob("*.md")):
        frontmatter(path, failures)
    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    skill_names = []
    for path in skill_paths:
        skill_names.append(frontmatter(path, failures).get("name"))
    if skill_names != ["design-visual-asset", "image-ascii-art"]:
        fail(f"unexpected skill inventory: {skill_names}", failures)

    generation = parsed[ROOT / "behaviors/image-generation.yaml"]
    editing = parsed[ROOT / "behaviors/image-editing.yaml"]
    for label, behavior in (("generation", generation), ("editing", editing)):
        tools = behavior.get("tools", [])
        imagen = [item for item in tools if item.get("module") == "tool-imagen"]
        if len(imagen) != 1 or imagen[0].get("source") != "../modules/tool-imagen":
            fail(
                f"{label} behavior must mount relative tool-imagen exactly once",
                failures,
            )
        elif imagen[0].get("config", {}).get("mode") != "mcp":
            fail(f"{label} behavior must use canonical adapter mode 'mcp'", failures)

    module_root = ROOT / "modules/tool-imagen"
    module_metadata = tomllib.loads(
        (module_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    runtime_dependencies = module_metadata.get("project", {}).get("dependencies", [])
    if module_metadata.get("project", {}).get("license") != "MIT":
        fail("tool-imagen must use a PEP 639 MIT license expression", failures)
    if "LICENSE" not in module_metadata.get("project", {}).get("license-files", []):
        fail("tool-imagen wheel must include its LICENSE file", failures)
    if any(
        re.match(r"(?i)imagen[-_]mcp(?:\W|$)", str(item))
        for item in runtime_dependencies
    ):
        fail(
            "tool-imagen must integrate over MCP, not depend on the imagen-mcp package",
            failures,
        )
    if not any(
        str(item).lower().startswith("amplifier-core") for item in runtime_dependencies
    ):
        fail("tool-imagen must declare its amplifier-core runtime import", failures)
    if not any(
        str(item).lower().startswith("mcp") and "<2" in str(item).replace(" ", "")
        for item in runtime_dependencies
    ):
        fail("tool-imagen must bound the supported MCP major version below 2", failures)
    adapter_source = (
        module_root / "amplifier_module_tool_imagen/__init__.py"
    ).read_text(encoding="utf-8")
    if re.search(
        r"(?m)^\s*(?:from|import)\s+(?:imagen_mcp|src)(?:\.|\s|$)", adapter_source
    ):
        fail("tool-imagen must not import imagen-mcp implementation modules", failures)
    if 'Path.home() / "dev" / "imagen-mcp"' in adapter_source:
        fail(
            "tool-imagen must not auto-discover a sibling imagen-mcp checkout", failures
        )

    skills_tools = [
        item
        for item in generation.get("tools", [])
        if item.get("module") == "tool-skills"
    ]
    if len(skills_tools) != 1:
        fail("generation behavior must register tool-skills exactly once", failures)
    else:
        sources = skills_tools[0].get("config", {}).get("skills", [])
        expected_source = (
            "git+https://github.com/michaeljabbour/"
            "amplifier-bundle-imagen@v2.0.0#subdirectory=skills"
        )
        if sources != [expected_source]:
            fail(
                "tool-skills must register the immutable v2.0.0 skills source",
                failures,
            )

    awareness = (ROOT / "context/imagen-awareness.md").read_text(encoding="utf-8")
    expected_tools = {
        "generate_image",
        "generate_image_batch",
        "conversational_image",
        "edit_image",
        "estimate_cost",
        "list_providers",
        "list_conversations",
        "list_gemini_models",
    }
    for name in expected_tools:
        if f"`{name}`" not in awareness:
            fail(f"awareness missing current tool: {name}", failures)

    text_scope = "\n".join(
        path.read_text(encoding="utf-8")
        for directory in ("agents", "behaviors", "bundles", "context", "docs", "skills")
        for path in sorted((ROOT / directory).rglob("*"))
        if path.is_file() and path.suffix in {".md", ".yaml"}
    ) + (ROOT / "README.md").read_text(encoding="utf-8")
    stale_patterns = {
        "legacy 1792 ceiling": r"(?:max(?:es)?(?:imum)?(?: resolution)?(?: is| at)?|up to)\s*~?1792",
        "configurable GPT Image 2 fidelity": r"input_fidelity\s*=\s*[\"']?(?:high|low)",
        "obsolete six-tool inventory": r"(?:all|expos(?:e|es|ing))\s+(?:the\s+)?six\b|\b6\s+(?:image\s+)?tools\b",
        "unpublished v1.2.0 reference": r"@v1\.2\.0|version:\s*1\.2\.0",
        "old Gemini default": r"default_gemini_size:\s*[\"']2K[\"']",
        "safety bypass wording": r"rephrase\s+(?:it\s+)?to\s+(?:a\s+)?generic",
        "mandatory director delegation": r"WHEN:\s*ALWAYS\s+consult|every image request[^\n]+before (?:any )?(?:prompt|generation)",
        "default-on prompt enhancement": r"enhance_prompt[^\n]{0,200}default\s+`?true`?",
        "Flash-only extended Gemini ratios": r"Flash-only\s+(?:aspect\s+)?ratios|Gemini 3\.1 Flash additionally supports\s+`1:4`",
    }
    for label, pattern in stale_patterns.items():
        if re.search(pattern, text_scope, re.IGNORECASE):
            fail(f"stale guidance found: {label}", failures)

    # Check repository-relative Markdown links without making network requests.
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for match in re.finditer(
            r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")
        ):
            raw = match.group(1).strip()
            if raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (
                raw[1 : raw.index(">")]
                if raw.startswith("<") and ">" in raw
                else raw.split()[0]
            )
            target = unquote(target.split("#", 1)[0])
            if target and not (path.parent / target).resolve().exists():
                fail(f"{path.relative_to(ROOT)}: broken local link: {raw}", failures)

    try:
        schema = json.loads(
            (ROOT / "schemas/artifact-manifest.schema.json").read_text(encoding="utf-8")
        )
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail("artifact manifest must use JSON Schema 2020-12", failures)
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        fail(f"invalid artifact manifest schema: {exc}", failures)

    evals = yaml_file(ROOT / "evals/workflow-scenarios.yaml", failures)
    if evals.get("kind") != "workflow-eval-specification":
        fail("workflow evals must identify themselves as specifications", failures)
    if evals.get("execution") != "deterministic-high-risk-gate":
        fail(
            "workflow eval execution status must identify the high-risk gate", failures
        )
    scenarios = evals.get("scenarios", [])
    ids = [item.get("id") for item in scenarios if isinstance(item, dict)]
    if len(ids) < 10 or len(ids) != len(set(ids)):
        fail("workflow evals require at least 10 uniquely named scenarios", failures)
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            fail(f"workflow eval #{index + 1} must be a mapping", failures)
            continue
        if (
            not isinstance(scenario.get("request"), str)
            or not scenario["request"].strip()
        ):
            fail(f"workflow eval {scenario.get('id')!r} needs a request", failures)
        expect = scenario.get("expect")
        if not isinstance(expect, dict):
            fail(f"workflow eval {scenario.get('id')!r} needs expectations", failures)
            continue
        if expect.get("mode") not in {"fast", "guided", "studio"}:
            fail(f"workflow eval {scenario.get('id')!r} has an invalid mode", failures)
        for field in ("required", "forbidden"):
            values = expect.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) and value for value in values)
            ):
                fail(
                    f"workflow eval {scenario.get('id')!r} needs non-empty {field} tokens",
                    failures,
                )

    deterministic = yaml_file(ROOT / "evals/deterministic-cases.yaml", failures)
    if deterministic.get("kind") != "deterministic-policy-cases":
        fail("deterministic eval cases must identify their contract kind", failures)
    deterministic_cases = deterministic.get("cases", [])
    deterministic_ids = [
        item.get("id") for item in deterministic_cases if isinstance(item, dict)
    ]
    expected_deterministic_ids = {
        "moderation-shopping",
        "watermark-removal",
        "sensitive-child-reference",
        "exact-artifact-refinement",
        "visual-qa-honesty",
    }
    if set(deterministic_ids) != expected_deterministic_ids:
        fail(
            f"unexpected deterministic high-risk cases: {sorted(deterministic_ids)}",
            failures,
        )
    for case in deterministic_cases:
        if not isinstance(case, dict):
            fail("deterministic eval case must be a mapping", failures)
            continue
        if case.get("scenario_id") not in ids:
            fail(
                f"deterministic case {case.get('id')!r} references an unknown scenario",
                failures,
            )
        if not isinstance(case.get("facts"), dict) or not case["facts"]:
            fail(f"deterministic case {case.get('id')!r} needs typed facts", failures)
        if not isinstance(case.get("rule"), str) or not case["rule"]:
            fail(f"deterministic case {case.get('id')!r} needs a policy rule", failures)

    try:
        behavioral_result = json.loads(
            (ROOT / "evals/results/2026-07-13.json").read_text(encoding="utf-8")
        )
        summary = behavioral_result.get("summary", {})
        if behavioral_result.get("result") != "passed":
            fail("committed behavioral evaluation must pass", failures)
        if summary.get("cases") != len(expected_deterministic_ids):
            fail(
                "committed behavioral evaluation has incomplete case coverage", failures
            )
        if summary.get("passed") != summary.get("cases"):
            fail("committed behavioral evaluation contains a failed case", failures)
        if summary.get("unsafe_mutations_rejected") != summary.get("unsafe_mutations"):
            fail("behavioral grader did not reject every unsafe mutation", failures)
    except Exception as exc:
        fail(f"invalid committed behavioral evaluation: {exc}", failures)

    if failures:
        print("Bundle validation failed:", file=sys.stderr)
        for message in failures:
            print(f"- {message}", file=sys.stderr)
        return 1
    print(
        f"Bundle validation passed ({len(yaml_paths)} YAML files, {len(skill_names)} skills, {len(ids)} evals)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

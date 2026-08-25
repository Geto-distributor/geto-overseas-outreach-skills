#!/usr/bin/env python3
"""Validate every Skill package in this repository."""

from __future__ import annotations

import re
import sys
import py_compile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXPECTED = {
    "geto-capability-foundation",
    "geto-find-leads",
    "geto-diligence-company",
    "geto-diligence-competitor",
    "geto-diligence-inquiry",
    "geto-mine-competitor-customers",
    "geto-map-relationships",
    "geto-assess-precontract-risk",
    "geto-run-market-research",
}
FORBIDDEN_PROVIDER_SKILLS = {
    "omnix-market",
    "netease-waimao",
    "tradewind-api",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_skill(path: Path, errors: list[str]) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter fence")
        return {}, text
    try:
        _, frontmatter, body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
    except (ValueError, yaml.YAMLError) as error:
        errors.append(f"{path.relative_to(ROOT)}: invalid frontmatter: {error}")
        return {}, text
    if not isinstance(metadata, dict):
        errors.append(f"{path.relative_to(ROOT)}: frontmatter must be an object")
        return {}, body
    return metadata, body


def validate_skill(skill_dir: Path, errors: list[str]) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        return
    metadata, body = parse_skill(skill_file, errors)
    extra = set(metadata) - {"name", "description"}
    if extra:
        errors.append(f"{skill_file.relative_to(ROOT)}: unsupported frontmatter keys {sorted(extra)}")
    name = metadata.get("name")
    description = metadata.get("description")
    if name != skill_dir.name:
        errors.append(f"{skill_file.relative_to(ROOT)}: name must equal folder name")
    if not isinstance(name, str) or len(name) > 64 or not NAME_PATTERN.fullmatch(name):
        errors.append(f"{skill_file.relative_to(ROOT)}: invalid skill name")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file.relative_to(ROOT)}: description is required")
    if len(skill_file.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append(f"{skill_file.relative_to(ROOT)}: SKILL.md exceeds 500 lines")
    if "TODO" in body:
        errors.append(f"{skill_file.relative_to(ROOT)}: unresolved TODO")

    agent_file = skill_dir / "agents" / "openai.yaml"
    if not agent_file.is_file():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing agents/openai.yaml")
    else:
        try:
            agent = yaml.safe_load(agent_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            errors.append(f"{agent_file.relative_to(ROOT)}: invalid YAML: {error}")
            agent = {}
        interface = agent.get("interface", {}) if isinstance(agent, dict) else {}
        for field in ("display_name", "short_description", "default_prompt"):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                errors.append(f"{agent_file.relative_to(ROOT)}: interface.{field} is required")
        if isinstance(interface.get("default_prompt"), str) and f"${name}" not in interface["default_prompt"]:
            errors.append(f"{agent_file.relative_to(ROOT)}: default_prompt must mention ${name}")

    for markdown in skill_dir.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            target = target.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (markdown.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{markdown.relative_to(ROOT)}: broken relative link {target}")

    for script in skill_dir.rglob("*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as error:
            errors.append(f"{script.relative_to(ROOT)}: {error.msg}")


def main() -> int:
    errors: list[str] = []
    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    if actual != EXPECTED:
        errors.append(f"skills set mismatch: expected={sorted(EXPECTED)}, actual={sorted(actual)}")
    forbidden = actual.intersection(FORBIDDEN_PROVIDER_SKILLS)
    if forbidden:
        errors.append(f"Provider Skills must not be bundled: {sorted(forbidden)}")
    for skill_dir in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        validate_skill(skill_dir, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {len(actual)} GETO Skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

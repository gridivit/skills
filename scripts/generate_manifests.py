#!/usr/bin/env python3
"""Generate all platform manifests from the SKILL.md files under plugins/.

    plugins/<plugin>/skills/<skill>/SKILL.md   <- source of truth (hand-authored)
    plugins/<plugin>/plugin.meta.json          <- optional, required for groups

Produces (idempotent, overwritten on every run - never hand-edit these):
    plugins/<plugin>/.claude-plugin/plugin.json
    plugins/<plugin>/.codex-plugin/plugin.json
    .claude-plugin/marketplace.json
    .agents/plugins/marketplace.json

Usage: python scripts/generate_manifests.py [--check]
    --check  exit non-zero if anything would change (for CI); writes nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"

MARKETPLACE_NAME = "gridin-skills"
MARKETPLACE_DISPLAY = "Gridin Skills"
MARKETPLACE_DESCRIPTION = (
    "Personal agent skills, installable on Claude Code, Codex, and Antigravity."
)
OWNER = {"name": "Vitalii Gridin", "email": "gridinv256@gmail.com"}
DEFAULT_VERSION = "0.1.0"

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONT_MATTER = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)

check_only = "--check" in sys.argv[1:]


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.stderr.write(f"generate-manifests: {msg}\n")
    raise SystemExit(1)


def list_dirs(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(
        (p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name,
    )


def parse_front_matter(file: Path) -> dict[str, str]:
    """Minimal `key: value` front-matter reader (optionally quoted values)."""
    match = FRONT_MATTER.match(file.read_text(encoding="utf-8"))
    if not match:
        fail(f"{file}: missing YAML front matter")
    out: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key] = value
    return out


writes: list[tuple[Path, str]] = []


def emit(path: Path, obj: dict) -> None:
    writes.append((path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n"))


seen_skill_names: dict[str, str] = {}
seen_plugin_names: dict[str, str] = {}
claude_plugins: list[dict] = []
codex_plugins: list[dict] = []

for plugin_path in list_dirs(PLUGINS_DIR):
    plugin_dir = plugin_path.name
    skills_root = plugin_path / "skills"
    skill_dirs = list_dirs(skills_root)
    if not skill_dirs:
        fail(f"plugins/{plugin_dir}: no skills found under skills/")

    skills: list[dict[str, str]] = []
    for skill_path in skill_dirs:
        skill_dir = skill_path.name
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            fail(f"plugins/{plugin_dir}/skills/{skill_dir}: missing SKILL.md")
        fm = parse_front_matter(skill_md)
        if not fm.get("name"):
            fail(f"{skill_md}: front matter missing 'name'")
        if not fm.get("description"):
            fail(f"{skill_md}: front matter missing 'description'")
        if not KEBAB.match(fm["name"]):
            fail(f"{skill_md}: name '{fm['name']}' must be kebab-case")
        if fm["name"] != skill_dir:
            fail(f"{skill_md}: name '{fm['name']}' must match directory '{skill_dir}'")
        if fm["name"] in seen_skill_names:
            fail(
                f"duplicate skill name '{fm['name']}' in plugins/{plugin_dir} "
                f"and {seen_skill_names[fm['name']]}"
            )
        seen_skill_names[fm["name"]] = f"plugins/{plugin_dir}"
        skills.append({"name": fm["name"], "description": fm["description"]})

    # Plugin-level metadata: meta file, else derive from the single skill.
    meta_path = plugin_path / "plugin.meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("name"):
            fail(f"{meta_path}: missing 'name'")
        if not meta.get("description"):
            fail(f"{meta_path}: missing 'description'")
    elif len(skills) == 1:
        meta = {"name": plugin_dir, "description": skills[0]["description"]}
    else:
        fail(
            f"plugins/{plugin_dir}: has {len(skills)} skills - "
            f"add a plugin.meta.json with name/description"
        )

    if not KEBAB.match(meta["name"]):
        fail(f"plugins/{plugin_dir}: plugin name '{meta['name']}' must be kebab-case")
    if meta["name"] != plugin_dir:
        fail(f"plugins/{plugin_dir}: plugin name '{meta['name']}' must match directory")
    if meta["name"] in seen_plugin_names:
        fail(f"duplicate plugin name '{meta['name']}'")
    seen_plugin_names[meta["name"]] = plugin_dir
    version = meta.get("version", DEFAULT_VERSION)

    # Per-plugin manifests.
    emit(
        plugin_path / ".claude-plugin" / "plugin.json",
        {
            "name": meta["name"],
            "description": meta["description"],
            "version": version,
            "author": OWNER,
        },
    )
    emit(
        plugin_path / ".codex-plugin" / "plugin.json",
        {
            "name": meta["name"],
            "version": version,
            "description": meta["description"],
            "skills": "./skills/",
        },
    )

    # Catalog entries.
    source = f"./plugins/{plugin_dir}"
    claude_plugins.append(
        {
            "name": meta["name"],
            "source": source,
            "description": meta["description"],
            "version": version,
            "author": OWNER,
        }
    )
    codex_plugins.append(
        {
            "name": meta["name"],
            "source": {"source": "path", "path": source},
            "description": meta["description"],
            "version": version,
            "author": OWNER,
            "category": "skills",
        }
    )

if not claude_plugins:
    fail("no plugins found under plugins/")

emit(
    ROOT / ".claude-plugin" / "marketplace.json",
    {
        "name": MARKETPLACE_NAME,
        "description": MARKETPLACE_DESCRIPTION,
        "owner": OWNER,
        "plugins": claude_plugins,
    },
)
emit(
    ROOT / ".agents" / "plugins" / "marketplace.json",
    {
        "name": MARKETPLACE_NAME,
        "description": MARKETPLACE_DESCRIPTION,
        "interface": {"displayName": MARKETPLACE_DISPLAY},
        "owner": OWNER,
        "plugins": codex_plugins,
    },
)

changed = 0
for path, content in writes:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        continue
    changed += 1
    if check_only:
        sys.stderr.write(f"would change: {path}\n")
        continue
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote: {path}")

if check_only and changed > 0:
    fail(f"{changed} manifest(s) out of date - run 'python scripts/generate_manifests.py'")

print(
    "manifests up to date"
    if check_only
    else f"done: {len(seen_plugin_names)} plugin(s), "
    f"{len(seen_skill_names)} skill(s), {changed} file(s) updated"
)

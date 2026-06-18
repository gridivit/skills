# gridin-skills

Personal agent **skills**, authored once and installed across **Claude Code**,
**Codex**, and **Antigravity (`agy`)** via each platform's native marketplace,
with a sync script as a fallback (and the supported path for Antigravity).

Repo: <https://github.com/gridivit/skills> · marketplace name: `gridin-skills`

## What's here

A skill is a directory with a `SKILL.md`. Skills are grouped into **plugins**
(the unit you install). A plugin holds one skill or several related ones.

```
plugins/
  coach/                             # single-skill plugin
    skills/programming-coach/SKILL.md
```

The `SKILL.md` files are the **only thing you hand-author**. Everything under
`.claude-plugin/`, `.codex-plugin/`, and `.agents/plugins/` is generated.

## Install

### Claude Code
```
/plugin marketplace add gridivit/skills
/plugin install coach@gridin-skills
```
Installed skills are namespaced, e.g. `/coach:programming-coach`.

### Codex
```
codex plugin marketplace add gridivit/skills
codex plugin install coach
```

### Antigravity (`agy`)
Try the native marketplace first:
```
/plugin marketplace add gridivit/skills
/plugin install coach
```
If your `agy` build doesn't pick up the marketplace, use the sync script below —
it copies skills into `~/.gemini/antigravity-cli/skills/`.

### Sync (fallback / any tool)
Links every skill into `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`,
and `~/.gemini/antigravity-cli/skills`.

```bash
scripts/sync.sh            # symlink (default)
scripts/sync.sh --copy     # copy instead (no symlink permission)
scripts/sync.sh --clean    # remove this repo's skills first, then sync
```
```powershell
./scripts/sync.ps1         # symlink (needs Developer Mode or elevated shell)
./scripts/sync.ps1 -Copy   # copy instead
./scripts/sync.ps1 -Clean  # remove first, then sync
```

## Add a skill

**Single-skill plugin** — create one file, regenerate:
```
plugins/<name>/skills/<name>/SKILL.md
```
with front matter:
```yaml
---
name: <name>          # kebab-case, must match the directory, globally unique
description: <one line: when to use this skill>
---
```

**Group plugin** — put multiple skill dirs under one plugin and add
`plugins/<plugin>/plugin.meta.json`:
```json
{ "name": "<plugin>", "description": "...", "version": "0.1.0" }
```

Then regenerate the manifests and (optionally) sync:
```
python scripts/generate_manifests.py
scripts/sync.sh
```

After pushing to GitHub, users refresh with `/plugin marketplace update` (Claude)
or `codex plugin marketplace update` (Codex).

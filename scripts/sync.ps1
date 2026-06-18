<#
.SYNOPSIS
  Sync every skill in this repo into each tool's personal skills directory.
.DESCRIPTION
  Default: symlink (repo edits are reflected immediately). On Windows, symlinks
  require Developer Mode or an elevated shell; use -Copy if linking fails.
.PARAMETER Copy
  Copy instead of symlinking.
.PARAMETER Clean
  Remove existing links/dirs for this repo's skills before syncing.
.EXAMPLE
  ./scripts/sync.ps1
  ./scripts/sync.ps1 -Copy -Clean
#>
[CmdletBinding()]
param(
  [switch]$Copy,
  [switch]$Clean
)
$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$targets = @(
  Join-Path $HOME ".claude/skills"
  Join-Path $HOME ".codex/skills"
  Join-Path $HOME ".agents/skills"
  Join-Path $HOME ".gemini/antigravity-cli/skills"
)

$skills = Get-ChildItem -Path (Join-Path $repo "plugins/*/skills/*") -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }
if (-not $skills) { throw "no skills found under plugins/*/skills/*" }

foreach ($target in $targets) {
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  foreach ($src in $skills) {
    $dest = Join-Path $target $src.Name
    if ($Clean -or (Test-Path $dest)) {
      Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
    }
    if ($Copy) {
      Copy-Item -Recurse -Force $src.FullName $dest
    } else {
      try {
        New-Item -ItemType SymbolicLink -Path $dest -Target $src.FullName | Out-Null
      } catch {
        throw "Symlink failed for '$dest'. Enable Developer Mode / run elevated, or re-run with -Copy. ($_)"
      }
    }
  }
  $mode = if ($Copy) { "copy" } else { "link" }
  Write-Host "synced $($skills.Count) skill(s) -> $target ($mode)"
}

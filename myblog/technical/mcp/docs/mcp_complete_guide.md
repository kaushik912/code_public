# MCP Quick Reference

## Scope / Storage

| Scope | Use Case | Storage | Visibility |
|-------|----------|---------|-----------|
| `user` | Personal tools everywhere | `~/.claude.json` | All projects |
| `project` | Team-standard tools | `.mcp.json` (repo root) | This repo only |
| `local` | Temporary/experimental | `~/.claude.json` (path-specific) | Your machine only |

Secrets: use `${VAR}` env expansion in `.mcp.json` (url/headers/args/env/command), never hardcode. Prefer OAuth over API keys.

`user` vs `local` — same file (`~/.claude.json`), different key:
```json
{
  "mcpServers": {                              // user scope: top-level, all projects
    "codebase-memory-mcp": {"type": "stdio", "command": "/home/kaush/.local/bin/codebase-memory-mcp"}
  },
  "projects": {
    "/home/kaush/github_projs/code_public": {  // local scope: keyed by path, only active in that dir
      "mcpServers": {}
    }
  }
}
```

## CLI Commands

```bash
# Add (scope: user/project/local, default local)
claude mcp add --transport http <name> --scope user <URL>
claude mcp add --transport http <name> --scope project <URL>
claude mcp add --transport http docs-experiment --scope local https://staging-docs.internal/mcp
claude mcp add <name> --url <URL> --bearer-token-env-var VAR_NAME
claude mcp add --transport http github https://api.github.com/mcp   # then OAuth in browser

# Manage
claude mcp list
claude mcp get <name>
claude mcp remove <name>
claude mcp login <name>
claude mcp logout <name>

# One-off clean session (only specified servers, no persistence)
claude --strict-mcp-config --mcp-config /path/to/temp-mcp.json
```

Persistent disable: `disabledMcpServers` (`~/.claude.json`, user-level) or `disabledMcpjsonServers` (`.claude/settings.json`, project-level).

In-session toggle: `/mcp`, or `/mcp enable <server>` / `/mcp disable <server>` (session-only).

Permission restrictions (`settings.json`), pattern `mcp__<server>__<tool>`:
```json
{ "permissions": { "ask": ["mcp__github__create_pull_request"], "deny": ["mcp__github__delete_repository"] } }
```

## My note
- `claude --strict-mcp-config` in case you want a no-mcp session. Quick for some simple use-cases. Better for pure doc generation cases where it may just require iterating over codebase.

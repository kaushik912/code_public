# MCP Complete Guide: Setup, Security & Management

## Part 1: API Token Handling

### Environment Variable Expansion
Claude Code supports `${VAR}` syntax in `.mcp.json` for `url`, `headers`, `args`, `env`, `command`.

**HTTP MCP with Bearer Token:**
```json
{
  "mcpServers": {
    "shared-docs": {
      "transport": {
        "type": "http",
        "url": "https://docs.internal.company.com/mcp",
        "headers": {
          "Authorization": "Bearer ${INTERNAL_DOCS_TOKEN}"
        }
      }
    }
  }
}
```

**Set env var:**
```bash
export INTERNAL_DOCS_TOKEN="sk_live_..."
```

**With default fallback:**
```json
"Authorization": "Bearer ${INTERNAL_DOCS_TOKEN:-}"
```

### API Keys (Avoid hardcoding)

❌ **BAD – secrets in file:**
```json
{
  "mcpServers": {
    "finance-mcp": {
      "transport": {
        "type": "http",
        "url": "https://finance.example.com/mcp?token=sk_live_12345"
      }
    }
  }
}
```

❌ **BAD – secret in args:**
```json
{
  "mcpServers": {
    "db-mcp": {
      "command": "node",
      "args": ["server.js", "--api-key", "sk_live_12345"]
    }
  }
}
```

✅ **GOOD – env var expansion:**
```json
{
  "mcpServers": {
    "db-mcp": {
      "command": "node",
      "args": ["server.js", "--api-key", "${DB_MCP_API_KEY}"]
    }
  }
}
```

### CLI Setup with Secrets

```bash
claude mcp add quicknode \
  --url https://mcp.quicknode.com/mcp \
  --bearer-token-env-var YOUR_API_KEY
```

```bash
claude mcp add quicknode \
  --transport http \
  https://mcp.quicknode.com/mcp \
  --header "Authorization: Bearer ${QUICKNODE_TOKEN}"
```

### OAuth (Preferred)
```bash
claude mcp add --transport http github https://api.github.com/mcp
# Then follow OAuth prompt in browser
```

### `.env` Template (commit to repo)

`.env.example`:
```bash
# MCP tokens – do not commit real values
INTERNAL_DOCS_TOKEN=
FINANCE_MCP_API_KEY=
DB_MCP_API_KEY=
```

Add to `.gitignore`:
```
.env
```

### Permission Restrictions

In `~/.claude/settings.json` or `.claude/settings.json`:
```json
{
  "permissions": {
    "ask": [
      "mcp__github__create_pull_request",
      "mcp__linear__create_issue"
    ],
    "deny": [
      "mcp__github__delete_repository",
      "mcp__linear__delete_project"
    ]
  }
}
```

Pattern: `mcp__<server>__<tool>`

---

## Part 2: Organizing MCPs by Scope

### Decision Matrix

| Scope | Use Case | Storage | Visibility |
|-------|----------|---------|-----------|
| `user` | Personal tools everywhere | `~/.claude.json` | All projects |
| `project` | Team-standard tools | `.mcp.json` (repo root) | This repo only |
| `local` | Temporary/experimental | `~/.claude.json` (path-specific) | Your machine only |

### User Scope (Global)

Available in all projects on your machine:
```bash
claude mcp add --transport http personal-docs --scope user https://docs.your-personal-domain.com/mcp
claude mcp add --transport http finance-mcp --scope user https://finance.your-domain.com/mcp
```

### Project Scope (Team-standard)

Run from repo root; committed to `.mcp.json`:
```bash
cd ~/work/order-service
claude mcp add --transport http shared-docs --scope project https://docs.internal.company.com/mcp
claude mcp add --transport http issue-tracker --scope project https://linear.internal.company.com/mcp
```

**With secrets (env vars):**
```json
{
  "mcpServers": {
    "shared-docs": {
      "transport": {
        "type": "http",
        "url": "https://docs.internal.company.com/mcp",
        "headers": {
          "Authorization": "Bearer ${INTERNAL_DOCS_TOKEN}"
        }
      }
    }
  }
}
```

Then export `INTERNAL_DOCS_TOKEN` in shell or `.env`.

### Local Scope (Temporary)

Your machine only, not committed:
```bash
cd ~/work/order-service
claude mcp add --transport http docs-experiment --scope local https://staging-docs.internal/mcp
```

Remove later:
```bash
claude mcp remove docs-experiment
```

### Complete Setup Example

**Step 1: Global tools (once)**
```bash
claude mcp add --transport http personal-docs --scope user https://docs.you.example.com/mcp
claude mcp add --transport http finance-mcp --scope user https://finance.you.example.com/mcp
```

**Step 2: Per repo (order-service)**
```bash
cd ~/work/order-service
claude mcp add --transport http shared-docs --scope project https://docs.internal.company.com/mcp
claude mcp add --transport http issue-tracker --scope project https://linear.internal.company.com/mcp
```

**Step 3: Per repo (payment-service)**
```bash
cd ~/work/payment-service
claude mcp add --transport http shared-docs --scope project https://docs.internal.company.com/mcp
claude mcp add --transport http issue-tracker --scope project https://jira.internal.company.com/mcp
```

---

## Part 3: Managing & Toggling MCPs

### CLI Commands (Outside sessions)

```bash
# List all configured servers
claude mcp list

# Inspect specific server
claude mcp get shared-docs

# Remove server entirely
claude mcp remove <name>

# Manage OAuth tokens
claude mcp login <name>
claude mcp logout <name>
```

### Disable Servers (Persistent)

**User-level** (in `~/.claude.json`):
```json
{
  "disabledMcpServers": ["notion", "slack"]
}
```

**Project-level** (in `.claude/settings.json`):
```json
{
  "disabledMcpjsonServers": ["github", "linear"]
}
```

Toggle back on later via `/mcp` in-session or by removing from `disabledMcpServers`.

### Toggle Per Session (Interactive)

Inside Claude Code:
```
/mcp
```

Shows all servers with on/off toggles. Changes only affect current session.

Also per-session disable/enable:
```
/mcp disable <server>
/mcp enable <server>
```

### Strict MCP Config (One-off Clean Session)

Use only specific servers for one run:
```bash
claude --strict-mcp-config --mcp-config /path/to/temp-mcp.json
```

Creates isolated session. Future runs use normal config again.

Example `temp-mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "transport": { "type": "http", "url": "..." }
    },
    "linear": {
      "transport": { "type": "http", "url": "..." }
    }
  }
}
```

### Persistence Summary

| Method | Per-Session | Persistent | Command |
|--------|------------|-----------|---------|
| `/mcp` toggle | ✓ | ✗ | Inside session |
| `disabledMcpServers` | ✗ | ✓ | Edit `~/.claude.json` |
| `disabledMcpjsonServers` | ✗ | ✓ | Edit `.claude/settings.json` |
| `--strict-mcp-config` | ✓ (one run) | ✗ | CLI flag |
| `claude mcp remove` | N/A | ✓ (deletes) | CLI command |

---

## Quick Reference Workflow

### First Time Setup
```bash
# 1. Add personal tools globally
claude mcp add --transport http personal-docs --scope user <URL>

# 2. Go to repo
cd ~/my-project

# 3. Add team tools
claude mcp add --transport http shared-docs --scope project <URL>

# 4. Start session
claude
```

### Keep Servers Minimal by Default
```bash
# Disable by default, enable when needed
# Edit ~/.claude.json:
{
  "disabledMcpServers": ["experimental", "heavy-tool"]
}

# In session, toggle on if needed:
/mcp
```

### Clean Session for Focused Work
```bash
# Create minimal config
cat > /tmp/focused-mcps.json <<'EOF'
{
  "mcpServers": {
    "github": { "transport": { "type": "http", "url": "..." } }
  }
}
EOF

# Run with only these servers
claude --strict-mcp-config --mcp-config /tmp/focused-mcps.json
```

### Security Checklist
- [ ] All secrets use `${VAR}` syntax
- [ ] `.env` added to `.gitignore`
- [ ] `.env.example` committed with empty values
- [ ] OAuth preferred over API keys
- [ ] Dangerous tools restricted via `permissions`
- [ ] `.mcp.json` reviewed in PRs like code

## My note
- `claude --strict-mcp-config` in case you want a no-mcp session. Quick for some simple use-cases. Better for pure doc generation cases where it may just require iterating over codebase.
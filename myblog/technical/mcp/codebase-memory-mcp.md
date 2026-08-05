### **Overview**

Github Repo: `https://github.com/DeusData/codebase-memory-mcp`

**`codebase-memory-mcp`** (by DeusData) turns your repo into a local, compressed knowledge graph using Tree-sitter parsers across 158 languages. Instead of AI agents consuming hundreds of thousands of tokens on repetitive `grep` and file-reading loops, it delivers sub-millisecond structural queries (call chains, dead code, IaC, type maps)—**cutting token usage by up to 99%** with zero code leaving your machine.

---

### **Quickstart Cheat-Sheet**

1. **Install Server**
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash

# Windows (PowerShell)
iwr -useb https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 | iex

```


2. **Verify Client Config** (`~/.claude.json` or `claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "codebase-memory": { "command": "codebase-memory-mcp", "args": [] }
  }
}

```


3. **Build & Query (in Claude)**
* **Index:** Prompt `"Index this project"`
* **Query:** Prompt `"Trace the call graph for /login"` or `"What is the impact if I refactor class X?"`

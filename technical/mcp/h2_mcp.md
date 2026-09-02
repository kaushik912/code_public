If you are running **everything inside WSL** (including running Claude Code via CLI or your MCP client inside Ubuntu), the setup gets much simpler. You don't have to bridge `wsl.exe` or deal with Windows networking.

Here is the clean, WSL-only setup using H2 Database and an MCP server.

---

## 1. Install Java & Start H2 Database

Open your WSL terminal and launch H2 in TCP mode:

```bash
# Install Java
sudo apt update && sudo apt install -y openjdk-17-jre wget unzip

# Download H2
mkdir -p ~/h2-db && cd ~/h2-db
wget https://github.com/h2database/h2database/releases/download/version-2.2.224/h2-2023-09-17.zip
unzip h2-2023-09-17.zip

# Start H2 Server (runs on tcp://localhost:9092)
java -cp h2/bin/h2-*.jar org.h2.tools.Server -tcp -web

```

---

## 2. Configure MCP Client in WSL

Since your MCP host (e.g., Claude CLI, Claude Code, or VS Code running in WSL remote mode) is inside Linux, configure your `mcp` setup directly using standard Linux paths.

Add the following to your local MCP configuration file (e.g., `~/.claude/mcp.json` or your client's config file):

```json
{
  "mcpServers": {
    "h2-database": {
      "command": "npx",
      "args": [
        "-y",
        "@bytebase/db-mcp",
        "--driver", "h2",
        "--url", "jdbc:h2:tcp://localhost:9092/~/test",
        "--user", "sa",
        "--password", ""
      ]
    }
  }
}

```

*Note: Replace `jdbc:h2:tcp://localhost:9092/~/test` with your specific database name or path if needed.*

---

## 3. Verify Connection

From your WSL environment, start your MCP client (e.g., `claude` CLI):

```bash
# Launch Claude in CLI mode
claude

```

Ask Claude:

> *"List the tables in my H2 database and create a test table called `users`."*
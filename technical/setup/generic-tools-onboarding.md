# New Laptop — Generic Tools Onboarding

A provider-agnostic "getting started" checklist for setting up a development
machine (macOS-focused, Apple Silicon paths shown). Everything company-specific
has been replaced with `<PLACEHOLDERS>` — fill them in from your org's wiki /
IT portal.

> Convention: anything in `<ANGLE_BRACKETS>` is a value you supply.
> Store real secrets in a password manager, **never** commit them.

---

## 0. Prerequisites — Homebrew

Homebrew is the base package manager most other tools install through.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After install, follow the printed instructions to add `brew` to your `PATH`
(on Apple Silicon it lives in `/opt/homebrew/bin`).

---

## 1. Shell environment (`~/.zshrc`)

Keep a backed-up copy of your shell config (OneDrive / Dropbox / a private repo)
so a new machine is a copy-paste away. **Export** variables — don't just set them,
or child processes won't see them.

```bash
# --- Secrets / registry (fill from your artifact registry) ---
export ARTIFACTORY_USER=<YOUR_USERNAME>
export ARTIFACTORY_API_TOKEN=<ARTIFACTORY_TOKEN>   # keep out of git

# --- Java ---
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"

# --- Common PATHs ---
export PATH="/usr/local/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"                # CLIs like claude land here
export PATH="/opt/homebrew/opt/mysql-client:$PATH"  # keg-only client

# --- Aliases ---
alias mcis='mvn clean install -DskipTests'

# --- Switch JDK versions on demand ---
use-java() { export JAVA_HOME=$(/usr/libexec/java_home -v "$1"); export PATH="$JAVA_HOME/bin:$PATH"; }
# usage: use-java 11   /   use-java 17
```

Apply changes without reopening the terminal:

```bash
source ~/.zshrc
```

---

## 2. Git & GitHub (SSH)

```bash
brew install git gh          # git + GitHub CLI

# Generate an SSH key and add it to your Git host
ssh-keygen -t ed25519 -C "<YOUR_EMAIL>"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
pbcopy < ~/.ssh/id_ed25519.pub   # paste into Git host → Settings → SSH keys
```

- Enterprise GitHub vs public GitHub often use **different usernames** — note
  which host maps to which account.
- Ask a repo admin (Settings → Collaborators / Teams) to grant you access to the
  repos you need; SSH access alone doesn't grant repo membership.

**Git safety habit** — before a risky rebase/squash, snapshot the branch:

```bash
git checkout -b <branch>-backup   # cheap escape hatch, then go back and squash
```

---

## 3. Java + Maven

```bash
brew install maven
# JDKs via your preferred vendor (temurin shown)
brew install --cask temurin@17
brew install --cask temurin@11    # if you need to switch
```

- Pick the JDK your project targets (this repo family assumes **JDK 17**).
- **Lombok + newer JDK**: if the IDE throws Lombok/compile errors, pin a Lombok
  version that supports your JDK:

  ```xml
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.34</version>   <!-- supports JDK 17 -->
    <scope>provided</scope>
  </dependency>
  ```

- **IntelliJ clean build**: File → Project Structure → set Project SDK to your
  JDK → rebuild (clean + install). Resolves most Lombok/SDK mismatch errors.

---

## 4. IDEs / editors

| Tool | Install | Notes |
|---|---|---|
| VS Code | `brew install --cask visual-studio-code` | + SQL Server (mssql) ext for DB, see §8 |
| IntelliJ IDEA | `brew install --cask intellij-idea` | primary for JVM projects |
| Cursor | `brew install --cask cursor` | AI editor |

Add whichever AI coding assistant your org licenses (Claude Code, Copilot, etc.).

---

## 5. Docker (via Colima, if Docker Desktop isn't approved)

Colima is a free, license-unencumbered Docker runtime.

```bash
brew install colima docker docker-compose
colima start
docker run hello-world      # smoke test
```

Enable the Go-based `docker compose` plugin:

```bash
mkdir -p ~/.docker/cli-plugins
ln -sfn $(brew --prefix)/opt/docker-compose/bin/docker-compose ~/.docker/cli-plugins/docker-compose
docker compose version
```

Start Colima automatically at login:

```bash
brew services start colima
```

Log in to a private image registry once:

```bash
docker login -u "$ARTIFACTORY_USER" -p "$ARTIFACTORY_API_TOKEN" <REGISTRY_HOST>
```

---

## 6. Kubernetes CLI

```bash
brew install kubectl
brew install Azure/kubelogin/kubelogin      # if your cluster uses Azure AD auth
export KUBECONFIG=<PATH_TO_KUBECONFIG_YAML>
```

---

## 7. Database access via a Teleport (`tsh`) proxy

A common enterprise pattern: DBs aren't exposed directly; you tunnel through a
bastion/proxy (here Teleport) to a **local port**, then point any client at
`127.0.0.1:<port>`.

### Install the clients

```bash
brew install mysql-client           # path: /opt/homebrew/opt/mysql-client/bin/mysql
# tsh: install per your Teleport provider's docs
```

### Log in

```bash
tsh login --proxy=<TELEPORT_PROXY_HOST>
tsh db ls                           # list databases you can reach
```

### Two proxy modes (important distinction)

| Mode | Local port (example) | Client needs TLS certs? | Use for |
|---|---|---|---|
| Normal (mTLS) | `13307` | **Yes** — `--ssl-ca/cert/key` | MCP servers, MySQL CLI |
| Tunnel | `13308` | **No** — plain TCP, `useSSL=false` | App JDBC (Spring Boot, etc.) |

Only one process can bind a given port — kill an existing proxy before switching.

Handy aliases (`~/.zshrc`):

```bash
alias db_proxy='tsh proxy db <DB_ALIAS> --db-user=<DB_USER> --db-name=<DB_SCHEMA> --port=13307'
alias db_tunnel='tsh proxy db <DB_ALIAS> --tunnel --db-user=<DB_USER> --db-name=<DB_SCHEMA> --port=13308'
```

Start / verify / stop:

```bash
# start (background) and record PID so it survives shell exit
tsh proxy db <DB_ALIAS> --db-user=<DB_USER> --db-name=<DB_SCHEMA> --port=13307 &
echo $! > /tmp/db-proxy.pid
lsof -i :13307 | grep LISTEN        # confirm it's ready

# stop
kill "$(cat /tmp/db-proxy.pid)" && rm /tmp/db-proxy.pid
pkill -f "tsh proxy db"             # fallback: kill all proxies
lsof -ti :13307 | xargs kill        # last resort: by port
```

> The proxy is detached from the terminal and keeps running until killed — always
> stop it when done. If `tsh` returns an auth error, your session expired →
> re-run `tsh login`.

> The Teleport **alias** (`<DB_ALIAS>`) appears in cert filenames — it is *not*
> the same as the MySQL **schema** name (`<DB_SCHEMA>`).

Cert locations after login (used by mTLS clients below):

```
~/.tsh/keys/<TELEPORT_PROXY_HOST>/cas/<CA_NAME>.pem                    # CA
~/.tsh/keys/<TELEPORT_PROXY_HOST>/<YOUR_EMAIL>-db/<CLUSTER>/<DB_ALIAS>.crt
~/.tsh/keys/<TELEPORT_PROXY_HOST>/<YOUR_EMAIL>-db/<CLUSTER>/<DB_ALIAS>.key
```

---

## 8. Query a SQL Server / Dataverse-style DB from VS Code

For DBs exposing a TDS (SQL) endpoint (e.g. Dataverse/D365):

1. Install the **SQL Server (mssql)** extension by Microsoft.
2. Add Connection:

   | Field | Value |
   |---|---|
   | Server | `<HOST>,<TDS_PORT>` (e.g. `...,5558`) |
   | Authentication | Azure Active Directory – Universal with MFA |
   | Database | *(leave blank)* |

3. Test Connection → Connect → sign in via the SSO prompt.
4. Open a `.sql` file and run standard `SELECT`s against logical table names.

> Read-only via TDS: `SELECT` works; `INSERT/UPDATE/DELETE` and metadata queries
> generally don't. Initial connect can be slow — that's normal.

---

## 9. MySQL access from Claude Code / Claude Desktop (MCP)

This is the headline setup: expose a MySQL DB to Claude as an MCP tool. It relies
on the local proxy from §7 already listening.

### Add via CLI (Claude Code)

```bash
# remove stale entries first (stored in ~/.claude.json)
claude mcp remove <MCP_NAME> --scope user

claude mcp add --scope user <MCP_NAME> \
  -e MYSQL_HOST=127.0.0.1 \
  -e MYSQL_PORT=13307 \
  -e MYSQL_USER=<DB_USER> \
  -e MYSQL_PASS= \
  -e MYSQL_DB=<DB_SCHEMA> \
  -- npx -y @benborla29/mcp-server-mysql
```

### Or edit config directly

`~/.claude.json` (Claude Code) / `claude_desktop_config.json` (Claude Desktop)
share the same `mcpServers` shape:

```json
{
  "mcpServers": {
    "<MCP_NAME>": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/npx",
      "args": ["-y", "@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "127.0.0.1",
        "MYSQL_PORT": "13307",
        "MYSQL_USER": "<DB_USER>",
        "MYSQL_PASS": "",
        "MYSQL_DB": "<DB_SCHEMA>",

        "// mTLS certs — only if the proxy runs WITHOUT --tunnel": "",
        "MYSQL_SSL_CA":   "<HOME>/.tsh/keys/<PROXY_HOST>/cas/<CA_NAME>.pem",
        "MYSQL_SSL_CERT": "<HOME>/.tsh/keys/<PROXY_HOST>/<EMAIL>-db/<CLUSTER>/<DB_ALIAS>.crt",
        "MYSQL_SSL_KEY":  "<HOME>/.tsh/keys/<PROXY_HOST>/<EMAIL>-db/<CLUSTER>/<DB_ALIAS>.key",
        "MYSQL_SSL_REJECT_UNAUTHORIZED": "false"
      }
    }
  }
}
```

- If the proxy is in **tunnel** mode (plain TCP, port `13308`), drop all four
  `MYSQL_SSL_*` keys.
- If the proxy is in **mTLS** mode (port `13307`), keep them.

### A filesystem MCP (bonus — lets Claude read a codebase)

```json
"<CODEBASE_MCP_NAME>": {
  "command": "/opt/homebrew/bin/npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "<PATH_TO_REPO>"]
}
```

### A GitHub MCP (bonus)

```json
"github": {
  "type": "stdio",
  "command": "docker",
  "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<GH_TOKEN>" }
}
```

---

## 10. Claude Code CLI

```bash
# install per Anthropic's current docs, then:
claude            # first run
/login            # SSO / API sign-in
/terminal-setup   # sets up terminal key bindings
# restart the terminal app afterwards
```

**`claude: command not found`?** A tooling update sometimes clobbers `~/.zshrc`.
Ensure the local bin is on PATH and the binary exists:

```bash
export PATH="$HOME/.local/bin:$PATH"
ls ~/.local/bin/claude
```

---

## 11. App DB connection with mTLS (JDBC) — when tunnel mode isn't available

JVM MySQL drivers can't read PEM files directly; convert the Teleport certs to
Java keystores first.

```bash
mkdir -p /tmp/jdbc-ssl

# 1. client keystore (PKCS12)
openssl pkcs12 -export \
  -in  ~/.tsh/keys/<PROXY_HOST>/<EMAIL>-db/<CLUSTER>/<DB_ALIAS>.crt \
  -inkey ~/.tsh/keys/<PROXY_HOST>/<EMAIL>-db/<CLUSTER>/<DB_ALIAS>.key \
  -out /tmp/jdbc-ssl/client-keystore.p12 -passout pass:<KEYSTORE_PASS>

# 2. truststore (JKS)
keytool -import -alias teleport-ca \
  -file ~/.tsh/keys/<PROXY_HOST>/cas/<CA_NAME>.pem \
  -keystore /tmp/jdbc-ssl/truststore.jks -storepass <KEYSTORE_PASS> -noprompt
```

JDBC URL (Spring Boot `application-*.properties`):

```properties
spring.datasource.url=jdbc:mysql://127.0.0.1:13307/<DB_SCHEMA>\
  ?useSSL=true\
  &verifyServerCertificate=false\
  &clientCertificateKeyStoreUrl=file:///tmp/jdbc-ssl/client-keystore.p12\
  &clientCertificateKeyStoreType=PKCS12\
  &clientCertificateKeyStorePassword=<KEYSTORE_PASS>\
  &trustCertificateKeyStoreUrl=file:///tmp/jdbc-ssl/truststore.jks\
  &trustCertificateKeyStorePassword=<KEYSTORE_PASS>\
  &allowPublicKeyRetrieval=true&serverTimezone=UTC
```

For **tunnel** mode instead, this collapses to a plain
`jdbc:mysql://127.0.0.1:13308/<DB_SCHEMA>?useSSL=false&allowPublicKeyRetrieval=true`.

---

## Quick checklist for a fresh machine

- [ ] Homebrew installed, `brew` on PATH
- [ ] `~/.zshrc` restored (exports, aliases, JDK switcher) → `source ~/.zshrc`
- [ ] Git + `gh`, SSH key generated & added to Git host
- [ ] JDK (17) + Maven; IntelliJ Project SDK set
- [ ] IDE(s): VS Code / IntelliJ / Cursor + AI assistant
- [ ] Docker runtime (Colima) up; registry login works
- [ ] `kubectl` (+ kubelogin) with `KUBECONFIG` set
- [ ] `tsh` login + `mysql-client`; proxy starts and binds its port
- [ ] Claude Code: `/login`, `/terminal-setup`, MCP entries added & connecting

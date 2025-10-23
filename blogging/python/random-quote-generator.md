# Random Quote — Multi-Package Workspace (Hatch)

## 0) Create workspace + venv (inside `multi-quote/`)

```bash
# create workspace
mkdir multi-quote
cd multi-quote

# create a local virtualenv in this folder
python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows powershell:
# .\.venv\Scripts\Activate.ps1

# tools we’ll use
python -m pip install --upgrade pip
pip install hatch fastapi "uvicorn[standard]"
```

---

## 1) Scaffold projects (names match `pyproject.toml`)

> We’ll create **three libraries** under `packages/` and **one API app** under `apps/`.
> Project names use hyphens; package folders use underscores (Hatch handles this).

```bash
# libraries
mkdir packages && cd packages
hatch new quotes-core
hatch new quotes-list
hatch new quotes-file
cd ..

# api
mkdir apps && cd apps
hatch new quotes-api
cd ..
```

After this, the key bits of your tree will look like:

```
multi-quote/
├── packages/
│   ├── quotes-core/   └─ src/quotes_core/
│   ├── quotes-list/   └─ src/quotes_list/
│   └── quotes-file/   └─ src/quotes_file/
└── apps/
    └── quotes-api/    └─ src/quotes_api/
```

Hatch created `src/<sanitized_name>/__init__.py` for each.

---

## 2) Add/replace files (code + pyproject)

### 2.1 `packages/quotes-core/pyproject.toml`

Keep Hatch’s generated `[build-system]` and `[tool.hatch.*]` sections. Ensure the **[project]** section is:

```toml
[project]
name = "quotes-core"
version = "0.1.0"
description = "Core interfaces and plugin loader for quote providers"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []
authors = [{ name = "You" }]
license = { text = "MIT" }
```

### 2.2 `packages/quotes-core/src/quotes_core/providers.py`

```python
from __future__ import annotations
from typing import Protocol, Optional
from dataclasses import dataclass
import importlib.metadata as md

class QuoteProvider(Protocol):
    """Any provider must implement this method."""
    def get_quote(self) -> str: ...

PLUGIN_GROUP = "random_quotes.providers"

@dataclass(frozen=True)
class ProviderSpec:
    name: str
    obj: object  # class or factory/instance

def list_providers() -> list[ProviderSpec]:
    """Discover installed providers via entry points."""
    specs: list[ProviderSpec] = []
    for ep in md.entry_points(group=PLUGIN_GROUP):
        specs.append(ProviderSpec(name=ep.name, obj=ep.load()))
    return specs

def get_provider(name: str, *, fallback: Optional[str] = None) -> QuoteProvider:
    """Instantiate a provider by entry-point name, with optional fallback."""
    eps = {ep.name: ep for ep in md.entry_points(group=PLUGIN_GROUP)}
    chosen = name if name in eps else fallback
    if not chosen or chosen not in eps:
        raise LookupError(f"No provider '{name}'. Available: {', '.join(eps) or 'none'}")
    loaded = eps[chosen].load()
    instance = loaded() if isinstance(loaded, type) else loaded
    return instance  # type: ignore[return-value]
```

---

### 2.3 `packages/quotes-list/pyproject.toml`

```toml
[project]
name = "quotes-list"
version = "0.1.0"
description = "Random quote provider from an in-memory list"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["quotes-core>=0.1.0"]
authors = [{ name = "You" }]
license = { text = "MIT" }

[project.entry-points."random_quotes.providers"]
list = "quotes_list.provider:ListQuoteProvider"
```

### 2.4 `packages/quotes-list/src/quotes_list/provider.py`

```python
from __future__ import annotations
import random

class ListQuoteProvider:
    def __init__(self) -> None:
        self._quotes = [
            "Simplicity is the soul of efficiency.",
            "Programs must be written for people to read.",
            "Premature optimization is the root of all evil.",
            "Code never lies, comments sometimes do.",
        ]

    def get_quote(self) -> str:
        return random.choice(self._quotes)
```

---

### 2.5 `packages/quotes-file/pyproject.toml`

```toml
[project]
name = "quotes-file"
version = "0.1.0"
description = "Random quote provider that reads from a text file"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["quotes-core>=0.1.0"]
authors = [{ name = "You" }]
license = { text = "MIT" }

[project.entry-points."random_quotes.providers"]
file = "quotes_file.provider:FileQuoteProvider"
```

### 2.6 `packages/quotes-file/src/quotes_file/provider.py`

```python
from __future__ import annotations
import os, pathlib, random

class FileQuoteProvider:
    """
    Reads quotes from a newline-delimited text file.
    Path via env QUOTES_FILE (default ./quotes.txt).
    """
    def __init__(self) -> None:
        self._path = pathlib.Path(os.getenv("QUOTES_FILE", "quotes.txt"))
        if not self._path.exists():
            self._path.write_text(
                "Talk is cheap. Show me the code.\n"
                "Simple is better than complex.\n"
                "In theory, theory and practice are the same.\n"
            )
        self._quotes = [q.strip() for q in self._path.read_text().splitlines() if q.strip()]
        if not self._quotes:
            raise RuntimeError(f"No quotes found in {self._path}")

    def get_quote(self) -> str:
        return random.choice(self._quotes)
```

---

### 2.7 `apps/quotes-api/pyproject.toml`

No special wheel config needed because **project name** = `quotes-api` and **package folder** = `src/quotes_api` (Hatch’s default). Add this **[project]** and an optional run script:

```toml
[project]
name = "quotes-api"
version = "0.1.0"
description = "FastAPI app exposing a random quote endpoint"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.111",
  "uvicorn[standard]>=0.30",
  "quotes-core>=0.1.0"
]
authors = [{ name = "You" }]
license = { text = "MIT" }

[tool.hatch.envs.default.scripts]
serve = "uvicorn quotes_api.main:app --app-dir src --reload"
```

### 2.8 `apps/quotes-api/src/quotes_api/main.py`

```python
from __future__ import annotations
import os
from fastapi import FastAPI, Depends, HTTPException
from quotes_core.providers import QuoteProvider, get_provider, list_providers

def build_app() -> FastAPI:
    app = FastAPI(title="Random Quote API", version="0.1.0")

    provider_name = os.getenv("QUOTE_PROVIDER", "list")
    try:
        provider_instance = get_provider(provider_name, fallback="list")
    except Exception as e:
        raise RuntimeError(f"Failed to load quote provider: {e}") from e

    def provider_dep() -> QuoteProvider:
        return provider_instance

    @app.get("/quotes/random")
    def random_quote(p: QuoteProvider = Depends(provider_dep)):
        try:
            return {"quote": p.get_quote(), "provider": provider_name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/providers")
    def providers():
        return {"providers": [spec.name for spec in list_providers()]}

    return app

app = build_app()
```

---

## 3) Install everything (editable) into your venv

From the workspace root (`multi-quote/`):

```bash
pip install -e packages/quotes-core
pip install -e packages/quotes-list
pip install -e packages/quotes-file
pip install -e apps/quotes-api
```

> Re-run `pip install -e <package>` if you later change entry points in a provider’s `pyproject.toml`.

---

## 4) Final testing

### 4.1 Verify providers are discovered

```bash
python -c "from quotes_core.providers import list_providers; print([p.name for p in list_providers()])"
# Expected output: ['list', 'file']
```

### 4.2 Run the API (two equivalent ways)

**From workspace root**:

```bash
uvicorn quotes_api.main:app --app-dir apps/quotes-api/src --reload
```

**Or using Hatch inside the API project**:

```bash
cd apps/quotes-api
hatch run serve
```

You should see Uvicorn start on `http://127.0.0.1:8000`.

### 4.3 Hit the endpoints

```bash
curl http://127.0.0.1:8000/providers
# {"providers":["list","file"]}

curl http://127.0.0.1:8000/quotes/random
# {"quote":"...", "provider":"list"}
```

### 4.4 Switch implementations (no code changes)

**mac/linux (bash/zsh):**

```bash
export QUOTE_PROVIDER=file
export QUOTES_FILE=./my_quotes.txt
printf "Stay hungry, stay foolish.\nLess is more.\n" > my_quotes.txt
# restart uvicorn if needed
```

**windows powershell:**

```powershell
$env:QUOTE_PROVIDER = "file"
$env:QUOTES_FILE = ".\my_quotes.txt"
"Stay hungry, stay foolish.`nLess is more." | Set-Content -Path my_quotes.txt
# restart uvicorn if needed
```

Test again:

```bash
curl http://127.0.0.1:8000/quotes/random
# {"quote":"Stay hungry, stay foolish.", "provider":"file"}  (example)
```

---

## 5) Troubleshooting quickies

* **`list_providers()` returns `[]`**
  Ensure you installed `quotes-list` and `quotes-file` into the *same* venv as the API (`pip install -e ...`), and their `pyproject.toml` has the `[project.entry-points."random_quotes.providers"]` block.

* **`ModuleNotFoundError` when starting Uvicorn**
  Use the correct module + app-dir for this layout:
  `uvicorn quotes_api.main:app --app-dir apps/quotes-api/src --reload`

* **Changed entry points but nothing updates**
  Re-run `pip install -e packages/<provider>` after editing a provider’s `pyproject.toml`.

---

## 6) Optional niceties

* Add `.gitignore` to keep `.venv/` and build artifacts out of Git:

  ```
  .venv/
  __pycache__/
  *.pyc
  build/
  dist/
  *.egg-info/
  .pytest_cache/
  .hatch/
  .env
  *.env
  .DS_Store
  .vscode/
  .idea/
  ```

---
### 🏗 project overview

| package         | role                                                | depends on                                 | entry-points group                             | provides                                                         |
| --------------- | --------------------------------------------------- | ------------------------------------------ | ---------------------------------------------- | ---------------------------------------------------------------- |
| **quotes-core** | defines the plugin interface and discovery system   | —                                          | `random_quotes.providers` (declared by others) | `QuoteProvider` Protocol + `list_providers()` / `get_provider()` |
| **quotes-list** | simple in-memory provider                           | `quotes-core>=0.1.0`                       | `random_quotes.providers`                      | `list = quotes_list.provider:ListQuoteProvider`                  |
| **quotes-file** | file-based provider                                 | `quotes-core>=0.1.0`                       | `random_quotes.providers`                      | `file = quotes_file.provider:FileQuoteProvider`                  |
| **quotes-api**  | REST API using FastAPI, dynamically loads providers | `quotes-core>=0.1.0`, `fastapi`, `uvicorn` | *(none — it consumes, not provides)*           | REST endpoints `/quotes/random` and `/providers`                 |

---


## 🧩 recap of what’s declared

in your `quotes-file` package’s `pyproject.toml` you have:

```toml
[project.entry-points."random_quotes.providers"]
file = "quotes_file.provider:FileQuoteProvider"
```

and similar for the list provider:

```toml
[project.entry-points."random_quotes.providers"]
list = "quotes_list.provider:ListQuoteProvider"
```

---

## 🧠 what’s really happening

the **left-hand side** (`file`, `list`, etc.)
is **not** a Python variable in your code.

instead, it’s an **entry-point name** — a *key* in a registry that Python packaging builds at install time.

---

## 🗂️ when you install the package

when you run:

```bash
pip install -e packages/quotes-file
```

pip writes metadata to your environment:

```
.../site-packages/quotes_file-0.1.0.dist-info/entry_points.txt
```

and it contains:

```
[random_quotes.providers]
file = quotes_file.provider:FileQuoteProvider
```

so Python now knows:

> “in the group `random_quotes.providers`, there’s a plugin named `file` that loads from `quotes_file.provider:FileQuoteProvider`.”


## ✅ TL;DR

* `file` is not a normal variable — it’s a **plugin name**.
* It’s stored as metadata when your package is installed.
* Your `quotes_core` uses it dynamically when discovering or loading plugins.
* When you set `QUOTE_PROVIDER=file`, you’re *selecting* that plugin by its name.


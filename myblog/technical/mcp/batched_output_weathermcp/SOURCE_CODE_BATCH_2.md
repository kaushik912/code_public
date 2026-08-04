# Source Code Batch

This file contains 5 source files.

---

## File: requirements.txt

```text
litellm>=1.50
mcp>=1.9,<2
httpx>=0.27
fastapi>=0.110
uvicorn[standard]>=0.29
```

---

## File: static/app.js

```javascript
const log = document.getElementById("log");
const input = document.getElementById("q");

function add(cls, text) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.textContent = text;
  log.appendChild(d);
  return d;
}

async function send() {
  const msg = input.value.trim();
  if (!msg) return;
  add("user", msg);
  input.value = "";
  const thinking = add("bot", "…");
  try {
    const r = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });
    const data = await r.json();
    thinking.textContent = data.answer;
    if (data.steps && data.steps.length) {
      add(
        "steps",
        data.steps
          .map((s) => `🔧 ${s.tool}(${JSON.stringify(s.args)}) -> ${s.result}`)
          .join("\n")
      );
    }
  } catch (e) {
    thinking.textContent = "Error: " + e;
  }
}

document.getElementById("ask").addEventListener("click", send);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});
```

---

## File: static/index.html

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weather Agent</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <h2>🌤️ Weather Agent <small>(LiteLLM + MCP)</small></h2>
  <div class="bar">
    <input id="q" placeholder="how is the weather today?" autofocus>
    <button id="ask">Ask</button>
  </div>
  <div id="log"></div>
  <script src="/static/app.js"></script>
</body>
</html>
```

---

## File: static/styles.css

```css
body {
  font-family: system-ui, sans-serif;
  max-width: 640px;
  margin: 40px auto;
  padding: 0 16px;
}
h2 small { color: #888; font-weight: 400; }
.bar { display: flex; gap: 8px; }
input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
button {
  padding: 10px 16px;
  border: 0;
  border-radius: 8px;
  background: #3b5bdb;
  color: #fff;
  cursor: pointer;
}
#log { margin-top: 20px; }
.msg {
  padding: 10px 14px;
  border-radius: 10px;
  margin: 8px 0;
  white-space: pre-wrap;
}
.user { background: #e8eefc; }
.bot { background: #f2f2f2; }
.steps {
  font-size: 12px;
  color: #666;
  background: #fafafa;
  border: 1px solid #eee;
}
```

---

## File: test_mcp.py

```python
"""Quick check that the MCP server works WITHOUT any LLM/API key."""
import asyncio, os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.getenv("WEATHER_MCP_URL", "http://127.0.0.1:8001/mcp")


async def main():
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])
            res = await session.call_tool("get_weather", {"city": "Tokyo"})
            print("result:", "\n".join(c.text for c in res.content if getattr(c, "type", None) == "text"))


if __name__ == "__main__":
    asyncio.run(main())
```

---


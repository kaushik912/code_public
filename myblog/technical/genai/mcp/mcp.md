### What is MCP?
MCP is an open protocol that enables AI models to securely interact with local and remote resources through standardized server implementations. This list focuses on production-ready and experimental MCP clients that extend AI capabilities through file access, database connections, API integrations, and other contextual services.

## MCP Example1
https://github.com/amidabuddha/console-chat-gpt
- This is a CLI tool that allows us to chat in command-line itself. 
- I was able to generate code using prompts in ollama locally.
- Didn't test any MCP flow though.

### More examples
- FastMCP article : https://medium.com/@shmilysyg/fastmcp-the-fastway-to-build-mcp-servers-aa14f88536d2
    - Talks about using Claude Desktop along with MCP
    - code repo is https://github.com/jlowin/fastmcp
- https://medium.com/@richardhightower/setting-up-claude-filesystem-mcp-80e48a1d3def
- unified markdown documentation : https://github.com/RichardHightower/create_project_markdown/tree/main
- List of Awesome MCP servers: https://github.com/punkpeye/awesome-mcp-servers?tab=readme-ov-file#tutorials

# MCP Inspector:
- Install & Run MCP Inspector: `npx @modelcontextprotocol/inspector`
- This command starts both a client UI (default port 5173) and an MCP proxy server (default port 3000).
- Connect to Your MCP Server:
    - Enter the URL of your local or remote MCP server in the Inspector's UI to start testing.




# MCP Steps to connect to local MySQL server
- [Github Reference](https://github.com/modelcontextprotocol/quickstart-resources.git)
## Prompt Used as a starting point
```
I have a mysql database running locally. How can i connect to that using MCP? Give me step by step way to run a sample query using MCP.
```

## Key Steps
- `mkdir -p your_project/mysql-server-python`
- Activate the virtual env and install dependent packages using: `python -m pip install mysql-connector-python "mcp[cli]"`
- Create a file named [mysql_mcp_server.py](mysql_server.py) that contains the mcp tools like connectivity, show databases and describe tables. 
  - This will help LLM to understand the schema and then accordingly create queries.
- Under .vscode/mcp.json, add the following entry
```json
{
    "servers": {
        "mysql-mcp-server": {
            "type": "stdio",
            "command": "/Users/kkailasnath/projects/genai/mcp/quickstart-resources/.venv/bin/python3",
            "args": [
                "/Users/kkailasnath/projects/genai/mcp/quickstart-resources/mysql-server-python/mysql_server.py"
            ]
        }
    }
}
```
- After this, `start` the MCP server.
- It should also appear in the Github copilot Agent Chat view.


## Try it out!

  > "Show me all tables in the almdb database" 
  
  and Copilot will use the `list_tables` MCP command.

  > "Run a query to select all records from the application table where name equals 'dockerserv'" 
  
  and Copilot will use the `run_mysql_query` command.
  
  > "how many applications were created in 2021 where deleted=0, provide me month wise report"
  
There's no special syntax required - just ask what you want to do with the MySQL database in plain English, and GitHub Copilot will use the appropriate MCP command configured in your workspace.



## Tool list in this example

The MCP servers in your workspace are configured to handle specific functions. The MySQL server implementation provides the following tools:

- `connect_mysql`
- `run_mysql_query`
- `list_databases`
- `list_tables`
- `describe_table`


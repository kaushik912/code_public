# Revolutionize Your Database Workflow: Connecting MySQL to GitHub Copilot with MCP

In this guide, we'll explore how to supercharge your database workflow by connecting your local MySQL database to GitHub Copilot using the Model Context Protocol (MCP). This integration allows you to interact with your database using natural language, making database operations more intuitive and efficient.

> 🔥 **Game Changer**: With MCP, you can query your MySQL database using plain English through GitHub Copilot, eliminating the need to switch contexts or remember exact SQL syntax.

## What is Model Context Protocol (MCP)?

MCP is a protocol that enables AI assistants like GitHub Copilot to interact with external tools and services. By connecting your MySQL database to Copilot via MCP, you can leverage the power of natural language to perform database operations.

> 💡 **Key Insight**: MCP bridges the gap between large language models and external systems, allowing LLMs to execute actions in your environment rather than just providing suggestions.

## Step-by-Step Setup Guide

### Demo Video
In case you want to skip all the reading, here is the demo video showing all steps in detail!
[Watch the video](mcp_local_mysql_high.mp4)

### 1. Create Your Project Structure

First, let's set up a directory for our MCP server:

```bash
mkdir -p your_project/mysql-server-python
```

### 2. Install Required Packages

Set up a virtual environment and install the necessary packages:

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
python -m pip install mysql-connector-python "mcp[cli]"
```

> ⚠️ **Best Practice**: Always use a virtual environment to avoid conflicts between project dependencies.

### 3. Create the MCP Server

Create a file named `mysql_server.py` with the following code:

```python
from typing import Any, Dict, List, Optional
import mysql.connector
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mysql")

# MySQL credentials - customize these for your setup
DEFAULT_HOST = "localhost"
DEFAULT_USER = "root"
DEFAULT_PASSWORD = "<root_password>"  # Replace with your actual password
DEFAULT_DATABASE = "<your_db>"  # Change to your default database

class MySQLConnection:
    def __init__(self, host: str, user: str, password: str, database: Optional[str] = None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self) -> None:
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"Connected to MySQL database: {self.database}")
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            raise err

    def close(self) -> None:
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a MySQL query and return results"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        
        if cursor.with_rows:
            results = cursor.fetchall()
        else:
            # For non-SELECT queries, return rowcount
            results = [{"affected_rows": cursor.rowcount}]
            
        cursor.close()
        return results

# MySQL connection instance
mysql_conn = None

@mcp.tool()
async def connect_mysql(host: str = DEFAULT_HOST, user: str = DEFAULT_USER, 
                       password: str = DEFAULT_PASSWORD, database: Optional[str] = DEFAULT_DATABASE) -> str:
    """Connect to a MySQL database."""
    global mysql_conn
    try:
        # Use the provided parameters or fall back to defaults
        actual_host = host or DEFAULT_HOST
        actual_user = user or DEFAULT_USER
        actual_password = password or DEFAULT_PASSWORD
        actual_database = database or DEFAULT_DATABASE
        
        mysql_conn = MySQLConnection(actual_host, actual_user, actual_password, actual_database)
        mysql_conn.connect()
        return f"Successfully connected to MySQL at {actual_host}" + (f", database: {actual_database}" if actual_database else "")
    except Exception as e:
        return f"Failed to connect to MySQL: {str(e)}"

# Other MCP tools defined here...

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
```

> 🔒 **Security Note**: Never commit your actual database password to version control. Consider using environment variables or a secure configuration method in production.

### 4. Configure VS Code Integration

Create a `.vscode/mcp.json` file with the following configuration:

```json
{
    "servers": {
        "mysql-mcp-server": {
            "type": "stdio",
            "command": "/path/to/your/venv/bin/python3",
            "args": [
                "/path/to/your/project/mysql_server.py"
            ]
        }
    }
}
```

Make sure to update the paths to match your environment.

### 5. Start the MCP Server

Start the MCP server from VS Code. Once started, the server should appear in the GitHub Copilot Agent Chat view.


## Using Natural Language with Your Database

Once everything is set up, you can interact with your database using natural language in GitHub Copilot:

### Example 1: Exploring Database Tables

Simply ask:
> "Show me all tables in the almdb database"

GitHub Copilot will call the `list_tables` MCP command behind the scenes.

### Example 2: Querying Specific Records

Ask:
> "Run a query to select all records from the application table where name equals 'dockerserv'"

GitHub Copilot will translate this to SQL and use the `run_mysql_query` command to execute it.

### Example 3: Complex Analysis

You can even request complex analytics:
> "How many applications were created in 2021 where deleted=0, provide me month wise report"

GitHub Copilot will generate the appropriate SQL query based on your natural language request.

> 🚀 **Productivity Boost**: No need for context switching between writing application code and crafting SQL queries - do everything through natural conversation with GitHub Copilot!

## Benefits of Using MCP with MySQL

1. **Productivity**: Interact with your database without leaving your IDE or switching contexts
2. **Accessibility**: No need to remember exact SQL syntax or table structures
3. **Learning**: See the SQL that gets generated from your natural language queries
4. **Flexibility**: Easily modify and refine queries through conversation


## Conclusion

Connecting your MySQL database to GitHub Copilot using MCP opens up powerful new ways to work with your data. By using natural language, you can solve complex problems rather than crafting perfect SQL syntax, leading to a more efficient and enjoyable development experience.

Give it a try and see how it transforms your database workflow!

## Reference: Available MCP Tools in this Code

The MySQL server implementation provides several powerful tools:

- `connect_mysql`: Establishes a connection to your MySQL server
- `run_mysql_query`: Executes SQL queries against your database
- `list_databases`: Shows all available databases
- `list_tables`: Lists tables in a specific database
- `describe_table`: Provides the schema of a selected table
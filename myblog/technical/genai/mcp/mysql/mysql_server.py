from typing import Any, Dict, List, Optional
import mysql.connector
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mysql")

# Hard-coded MySQL credentials
DEFAULT_HOST = "localhost"
DEFAULT_USER = "root"
DEFAULT_PASSWORD = "<root_password>"  # Replace with your actual MySQL password and restart MCP server post changes
DEFAULT_DATABASE = "almdb"  # Set to a specific database name if desired

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
    """Connect to a MySQL database.

    Args:
        host: Database host address
        user: Database username
        password: Database password
        database: Optional database name to use
    """
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

@mcp.tool()
async def run_mysql_query(query: str) -> str:
    """Run a SQL query on the connected MySQL database.

    Args:
        query: SQL query to execute
    """
    global mysql_conn
    if not mysql_conn:
        return "Not connected to a MySQL database. Use connect_mysql tool first."
    
    try:
        results = mysql_conn.execute_query(query)
        
        if not results:
            return "Query executed successfully. No results returned."
            
        # Format results as readable text
        if "affected_rows" in results[0]:
            return f"Query executed successfully. Affected rows: {results[0]['affected_rows']}"
        
        # For SELECT queries with results
        headers = results[0].keys()
        rows = []
        
        # Add header row
        header_row = " | ".join(str(h) for h in headers)
        separator = "-" * len(header_row)
        rows.append(header_row)
        rows.append(separator)
        
        # Add data rows
        for result in results:
            row = " | ".join(str(result[h]) for h in headers)
            rows.append(row)
            
        return "\n".join(rows)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
async def list_databases() -> str:
    """List all databases on the connected MySQL server."""
    global mysql_conn
    if not mysql_conn:
        return "Not connected to a MySQL database. Use connect_mysql tool first."
    
    try:
        results = mysql_conn.execute_query("SHOW DATABASES")
        databases = [result["Database"] for result in results]
        return "Available databases:\n" + "\n".join(databases)
    except Exception as e:
        return f"Error listing databases: {str(e)}"

@mcp.tool()
async def list_tables(database: Optional[str] = None) -> str:
    """List all tables in the current or specified database.
    
    Args:
        database: Optional database name to list tables from
    """
    global mysql_conn
    if not mysql_conn:
        return "Not connected to a MySQL database. Use connect_mysql tool first."
    
    try:
        # Switch database if specified
        if database:
            mysql_conn.execute_query(f"USE {database}")
            
        results = mysql_conn.execute_query("SHOW TABLES")
        table_column = list(results[0].keys())[0] if results else "Tables_in_database"
        tables = [result[table_column] for result in results]
        
        db_name = database if database else mysql_conn.database if mysql_conn.database else "current"
        return f"Tables in {db_name} database:\n" + "\n".join(tables)
    except Exception as e:
        return f"Error listing tables: {str(e)}"

@mcp.tool()
async def describe_table(table_name: str) -> str:
    """Show the structure of a table.
    
    Args:
        table_name: Name of the table to describe
    """
    global mysql_conn
    if not mysql_conn:
        return "Not connected to a MySQL database. Use connect_mysql tool first."
    
    try:
        results = mysql_conn.execute_query(f"DESCRIBE {table_name}")
        
        if not results:
            return f"No structure information available for table {table_name}"
            
        # Format table structure
        headers = results[0].keys()
        rows = []
        
        # Add header row
        header_row = " | ".join(str(h) for h in headers)
        separator = "-" * len(header_row)
        rows.append(header_row)
        rows.append(separator)
        
        # Add data rows
        for result in results:
            row = " | ".join(str(result[h]) for h in headers)
            rows.append(row)
            
        return f"Structure of table {table_name}:\n" + "\n".join(rows)
    except Exception as e:
        return f"Error describing table: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
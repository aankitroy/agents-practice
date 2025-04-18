import logging
import concurrent.futures
import atexit

import clickhouse_connect
from clickhouse_connect.driver.binding import quote_identifier, format_query_value
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp_env import config

# Server configuration
MCP_SERVER_NAME = "mcp-clickhouse"
SELECT_QUERY_TIMEOUT_SECS = 30

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Executor for asynchronous query handling
QUERY_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=10)
atexit.register(lambda: QUERY_EXECUTOR.shutdown(wait=True))

# Load environment variables
load_dotenv()

# Define MCP dependencies
deps = [
    "clickhouse-connect",
    "python-dotenv",
    "uvicorn",
    "pip-system-certs",
]

# Initialize MCP server
mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)

# Create ClickHouse client helper
def create_clickhouse_client():
    client_config = config.get_client_config()
    try:
        client = clickhouse_connect.get_client(**client_config)
        logger.info("Successfully connected to ClickHouse server")
        return client
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise

@mcp.tool()
def list_databases():
    client = create_clickhouse_client()
    try:
        result = client.command("SHOW DATABASES")
        return result if isinstance(result, list) else [result]
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        return f"Error: {e}"

@mcp.tool()
def list_tables(database: str, like: str = None):
    client = create_clickhouse_client()
    try:
        query = f"SHOW TABLES FROM {quote_identifier(database)}"
        if like:
            query += f" LIKE {format_query_value(like)}"

        tables = client.command(query)
        if isinstance(tables, str):
            tables = tables.split()

        table_info_list = []
        for table in tables:
            schema_query = f"DESCRIBE TABLE {quote_identifier(database)}.{quote_identifier(table)}"
            schema_result = client.query(schema_query)

            columns = [{col_name: row[idx] for idx, col_name in enumerate(schema_result.column_names)}
                       for row in schema_result.result_rows]

            table_info = {
                "database": database,
                "table": table,
                "columns": columns
            }
            table_info_list.append(table_info)

        return table_info_list
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error: {e}"

@mcp.tool()
def run_select_query(query: str):
    future = QUERY_EXECUTOR.submit(execute_query, query)
    try:
        result = future.result(timeout=SELECT_QUERY_TIMEOUT_SECS)
        return result
    except concurrent.futures.TimeoutError:
        logger.error("Query timeout")
        future.cancel()
        return f"Query exceeded {SELECT_QUERY_TIMEOUT_SECS}s limit."

# Execute query helper function
def execute_query(query: str):
    client = create_clickhouse_client()
    try:
        res = client.query(query, settings={"readonly": 1})
        return [{col: row[idx] for idx, col in enumerate(res.column_names)}
                for row in res.result_rows]
    except Exception as err:
        logger.error(f"Query execution error: {err}")
        return f"Error: {err}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
import json
from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from sql_agent import query_sql_agent  # ✅ Import the fixed function

def fetch_data() -> str:
    """Fetches and prepares the actual data for context usage."""
    query = dedent("""
        Retrieve **both the structure and actual data** from all tables in the database.
        
        - For **each table**, include:
          - Table name
          - Column names and their data types
          - Foreign key relationships (if any)
          - **A complete snapshot of all rows in JSON format**
        
        **Ensure the output is structured in JSON format** with table names as keys 
        and their rows as a list of dictionaries.
        
        **Important:** 
        - Do not fabricate data.
        - Ensure all numerical values retain their precision.
    """)

    response: RunResponse = query_sql_agent(query)  # ✅ Uses `RunResponse`
    return json.dumps(response.content, indent=4)  # ✅ Extract structured content

# Fetch database schema
data = fetch_data()

# --- Context Agent ---
context_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    context={"context_data": data},
    add_context=True,  # ✅ Enable automatic context injection
    markdown=True,
)

# Example Usage
user_query = input("Enter your question about retail data: ")
print("\n--- Context Agent Output ---\n")
context_agent.print_response(user_query,stream=True)


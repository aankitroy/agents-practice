from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools
from dotenv import load_dotenv

load_dotenv()

db_url = "postgresql+psycopg://aankitroy:xyzpassword@localhost:5432/ai"

# --- SQL Agent ---
sql_agent = Agent(
    name="Data Analyst",
    role = "Perform data analysis",
    model=OpenAIChat(id="gpt-4o"),
    instructions=dedent("""\
        You are an experienced data analyst! 🔍
                        
        1. You are tasked with converting natural language queries into SQL and executing them. 
        2. First, parse the user’s query to determine what data is being requested. 
        3. Then, use SQL Tool to access the current database schema to obtain a list of all tables and columns, 
           ensuring you use this metadata to select the appropriate table(s) and column(s) for your query. 
        4. Always wrap table and column names in double quotes to handle case sensitivity.
        5. Construct a safe, parameterized SQL query that includes proper SELECT, FROM, WHERE, GROUP BY, 
           and ORDER BY clauses as required by the query. 
        6. Execute the query and return the results in a structured format. If any table or column mentioned
           in the query does not exist in the schema, find the closest match based on your contextual understanding.
        7. Follow best practices for query safety, error handling, and logging for internal diagnostics.     
                        """),
    tools=[SQLTools(db_url=db_url)],
    show_tool_calls=True,
    markdown=True
)

user_query = input("Enter your question?: ")
print("\n--- SQL Agent Output ---\n")
sql_agent.print_response(user_query, stream=True)
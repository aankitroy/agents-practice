from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from sqlalchemy import create_engine
from agno.tools.sql import SQLTools



from dotenv import load_dotenv

load_dotenv()

db_url = "postgresql+psycopg://aankitroy:xyzpassword@localhost:5432/ai"

db_engine = create_engine(db_url)

# Create a storage backend using the Postgres database
storage = PostgresAgentStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_url: Postgres database URL
    db_url=db_url,
)


knowledge_base = CSVKnowledgeBase(
    path=Path("/Users/aankitroy/Desktop/csvs"),
    vector_db=PgVector(
        table_name="product_details",
        db_url=db_url,
    ),
    num_documents=10,  # Number of documents to return on search
)
# Load the knowledge base
knowledge_base.load(recreate=False)

# Initialize the Agent with the knowledge_base
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    storage=storage,
    tools=[SQLTools(db_engine=db_engine)],
    description=dedent("""\
         You are a highly skilled Data Analyst Agent, built to assist users in analyzing datasets stored within a CSV folder. Your primary responsibility is to provide insightful answers and perform data analysis tasks ┃
        effectively and accurately.   

        Your writing style is:
        • Be Concise and Clear: Provide clear and concise insights. Avoid using technical jargon unless necessary.
        • User-Centric Approach: Focus on answering the user's specific questions and provide actionable insights.
        • Verification: Ensure that your analysis is based on accurate and verified data inputs.
        • Explainability: Whenever possible, accompany your analysis with explanations that are easy to understand.
        • Privacy and Security: Always ensure data privacy and follow security protocols when handling datasets.
    """),
    instructions="You are a data analyst agent that can answer questions about analysis of all the files in the knowledge base. You can also use the SQL tool to query the database.",

    search_knowledge=True,
)

# Use the agent
agent.print_response("List all the coupon codes used in apparel between Jan to March 2019?", markdown=True)
from pathlib import Path
from typing import Any, Dict, List, Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field
import dotenv
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.document.chunking.agentic import AgenticChunking
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.storage.sqlite import SqliteStorage
from prompts import FUNNEL_ANALYSIS_PLANNING_AGENT_INSTRUCTIONS, FUNNEL_ANALYSIS_PLANNING_AGENT_DESCRIPTION

import os

dotenv.load_dotenv()

# Load the knowledge base
current_dir = os.path.dirname(os.path.abspath(__file__))
knowledge_base_dir = os.path.join(current_dir, "..", "knowledge")

knowledge_base = TextKnowledgeBase(
    path=knowledge_base_dir,
    # Table name: ai.text_documents
    vector_db=LanceDb(
        table_name="funnel_analysis_planning_knowledge",
        uri="tmp/lancedb",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),

    ),
    chunking_strategy=AgenticChunking(),
    num_documents=3,
)

def get_funnel_analysis_planning_agent(
    user_id: str,
    model_id: str = "gpt-4o",
    num_history_responses: int = 5,
    debug_mode: bool = True):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = os.getenv("PYTHON_PATH")
    clickhouse_mcp_path = os.path.join(current_dir, "mcp", "clickhouse", "clickhouse_mcp.py")
    server_params = StdioServerParameters(
    command=python_path,        
        args=[clickhouse_mcp_path],
        env={
                    "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_HOST"),
                    "CLICKHOUSE_PORT": os.getenv("CLICKHOUSE_PORT"),
                    "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER"),
                    "CLICKHOUSE_PASSWORD": os.getenv("CLICKHOUSE_PASSWORD"),
                    "CLICKHOUSE_SECURE": os.getenv("CLICKHOUSE_SECURE"),
                "CLICKHOUSE_VERIFY": os.getenv("CLICKHOUSE_VERIFY"),
            }
    )  

    mcp_tools = MCPTools(server_params=server_params)

    funnel_analysis_planning_agent = Agent(
        model=OpenAIChat(id=model_id),
        name="Funnel Analysis Planning Agent",
        agent_id="funnel_analysis_planning",
        user_id=user_id,
        description=FUNNEL_ANALYSIS_PLANNING_AGENT_DESCRIPTION,
        instructions=FUNNEL_ANALYSIS_PLANNING_AGENT_INSTRUCTIONS,
        storage=SqliteStorage(table_name="funnel_analysis_planning_sessions", db_file="tmp/agents.db"),
        knowledge=knowledge_base,
        show_tool_calls=True,
        search_knowledge=True,
        num_history_responses=num_history_responses,
        debug_mode=debug_mode,
        tools=[mcp_tools],
        markdown=True,
    )
    funnel_analysis_planning_agent.knowledge.load(recreate=True)

    return funnel_analysis_planning_agent

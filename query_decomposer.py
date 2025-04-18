from typing import Any, Dict, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import dotenv
from pydantic import BaseModel, Field
from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.document.chunking.agentic import AgenticChunking
dotenv.load_dotenv()

class SubQuestion(BaseModel):
    id: str = Field(...)
    question: str = Field(...)
    dependencies: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "forbid"

class MetadataModel(BaseModel):
    intent: str = Field(...)
    entities: List[str] = Field(...)
    metrics: List[str] = Field(...)
    time_periods: List[str] = Field(...)
    
    class Config:
        extra = "forbid"

class QueryDecomposition(BaseModel):
    metadata: MetadataModel = Field(...)
    sub_questions: List[SubQuestion] = Field(...)
    execution_order: List[str] = Field(...)

    class Config:
        extra = "forbid"

model_id = "gpt-4o"


knowledge_base = JSONKnowledgeBase(
    path="/Users/aankitroy/Workspace/Experiments/agents-practice/json/question_decomposition_knowledge.json",
    # Table name: ai.json_documents
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="miracle_of_minds_knowledge_base",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    chunking_strategy=AgenticChunking(),
    num_documents=1,
)

query_decomposer = Agent(
        model=OpenAIChat(id=model_id),
        description="You are a Query Decomposition Agent specialized in analytics for digital products like meditation or wellness apps.",
        instructions=[
            "Given a high-level analytical question, Exactly match the question to the knowledge base(miracle_of_minds_knowledge_base) to generate the output as mentioned in the knowledge base and return in the format mentioned below. Follow these steps strictly for the output structure:",
            "1. Identify metadata:",
            "   - intent (e.g., 'conversion_analysis', 'retention_analysis')",
            "   - entities (e.g., ['user', 'session'])",
            "   - metrics (e.g., ['conversion_rate', 'retention_rate'])",
            "   - time_periods (e.g., ['last_30_days'])",
            "2. Decompose into 4–7 sub-questions.",
            "3. Identify dependencies between sub-questions (use question IDs like 'q1', 'q2').",
            "4. Create a valid execution order using topological sorting.",
            "Return strictly in this format:",
            "{",
            "  'metadata': {",
            "    'intent': '...',",
            "    'entities': [...],",
            "    'metrics': [...],",
            "    'time_periods': [...]",
            "  },",
            "  'sub_questions': [",
            "    { 'id': 'q1', 'question': '...', 'dependencies': [] },",
            "    ...",
            "  ],",
            "  'execution_order': ['q1', 'q2', ...]",
            "}"
        ],
        knowledge=knowledge_base,
        search_knowledge=True,
        debug_mode=True,
        tools=[DuckDuckGoTools()],
        response_model=QueryDecomposition,
        show_tool_calls=True,
        markdown=True,
)

# Comment out after the knowledge base is loaded
# if query_decomposer.knowledge is not None:
#     query_decomposer.knowledge.load()

def get_query_decomposer(model_id: str):
    return query_decomposer

#query_decomposer.print_response("What is the history of Thai curry?", stream=True)
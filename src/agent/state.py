from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """
    Represents the state of the SQL generation agent.
    """
    question: str
    sql_query: Optional[str]
    query_result: Optional[str]
    answer: Optional[str]
    error: Optional[str]
    model_provider: str = "openai"
    iterations: int = 0

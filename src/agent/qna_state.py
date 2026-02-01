from typing import TypedDict, Optional, List, Dict, Any

class QnAState(TypedDict):
    question: str
    model_provider: str
    model_name: Optional[str]
    
    # Outputs
    business_explanation: Optional[str]
    entity_explanation: Optional[str]
    sql_query: Optional[str]
    table_layout: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    summary: Optional[str]
    
    error: Optional[str]

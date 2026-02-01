from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from src.agent.qna_graph import qna_graph

router = APIRouter(prefix="/api/v1", tags=["qna"])

class QnARequest(BaseModel):
    question: str
    model_provider: Literal["openai", "gemini"] = Field("openai", description="LLM Provider to use")
    model_name: Optional[str] = Field(None, description="Specific model to use")

class QnAResponse(BaseModel):
    question: str
    business_explanation: str
    entity_explanation: str
    sql_query: str
    table_layout: str # JSON string or description of schema used
    data: List[Dict[str, Any]]
    summary: str
    error: Optional[str] = None

@router.post("/qna", response_model=QnAResponse)
async def ask_qna(request: QnARequest):
    try:
        # Invoke the QnA graph
        result = await qna_graph.ainvoke({
            "question": request.question,
            "model_provider": request.model_provider,
            "model_name": request.model_name
        })
        
        if result.get("error"):
             return QnAResponse(
                question=request.question,
                business_explanation="Error",
                entity_explanation="Error",
                sql_query="",
                table_layout="",
                data=[],
                summary="An error occurred.",
                error=result["error"]
            )

        return QnAResponse(
            question=request.question,
            business_explanation=result.get("business_explanation", ""),
            entity_explanation=result.get("entity_explanation", ""),
            sql_query=result.get("sql_query", ""),
            table_layout=result.get("table_layout", ""),
            data=result.get("query_result", []),
            summary=result.get("summary", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

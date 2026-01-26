from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.agent.graph import graph
from typing import Literal

router = APIRouter(prefix="/api/v1", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    model_provider: Literal["openai", "gemini"] = Field("openai", description="LLM Provider to use")
    model_name: Optional[str] = Field(None, description="Specific model to use (e.g. gpt-4o)")

class QueryResponse(BaseModel):
    question: str
    sql_query: str | None = None
    query_result: str | None = None
    answer: str | None = None
    error: str | None = None
    provider: str
    model: str | None = None

@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # Invoke the graph with question AND model_provider
        result = graph.invoke({
            "question": request.question,
            "model_provider": request.model_provider,
            "model_name": request.model_name
        })
        
        return QueryResponse(
            question=result["question"],
            sql_query=result.get("sql_query"),
            query_result=result.get("query_result"),
            answer=result.get("answer"),
            error=result.get("error"),
            provider=result.get("model_provider", request.model_provider),
            model=request.model_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

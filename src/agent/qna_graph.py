from langgraph.graph import StateGraph, END
from src.agent.qna_state import QnAState
from src.database import get_db
from src.agent.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Pydantic model for the LLM structured output
class StructuredQnAPlan(BaseModel):
    business_explanation: str = Field(..., description="Why this question is important from a business perspective.")
    entity_explanation: str = Field(..., description="Which tables and columns were chosen and why.")
    sql_query: str = Field(..., description="The valid SQL query to answer the question.")
    table_layout: str = Field(..., description="A summary of the table schema used.")

class SummaryOutput(BaseModel):
    summary: str = Field(..., description="The natural language answer based on the data.")

def generate_plan_node(state: QnAState):
    """
    Generates usage explanation, SQL, and schema info.
    """
    db = get_db()
    schema = db.get_table_info()
    
    provider = state.get("model_provider", "openai")
    model_name = state.get("model_name")
    
    try:
        llm = get_llm(provider, model_name)
        # Force structured output
        structured_llm = llm.with_structured_output(StructuredQnAPlan)
    except Exception as e:
        return {"error": f"LLM Setup Error: {str(e)}"}
    
    template = """You are an expert SQL data analyst.
    Given the database schema, answer the user's question by generating a valid SQL query and explaining your reasoning.
    
    Schema:
    {schema}
    
    User Question: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | structured_llm
    
    try:
        result: StructuredQnAPlan = chain.invoke({"schema": schema, "question": state["question"]})
        return {
            "business_explanation": result.business_explanation,
            "entity_explanation": result.entity_explanation,
            "sql_query": result.sql_query,
            "table_layout": result.table_layout,
            "error": None
        }
    except Exception as e:
        return {"error": f"Planning Failed: {str(e)}"}

def execute_qna_query_node(state: QnAState):
    """Executes the generated SQL."""
    if state.get("error"):
        return {"error": state["error"]}
        
    db = get_db()
    try:
        from sqlalchemy import text
        
        # Use the underlying SQLAlchemy engine to get raw results as list of dicts
        with db._engine.connect() as connection:
            result_proxy = connection.execute(text(state["sql_query"]))
            # keys are internal in sqlalchemy 1.4+, need to convert to list/keys handle
            keys = result_proxy.keys()
            rows = result_proxy.fetchall()
            
            # Map columns to values
            results = [dict(zip(keys, row)) for row in rows]
            
        return {"query_result": results}
    except Exception as e:
        return {"error": f"Execution Failed: {str(e)}"}

def summarize_result_node(state: QnAState):
    """Summarizes the data result."""
    if state.get("error"):
        return {"summary": "Error occurred during processing."}
        
    provider = state.get("model_provider", "openai")
    model_name = state.get("model_name")
    
    try:
        llm = get_llm(provider, model_name)
    except:
        return {"summary": "Error initializing LLM for summary."}

    template = """You are a data analyst.
    Summarize the following data results to answer the user's original question.
    
    Question: {question}
    Business Context: {business_explanation}
    Data Results: {query_result}
    
    Provide a concise executive summary.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | PydanticOutputParser(pydantic_object=SummaryOutput) # Or just StrOutputParser
    
    # Let's just use StrOutputParser for the summary to be safe and simple
    from langchain_core.output_parsers import StrOutputParser
    chain = prompt | llm | StrOutputParser()
    
    try:
        summary = chain.invoke({
            "question": state["question"],
            "business_explanation": state["business_explanation"],
            "query_result": state.get("query_result", "No results")
        })
        return {"summary": summary}
    except Exception as e:
        return {"summary": f"Failed to generate summary: {str(e)}"}

# Build Graph
qna_workflow = StateGraph(QnAState)
qna_workflow.add_node("plan", generate_plan_node)
qna_workflow.add_node("execute", execute_qna_query_node)
qna_workflow.add_node("summarize", summarize_result_node)

qna_workflow.set_entry_point("plan")
qna_workflow.add_edge("plan", "execute")
qna_workflow.add_edge("execute", "summarize")
qna_workflow.add_edge("summarize", END)

qna_graph = qna_workflow.compile()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.agent.state import AgentState
from src.database import get_db
from src.agent.llm_factory import get_llm
import logging

logger = logging.getLogger(__name__)

def write_query(state: AgentState) -> AgentState:
    """
    Generates an SQL query based on the user question and database schema.
    """
    logger.info("Generating SQL query...")
    # Dynamically get DB (SQLite or Postgres) based on config
    db = get_db()
    schema = db.get_table_info()
    
    # 1. Get LLM based on provider in state (default to openai if missing)
    provider = state.get("model_provider", "openai")
    try:
        llm = get_llm(provider)
    except ValueError as e:
        return {"error": str(e)}

    template = """You are an expert SQL data analyst.
    Given the following database schema for a SALES database, write a SQL query to answer the user's question.
    
    The table name is 'sales_data'.
    Key columns: org_name, product_name, sales_amount, quantity, sale_date, year, quarter, month, region.
    
    - Always use 'sales_amount' for revenue calculations.
    - Always use 'sales_data' as the table name.
    - Return ONLY the SQL query. No markdown, no explanation.
    
    Schema:
    {schema}
    
    Question: {question}
    
    SQL Query:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        query = chain.invoke({"schema": schema, "question": state["question"]})
        cleaned_query = query.strip().replace("```sql", "").replace("```", "")
        logger.info(f"Generated Query ({provider}): {cleaned_query}")
        return {"sql_query": cleaned_query, "error": None}
    except Exception as e:
        return {"error": str(e)}

def execute_query(state: AgentState) -> AgentState:
    """
    Executes the generated SQL query against the database.
    """
    logger.info("Executing SQL query...")
    if state.get("error"):
        return {"error": state["error"]}

    if not state.get("sql_query"):
        return {"error": "No SQL query generated."}
    
    db = get_db()
    query = state["sql_query"]
    
    try:
        result = db.run(query)
        logger.info(f"Query Result: {result}")
        return {"query_result": str(result), "error": None}
    except Exception as e:
        return {"error": f"SQL Execution Failed: {str(e)}"}

def generate_answer(state: AgentState) -> AgentState:
    """
    Synthesizes a natural language answer from the SQL result.
    """
    logger.info("Generating final answer...")
    
    if state.get("error"):
        return {"answer": f"I enountered an error: {state['error']}"}
        
    # Get LLM based on provider
    provider = state.get("model_provider", "openai")
    try:
        llm = get_llm(provider)
    except ValueError as e:
        return {"error": str(e), "answer": "Configuration Error"}

    template = """You are a data analyst helper.
    Based on the original question and the SQL result, provide a clear, concise answer.
    
    Question: {question}
    SQL Query Used: {sql_query}
    SQL Result: {query_result}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        answer = chain.invoke({
            "question": state["question"], 
            "sql_query": state["sql_query"],
            "query_result": state["query_result"] or "No results found."
        })
        return {"answer": answer}
    except Exception as e:
        return {"answer": "Failed to generate answer.", "error": str(e)}

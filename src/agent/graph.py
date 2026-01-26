from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import write_query, execute_query, generate_answer

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("write_query", write_query)
workflow.add_node("execute_query", execute_query)
workflow.add_node("generate_answer", generate_answer)

# Add edges
workflow.set_entry_point("write_query")
workflow.add_edge("write_query", "execute_query")
workflow.add_edge("execute_query", "generate_answer")
workflow.add_edge("generate_answer", END)

# Compile
graph = workflow.compile()

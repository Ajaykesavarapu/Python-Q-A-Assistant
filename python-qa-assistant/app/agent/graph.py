from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import (
    classify_question_node,
    retrieve_context_node,
    generate_answer_node,
    fallback_node
)

def should_retrieve(state: AgentState) -> str:
    """Determines whether to take the retrieval route or fallback route."""
    if state["needs_retrieval"]:
        return "retrieve"
    return "fallback"

def build_graph():
    """Assembles and compiles the full LangGraph state engine flow."""
    workflow = StateGraph(AgentState)
    
    # Register Node functions
    workflow.add_node("classify", classify_question_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("generate", generate_answer_node)
    workflow.add_node("fallback", fallback_node)
    
    # Establish edges and conditional routing hooks
    workflow.add_edge(START, "classify")
    workflow.add_conditional_edges(
        "classify", 
        should_retrieve, 
        {"retrieve": "retrieve", "fallback": "fallback"}
    )
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    workflow.add_edge("fallback", END)
    
    return workflow.compile()

graph = build_graph()

async def run_agent(question: str, chat_history: list = []) -> dict:
    """
    Primary agent helper invoking the compiled stategraph asynchronously.
    """
    initial_state = {
        "question": question,
        "chat_history": chat_history,
        "retrieved_docs": [],
        "answer": "",
        "sources": [],
        "needs_retrieval": True,
        "steps_taken": []
    }
    result = await graph.ainvoke(initial_state)
    return result

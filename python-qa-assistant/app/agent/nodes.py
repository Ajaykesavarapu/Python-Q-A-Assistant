from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agent.state import AgentState
from app.core.llm import get_llm
from app.rag.retriever import get_retriever
from app.utils.logger import logger

def classify_question_node(state: AgentState) -> dict:
    """
    Evaluates whether the user's question relates to Python programming, syntax, 
    exception handling, libraries (like pandas, numpy), SQLite, etc.
    Updates needs_retrieval.
    """
    logger.info("[*] Executing: classify_question_node")
    question = state.get("question", "")
    steps = list(state.get("steps_taken", []))
    steps.append("classify_question")
    
    # Simple semantic rule-of-thumb mapping for failsafe operations
    keywords = ["python", "pandas", "numpy", "list", "tuple", "comprehension", "exception", "lambda", "sqlite", "gil", "multithreading", "script", "code", "csv", "dictionary", "merge"]
    is_python_kw = any(kw in question.lower() for kw in keywords)
    
    # Try querying the LLM for high-fidelity classification
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template(
            "You are a routing classification system. Answer ONLY 'YES' or 'NO'.\n"
            "Does the following question seek help with Python programming, libraries, architecture, coding issues, or syntax?\n"
            "Question: {question}\n\n"
            "Classification:"
        )
        # Handle fake llm or string output differences
        chain = prompt | llm | StrOutputParser()
        res = chain.invoke({"question": question}).strip().upper()
        needs_retrieval = "YES" in res or is_python_kw
    except Exception as e:
        logger.warning(f"Classification LLM call failed: {e}. Defaulting to keyword check.")
        needs_retrieval = is_python_kw or len(question.strip()) > 5

    logger.info(f"[✓] Question classification decision: needs_retrieval={needs_retrieval}")
    return {
        "needs_retrieval": needs_retrieval,
        "steps_taken": steps
    }

def retrieve_context_node(state: AgentState) -> dict:
    """Retrieves top-5 grounding context matches from Chroma Vector Database."""
    logger.info("[*] Executing: retrieve_context_node")
    question = state.get("question", "")
    steps = list(state.get("steps_taken", []))
    steps.append("retrieve_context")
    
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)
        logger.info(f"[✓] Retrieved {len(docs)} documents for context embedding.")
    except Exception as e:
        logger.exception(f"Error executing retrieve context node: {e}")
        docs = []
        
    return {
        "retrieved_docs": docs,
        "steps_taken": steps
    }

def generate_answer_node(state: AgentState) -> dict:
    """Uses LLM to answer the user request grounded specifically on retrieved context."""
    logger.info("[*] Executing: generate_answer_node")
    question = state.get("question", "")
    docs = state.get("retrieved_docs", [])
    steps = list(state.get("steps_taken", []))
    steps.append("generate_answer")
    
    # Map sources
    sources = []
    for d in docs:
        sources.append({
            "title": d.metadata.get("title", "Stack Overflow Python Solution"),
            "score": float(d.metadata.get("similarity_score", 0.94)),
            "snippet": d.page_content[:250] + "..."
        })
        
    # Standard format context
    context_str = "\n\n".join([f"--- Doc Chunk ---\n{d.page_content}" for d in docs])
    
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template(
            "You are a helpful Python Programming Q&A Assistant tutor.\n"
            "Answer the question thoroughly and with detailed code snippets using ONLY the retrieved context below.\n"
            "If the context is unrelated or insufficient, state 'I don't have enough information'.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Response:"
        )
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context_str, "question": question})
    except Exception as e:
        logger.exception(f"Answer generation node error: {e}")
        answer = "Error generating grounded answer. Please review vector database setup and API tokens."
        
    return {
        "answer": answer,
        "sources": sources,
        "steps_taken": steps
    }

def fallback_node(state: AgentState) -> dict:
    """Handles off-topic or security queries politely and informatively."""
    logger.info("[*] Executing: fallback_node")
    steps = list(state.get("steps_taken", []))
    steps.append("fallback")
    
    answer = (
        "I am your dedicated Python Programming Q&A Assistant! 👋\n\n"
        "I specialize in resolving questions regarding Python syntax, list comprehensions, "
        "exceptions, dictionary operations, local database connections (SQLite), "
        "and frameworks like Pandas or NumPy.\n\n"
        "Your current question appears off-topic. Please ask a Python-related programming question."
    )
    
    return {
        "answer": answer,
        "sources": [],
        "steps_taken": steps
    }

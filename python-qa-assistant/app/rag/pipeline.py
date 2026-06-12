import time
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings
from app.core.llm import get_llm
from app.rag.retriever import get_retriever
from app.utils.logger import logger

def format_docs(docs) -> str:
    """Formats document chunks in a clear layout for prompt ingestion."""
    formatted = []
    for i, doc in enumerate(docs):
        meta = doc.metadata
        formatted.append(
            f"--- Document Source [{i+1}] --- \n"
            f"Title: {meta.get('title', 'Unknown')}\n"
            f"Question ID: {meta.get('question_id', 'N/A')} | Answer ID: {meta.get('answer_id', 'N/A')}\n"
            f"Tags: {meta.get('tags', 'python')}\n"
            f"Content:\n{doc.page_content}\n"
        )
    return "\n\n".join(formatted)

def get_rag_chain():
    """Compiles the standard LangChain Expression Language (LCEL) chain."""
    retriever = get_retriever()
    llm = get_llm()
    
    # Custom system constraint prompt template
    prompt_template = """You are a software engineering tutor guiding Python learners.
Respond with clear explanations, structured sections, and verified code examples.
You MUST answer the question using ONLY the provided Stack Overflow derived context below.
If the retrieved documents do not contain enough relevant details, say "I don't have enough information".
Do NOT make up or hallucinate any facts.

--- RETRIEVED GROUNDING CONTEXT ---
{context}

--- QUESTION ---
Question: {question}

--- DETAILED ANNOTATED RESPONSE ---
Provide your grounded, Python-supported developer response here:"""

    prompt = PromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()
    
    # LCEL layout: context | input | chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )
    return chain

async def rag_query(question: str) -> dict:
    """
    Exposes full pipeline query resolution, measuring elapsed latency and reporting
    matched documentation node listings.
    """
    t0 = time.time()
    logger.info(f"RAG query initiated: '{question}'")
    
    try:
        retriever = get_retriever()
        # Retrieve docs directly first to return sources listing safely
        docs = retriever.invoke(question)
        
        # Build formatting list
        sources_list = []
        for d in docs:
            # simple score simulation since retriever direct results might not contain cosine score
            sources_list.append({
                "title": d.metadata.get("title", d.metadata.get("title", "Stack Overflow Python Solution")),
                "score": float(d.metadata.get("similarity_score", 0.92)),
                "snippet": d.page_content[:250] + "..."
            })
            
        # Execute prompt execution
        chain = get_rag_chain()
        # Ensure invoking doesn't crash on Fake/Real LLM differences
        answer = await chain.ainvoke(question)
        
        elapsed = int((time.time() - t0) * 1000)
        
        return {
            "answer": answer,
            "sources": sources_list,
            "context_used": [d.page_content for d in docs],
            "processing_time_ms": elapsed
        }
    except Exception as e:
        logger.exception(f"Error executing standard RAG chain: {e}")
        return {
            "answer": "Error occurred resolving question. Please check configuration logs.",
            "sources": [],
            "context_used": [],
            "processing_time_ms": int((time.time() - t0) * 1000)
        }

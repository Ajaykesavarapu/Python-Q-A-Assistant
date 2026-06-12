from langchain.tools import Tool
from app.rag.retriever import get_retriever

def get_retriever_tool() -> Tool:
    """
    Assembles a LangChain Tool instance around the ChromaDB retriever
    enabling agentic search query resolution.
    """
    retriever = get_retriever()
    
    def retrieve_func(query: str) -> str:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
        
    return Tool(
        name="python_qa_retriever",
        func=retrieve_func,
        description="Searches Stack Overflow Python Q&A database for relevant answers and code snippets."
    )

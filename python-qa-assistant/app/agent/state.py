from typing import TypedDict, List, Any
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class AgentState(TypedDict):
    question: str
    chat_history: List[Any]
    retrieved_docs: List[Document]
    answer: str
    sources: List[dict]
    needs_retrieval: bool
    steps_taken: List[str]

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker (e.g. 'user', 'assistant')")
    content: str = Field(..., description="Text content of the message")

class AskRequest(BaseModel):
    question: str = Field(..., description="The query to submit to the RAG/Agent system")
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Optional conversation context history")

class AskExternalRequest(BaseModel):
    question: str = Field(..., description="The query to submit to the external LLM")
    provider: str = Field(..., description="External LLM provider name (e.g. 'Google Gemini', 'OpenAI')")
    api_key: Optional[str] = Field(None, description="Optional API key configured by the user")
    model: Optional[str] = Field(None, description="Optional model identifier")

class SourceModel(BaseModel):
    title: str = Field(..., description="Title of the source Stack Overflow discussion")
    score: float = Field(0.0, description="Semantic matching or relevance confidence score")
    snippet: str = Field(..., description="Excerpt or summarized context snippet from the matched document")

class AskResponse(BaseModel):
    answer: str = Field(..., description="Cleansed and grounded answer provided by the Python Programming Assistant")
    sources: List[SourceModel] = Field(default_factory=list, description="List of source items referenced during assembly")
    steps_taken: List[str] = Field(default_factory=list, description="Audit log of agent/pipeline nodes executed")
    model_used: str = Field(..., description="Label indicating language model chosen")
    processing_time_ms: int = Field(..., description="Execution timeline in milliseconds")

class StatsResponse(BaseModel):
    total_documents_indexed: int = Field(..., description="Total documents currently registered in the vector index")
    vector_store_size_mb: float = Field(..., description="Physical footprint of vector database in megabytes")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health category check ('healthy')")
    version: str = Field(..., description="Software release version")
    vector_store: str = Field(..., description="Connectivity status check for Vector storage layer")

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import router as api_router
from app.utils.logger import logger
from app.core.config import settings

def create_app() -> FastAPI:
    """Builds and wires the primary FastAPI application routing stack."""
    app = FastAPI(
        title="Python Q&A Assistant",
        description="An AI-powered Q&A Assistant using LangGraph and RAG to answer Python coding queries.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS setup allowing wide standard cross-origin requirements
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register core API sub-router
    app.include_router(api_router, prefix="/api")
    
    # Extra root redirection endpoints for accessibility
    @app.get("/")
    def index():
        return {
            "message": "Welcome to the Python Programming Q&A Assistant API!",
            "swagger_docs": "/docs",
            "health_check": "/api/health"
        }
        
    # Exception Handler: Request Validation (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"[!] Request validation failed: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Exception",
                "details": exc.errors(),
                "message": "Ensure request payload strictly meets expected JSON parameters."
            }
        )
        
    # Exception Handler: Unhandled Server Errors (500)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"[!] Unhandled Global Exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "Our engineers are notified. Please check system logs for API credentials."
            }
        )
        
    # Startup event: warm up connections
    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 60)
        logger.info("BOOTSTRAPPING PYTHON Q&A MASTER ENGINE")
        logger.info(f"    - Environment: {settings.APP_ENV}")
        logger.info(f"    - LLM Chosen: {settings.LLM_PROVIDER} ({settings.LLM_MODEL})")
        logger.info(f"    - Database Path: {settings.CHROMA_DB_PATH}")
        logger.info("=" * 60)
        
        # Warmup retriever instance
        try:
            from app.rag.retriever import get_retriever
            get_retriever()
            logger.info("[✓] Pre-loaded Chroma Vector database successfully!")
        except Exception as e:
            logger.warning(f"[!] Failed to pre-load vector database at startup: {e}")
            
    return app

app = create_app()

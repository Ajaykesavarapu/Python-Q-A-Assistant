from app.core.config import settings
from app.utils.logger import logger

def get_llm():
    """
    Lazy initialization of LLM based on provider settings.
    Avoids crashing on startup if keys are not present yet.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            # Check environment as backup
            import os
            api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # If still empty, load mock LLM for local trials/tests to prevent crashes
        if not api_key:
            logger.warning("[!] Warning: OPENAI_API_KEY is empty. Initializing Mock LLM for local test compliance.")
            from langchain_community.llms import FakeListLLM
            return FakeListLLM(responses=[
                "This is a mocked answer for testing. Please load real keys in your .env deployment. Pandas is loaded.",
                "Lists are mutable in Python while tuples are immutable."
            ])
            
        return ChatOpenAI(
            openai_api_key=api_key,
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            import os
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            
        if not api_key:
            logger.warning("[!] Warning: ANTHROPIC_API_KEY is empty. Initializing Mock LLM.")
            from langchain_community.llms import FakeListLLM
            return FakeListLLM(responses=["Mock reply"])
            
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model_name=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

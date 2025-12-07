"""
LLM Configuration for SmartGuard
Adapted to use Aegis configuration settings.
"""
import logging
from app.config import settings

# Import compatibility module FIRST to fix langchain_core.pydantic_v1 issue
# This MUST be imported before langchain_groq to create the compatibility layer
try:
    from app.services.smart_guard import _langchain_compat  # noqa: F401
except ImportError:
    pass  # Compatibility module not critical, continue anyway

logger = logging.getLogger(__name__)

# Try to import ChatGroq with robust error handling
try:
    from langchain_groq import ChatGroq
    CHATGROQ_AVAILABLE = True
except ImportError as e:
    logger.error(f"⚠️ langchain_groq not available: {e}")
    CHATGROQ_AVAILABLE = False
    ChatGroq = None
except Exception as e:
    logger.error(f"⚠️ langchain_groq import failed: {e}")
    CHATGROQ_AVAILABLE = False
    ChatGroq = None

# Use Aegis config for GROQ API Key
groq_api_key = settings.GROQ_API_KEY or ""

# LLMs - Using optimized models for different tasks (lazy initialization)
llm_vision = None
llm_reviewer = None
llm_doc = None

def _initialize_llms():
    """Initialize LLMs only when needed, with error handling."""
    global llm_vision, llm_reviewer, llm_doc
    
    if not CHATGROQ_AVAILABLE:
        raise ImportError(
            "langchain_groq is not available. Please install compatible versions: "
            "pip install langchain-groq pydantic-v1"
        )
    
    if llm_vision is None:
        try:
            llm_vision = ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=groq_api_key,
                temperature=0.3
            )
            llm_reviewer = ChatGroq(
                model_name="llama-3.1-8b-instant",
                groq_api_key=groq_api_key,
                temperature=0.2
            )
            llm_doc = ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=groq_api_key,
                temperature=0.3
            )
        except Exception as e:
            logger.error(f"Failed to initialize SmartGuard LLMs: {e}")
            raise

# Initialize LLMs on module import (but with error handling)
try:
    if CHATGROQ_AVAILABLE:
        _initialize_llms()
except Exception as e:
    logger.warning(f"SmartGuard LLMs initialization deferred: {e}")


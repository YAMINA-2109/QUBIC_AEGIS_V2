"""
SmartGuard LLMs Module
Lazy import to avoid breaking if dependencies not available.
"""
# Import compatibility module FIRST
try:
    from app.services.smart_guard.llms import _compat  # noqa: F401
except ImportError:
    pass  # Not critical

# Lazy import LLMs
try:
    from app.services.smart_guard.llms.groqllm import llm_doc, llm_reviewer, llm_vision
    __all__ = ["llm_doc", "llm_reviewer", "llm_vision"]
except (ImportError, AttributeError):
    # LLMs not available, export None values
    llm_doc = None
    llm_reviewer = None
    llm_vision = None
    __all__ = ["llm_doc", "llm_reviewer", "llm_vision"]


"""
SmartGuard Service - Integrated into Qubic Aegis
Full LangGraph workflow for C++ Smart Contract auditing.
Preserves 100% of the original SmartGuard architecture.
"""
# Import compatibility module FIRST to fix langchain_core.pydantic_v1 issue
try:
    from app.services.smart_guard import _langchain_compat  # noqa: F401
except ImportError:
    pass  # Compatibility module not critical, continue anyway

# Lazy import to avoid breaking if dependencies not available
try:
    from app.services.smart_guard.service import SmartGuardService
    SMARTGUARD_IMPORT_SUCCESS = True
except ImportError as e:
    SMARTGUARD_IMPORT_SUCCESS = False
    print(f"⚠️ SmartGuard import failed: {e}")
    SmartGuardService = None
except Exception as e:
    SMARTGUARD_IMPORT_SUCCESS = False
    print(f"⚠️ SmartGuard import error: {e}")
    SmartGuardService = None

# Initialize service instance (singleton pattern)
_smart_guard_service: SmartGuardService = None

def get_smart_guard_service() -> SmartGuardService:
    """Get or create SmartGuard service instance (singleton)."""
    global _smart_guard_service
    if not SMARTGUARD_IMPORT_SUCCESS:
        raise ImportError("SmartGuard service not available. Please install langgraph dependencies.")
    if _smart_guard_service is None:
        _smart_guard_service = SmartGuardService()
    return _smart_guard_service

__all__ = ["SmartGuardService", "get_smart_guard_service"]


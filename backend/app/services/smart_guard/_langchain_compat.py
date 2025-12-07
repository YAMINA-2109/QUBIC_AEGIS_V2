"""
LangChain Compatibility Module
This module must be imported BEFORE any langchain_groq imports to fix pydantic_v1 compatibility.

It creates a compatibility layer for langchain_core.pydantic_v1 that langchain_groq expects.
"""
import sys
import types

# Try to import pydantic.v1 (Pydantic v2 compatibility layer)
# This is included in pydantic>=2.0, no separate package needed
try:
    from pydantic.v1 import (
        BaseModel,
        Field,
        SecretStr,
        root_validator,
        validator,
    )
    PYDANTIC_V1_AVAILABLE = True
except ImportError:
    # Fallback: if pydantic.v1 not available, compatibility layer won't work
    PYDANTIC_V1_AVAILABLE = False

# Create langchain_core.pydantic_v1 module if it doesn't exist
if PYDANTIC_V1_AVAILABLE:
    # Create langchain_core module if needed
    if 'langchain_core' not in sys.modules:
        langchain_core_module = types.ModuleType('langchain_core')
        sys.modules['langchain_core'] = langchain_core_module
    
    # Create langchain_core.pydantic_v1 module if needed
    if 'langchain_core.pydantic_v1' not in sys.modules:
        pydantic_v1_module = types.ModuleType('langchain_core.pydantic_v1')
        
        # Export pydantic.v1 classes as langchain_core.pydantic_v1
        pydantic_v1_module.BaseModel = BaseModel
        pydantic_v1_module.Field = Field
        pydantic_v1_module.SecretStr = SecretStr
        pydantic_v1_module.root_validator = root_validator
        pydantic_v1_module.validator = validator
        
        sys.modules['langchain_core.pydantic_v1'] = pydantic_v1_module

__all__ = ["PYDANTIC_V1_AVAILABLE"]


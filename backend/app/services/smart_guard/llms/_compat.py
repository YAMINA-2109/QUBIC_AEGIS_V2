"""
Compatibility module for langchain_core.pydantic_v1
This ensures langchain_groq can import langchain_core.pydantic_v1 even if it doesn't exist.
"""
import sys

# Try to import pydantic.v1 (Pydantic v2 compatibility layer)
try:
    from pydantic.v1 import (
        BaseModel as PydanticBaseModel,
        Field as PydanticField,
        SecretStr,
        root_validator,
        validator,
    )
    PYDANTIC_V1_AVAILABLE = True
except ImportError:
    try:
        # Fallback: try importing from pydantic directly (for older versions)
        from pydantic import (
            BaseModel as PydanticBaseModel,
            Field as PydanticField,
            SecretStr,
            root_validator,
            validator,
        )
        PYDANTIC_V1_AVAILABLE = True
    except ImportError:
        PYDANTIC_V1_AVAILABLE = False
        PydanticBaseModel = None
        PydanticField = None
        SecretStr = None
        root_validator = None
        validator = None

# Create a mock langchain_core.pydantic_v1 module if it doesn't exist
if 'langchain_core' not in sys.modules:
    import types
    langchain_core_module = types.ModuleType('langchain_core')
    sys.modules['langchain_core'] = langchain_core_module

if 'langchain_core.pydantic_v1' not in sys.modules:
    import types
    pydantic_v1_module = types.ModuleType('langchain_core.pydantic_v1')
    
    if PYDANTIC_V1_AVAILABLE:
        # Export pydantic.v1 classes as langchain_core.pydantic_v1
        pydantic_v1_module.BaseModel = PydanticBaseModel
        pydantic_v1_module.Field = PydanticField
        pydantic_v1_module.SecretStr = SecretStr
        pydantic_v1_module.root_validator = root_validator
        pydantic_v1_module.validator = validator
    
    sys.modules['langchain_core.pydantic_v1'] = pydantic_v1_module

__all__ = ["PYDANTIC_V1_AVAILABLE"]


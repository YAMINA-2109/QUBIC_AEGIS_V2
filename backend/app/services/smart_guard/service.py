"""
SmartGuard Service - Wrapper for LangGraph workflow
Exposes the complete SmartGuard auditing pipeline in a clean interface.
"""
from typing import Dict, Any, Optional
from app.services.smart_guard.state.state import SmartContractState
import logging

logger = logging.getLogger(__name__)


class SmartGuardService:
    """
    Service wrapper for SmartGuard LangGraph workflow.
    Provides clean API for auditing C++ smart contracts.
    """
    
    def __init__(self):
        """Initialize the service with the compiled LangGraph (lazy)."""
        self._graph = None
        logger.info("SmartGuard service initialized (lazy graph loading)")
    
    @property
    def graph(self):
        """Get the compiled LangGraph (lazy initialization)."""
        if self._graph is None:
            try:
                # Lazy import to avoid breaking if LangGraph not available
                from app.services.smart_guard.graph.graph_builder import get_generated_graph
                self._graph = get_generated_graph()
            except Exception as e:
                logger.error(f"Failed to initialize SmartGuard graph: {e}", exc_info=True)
                raise
        return self._graph
    
    async def audit_contract(
        self,
        code: str,
        language: str = "english",
        simulation_scenario: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete SmartGuard audit pipeline on a C++ contract.
        
        Args:
            code: C++ smart contract source code
            language: Language for prompts/responses (default: "english")
            simulation_scenario: Optional simulation scenario for onTransaction/onTick
        
        Returns:
            Dictionary containing all audit results (commented code, audit report, etc.)
        """
        try:
            # Initialize state
            state = SmartContractState(
                input_code=code,
                language=language,
                simulation_scenario=simulation_scenario
            )
            
            # Convert state to dict for LangGraph (it expects a dict, not Pydantic model)
            state_dict = state.model_dump() if hasattr(state, 'model_dump') else state.dict()
            
            # Run the complete workflow
            logger.info(f"Starting SmartGuard audit (language: {language})")
            result = await self.graph.ainvoke(state_dict)
            
            # LangGraph returns a dictionary (AddableValuesDict), not the state object directly
            # Convert to SmartContractState if needed, or access as dict
            if isinstance(result, dict):
                # Access values from dictionary
                result_dict = result
            else:
                # If it's already a SmartContractState, convert to dict
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
            
            # Convert to dictionary for API response
            return {
                "commented": result_dict.get("commented"),
                "semantic_report": result_dict.get("semantic_report"),
                "strict_validation_report": result_dict.get("strict_validation_report"),
                "audit_report": result_dict.get("audit_report"),
                "functional_spec": result_dict.get("functional_spec"),
                "flow_diagram": result_dict.get("flow_diagram"),
                "detailed_doc": result_dict.get("detailed_doc"),
                "business_summary": result_dict.get("business_summary"),
                "test_plan": result_dict.get("test_plan"),
                "simulation_result": result_dict.get("simulation_result"),
                "qubic_logs": result_dict.get("qubic_logs"),
                "compilation_success": result_dict.get("compilation_success"),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"SmartGuard audit failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "Audit failed. Please check the code and try again."
            }
    
    async def quick_audit(self, code: str, language: str = "english") -> Dict[str, Any]:
        """
        Quick security audit (semantic analysis + security audit only).
        Faster than full audit for quick checks.
        
        Args:
            code: C++ smart contract source code
            language: Language for prompts/responses
        
        Returns:
            Dictionary with semantic report and audit report only
        """
        try:
            state = SmartContractState(
                input_code=code,
                language=language
            )
            
            # Run only semantic analysis and audit
            from app.services.smart_guard.nodes.qubicdocs_nodes import (
                semantic_analysis,
                generate_audit
            )
            
            state = semantic_analysis(state)
            state = generate_audit(state)
            
            return {
                "semantic_report": state.semantic_report,
                "audit_report": state.audit_report,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"SmartGuard quick audit failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "Quick audit failed."
            }


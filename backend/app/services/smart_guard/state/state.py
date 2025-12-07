from pydantic import BaseModel
from typing import Optional

class SmartContractState(BaseModel):
    """
    The shared state object for the LangGraph workflow.
    Holds all intermediate and final results for the Qubic SmartGuard pipeline.
    """

    # === INPUTS ===
    input_code: Optional[str] = None              # Original C++ smart contract
    language: str = "english"           # Language for prompts/responses

    # === PARSING ===
    parsed: Optional[str] = None                  # Preprocessed / linted code

    # === COMMENTING & REVIEW ===
    commented: Optional[str] = None               # Code with generated comments
    status: str = "Valid"               # Review status: Valid / Needs Fix
    message: Optional[str] = None                 # Reviewer feedback
    reviewed: bool = False              # Flag if reviewed at least once
    review_attempts: int = 0            # Counter for loop limit

    # === SEMANTIC ANALYSIS ===
    semantic_report: Optional[str] = None         # Static analysis of smart contract

    # === AUDIT ===
    audit_report: Optional[str] = None            # Security & optimization audit

    # === FUNCTIONAL SPECIFICATION ===
    functional_spec: Optional[str] = None         # Introductory functional spec section

    # === FLOW DIAGRAM ===
    flow_diagram: Optional[str] = None            # Mermaid.js diagram text

    # === DETAILED DOCUMENTATION ===
    detailed_doc: Optional[str] = None            # Section 3 detailed technical doc

    # === SUMMARY REPORT ===
    business_summary: Optional[str] = None        # Combined final documentation report

    # === STRICT VALIDATION ===
    strict_validation_report: Optional[str] = None # Result of static validation rules

    # === SIMULATION ===
    simulation_scenario: Optional[str] = None     # User-defined or default simulation scenario
    simulation_result: Optional[str] = None       # VM simulation JSON result

    # === TEST PLAN ===
    test_plan: Optional[str] = None               # Generated test plan markdown

    # === DEV KIT EXECUTION ===
    qubic_logs: Optional[str] = None              # Compilation / execution logs
    compilation_success: Optional[bool] = None    # Compilation success flag

    # === EXPORT ===
    output_json: Optional[str] = None             # Path to exported JSON file


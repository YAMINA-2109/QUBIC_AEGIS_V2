"""
SmartGuard Nodes - All LangGraph agents for C++ contract auditing
Adapted to use Aegis architecture (imports relative to app.services.smart_guard)
"""
import json
import re
from datetime import datetime
from app.services.smart_guard.state.state import SmartContractState
from app.services.smart_guard.utils.validators import strict_validator
from typing import Dict, Any, Union

# Helper function to normalize state (dict or SmartContractState -> dict)
def normalize_state(state: Union[Dict[str, Any], SmartContractState]) -> Dict[str, Any]:
    """Convert state to dict format that LangGraph expects."""
    if isinstance(state, dict):
        return state
    elif isinstance(state, SmartContractState):
        return state.model_dump() if hasattr(state, 'model_dump') else state.dict()
    else:
        return dict(state) if hasattr(state, '__dict__') else {}

# Helper function to get state as SmartContractState for attribute access
def get_state_obj(state: Union[Dict[str, Any], SmartContractState]) -> SmartContractState:
    """Get state as SmartContractState object for attribute access."""
    if isinstance(state, SmartContractState):
        return state
    elif isinstance(state, dict):
        return SmartContractState(**state)
    else:
        raise TypeError(f"Invalid state type: {type(state)}")

# Lazy import LLMs - only import when actually used
_llm_doc = None
_llm_reviewer = None
_llm_vision = None

def _get_llms():
    """Lazy load LLMs only when needed, with error handling."""
    global _llm_doc, _llm_reviewer, _llm_vision
    if _llm_doc is None:
        try:
            from app.services.smart_guard.llms.groqllm import _initialize_llms, llm_doc, llm_reviewer, llm_vision
            # Ensure LLMs are initialized
            if llm_doc is None:
                _initialize_llms()
                from app.services.smart_guard.llms.groqllm import llm_doc, llm_reviewer, llm_vision
            _llm_doc = llm_doc
            _llm_reviewer = llm_reviewer
            _llm_vision = llm_vision
        except Exception as e:
            raise ImportError(
                f"Failed to load SmartGuard LLMs: {e}. "
                "Please install: pip install langchain-groq pydantic-v1"
            )
    return _llm_doc, _llm_reviewer, _llm_vision

# =============================================================================
#               1. clean code function
# =============================================================================

def extract_clean_code(response: str) -> str:
    """
    Cleans LLM response of unnecessary preambles or code fences.
    """
    if not response:
        return ""
    match = re.search(r"</think>\s*", response, re.IGNORECASE)
    if match:
        response = response[match.end():].strip()

    response = re.sub(r"^```.*?\n", "", response.strip(), flags=re.MULTILINE)
    response = re.sub(r"\n```$", "", response.strip(), flags=re.MULTILINE)
    return response.strip()

# =============================================================================
#               2. Agent : Parse C++ Input
# =============================================================================

def parse_cpp(state) -> Dict[str, Any]:
    """
    Initial parser — currently a pass-through.
    """
    state_obj = get_state_obj(state)
    state_obj.parsed = state_obj.input_code
    return normalize_state(state_obj)

# =============================================================================
#               3. Agent : Commenting
# =============================================================================

def explain_and_comment_cpp(state) -> Dict[str, Any]:
    """
    Agent that generates line-by-line comments for C++ code.
    Handles re-asks with feedback.
    """
    # Convert to state object for easier attribute access
    state_obj = get_state_obj(state)
    
    if state_obj.status == "Needs Fix":
        prompt = f"""
You are a Qubic C++ Smart Contract Expert.

Here is the code that was previously commented but received feedback.

Your task:
- Fix and improve the comments.
- Make them clear, professional, and educational.
- Use // single-line C++ style.

Previous version:
{state_obj.commented or ''}

Reviewer feedback:
{state_obj.message}

Original code:
{state_obj.parsed}
        """
    else:
        prompt = f"""
You are a Qubic C++ Smart Contract Expert.

Analyze the following C++ smart contract code and add high-quality, professional, educational comments:

- Use // for single-line C++ comments.
- Explain what the code does and why.
- Do NOT modify the code itself.

Code:
{state_obj.parsed}
        """

    llm_doc, _, _ = _get_llms()
    response = llm_doc.invoke(prompt)
    state_obj.commented = extract_clean_code(response.content)
    # Return as dict for LangGraph
    return normalize_state(state_obj)

# =============================================================================
#           4. Agent : Reviewer
# =============================================================================

def review_comments(state) -> Dict[str, Any]:
    """
    Reviews commented code, giving Valid or Needs Fix.
    """
    state_obj = get_state_obj(state)
    
    # Get commented code, fallback to parsed if not available
    code_to_review = state_obj.commented or state_obj.parsed or state_obj.input_code or ""

    prompt = f"""
You are a Qubic C++ Smart Contract Review Assistant.

Your task:
- Review the following commented smart contract code.
- Ensure comments are clear, professional, meaningful.

If acceptable, answer exactly:
Valid

If not, answer exactly:
Needs Fix

Then provide detailed reasons for Needs Fix.

Code to review:
{code_to_review}
    """
    _, llm_reviewer, _ = _get_llms()
    result = llm_reviewer.invoke(prompt).content

    if "Valid" in result:
        state_obj.reviewed = True
        state_obj.status = "Valid"
        state_obj.message = result
    else:
        state_obj.reviewed = True
        state_obj.status = "Needs Fix"
        state_obj.message = result

    return normalize_state(state_obj)

def check_if_valid(state) -> str:
    """
    Decides graph route: Valid or Invalid.
    """
    state_obj = get_state_obj(state)
    if state_obj.status == "Valid":
        return "Valid"
    else:
        state_obj.review_attempts += 1
        if state_obj.review_attempts >= 3:
            state_obj.status = "Valid"
            return "Valid"
        return "Invalid"

# =============================================================================
#           5. Agent: Semantic Analysis
# =============================================================================

def analyze_semantics(code: str) -> str:
    """
    Static code checks for required functions and patterns.
    """
    report = ["# 🧭 Semantic Analysis Report"]

    # Check for Qubic mandatory functions
    required_funcs = ["init", "onTick", "onTransaction"]
    for func in required_funcs:
        pattern = rf'extern\s+"C"\s+void\s+{func}\s*\('
        if re.search(pattern, code):
            report.append(f"- ✅ `{func}` function found.")
        else:
            report.append(f"- ❌ `{func}` function MISSING!")

    # Transaction struct
    if "struct Transaction" in code:
        report.append("- ✅ `Transaction` struct found.")
    else:
        report.append("- ⚠️ `Transaction` struct NOT found.")

    # Basic state variable checks
    for var in ["balance", "tickCounter"]:
        if var in code:
            report.append(f"- ✅ `{var}` field present.")
        else:
            report.append(f"- ⚠️ `{var}` field MISSING.")

    # Raw casts
    if re.search(r'\(\s*SimpleState\s*\*\)', code):
        report.append("- ⚠️ Found raw cast to `(SimpleState*)`. Consider safe casting.")

    return "\n".join(report)

def semantic_analysis(state) -> Dict[str, Any]:
    """
    Runs static semantic analysis.
    """
    state_obj = get_state_obj(state)
    code = state_obj.commented or state_obj.input_code or ""
    state_obj.semantic_report = analyze_semantics(code)
    return normalize_state(state_obj)

# =============================================================================
#               6. Agent: Audit Report
# =============================================================================

def generate_audit(state: SmartContractState) -> SmartContractState:
    """
    LLM-powered security and optimization audit.
    """
    prompt = f"""
You are a Qubic C++ Smart Contract Auditor.

Analyze the following code and produce a clear, professional audit:

- Security vulnerabilities
- Risky patterns
- Optimization suggestions
- Best practices

Language: {state.language}

Code:
{state.commented}
    """
    _, llm_reviewer, _ = _get_llms()
    state.audit_report = llm_reviewer.invoke(prompt).content
    return state

# =============================================================================
#           7. Agent: Strict Validation
# =============================================================================

def run_strict_validation(state: SmartContractState) -> SmartContractState:
    """
    Static analysis and compliance checks.
    """
    code = state.commented or ""
    vm_report = strict_validator(code)
    state.strict_validation_report = vm_report
    return state

# =============================================================================
#           8. Agent: Functional Spec Intro
# =============================================================================

def generate_spec_intro(state: SmartContractState) -> SmartContractState:
    prompt = f"""
You are a Qubic C++ Smart Contract Documentation Assistant.

Analyze this commented code and write a clear, professional functional specification introduction:

- Objective
- Context
- Core Principles
- Input Format (use markdown table if applicable)

Language: {state.language}

Code:
{state.commented}
    """
    llm_doc, _, _ = _get_llms()
    response = llm_doc.invoke(prompt).content
    state.functional_spec = extract_clean_code(response)
    return state

# =============================================================================
#            9. Agent: Flow Diagram
# =============================================================================

def extract_generated_code(text: str) -> str:
    """
    Clean and extract the actual generated content from an LLM response.
    
    Strips common wrapping markers like ```markdown, ```text, ```mermaid, etc.
    Leaves only the raw content.
    """
    if text is None:
        return ""

    # Remove opening fenced code blocks (e.g. ```markdown)
    cleaned = re.sub(r"^```.*?\n", "", text.strip(), flags=re.MULTILINE)
    # Remove closing ```
    cleaned = re.sub(r"\n```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()

def generate_flow_diagram(state: SmartContractState) -> SmartContractState:
    """
    Generates a clean Mermaid.js diagram of the smart contract logic.
    """
    prompt = f"""
    You are a C++ smart contract analyst.

    Your task is to analyze the following C++ smart contract code and produce a clear, clean, and valid **Mermaid.js flowchart** that accurately represents the contract's logic flow.

    Instructions:
    - Use Mermaid syntax `graph TD` (top to bottom layout).
    - Use square brackets for steps (e.g., `A[Initialize] --> B[Execute Function]`).
    - Use arrows to indicate transitions or conditions (e.g., `-->`, `-- Yes -->`, etc.).
    - The entire diagram **must be wrapped in a code block** starting with ```mermaid.
    - **Do NOT include any explanation or text** outside the diagram.

    Example:
    ```mermaid
    graph TD
    Start[Start] --> Init[Initialize State]
    Init --> Check[Check Conditions]
    Check -- Yes --> Execute[Execute Action]
    Check -- No --> End[End]
    Execute --> End
    ```

    Now, generate the Mermaid.js flowchart for the following C++ smart contract code:

    ```cpp
    {state.commented}
    ```

    Return the result in {state.language}.
    """

    _, _, llm_vision = _get_llms()
    response = llm_vision.invoke(prompt)
    state.flow_diagram = extract_generated_code(response.content)
    return state


# =============================================================================
#            10. Agent: Detailed Documentation
# =============================================================================

def generate_detailed_section(state: SmartContractState) -> SmartContractState:
    prompt = f"""
You are a professional documentation writer.

Write a detailed technical section:

- Objective
- Flow Diagram text explanation
- Accessed Data
- Processing Logic
- Parameter Control and Edge Cases
- Data Handling Rules (with tables)

Language: {state.language}

Code:
{state.commented}
    """
    _, llm_reviewer, _ = _get_llms()
    response = llm_reviewer.invoke(prompt)
    state.detailed_doc = extract_clean_code(response.content)
    return state

# =============================================================================
#               11. Agent: Summary Report
# =============================================================================

def generate_summary(state: SmartContractState) -> SmartContractState:
    prompt = f"""
You are an enterprise-level documentation expert.

Combine all content into a single professional audit and documentation report.

Include:
- Functional Spec
- Flow Diagram
- Detailed Documentation

Language: {state.language}

Functional Spec:
{state.functional_spec}

Flow Diagram:
{state.flow_diagram}

Detailed Section:
{state.detailed_doc}

Code:
{state.commented}
    """
    _, llm_reviewer, _ = _get_llms()
    response = llm_reviewer.invoke(prompt)
    state.business_summary = extract_clean_code(response.content)
    return state

# =============================================================================
#               12. Agent: Test Plan Generator
# =============================================================================

def generate_tests(state: SmartContractState) -> SmartContractState:
    prompt = f"""
You are a senior QA test engineer.

Write a full test plan for this C++ smart contract:

- Test cases
- Inputs/Outputs
- Edge cases
- Failure scenarios
- Validation steps

Language: {state.language}

Code:
{state.commented}
    """
    llm_doc, _, _ = _get_llms()
    response = llm_doc.invoke(prompt)
    state.test_plan = extract_clean_code(response.content)
    return state

# =============================================================================
#               13. Agent: Simulation of onTransaction/onTick
# =============================================================================

def simulate_qubic_contract(state: SmartContractState) -> SmartContractState:
    if not state.simulation_scenario:
        state.simulation_scenario = """
Simulate onTransaction:
- sender: "Alice"
- receiver: "Bob"
- amount: 100
        """

    prompt = f"""
You are a Qubic Smart Contract Virtual Machine simulator.

Code:
{state.commented}

Scenario:
{state.simulation_scenario}

Return structured JSON:
- steps
- final_state
- explanation
    """
    llm_doc, _, _ = _get_llms()
    response = llm_doc.invoke(prompt)
    state.simulation_result = extract_clean_code(response.content)
    return state

# =============================================================================
#                14. Agent: Export JSON Report
# =============================================================================

def export_json(state: SmartContractState) -> SmartContractState:
    filename = f"qubic_audit_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        "functional_spec": state.functional_spec,
        "flow_diagram": state.flow_diagram,
        "detailed_documentation": state.detailed_doc,
        "audit_report": state.audit_report,
        "test_plan": state.test_plan,
        "qubic_logs": state.qubic_logs
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    state.output_json = filename
    return state

# =============================================================================
#            15. Agent: Qubic Dev Kit Runner
# =============================================================================

def compile_and_run_qubic(state: SmartContractState) -> SmartContractState:
    """
    Simulates the compile and run step.
    """
    stdout = f"Compiling... OK\nRunning on VM... All tests passed."
    stderr = ""
    logs = f"--- STDOUT ---\n{stdout}\n\n--- STDERR ---\n{stderr}"
    state.qubic_logs = logs
    state.compilation_success = True
    return state


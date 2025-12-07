"""
LangGraph Builder for SmartGuard Workflow
Builds the complete 8-step pipeline for C++ contract auditing.
"""
# Lazy imports - only import when actually building the graph
from app.services.smart_guard.state.state import SmartContractState


def graph_builder():
    """
    Builds and returns the compiled LangGraph for the Qubic SmartGuard workflow.
    Defines all nodes (agents) and transitions for the complete documentation and validation pipeline.
    """
    # Import LangGraph only when needed
    try:
        from langgraph.graph import StateGraph, END, START
    except ImportError as e:
        raise ImportError(f"LangGraph is not available. Install with: pip install langgraph. Error: {e}")
    
    # Import nodes only when building
    from app.services.smart_guard.nodes.qubicdocs_nodes import (
        parse_cpp,
        explain_and_comment_cpp,
        review_comments,
        check_if_valid,
        semantic_analysis,
        generate_audit,
        generate_spec_intro,
        generate_flow_diagram,
        generate_detailed_section,
        generate_summary,
        generate_tests,
        run_strict_validation,
        simulate_qubic_contract,
        compile_and_run_qubic,
        export_json
    )
    
    graph = StateGraph(SmartContractState)

    # === Define nodes (agents) ===
    graph.add_node("parse", parse_cpp)
    graph.add_node("comment", explain_and_comment_cpp)
    graph.add_node("review", review_comments)
    graph.add_node("semantic_analysis", semantic_analysis)
    graph.add_node("audit", generate_audit)
    graph.add_node("spec_intro", generate_spec_intro)
    graph.add_node("generate_flow_diagram", generate_flow_diagram)
    graph.add_node("detailed_section", generate_detailed_section)
    graph.add_node("summary", generate_summary)
    graph.add_node("test", generate_tests)
    graph.add_node("strict_validation", run_strict_validation)
    graph.add_node("simulate", simulate_qubic_contract)
    graph.add_node("compile_and_run", compile_and_run_qubic)
    graph.add_node("export", export_json)

    # === Define edges (workflow) ===
    graph.add_edge(START, "parse")
    graph.add_edge("parse", "comment")
    graph.add_edge("comment", "review")
    graph.add_conditional_edges("review", check_if_valid, {
        "Valid": "semantic_analysis",
        "Invalid": "comment"
    })
    graph.add_edge("semantic_analysis", "audit")
    graph.add_edge("audit", "spec_intro")
    graph.add_edge("spec_intro", "generate_flow_diagram")
    graph.add_edge("generate_flow_diagram", "detailed_section")
    graph.add_edge("detailed_section", "summary")
    graph.add_edge("summary", "test")
    graph.add_edge("test", "strict_validation")
    graph.add_edge("strict_validation", "simulate")
    graph.add_edge("simulate", "compile_and_run")
    graph.add_edge("compile_and_run", "export")
    graph.add_edge("export", END)

    return graph.compile()


# === Compiled graph ready for use (lazy initialization) ===
_generated_graph = None

def get_generated_graph():
    """Get or create the compiled LangGraph (lazy initialization)."""
    global _generated_graph
    if _generated_graph is None:
        _generated_graph = graph_builder()
    return _generated_graph


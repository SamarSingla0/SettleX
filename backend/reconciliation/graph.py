from decimal import Decimal
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from reconciliation.state import ReconciliationState
from reconciliation.nodes import load_and_match_ledgers_node, investigate_exception_node


def route_after_matching(state: ReconciliationState) -> str:
    """Conditional router: triggers AI only if deterministic matching requires investigation."""
    if state.get("needs_ai", False):
        return "investigate_exception"
    return END


def create_reconciliation_graph():
    """Builds and compiles the LangGraph reconciliation workflow."""
    workflow = StateGraph(ReconciliationState)

    workflow.add_node("load_and_match", load_and_match_ledgers_node)
    workflow.add_node("investigate_exception", investigate_exception_node)

    workflow.add_edge(START, "load_and_match")
    workflow.add_conditional_edges(
        "load_and_match",
        route_after_matching,
        {
            "investigate_exception": "investigate_exception",
            END: END,
        },
    )
    workflow.add_edge("investigate_exception", END)

    return workflow.compile()


# Global compiled graph instance
reconciliation_agent_graph = create_reconciliation_graph()
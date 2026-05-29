from time import perf_counter
from typing import Any, Callable, Dict

from healthcare_ai_platform.observability.metrics import (
    GUARDRAIL_FAILURES_TOTAL,
    HUMAN_REVIEW_REQUIRED_TOTAL,
    LLM_LATENCY_MS,
    RAG_RETRIEVAL_LATENCY_MS,
    RISK_MODEL_LATENCY_MS,
    UNSUPPORTED_CLAIMS_TOTAL,
    metrics,
)
from healthcare_ai_platform.observability.tracing import tracer
from healthcare_ai_platform.workflows import nodes

NODE_SEQUENCE = [
    nodes.validate_request_node,
    nodes.rbac_node,
    nodes.patient_context_node,
    nodes.clinical_nlp_node,
    nodes.retrieval_node,
    nodes.risk_model_node,
    nodes.generation_node,
    nodes.grounding_validation_node,
    nodes.guardrail_node,
    nodes.human_review_node,
    nodes.final_response_node,
]


def _record_node_metrics(name: str, elapsed_ms: float, state: Dict[str, Any]) -> None:
    if name == "retrieval_node":
        metrics.set_gauge(RAG_RETRIEVAL_LATENCY_MS, elapsed_ms)
    elif name == "risk_model_node":
        metrics.set_gauge(RISK_MODEL_LATENCY_MS, elapsed_ms)
    elif name == "generation_node":
        metrics.set_gauge(LLM_LATENCY_MS, elapsed_ms)
    elif name == "guardrail_node" and state.get("governance_flags"):
        metrics.increment(GUARDRAIL_FAILURES_TOTAL, len(state.get("governance_flags", [])))
    elif name == "grounding_validation_node":
        unsupported = [flag for flag in state.get("governance_flags", []) if "unsupported" in flag]
        if unsupported:
            metrics.increment(UNSUPPORTED_CLAIMS_TOTAL, len(unsupported))
    elif name == "human_review_node" and state.get("human_review_required"):
        metrics.increment(HUMAN_REVIEW_REQUIRED_TOTAL)


def _instrument(node: Callable[[Dict[str, Any]], Dict[str, Any]]):
    def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        name = node.__name__
        start = perf_counter()
        tracer.start_span(name)
        try:
            result = node(state)
            tracer.log_event("workflow.node.executed", {"workflow.node.name": name, "audit_id": result.get("audit_id")})
            return result
        finally:
            elapsed_ms = (perf_counter() - start) * 1000
            tracer.end_span(name)
            _record_node_metrics(name, elapsed_ms, locals().get("result", state))

    wrapped.__name__ = node.__name__
    return wrapped


INSTRUMENTED_SEQUENCE = [_instrument(node) for node in NODE_SEQUENCE]


class ClinicalDecisionGraph:
    def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        state = {"request": request}
        for node in INSTRUMENTED_SEQUENCE:
            state = node(state)
            if node.__name__ == "rbac_node" and state.get("access_denied"):
                state = _instrument(nodes.final_response_node)(state)
                break
        return state


class LangGraphClinicalDecisionGraph:
    def __init__(self, compiled_graph):
        self.compiled_graph = compiled_graph

    def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self.compiled_graph.invoke({"request": request})


def build_clinical_decision_graph() -> ClinicalDecisionGraph:
    try:
        from langgraph.graph import StateGraph, END
        from healthcare_ai_platform.workflows.state import ClinicalDecisionState

        graph = StateGraph(ClinicalDecisionState)
        for node in NODE_SEQUENCE:
            graph.add_node(node.__name__.replace("_node", ""), _instrument(node))

        graph.set_entry_point("validate_request")
        graph.add_edge("validate_request", "rbac")
        graph.add_conditional_edges(
            "rbac",
            lambda state: "final_response" if state.get("access_denied") else "patient_context",
            {"final_response": "final_response", "patient_context": "patient_context"},
        )
        graph.add_edge("patient_context", "clinical_nlp")
        graph.add_edge("clinical_nlp", "retrieval")
        graph.add_edge("retrieval", "risk_model")
        graph.add_edge("risk_model", "generation")
        graph.add_edge("generation", "grounding_validation")
        graph.add_edge("grounding_validation", "guardrail")
        graph.add_edge("guardrail", "human_review")
        graph.add_edge("human_review", "final_response")
        graph.add_edge("final_response", END)
        return LangGraphClinicalDecisionGraph(graph.compile())
    except Exception:
        pass
    return ClinicalDecisionGraph()

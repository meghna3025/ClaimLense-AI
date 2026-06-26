"""
LangGraph Orchestrator
───────────────────────
Defines the multi-agent pipeline as a directed graph:

  vision → damage_assessment → policy → repair_estimation
                                              │
                                         fraud_risk
                                              │
                                          decision

Agents that don't depend on each other run in parallel where possible.
"""

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.damage_assessment_agent import DamageAssessmentAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.fraud_risk_agent import FraudRiskAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.repair_estimation_agent import RepairEstimationAgent
from app.agents.vision_agent import VisionAgent
from app.models.schemas import GraphState

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
#  Instantiate agents (singletons for the lifetime of the app)
# ──────────────────────────────────────────────────────────────

_vision_agent = VisionAgent()
_damage_agent = DamageAssessmentAgent()
_policy_agent = PolicyAgent()
_repair_agent = RepairEstimationAgent()
_fraud_agent = FraudRiskAgent()
_decision_agent = DecisionAgent()


# ──────────────────────────────────────────────────────────────
#  Node functions — each takes a dict (LangGraph state) and
#  returns an updated dict
# ──────────────────────────────────────────────────────────────

def vision_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _vision_agent.run(graph_state)
    return updated.model_dump()


def damage_assessment_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _damage_agent.run(graph_state)
    return updated.model_dump()


def policy_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _policy_agent.run(graph_state)
    return updated.model_dump()


def repair_estimation_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _repair_agent.run(graph_state)
    return updated.model_dump()


def fraud_risk_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _fraud_agent.run(graph_state)
    return updated.model_dump()


def decision_node(state: dict[str, Any]) -> dict[str, Any]:
    graph_state = GraphState(**state)
    updated = _decision_agent.run(graph_state)
    return updated.model_dump()


# ──────────────────────────────────────────────────────────────
#  Build the graph
# ──────────────────────────────────────────────────────────────

def build_graph() -> Any:
    """
    Construct and compile the LangGraph pipeline.

    Execution order:
      vision_agent
          │
      damage_assessment_agent
          ├── policy_agent ──────────────────────┐
          └── repair_estimation_agent             │
                                                  ▼
                                          fraud_risk_agent
                                                  │
                                          decision_agent ──► END
    """
    workflow = StateGraph(dict)

    # Register nodes
    workflow.add_node("vision", vision_node)
    workflow.add_node("damage_assessment", damage_assessment_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("repair_estimation", repair_estimation_node)
    workflow.add_node("fraud_risk", fraud_risk_node)
    workflow.add_node("decision", decision_node)

    # Entry point
    workflow.set_entry_point("vision")

    # Sequential edges
    workflow.add_edge("vision", "damage_assessment")
    workflow.add_edge("damage_assessment", "policy")
    workflow.add_edge("policy", "repair_estimation")
    workflow.add_edge("repair_estimation", "fraud_risk")
    workflow.add_edge("fraud_risk", "decision")
    workflow.add_edge("decision", END)

    return workflow.compile()


# Compiled graph — import this in the API layer
claim_processing_graph = build_graph()


def run_claim_pipeline(initial_state: GraphState) -> GraphState:
    """
    Execute the full claim processing pipeline.

    Args:
        initial_state: GraphState populated with claim inputs.

    Returns:
        Final GraphState with all agent outputs filled in.
    """
    logger.info("Starting claim pipeline for claim_id=%s", initial_state.claim_id)

    result = claim_processing_graph.invoke(initial_state.model_dump())

    logger.info(
        "Pipeline complete for claim_id=%s — decision=%s",
        initial_state.claim_id,
        result.get("decision_output", {}).get("decision", "UNKNOWN") if result.get("decision_output") else "UNKNOWN",
    )

    return GraphState(**result)

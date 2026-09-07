"""
LangGraph Workflow Assembly & Pipeline Executor
Compiles the inspection state graph connecting vision, rules, RAG, trade-off, and verdict.
"""
from typing import Dict, Any
from backend.pipeline.state import InspectionGraphState
from backend.pipeline.nodes import (
    vision_node,
    rules_node,
    rag_node,
    tradeoff_node,
    verdict_node,
    capa_node
)

class InspectionPipeline:
    """
    Executes the pharmaceutical quality verification workflow graph.
    """
    def run(self, initial_state: InspectionGraphState) -> InspectionGraphState:
        state = dict(initial_state)

        # Step 1: Computer Vision & OCR Node
        v_out = vision_node(state)
        state.update(v_out)

        # Step 2: Deterministic GDP Rules Engine Node
        r_out = rules_node(state)
        state.update(r_out)

        # Step 3: RAG SOP Guidance Node
        rag_out = rag_node(state)
        state.update(rag_out)

        # Step 4: Multi-Objective Trade-Off Optimizer Node
        t_out = tradeoff_node(state)
        state.update(t_out)

        # Step 5: Verdict & HITL Routing Node
        verd_out = verdict_node(state)
        state.update(verd_out)

        # Step 6: CAPA Recommendation Generator Node
        capa_out = capa_node(state)
        state.update(capa_out)

        return state

pipeline_executor = InspectionPipeline()

import pytest
import os
from backend.models.procurement_models import ProcurementState, ProcurementRequest
from backend.workflows.procurement_workflow import build_procurement_graph

def test_full_workflow():
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No API keys found in environment, skipping LLM test.")
        
    app = build_procurement_graph()
    
    initial_state = ProcurementState(
        request=ProcurementRequest(
            request_id="REQ-TEST",
            description="We need 50 laptops under 40 lakh rupees. Must be 16GB RAM, minimum 3 years warranty, delivery within 14 days. We prefer onsite support.",
            requested_by="Alice",
            department="IT"
        )
    )
    
    # Run the graph
    result = app.invoke({"state_obj": initial_state})
    
    final_state = result["state_obj"]
    
    # Verify the state passed through all nodes
    assert final_state.requirements is not None
    assert len(final_state.vendor_quotes) > 0
    assert len(final_state.price_analysis) > 0
    assert len(final_state.budget_analysis) > 0
    assert len(final_state.compliance_analysis) > 0
    assert len(final_state.deal_evaluation) > 0
    assert len(final_state.negotiation_status) > 0
    assert len(final_state.approval_status) > 0

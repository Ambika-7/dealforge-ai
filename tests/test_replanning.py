import pytest
import os
from backend.models.procurement_models import ProcurementState, ProcurementRequest, Requirement
from backend.workflows.replanning_workflow import Replanner

def test_budget_replanning():
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No API keys found in environment, skipping LLM test.")
        
    state = ProcurementState(
        requirements=Requirement(
            product="laptop",
            quantity=50,
            budget=4000000
        ),
        vendor_quotes=[
            {
                "vendor_id": "V001",
                "product_name": "laptop",
                "unit_price": 84000.0,
                "quantity": 50,
                "warranty_years": 3,
                "delivery_days": 10,
                "support_type": "onsite",
                "payment_terms_days": 15,
                "discount_percentage": 0.0,
                "availability": True
            }
        ],
        price_analysis={
            "V001": {
                "total_cost": 4620000.0, # (84k * 50) + 10% tax
                "payment_terms_score": 3
            }
        },
        budget_analysis={
            "V001": {
                "within_budget": False,
                "exceeded_amount": 620000.0
            }
        },
        compliance_analysis={
            "V001": {
                "is_compliant": True,
                "violated_rules": [],
                "warnings": []
            }
        },
        deal_evaluation={
            "V001": {
                "total_score": 75.0,
                "strengths": [],
                "weaknesses": [],
                "risks": [],
                "recommendation_rationale": ""
            }
        }
    )
    
    replanner = Replanner()
    
    # 1. Change budget to 5,000,000 (enough to cover the 4.62M cost)
    updated_state = replanner.handle_budget_change(state, 5000000)
    
    assert updated_state.requirements.budget == 5000000
    
    b_analysis = updated_state.budget_analysis["V001"]
    assert b_analysis["within_budget"] is True
    assert b_analysis["exceeded_amount"] == 0.0
    
    # Check that it triggered downstream evaluation and negotiation
    assert "V001" in updated_state.deal_evaluation
    assert "V001" in updated_state.negotiation_status
    assert "V001" in updated_state.approval_status

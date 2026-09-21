import pytest
import os
from backend.models.procurement_models import ProcurementState, ProcurementRequest, Requirement
from backend.agents.requirement_agent import RequirementAgent
from backend.agents.vendor_research_agent import VendorResearchAgent
from backend.agents.price_analysis_agent import PriceAnalysisAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.deal_evaluation_agent import DealEvaluationAgent
from backend.agents.negotiation_agent import NegotiationAgent
from backend.agents.approval_agent import ApprovalAgent

def test_requirement_agent():
    # Make sure we have an API key set for testing, otherwise skip
    # (Since this tests an LLM call, it requires a valid API key)
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No API keys found in environment, skipping LLM test.")
        
    agent = RequirementAgent()
    
    # Mock state
    state = ProcurementState(
        request=ProcurementRequest(
            request_id="REQ-001",
            description="We need 50 laptops under 40 lakh rupees for new employees. They should have at least 16GB RAM, 512GB SSD. We need 3 years warranty and delivery within 14 days. Onsite support is required. Preferred payment is 30 days.",
            requested_by="Alice",
            department="IT"
        )
    )
    
    # Process
    updated_state = agent.process_request(state)
    
    # Verify outputs
    reqs = updated_state.requirements
    assert reqs is not None
    assert reqs.product.lower() in ["laptop", "laptops"]
    assert reqs.quantity == 50
    assert reqs.budget == 4000000
    assert "16" in reqs.minimum_ram
    assert "512" in reqs.minimum_storage
    assert reqs.minimum_warranty_years == 3
    assert reqs.maximum_delivery_days == 14
    assert reqs.support_requirement.lower() == "onsite"
    assert "30" in reqs.payment_preference

def test_vendor_research_agent():
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No API keys found in environment, skipping LLM test.")
        
    agent = VendorResearchAgent()
    
    # Mock state with requirement already filled
    state = ProcurementState(
        requirements=Requirement(
            product="laptop",
            quantity=50,
            budget=4000000
        )
    )
    
    updated_state = agent.process_request(state)
    
    assert len(updated_state.vendors_found) > 0
    assert len(updated_state.vendor_quotes) > 0
    
    # Ensure quotes are structured properly
    first_quote = updated_state.vendor_quotes[0]
    assert "vendor_id" in first_quote
    assert first_quote["quantity"] == 50
    assert "unit_price" in first_quote

def test_price_and_budget_agents():
    # We can test these without an LLM!
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
                "discount_percentage": 10.0,
                "availability": True
            }
        ]
    )
    
    # Run Price Agent
    price_agent = PriceAnalysisAgent()
    state = price_agent.process_request(state)
    
    assert "V001" in state.price_analysis
    p_analysis = state.price_analysis["V001"]
    
    base_cost = 84000 * 50 # 42,00,000
    discount = base_cost * 0.10 # 4,20,000
    expected_before_tax = base_cost - discount # 37,80,000
    taxes = expected_before_tax * 0.10 # 3,78,000
    expected_total = expected_before_tax + taxes # 41,58,000
    
    assert p_analysis["total_cost"] == expected_total
    
    # Run Budget Agent
    budget_agent = BudgetAgent()
    state = budget_agent.process_request(state)
    
    assert "V001" in state.budget_analysis
    b_analysis = state.budget_analysis["V001"]
    
    # Budget was 4,000,000, cost is 4,158,000. Over budget by 158,000.
    assert b_analysis["within_budget"] is False
    assert b_analysis["exceeded_amount"] == 158000

def test_compliance_agent():
    state = ProcurementState(
        requirements=Requirement(
            product="laptop",
            quantity=50,
            budget=4000000,
            minimum_warranty_years=3,
            maximum_delivery_days=14,
            support_requirement="onsite"
        ),
        vendors_found=[
            {
                "vendor_id": "V001",
                "name": "TechPro",
                "certifications": ["Authorized Reseller"]
            },
            {
                "vendor_id": "V002",
                "name": "BadVendor",
                "certifications": []
            }
        ],
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
            },
            {
                "vendor_id": "V002",
                "product_name": "laptop",
                "unit_price": 60000.0,
                "quantity": 50,
                "warranty_years": 1, # Fails requirement
                "delivery_days": 20, # Fails requirement
                "support_type": "remote", # Fails requirement
                "payment_terms_days": 30,
                "discount_percentage": 0.0,
                "availability": True
            }
        ]
    )
    
    agent = ComplianceAgent()
    state = agent.process_request(state)
    
    assert "V001" in state.compliance_analysis
    assert "V002" in state.compliance_analysis
    
    c_good = state.compliance_analysis["V001"]
    assert c_good["is_compliant"] is True
    assert len(c_good["violated_rules"]) == 0
    
    c_bad = state.compliance_analysis["V002"]
    assert c_bad["is_compliant"] is False
    assert len(c_bad["violated_rules"]) == 3 # Warranty, Delivery, Support

def test_deal_evaluation_agent():
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No API keys found in environment, skipping LLM test.")
        
    state = ProcurementState(
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
                "discount_percentage": 5.0,
                "availability": True
            }
        ],
        price_analysis={
            "V001": {
                "payment_terms_score": 3
            }
        },
        budget_analysis={
            "V001": {
                "within_budget": True,
                "exceeded_amount": 0.0
            }
        },
        compliance_analysis={
            "V001": {
                "is_compliant": True,
                "violated_rules": [],
                "warnings": []
            }
        }
    )
    
    agent = DealEvaluationAgent()
    state = agent.process_request(state)
    
    assert "V001" in state.deal_evaluation
    eval_data = state.deal_evaluation["V001"]
    
    # Check quantitative
    assert eval_data["total_score"] > 0
    assert eval_data["budget_score"] == 10.0
    
    # Check qualitative from LLM
    assert len(eval_data["strengths"]) > 0
    assert eval_data["recommendation_rationale"] != ""

def test_negotiation_agent():
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
                "vendor_id": "V002",
                "product_name": "laptop",
                "unit_price": 85000.0,
                "quantity": 50,
                "warranty_years": 2,
                "delivery_days": 10,
                "support_type": "remote",
                "payment_terms_days": 15,
                "discount_percentage": 0.0,
                "availability": True
            }
        ],
        deal_evaluation={
            "V002": {
                "total_score": 55.0,
                "price_score": 5.0,
                "budget_score": 0.0,
                "warranty_score": 5.0,
                "delivery_score": 8.0,
                "support_score": 5.0,
                "compliance_score": 0.0,
                "strengths": ["Fast delivery"],
                "weaknesses": ["Exceeds budget by 2.5 lakh", "Only 2 years warranty"],
                "risks": ["Non-compliant warranty"],
                "recommendation_rationale": "Over budget and weak warranty. Needs negotiation.",
                "vendor_id": "V002"
            }
        }
    )
    
    agent = NegotiationAgent()
    state = agent.process_request(state, "V002")
    
    assert "V002" in state.negotiation_status
    neg_data = state.negotiation_status["V002"]
    
    assert neg_data["target_price"] > 0
    assert len(neg_data["requested_improvements"]) > 0
    assert "dear" in neg_data["negotiation_email"].lower() or "hello" in neg_data["negotiation_email"].lower()

def test_approval_agent():
    state = ProcurementState(
        request=ProcurementRequest(
            request_id="REQ-001",
            description="Laptops",
            requested_by="Alice",
            department="IT"
        ),
        requirements=Requirement(
            product="laptop",
            quantity=50,
            budget=4000000
        ),
        price_analysis={
            "V001": {
                "total_cost": 4200000.0  # Over manager threshold (1M) and budget (4M)
            }
        },
        budget_analysis={
            "V001": {
                "within_budget": False,
                "exceeded_amount": 200000.0
            }
        },
        compliance_analysis={
            "V001": {
                "is_compliant": False,
                "violated_rules": ["Missing warranty"]
            }
        }
    )
    
    agent = ApprovalAgent()
    state = agent.process_request(state, "V001")
    
    assert "V001" in state.approval_status
    status = state.approval_status["V001"]
    
    assert status["approval_required"] is True
    details = status["request_details"]
    assert details["risk_level"] == "High"
    assert "warranty" in details["reason_for_approval"].lower()
    assert details["approval_level_required"] == "Director"

import pytest
import os
from backend.models.procurement_models import ProcurementState, ProcurementRequest, Requirement
from backend.agents.requirement_agent import RequirementAgent
from backend.agents.vendor_research_agent import VendorResearchAgent
from backend.agents.price_analysis_agent import PriceAnalysisAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.compliance_agent import ComplianceAgent

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

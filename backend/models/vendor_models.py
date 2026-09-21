from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Vendor(BaseModel):
    vendor_id: str
    name: str
    rating: float
    certifications: List[str]
    products_offered: List[str]

class VendorQuote(BaseModel):
    vendor_id: str
    product_name: str
    unit_price: float
    quantity: int
    warranty_years: int
    delivery_days: int
    support_type: str
    payment_terms_days: int
    discount_percentage: float = 0.0
    availability: bool = True

class PriceAnalysis(BaseModel):
    vendor_id: str
    base_cost: float
    discount_amount: float
    taxes: float
    shipping_cost: float
    total_cost: float
    unit_cost_after_discount: float
    payment_terms_score: int

class BudgetAnalysis(BaseModel):
    vendor_id: str
    total_cost: float
    within_budget: bool
    remaining_budget: float
    budget_utilization_percentage: float
    exceeded_amount: float = 0.0

class ComplianceResult(BaseModel):
    vendor_id: str
    is_compliant: bool
    violated_rules: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class DealEvaluation(BaseModel):
    vendor_id: str
    total_score: float
    price_score: float
    budget_score: float
    warranty_score: float
    delivery_score: float
    support_score: float
    compliance_score: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendation_rationale: str

class NegotiationStrategy(BaseModel):
    vendor_id: str
    target_price: float
    requested_improvements: List[str]
    negotiation_email: str
    strategy_rationale: str

class NegotiationRound(BaseModel):
    round_number: int
    company_message: str
    vendor_response: str
    vendor_updated_quote: Optional[VendorQuote] = None
    accepted: bool

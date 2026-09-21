from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProcurementRequest(BaseModel):
    request_id: str
    description: str
    requested_by: str
    department: str

class Requirement(BaseModel):
    product: str
    quantity: int
    budget: float
    minimum_ram: Optional[str] = None
    minimum_storage: Optional[str] = None
    minimum_warranty_years: Optional[int] = None
    maximum_delivery_days: Optional[int] = None
    support_requirement: Optional[str] = None
    payment_preference: Optional[str] = None
    additional_notes: Optional[str] = None

class ProcurementState(BaseModel):
    request: Optional[ProcurementRequest] = None
    requirements: Optional[Requirement] = None
    vendors_found: List[Dict[str, Any]] = Field(default_factory=list)
    vendor_quotes: List[Dict[str, Any]] = Field(default_factory=list)
    price_analysis: Dict[str, Any] = Field(default_factory=dict)
    budget_analysis: Dict[str, Any] = Field(default_factory=dict)
    compliance_analysis: Dict[str, Any] = Field(default_factory=dict)
    deal_evaluation: Dict[str, Any] = Field(default_factory=dict)
    negotiation_status: Dict[str, Any] = Field(default_factory=dict)
    approval_status: Dict[str, Any] = Field(default_factory=dict)
    final_plan: Dict[str, Any] = Field(default_factory=dict)

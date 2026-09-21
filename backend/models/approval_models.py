from pydantic import BaseModel
from typing import Optional

class ApprovalRequest(BaseModel):
    request_id: str
    recommended_vendor_id: str
    total_cost: float
    budget: float
    risk_level: str
    reason_for_approval: str
    approval_level_required: str

class ApprovalDecision(BaseModel):
    request_id: str
    decision: str  # e.g., 'APPROVED', 'REJECTED', 'REQUEST_CHANGES'
    comments: Optional[str] = None
    approved_by: Optional[str] = None

class FinalProcurementPlan(BaseModel):
    request_id: str
    selected_vendor_id: str
    negotiated_price: float
    savings_achieved: float
    justification: str
    risks: str
    approval_status: str

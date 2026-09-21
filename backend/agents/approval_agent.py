from backend.models.procurement_models import ProcurementState
from backend.models.approval_models import ApprovalRequest
from backend.tools.approval_checker import check_approval_required

class ApprovalAgent:
    def __init__(self):
        # Deterministic rules-based agent, no LLM required
        pass
        
    def process_request(self, state: ProcurementState, target_vendor_id: str) -> ProcurementState:
        """
        Determines if human approval is needed for the target vendor deal.
        """
        if not state.price_analysis or not state.budget_analysis or not state.compliance_analysis:
            return state
            
        p_analysis = state.price_analysis.get(target_vendor_id, {})
        b_analysis = state.budget_analysis.get(target_vendor_id, {})
        c_analysis = state.compliance_analysis.get(target_vendor_id, {})
        
        total_cost = p_analysis.get("total_cost", 0.0)
        budget = state.requirements.budget if state.requirements else 0.0
        request_id = state.request.request_id if state.request else "REQ-UNKNOWN"
        
        needs_approval, reason, risk, level = check_approval_required(
            target_vendor_id, total_cost, b_analysis, c_analysis
        )
        
        # Store the required approval state
        state.approval_status[target_vendor_id] = {
            "approval_required": needs_approval,
            "request_details": ApprovalRequest(
                request_id=request_id,
                recommended_vendor_id=target_vendor_id,
                total_cost=total_cost,
                budget=budget,
                risk_level=risk,
                reason_for_approval=reason,
                approval_level_required=level
            ).model_dump() if needs_approval else None
        }
        
        return state

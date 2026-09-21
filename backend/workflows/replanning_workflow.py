from backend.models.procurement_models import ProcurementState
from backend.agents.price_analysis_agent import PriceAnalysisAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.deal_evaluation_agent import DealEvaluationAgent
from backend.agents.negotiation_agent import NegotiationAgent
from backend.agents.approval_agent import ApprovalAgent

class Replanner:
    def __init__(self):
        self.price_agent = PriceAnalysisAgent()
        self.budget_agent = BudgetAgent()
        self.compliance_agent = ComplianceAgent()
        self.eval_agent = DealEvaluationAgent()
        self.negotiation_agent = NegotiationAgent()
        self.approval_agent = ApprovalAgent()
        
    def get_best_vendor(self, state: ProcurementState) -> str:
        if not state.deal_evaluation:
            return ""
        return max(
            state.deal_evaluation.keys(),
            key=lambda vid: state.deal_evaluation[vid].get("total_score", 0)
        )

    def handle_budget_change(self, state: ProcurementState, new_budget: float) -> ProcurementState:
        """
        Only affects Budget Analysis -> Deal Evaluation -> Negotiation -> Approval
        """
        if state.requirements:
            state.requirements.budget = new_budget
            
        state = self.budget_agent.process_request(state)
        state = self.eval_agent.process_request(state)
        
        best_vendor = self.get_best_vendor(state)
        if best_vendor:
            state = self.negotiation_agent.process_request(state, best_vendor)
            state = self.approval_agent.process_request(state, best_vendor)
            
        return state
        
    def handle_quantity_change(self, state: ProcurementState, new_quantity: int) -> ProcurementState:
        """
        Affects Price Analysis -> Budget -> Compliance -> Eval -> Neg -> Approval
        """
        if state.requirements:
            state.requirements.quantity = new_quantity
            
        # Update quantity in all vendor quotes so price calculation works correctly
        for quote in state.vendor_quotes:
            quote["quantity"] = new_quantity
            
        state = self.price_agent.process_request(state)
        state = self.budget_agent.process_request(state)
        state = self.compliance_agent.process_request(state)
        state = self.eval_agent.process_request(state)
        
        best_vendor = self.get_best_vendor(state)
        if best_vendor:
            state = self.negotiation_agent.process_request(state, best_vendor)
            state = self.approval_agent.process_request(state, best_vendor)
            
        return state
        
    def handle_vendor_removal(self, state: ProcurementState, vendor_id_to_remove: str) -> ProcurementState:
        """
        Affects Deal Evaluation (to pick a new winner) -> Neg -> Approval
        """
        # Remove vendor from quotes
        state.vendor_quotes = [q for q in state.vendor_quotes if q["vendor_id"] != vendor_id_to_remove]
        
        # Remove from analysis states
        state.price_analysis.pop(vendor_id_to_remove, None)
        state.budget_analysis.pop(vendor_id_to_remove, None)
        state.compliance_analysis.pop(vendor_id_to_remove, None)
        state.deal_evaluation.pop(vendor_id_to_remove, None)
        state.negotiation_status.pop(vendor_id_to_remove, None)
        state.approval_status.pop(vendor_id_to_remove, None)
        
        # If no vendors left, abort
        if not state.vendor_quotes:
            return state
            
        # Pick the new best vendor and negotiate
        best_vendor = self.get_best_vendor(state)
        if best_vendor:
            state = self.negotiation_agent.process_request(state, best_vendor)
            state = self.approval_agent.process_request(state, best_vendor)
            
        return state

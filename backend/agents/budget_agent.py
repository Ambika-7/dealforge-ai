from backend.models.procurement_models import ProcurementState
from backend.tools.budget_checker import check_budget
from backend.models.vendor_models import BudgetAnalysis

class BudgetAgent:
    def __init__(self):
        # We use deterministic checks rather than an LLM
        pass
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        if not state.requirements or not state.price_analysis:
            return state
            
        allocated_budget = state.requirements.budget
        budget_results = {}
        
        for vendor_id, price_data in state.price_analysis.items():
            total_cost = price_data["total_cost"]
            b_data = check_budget(total_cost, allocated_budget)
            b_data["vendor_id"] = vendor_id
            
            # Validate output via Pydantic schema
            analysis = BudgetAnalysis(**b_data)
            budget_results[vendor_id] = analysis.model_dump()
            
        state.budget_analysis = budget_results
        return state

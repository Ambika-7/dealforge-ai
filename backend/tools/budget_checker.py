from typing import Dict, Any

def check_budget(total_cost: float, allocated_budget: float) -> Dict[str, Any]:
    remaining_budget = allocated_budget - total_cost
    within_budget = remaining_budget >= 0
    exceeded_amount = abs(remaining_budget) if not within_budget else 0.0
    
    budget_utilization = (total_cost / allocated_budget * 100) if allocated_budget > 0 else 100.0
    
    return {
        "total_cost": total_cost,
        "within_budget": within_budget,
        "remaining_budget": remaining_budget,
        "budget_utilization_percentage": round(budget_utilization, 2),
        "exceeded_amount": exceeded_amount
    }

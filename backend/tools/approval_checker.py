import os
import json
from typing import Dict, Any, Tuple

def load_approval_policies() -> Dict[str, Any]:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "policies.json")
    if not os.path.exists(data_path):
        return {}
    with open(data_path, "r") as f:
        policies = json.load(f)
        return policies.get("approval_policies", {})

def check_approval_required(
    vendor_id: str,
    total_cost: float,
    budget_analysis: Dict[str, Any],
    compliance_analysis: Dict[str, Any]
) -> Tuple[bool, str, str, str]:
    """
    Returns (approval_required, reason, risk_level, approval_level)
    """
    policies = load_approval_policies()
    
    reasons = []
    risk_level = "Low"
    approval_level = "None"
    
    # 1. Cost thresholds
    manager_threshold = policies.get("manager_approval_threshold", 1000000)
    director_threshold = policies.get("director_approval_threshold", 5000000)
    
    if total_cost >= director_threshold:
        reasons.append(f"Total cost ({total_cost}) exceeds director threshold ({director_threshold}).")
        risk_level = "High"
        approval_level = "Director"
    elif total_cost >= manager_threshold:
        reasons.append(f"Total cost ({total_cost}) exceeds manager threshold ({manager_threshold}).")
        if risk_level == "Low": risk_level = "Medium"
        if approval_level == "None": approval_level = "Manager"
        
    # 2. Budget violation
    if policies.get("require_approval_if_budget_exceeded", True):
        if not budget_analysis.get("within_budget", True):
            reasons.append(f"Purchase exceeds budget by {budget_analysis.get('exceeded_amount', 0)}.")
            risk_level = "High"
            if approval_level in ["None", "Manager"]: approval_level = "Director"
            
    # 3. Compliance violation
    if policies.get("require_approval_if_non_compliant", True):
        if not compliance_analysis.get("is_compliant", True):
            violations = compliance_analysis.get("violated_rules", [])
            reasons.append(f"Vendor is non-compliant. Violations: {', '.join(violations)}")
            risk_level = "High"
            if approval_level in ["None", "Manager"]: approval_level = "Director"
            
    approval_required = len(reasons) > 0
    reason_str = " | ".join(reasons) if approval_required else "No approval required. Within safe thresholds."
    
    return approval_required, reason_str, risk_level, approval_level

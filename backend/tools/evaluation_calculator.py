import os
import json
from typing import Dict, Any

def load_evaluation_weights() -> Dict[str, float]:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "policies.json")
    if not os.path.exists(data_path):
        return {}
    with open(data_path, "r") as f:
        policies = json.load(f)
        return policies.get("evaluation_weights", {
            "price": 30,
            "budget_fit": 20,
            "warranty": 15,
            "delivery": 15,
            "support": 10,
            "payment_terms": 5,
            "compliance": 5
        })

def calculate_deal_score(
    quote: Dict[str, Any], 
    price_analysis: Dict[str, Any], 
    budget_analysis: Dict[str, Any], 
    compliance_analysis: Dict[str, Any]
) -> Dict[str, float]:
    
    weights = load_evaluation_weights()
    
    # 1. Price
    discount = quote.get("discount_percentage", 0)
    price_score = min(10.0, 5.0 + (discount / 3.0))
    
    # 2. Budget Fit
    budget_score = 10.0 if budget_analysis.get("within_budget", False) else max(0.0, 10.0 - (budget_analysis.get("exceeded_amount", 0) / 100000))
    
    # 3. Warranty
    w_years = quote.get("warranty_years", 0)
    warranty_score = min(10.0, w_years * 2.5)
    
    # 4. Delivery
    d_days = quote.get("delivery_days", 999)
    delivery_score = max(0.0, min(10.0, 12.0 - (d_days / 3.0)))
    
    # 5. Support
    support = quote.get("support_type", "").lower()
    support_score = 10.0 if support == "onsite" else (5.0 if support == "remote" else 0.0)
    
    # 6. Payment terms
    payment_score = float(price_analysis.get("payment_terms_score", 0))
    
    # 7. Compliance
    compliance_score = 10.0 if compliance_analysis.get("is_compliant", False) else 0.0
    
    # Calculate weighted total (Scale roughly to 100)
    total_score = (
        (price_score * (weights.get("price", 30) / 100.0)) +
        (budget_score * (weights.get("budget_fit", 20) / 100.0)) +
        (warranty_score * (weights.get("warranty", 15) / 100.0)) +
        (delivery_score * (weights.get("delivery", 15) / 100.0)) +
        (support_score * (weights.get("support", 10) / 100.0)) +
        (payment_score * (weights.get("payment_terms", 5) / 100.0)) +
        (compliance_score * (weights.get("compliance", 5) / 100.0))
    ) * 10 
    
    return {
        "total_score": round(total_score, 2),
        "price_score": round(price_score, 2),
        "budget_score": round(budget_score, 2),
        "warranty_score": round(warranty_score, 2),
        "delivery_score": round(delivery_score, 2),
        "support_score": round(support_score, 2),
        "compliance_score": round(compliance_score, 2)
    }

import os
import json
from typing import Dict, Any, List

def load_policies() -> Dict[str, Any]:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "policies.json")
    if not os.path.exists(data_path):
        return {}
    with open(data_path, "r") as f:
        return json.load(f)

def check_compliance(vendor: Dict[str, Any], quote: Dict[str, Any], requirement: Dict[str, Any]) -> Dict[str, Any]:
    policies = load_policies().get("compliance_rules", {})
    
    violated_rules = []
    warnings = []
    
    # Check Warranty
    req_warranty = requirement.get("minimum_warranty_years")
    pol_warranty = policies.get("minimum_warranty_years", 0)
    target_warranty = max(req_warranty or 0, pol_warranty)
    
    if quote.get("warranty_years", 0) < target_warranty:
        violated_rules.append(f"Warranty {quote.get('warranty_years')} years is less than required {target_warranty} years.")
        
    # Check Delivery
    req_delivery = requirement.get("maximum_delivery_days")
    pol_delivery = policies.get("maximum_delivery_days", 999)
    target_delivery = min(req_delivery if req_delivery is not None else 999, pol_delivery)
    
    if quote.get("delivery_days", 999) > target_delivery:
        violated_rules.append(f"Delivery of {quote.get('delivery_days')} days exceeds maximum {target_delivery} days.")
        
    # Check Support
    req_support = requirement.get("support_requirement")
    if req_support and req_support.lower() != quote.get("support_type", "").lower():
        violated_rules.append(f"Vendor offers {quote.get('support_type')} support, but {req_support} is required.")
        
    # Check Certifications (From vendor data vs policies)
    vendor_certs = [c.lower() for c in vendor.get("certifications", [])]
    mandated_certs = [c.lower() for c in policies.get("mandatory_certifications", [])]
    
    for cert in mandated_certs:
        if cert not in vendor_certs:
            warnings.append(f"Vendor missing recommended certification: {cert.title()}")
            
    is_compliant = len(violated_rules) == 0
    
    return {
        "vendor_id": quote["vendor_id"],
        "is_compliant": is_compliant,
        "violated_rules": violated_rules,
        "warnings": warnings
    }

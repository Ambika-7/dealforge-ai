from backend.models.procurement_models import ProcurementState
from backend.tools.compliance_checker import check_compliance
from backend.models.vendor_models import ComplianceResult

class ComplianceAgent:
    def __init__(self):
        # Deterministic logic, no LLM required
        pass
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        if not state.requirements or not state.vendor_quotes:
            return state
            
        compliance_results = {}
        
        # We need the original vendor data for certifications. 
        # Create a lookup dictionary.
        vendors_lookup = {v["vendor_id"]: v for v in state.vendors_found}
        
        req_dict = state.requirements.model_dump()
        
        for quote in state.vendor_quotes:
            vendor_id = quote["vendor_id"]
            vendor_info = vendors_lookup.get(vendor_id, {})
            
            c_data = check_compliance(vendor_info, quote, req_dict)
            
            analysis = ComplianceResult(**c_data)
            compliance_results[vendor_id] = analysis.model_dump()
            
        state.compliance_analysis = compliance_results
        return state

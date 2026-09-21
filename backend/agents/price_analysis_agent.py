from backend.models.procurement_models import ProcurementState
from backend.tools.price_calculator import calculate_vendor_price
from backend.models.vendor_models import PriceAnalysis

class PriceAnalysisAgent:
    def __init__(self):
        # We do not need an LLM for deterministic math operations
        pass
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        if not state.vendor_quotes:
            return state
            
        analysis_results = {}
        for quote in state.vendor_quotes:
            price_data = calculate_vendor_price(quote)
            
            # Validate output via Pydantic schema
            analysis = PriceAnalysis(**price_data)
            analysis_results[quote["vendor_id"]] = analysis.model_dump()
            
        state.price_analysis = analysis_results
        return state

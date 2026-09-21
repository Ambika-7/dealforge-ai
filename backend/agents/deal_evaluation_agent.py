import os
import json
from langchain_core.prompts import ChatPromptTemplate
from backend.agents.requirement_agent import get_llm
from backend.models.procurement_models import ProcurementState
from backend.models.vendor_models import DealEvaluation
from backend.tools.evaluation_calculator import calculate_deal_score

class DealEvaluationAgent:
    def __init__(self):
        self.llm = get_llm()
        
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "evaluation_prompt.txt")
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
            
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Vendor ID: {vendor_id}\nQuote: {quote}\nScores: {scores}\nCompliance: {compliance}")
        ])
        
        # We use structured output directly mapping to DealEvaluation model
        self.chain = self.prompt | self.llm.with_structured_output(DealEvaluation)
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        if not state.vendor_quotes or not state.price_analysis or not state.budget_analysis or not state.compliance_analysis:
            return state
            
        evaluation_results = {}
        
        for quote in state.vendor_quotes:
            vendor_id = quote["vendor_id"]
            
            p_analysis = state.price_analysis.get(vendor_id, {})
            b_analysis = state.budget_analysis.get(vendor_id, {})
            c_analysis = state.compliance_analysis.get(vendor_id, {})
            
            # 1. Calculate quantitative scores
            scores = calculate_deal_score(quote, p_analysis, b_analysis, c_analysis)
            
            # 2. Use LLM for qualitative reasoning
            try:
                eval_result = self.chain.invoke({
                    "vendor_id": vendor_id,
                    "quote": json.dumps(quote),
                    "scores": json.dumps(scores),
                    "compliance": json.dumps(c_analysis)
                })
                
                # Merge quantitative scores into the LLM's response
                eval_dict = eval_result.model_dump()
                eval_dict.update(scores)
                eval_dict["vendor_id"] = vendor_id
                
                evaluation_results[vendor_id] = eval_dict
            except Exception as e:
                print(f"Error evaluating vendor {vendor_id}: {e}")
                
        state.deal_evaluation = evaluation_results
        return state

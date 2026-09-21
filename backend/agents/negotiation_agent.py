import os
import json
from langchain_core.prompts import ChatPromptTemplate
from backend.agents.requirement_agent import get_llm
from backend.models.procurement_models import ProcurementState
from backend.models.vendor_models import NegotiationStrategy

class NegotiationAgent:
    def __init__(self):
        self.llm = get_llm()
        
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "negotiation_prompt.txt")
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
            
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Vendor ID: {vendor_id}\nQuote: {quote}\nBudget: {budget}\nEvaluation: {evaluation}")
        ])
        
        self.chain = self.prompt | self.llm.with_structured_output(NegotiationStrategy)
        
    def process_request(self, state: ProcurementState, target_vendor_id: str) -> ProcurementState:
        """
        Generates a negotiation strategy for a specific target vendor.
        """
        if not state.deal_evaluation or target_vendor_id not in state.deal_evaluation:
            return state
            
        quote = next((q for q in state.vendor_quotes if q["vendor_id"] == target_vendor_id), None)
        if not quote:
            return state
            
        evaluation = state.deal_evaluation[target_vendor_id]
        budget = state.requirements.budget if state.requirements else 0
        
        try:
            result = self.chain.invoke({
                "vendor_id": target_vendor_id,
                "quote": json.dumps(quote),
                "budget": budget,
                "evaluation": json.dumps(evaluation)
            })
            
            # Store it in negotiation_status
            state.negotiation_status[target_vendor_id] = result.model_dump()
        except Exception as e:
            print(f"Error negotiating with {target_vendor_id}: {e}")
            
        return state

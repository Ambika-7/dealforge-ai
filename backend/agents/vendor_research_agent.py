import os
import json
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from backend.agents.requirement_agent import get_llm
from backend.models.procurement_models import ProcurementState
from backend.models.vendor_models import VendorQuote
from backend.tools.vendor_search import search_vendors

class VendorQuotesList(BaseModel):
    quotes: List[VendorQuote]

class VendorResearchAgent:
    def __init__(self):
        self.llm = get_llm()
        
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "vendor_prompt.txt")
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
            
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Requirement: {requirement}\n\nRaw Vendor Data: {vendor_data}")
        ])
        
        self.chain = self.prompt | self.llm.with_structured_output(VendorQuotesList)
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        if not state.requirements or not state.requirements.product:
            raise ValueError("State must contain validated requirements with a product name.")
            
        # 1. Use Tool to search vendors
        raw_vendors = search_vendors(state.requirements.product)
        state.vendors_found = raw_vendors  # Store raw for record
        
        # 2. If no vendors found, return empty
        if not raw_vendors:
            state.vendor_quotes = []
            return state
            
        # 3. Use LLM to parse raw data into normalized VendorQuote objects
        requirement_str = state.requirements.model_dump_json()
        vendor_data_str = json.dumps(raw_vendors, indent=2)
        
        result = self.chain.invoke({
            "requirement": requirement_str,
            "vendor_data": vendor_data_str
        })
        
        # 4. Update state with proper dictionaries
        state.vendor_quotes = [quote.model_dump() for quote in result.quotes]
        
        return state

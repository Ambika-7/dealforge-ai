import os
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.models.procurement_models import Requirement, ProcurementState
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model_name = os.getenv("LLM_MODEL", "")
    
    if provider == "gemini":
        actual_model = model_name if model_name and "gemini" in model_name.lower() else "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(model=actual_model, temperature=0)
    else:
        # Default to OpenAI
        actual_model = model_name if model_name else "gpt-4o-mini"
        return ChatOpenAI(model=actual_model, temperature=0)

class RequirementAgent:
    def __init__(self):
        self.llm = get_llm()
        
        # Load the prompt from file
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "requirement_prompt.txt")
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
            
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Request: {user_request}")
        ])
        
        # We use structured output to enforce the Requirement Pydantic model
        self.chain = self.prompt | self.llm.with_structured_output(Requirement)
        
    def process_request(self, state: ProcurementState) -> ProcurementState:
        """
        Takes the current ProcurementState (which should have a request),
        extracts the requirements, and updates the state.
        """
        if not state.request or not state.request.description:
            raise ValueError("ProcurementState must contain a valid request description.")
            
        # Invoke the chain to extract requirements
        extracted_requirement = self.chain.invoke({
            "user_request": state.request.description
        })
        
        # Update the state with the extracted requirements
        state.requirements = extracted_requirement
        
        return state

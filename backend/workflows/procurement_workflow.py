from langgraph.graph import StateGraph, END
from typing import TypedDict

from backend.models.procurement_models import ProcurementState
from backend.agents.requirement_agent import RequirementAgent
from backend.agents.vendor_research_agent import VendorResearchAgent
from backend.agents.price_analysis_agent import PriceAnalysisAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.deal_evaluation_agent import DealEvaluationAgent
from backend.agents.negotiation_agent import NegotiationAgent
from backend.agents.approval_agent import ApprovalAgent

class GraphState(TypedDict):
    state_obj: ProcurementState

def build_procurement_graph():
    workflow = StateGraph(GraphState)
    
    # Initialize agents
    req_agent = RequirementAgent()
    vendor_agent = VendorResearchAgent()
    price_agent = PriceAnalysisAgent()
    budget_agent = BudgetAgent()
    compliance_agent = ComplianceAgent()
    eval_agent = DealEvaluationAgent()
    negotiation_agent = NegotiationAgent()
    approval_agent = ApprovalAgent()

    # Define Node Wrappers
    def extract_requirements(data: GraphState):
        new_state = req_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    def research_vendors(data: GraphState):
        new_state = vendor_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    # We execute these sequentially in the graph to ensure state safety,
    # though conceptually they represent the "parallel" analysis phase.
    def analyze_price(data: GraphState):
        new_state = price_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    def check_budget(data: GraphState):
        new_state = budget_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    def check_compliance(data: GraphState):
        new_state = compliance_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    def evaluate_deals(data: GraphState):
        new_state = eval_agent.process_request(data["state_obj"])
        return {"state_obj": new_state}
        
    def negotiate_deals(data: GraphState):
        state_obj = data["state_obj"]
        if not state_obj.deal_evaluation:
            return {"state_obj": state_obj}
            
        best_vendor_id = max(
            state_obj.deal_evaluation.keys(),
            key=lambda vid: state_obj.deal_evaluation[vid].get("total_score", 0)
        )
        
        new_state = negotiation_agent.process_request(state_obj, best_vendor_id)
        return {"state_obj": new_state}
        
    def approve_deal(data: GraphState):
        state_obj = data["state_obj"]
        if not state_obj.deal_evaluation:
            return {"state_obj": state_obj}
            
        best_vendor_id = max(
            state_obj.deal_evaluation.keys(),
            key=lambda vid: state_obj.deal_evaluation[vid].get("total_score", 0)
        )
        
        new_state = approval_agent.process_request(state_obj, best_vendor_id)
        return {"state_obj": new_state}

    # Add Nodes
    workflow.add_node("requirement", extract_requirements)
    workflow.add_node("vendor_research", research_vendors)
    workflow.add_node("price_analysis", analyze_price)
    workflow.add_node("budget_analysis", check_budget)
    workflow.add_node("compliance_analysis", check_compliance)
    workflow.add_node("deal_evaluation", evaluate_deals)
    workflow.add_node("negotiation", negotiate_deals)
    workflow.add_node("approval", approve_deal)
    
    # Define Edges
    workflow.set_entry_point("requirement")
    workflow.add_edge("requirement", "vendor_research")
    
    # Sequential Analysis Phase
    workflow.add_edge("vendor_research", "price_analysis")
    workflow.add_edge("price_analysis", "budget_analysis")
    workflow.add_edge("budget_analysis", "compliance_analysis")
    workflow.add_edge("compliance_analysis", "deal_evaluation")
    
    # Negotiation and Approval
    workflow.add_edge("deal_evaluation", "negotiation")
    workflow.add_edge("negotiation", "approval")
    workflow.add_edge("approval", END)
    
    return workflow.compile()

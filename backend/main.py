from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
import uvicorn
from typing import Dict, Any

from backend.models.procurement_models import ProcurementState, ProcurementRequest
from backend.workflows.procurement_workflow import build_procurement_graph
from backend.utils.logger import logger, log_audit_trail

app = FastAPI(
    title="DealForge AI API",
    description="Multi-Agent Procurement and Vendor Negotiation System",
    version="1.0.0"
)

# In-memory store for demo purposes
# Key: request_id, Value: {"status": "processing" | "completed" | "failed", "state": ProcurementState}
job_store: Dict[str, Dict[str, Any]] = {}

class NewProcurementRequest(BaseModel):
    description: str
    requested_by: str
    department: str

class ApprovalDecision(BaseModel):
    decision: str  # "approve" or "reject"
    reason: str = ""

def run_procurement_workflow(request_id: str, description: str, requested_by: str, department: str):
    logger.info(f"Received new procurement request {request_id} from {requested_by}")
    log_audit_trail("PROCUREMENT_REQUESTED", {
        "request_id": request_id, 
        "requested_by": requested_by, 
        "department": department
    })
    try:
        initial_state = ProcurementState(
            request=ProcurementRequest(
                request_id=request_id,
                description=description,
                requested_by=requested_by,
                department=department
            )
        )
        
        workflow = build_procurement_graph()
        result = workflow.invoke({"state_obj": initial_state})
        
        
        job_store[request_id]["status"] = "completed"
        job_store[request_id]["state"] = result["state_obj"]
        logger.info(f"Successfully completed workflow for {request_id}")
    except Exception as e:
        logger.error(f"Workflow {request_id} failed: {e}")
        job_store[request_id]["status"] = "failed"
        job_store[request_id]["error"] = str(e)


@app.post("/api/request")
async def start_procurement_request(req: NewProcurementRequest, background_tasks: BackgroundTasks):
    request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    
    job_store[request_id] = {
        "status": "processing",
        "state": None
    }
    
    background_tasks.add_task(
        run_procurement_workflow,
        request_id, req.description, req.requested_by, req.department
    )
    
    return {"request_id": request_id, "status": "processing", "message": "Procurement workflow started in background."}

@app.get("/api/status/{request_id}")
async def get_request_status(request_id: str):
    if request_id not in job_store:
        raise HTTPException(status_code=404, detail="Request ID not found.")
        
    job = job_store[request_id]
    
    if job["status"] == "completed":
        state: ProcurementState = job["state"]
        return {
            "status": "completed",
            "requirements": state.requirements.model_dump() if state.requirements else None,
            "best_vendor": max(state.deal_evaluation.keys(), key=lambda vid: state.deal_evaluation[vid].get("total_score", 0)) if state.deal_evaluation else None,
            "negotiation": state.negotiation_status,
            "approval_required": any(s["approval_required"] for s in state.approval_status.values()) if state.approval_status else False,
            "approval_status": state.approval_status
        }
    else:
        return {"status": job["status"], "error": job.get("error")}

@app.post("/api/approve/{request_id}")
async def handle_approval(request_id: str, decision: ApprovalDecision):
    if request_id not in job_store:
        raise HTTPException(status_code=404, detail="Request ID not found.")
        
    job = job_store[request_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Cannot approve a job that is not completed.")
        
    state: ProcurementState = job["state"]
    
    log_audit_trail("MANAGER_DECISION", {
        "request_id": request_id,
        "decision": decision.decision,
        "reason": decision.reason
    })
    
    return {
        "message": f"Successfully {decision.decision}d request {request_id}",
        "reason_recorded": decision.reason
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

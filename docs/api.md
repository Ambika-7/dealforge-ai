# API Documentation

The FastAPI backend provides REST endpoints for triggering workflows.

### `POST /api/request`
Initiates a new multi-agent procurement workflow in the background.
**Payload:**
```json
{
  "description": "Need 50 laptops under 40 lakh rupees.",
  "requested_by": "Alice",
  "department": "IT"
}
```
**Response:** `{"request_id": "REQ-ABCD123", "status": "processing"}`

### `GET /api/status/{request_id}`
Polls the execution status of the graph and returns the accumulated AI state.
**Response:**
Returns a JSON object containing the `best_vendor`, the `negotiation` strategy and email, and the `approval_status`.

### `POST /api/approve/{request_id}`
Allows a human manager to unblock a gated deal.
**Payload:**
```json
{
  "decision": "approve",
  "reason": "Approved the budget override."
}
```

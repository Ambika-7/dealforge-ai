# Architecture Overview

DealForge AI uses a decentralized, functional-node architecture orchestrated by **LangGraph**. The entire system shares a common structured state (`ProcurementState`) built on Pydantic.

## 1. State Management
`backend/models/procurement_models.py` defines the global state. As agents execute, they append their findings (e.g., `budget_analysis`, `deal_evaluation`) to this state.

## 2. Orchestration (`ProcurementCoordinator`)
LangGraph defines the execution flow.
- The entry point is the **Requirement Agent**.
- The graph transitions into sequential/parallel analyses (**Price, Budget, Compliance**).
- It converges at the **Deal Evaluation Agent** to mathematically pick a winner.
- The winning vendor is passed to the **Negotiation Agent**, and finally gated by the **Approval Agent**.

## 3. Dynamic Replanning
The `Replanner` class dynamically modifies specific fields in the state (e.g., changing the budget threshold) and intelligently routes execution back to the affected nodes (e.g., re-triggering Budget Analysis and skipping Vendor Research), drastically reducing AI compute costs and latency.

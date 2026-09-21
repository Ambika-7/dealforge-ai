# Agent Roles and Workflows

The system separates concerns among 7 highly specialized agents:

1. **Requirement Agent**: Translates unstructured user text ("I need 50 laptops fast") into strict `Requirement` schemas. (Uses LLM).
2. **Vendor Research Agent**: Simulates interacting with a vendor database (`vendors.json`) to fetch raw vendor quotes matching the required product. (Deterministic Tool).
3. **Price Analysis Agent**: Calculates bulk discounts, tax, and total landed cost. (Deterministic Tool).
4. **Budget Agent**: Compares the landed cost against corporate budget allocations to flag overruns. (Deterministic Tool).
5. **Compliance Agent**: Validates the deal against mandatory company rules (`policies.json`). (Deterministic Tool).
6. **Deal Evaluation Agent**: Computes a numerical score across 7 categories, then uses an LLM to interpret the scores and provide a human-readable recommendation logic. (Hybrid).
7. **Negotiation Agent**: Reviews vendor weaknesses (e.g., "Slightly over budget" or "Short warranty") and leverages the LLM to calculate a target counter-price and draft a professional negotiation email. (Uses LLM).
8. **Approval Agent**: A rigid rule-based gatekeeper that halts the process and requests human authorization if the deal is too expensive or risky. (Deterministic Tool).

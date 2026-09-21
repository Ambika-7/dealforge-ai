# DealForge AI - Multi-Agent Procurement System

DealForge AI is a state-of-the-art autonomous Multi-Agent Procurement and Vendor Negotiation System. It replaces traditional manual procurement by leveraging specialized AI agents orchestrated via LangGraph. 

## Features
- **Requirement Analysis**: Automatically parses natural language requests into structured procurement goals.
- **Vendor Evaluation**: Mathematically scores vendors based on Price, Budget, Warranty, Delivery, and Compliance.
- **Autonomous Negotiation**: Strategizes target prices and drafts negotiation emails to vendors based on identified weaknesses.
- **Human-in-the-Loop Approval**: Enforces strict financial gating rules.
- **Dynamic Replanning**: Intelligently handles unexpected budget cuts or vendor availability changes without restarting the workflow.
- **Sleek UI**: Built-in responsive dashboard to track AI agent thought processes.

## Getting Started

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ambika-7/dealforge-ai.git
   cd dealforge-ai
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API Keys**:
   Copy `.env.example` to `.env` and insert your OpenAI/Gemini API keys.
4. **Run the Backend API**:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. **View the Dashboard**:
   Open `frontend/index.html` in your web browser.

### Docker Setup
To run the backend completely isolated:
```bash
docker build -t dealforge-ai .
docker run -p 8000:8000 --env-file .env dealforge-ai
```

## Documentation
- [Architecture](docs/architecture.md)
- [Agent Workflows](docs/agent_workflows.md)
- [API Reference](docs/api.md)
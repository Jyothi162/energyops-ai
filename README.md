# EnergyOps AI ☀️

**An AI-powered solar energy customer-support assistant built with LangGraph, Retrieval-Augmented Generation (RAG), Ollama, FastAPI, Streamlit, SQLite, and Docker.**

## Project Overview

EnergyOps AI is a portfolio prototype that demonstrates how agentic AI can assist solar energy companies with customer-support workflows.

The system classifies customer requests, retrieves information from support documents, checks installation statuses, identifies potentially dangerous situations, and proposes support tickets for human approval.

The application uses fictional customer records and demonstration documents.

## Key Features

- **AI Request Classification:** Categorizes installation, billing, technical-support, and appointment requests.
- **Agentic Workflow:** Uses LangGraph to route requests to appropriate tools and actions.
- **Retrieval-Augmented Generation:** Retrieves relevant information from a ChromaDB knowledge base.
- **Local LLM:** Uses Ollama with Llama 3.2 for classification and response generation.
- **Installation Tracking:** Retrieves customer installation records from SQLite.
- **Safety Escalation:** Routes recognized electrical-danger scenarios for human review.
- **Human-in-the-Loop Approval:** Requires approval before creating support tickets.
- **REST API:** Exposes agent functionality through FastAPI.
- **Web Interface:** Provides a Streamlit customer-support dashboard.
- **Docker Deployment:** Runs FastAPI and Streamlit using Docker Compose.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Large language model | Llama 3.2 via Ollama |
| AI orchestration | LangGraph |
| Retrieval-Augmented Generation | ChromaDB and Ollama embeddings |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Containerization | Docker and Docker Compose |
| Testing | pytest |

## System Architecture

```text
Customer
   |
   v
Streamlit Web Interface
   |
   v
FastAPI Backend
   |
   v
LangGraph AI Agent
   |
   +---- Request Classification
   |
   +---- Installation Status ----> SQLite
   |
   +---- Technical Support ------> Human Approval
   |                                  |
   |                                  v
   |                              SQLite Ticket
   |
   +---- Knowledge Question -----> RAG Pipeline
   |                                  |
   |                                  v
   |                             ChromaDB
   |                                  |
   |                                  v
   |                             Ollama LLM
   |
   +---- Safety Issue -----------> Human Review
```

## Project Structure

```text
energyops-ai/
├── agent.py
├── api.py
├── app.py
├── database.py
├── tools.py
├── schemas.py
├── startup.py
├── main.py
├── rag/
│   ├── __init__.py
│   ├── ingest.py
│   ├── retriever.py
│   └── rag_chain.py
├── knowledge_base/
│   ├── billing_faq.txt
│   ├── installation_guide.txt
│   └── inverter_troubleshooting.txt
├── tests/
│   └── test_routing.py
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python
- Docker Desktop
- Ollama
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/energyops-ai.git
cd energyops-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Download Ollama Models

Install Ollama and run:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Ensure the Ollama service is running locally.

### 3. Start the Application

```bash
docker compose up -d --build
```

The startup process initializes the demonstration database and indexes the knowledge-base documents.

### 4. Open the Application

**Streamlit interface:** http://localhost:8502

**FastAPI Swagger UI:** http://localhost:8001/docs

### 5. Stop the Application

```bash
docker compose down
```

The Docker volume retains the application's database and vector-store data.

## Demonstration Scenarios

### Scenario 1 — Knowledge Retrieval

**Customer question:**

> What is a solar inverter?

The agent retrieves relevant documents and generates an answer with source references.

### Scenario 2 — Installation Status

**Customer question:**

> What is my installation status?

**Customer ID:** 101

The agent queries SQLite and retrieves the fictional customer's installation status.

### Scenario 3 — Safety Escalation

**Customer question:**

> My solar inverter is sparking and smoking.

The agent identifies a potentially dangerous situation and routes the request for human review.

### Scenario 4 — Human-Approved Support Ticket

**Customer question:**

> My solar inverter is not working properly.

**Customer ID:** 101

The agent proposes a support ticket. The user must approve the action before the ticket is created in SQLite.

## Running Tests

Install the Python dependencies and run:

```bash
python -m pytest tests/ -v
```

The current automated test suite covers key routing scenarios. Additional integration and security testing are future improvements.

## Safety and Limitations

EnergyOps AI is an educational portfolio prototype, not a production customer-support service.

- Customer data and documents are fictional.
- Safety detection is demonstrated with selected test scenarios and is not a certified electrical-safety system.
- The application does not replace emergency services or qualified technicians.
- Authentication, authorization, and production-grade security controls are not yet implemented.
- The application requires a locally accessible Ollama service.

## Future Improvements

- Authentication and role-based access control
- Expanded automated integration testing
- RAG quality evaluation and citation verification
- Monitoring and structured logging
- Improved safety classification and escalation policies
- Cloud deployment
- Integration with real customer-support platforms

## Project Purpose

This project demonstrates practical skills in AI agents, RAG, local LLM integration, workflow automation, API development, database operations, human-in-the-loop decision-making, and containerized deployment.

It was developed as an independent portfolio project focused on AI automation applications in the renewable-energy industry.

## License

No license has been selected yet.
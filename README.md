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

## System Architecture

See the [architecture diagram](docs/architecture.md).

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Large language model | Llama 3.2 via Ollama |
| AI orchestration | LangGraph |
| Retrieval-Augmented Generation | ChromaDB, Ollama embeddings, BM25, Hybrid Search, RRF |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Security evaluation | pytest, prompt-injection test scenarios |
| Containerization | Docker and Docker Compose |
| Testing | pytest |

## AI Evaluation Results

EnergyOps AI was evaluated on 10 manually labeled customer-support scenarios covering installation, billing, technical support, appointments, and electrical safety.

| Metric | Result |
|---|---|
| Test cases | 10 |
| Completed evaluations | 10 |
| Request classification accuracy | 100% (10/10) |
| Routing accuracy | 100% (10/10) |

## Retrieval Evaluation: Semantic vs Hybrid Search

EnergyOps AI compares semantic vector search with hybrid
retrieval combining semantic similarity, keyword matching
(BM25), and Reciprocal Rank Fusion (RRF).

Both methods were evaluated on the same five solar-energy
customer-support questions.

| Metric | Semantic | Hybrid |
|---|---:|---:|
| Questions evaluated | 5 | 5 |
| Completed evaluations | 5 | 5 |
| Source Hit Rate@2 | 80% | 100% |
| Mean Reciprocal Rank (MRR) | 0.867 | 1.000 |

### Findings

- Hybrid retrieval improved Source Hit Rate@2 by 20 percentage points.
- Hybrid retrieval ranked the expected document first for all five questions.
- The evaluation demonstrates the benefit of combining keyword and semantic retrieval for this small knowledge base.

### Reproduce the Evaluation

Run:

```bash
python evaluation/compare_retrievers.py
```

Detailed results are saved in:

`evaluation/comparison_results.json`

**Limitation:** The benchmark contains five questions and three
support documents. Results are specific to this prototype and
should not be interpreted as production-level accuracy.


### RAG Retrieval Improvement

EnergyOps AI was evaluated using 9 manually labeled
solar customer-support questions.

Initial Source Hit Rate@2: 77.78% (7/9)

Investigation identified two billing-related questions
where the expected billing FAQ document ranked third.

Improvement:
- Inspected ChromaDB document rankings.
- Identified gaps in billing FAQ coverage.
- Added relevant billing question-and-answer content.
- Regenerated document embeddings.
- Repeated the retrieval evaluation.

Updated Source Hit Rate@2: 100% (9/9)

Limitation:
These results are based on a small evaluation dataset.
Additional unseen questions are required to assess
retrieval generalization.

### Evaluation Methodology

- Model: Llama 3.2 running locally through Ollama
- Classification: Structured output validated with Pydantic
- Routing: Application routing rules
- Dataset: `evaluation/test_cases.json`
- Evaluation script: `evaluation/evaluate.py`


**Limitations:** The classification and routing results come from a small, manually curated dataset. These metrics do not establish production reliability. Retrieval quality and selected human-approval behaviors are evaluated separately in the sections below.


To reproduce the evaluation:

```powershell
python evaluation/evaluate.py
```


## Workflow Overview

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
│
├── agent.py
├── api.py
├── app.py
├── database.py
├── tools.py
├── schemas.py
├── startup.py
├── main.py
│
├── rag/
│   ├── __init__.py
│   ├── ingest.py
│   ├── retriever.py
│   ├── hybrid_retriever.py
│   └── rag_chain.py
│
├── knowledge_base/
│   ├── billing_faq.txt
│   ├── installation_guide.txt
│   └── inverter_troubleshooting.txt
│
├── evaluation/
│   ├── evaluate.py
│   ├── evaluate_answers.py
│   ├── compare_retrievers.py
│   ├── test_safety.py
│   ├── test_human_approval.py
│   ├── test_cases.json
│   ├── answer_results.json
│   └── comparison_results.json
│
├── security_tests/
│   ├── test_prompt_injection.py
│   ├── evaluate_security.py
│   ├── baseline_results.txt
│   └── security_results.json
│
├── tests/
│   └── test_routing.py
│
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
├── README.md
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
git clone https://github.com/Jyothi162/energyops-ai.git
cd energyops-ai
```


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

Run the routing, safety, and human-approval tests:

```bash
python -m pytest tests/ evaluation/test_safety.py evaluation/test_human_approval.py -v
```

The safety and human-approval test files were verified
together with 10 passing tests.

Routing tests can be run separately:

```bash
python -m pytest tests/ -v
```



## Safety and Human-in-the-Loop Testing

EnergyOps AI uses pytest to validate electrical hazard
escalation and human-controlled support ticket creation.

### Automated Test Results

| Test Category | Passed |
|---|---:|
| Electrical hazard escalation | 5/5 |
| Normal request handling | 1/1 |
| Pending approval | 1/1 |
| Approved ticket creation | 1/1 |
| Rejected ticket creation | 1/1 |
| Unsafe ticket blocked after approval | 1/1 |
| **Total** | **10/10** |

### Run Safety and Approval Tests

```bash
python -m pytest evaluation/test_safety.py evaluation/test_human_approval.py -v
```

**Result:** 10 tests passed.

Approval tests use mocked database writes and isolated
LangGraph checkpointers. These tests validate selected
workflow behaviors, not comprehensive production security.



## Safety and Limitations

EnergyOps AI is an educational portfolio prototype, not a production customer-support service.

- Customer data and documents are fictional.
- Safety detection is demonstrated with selected test scenarios and is not a certified electrical-safety system.
- The application does not replace emergency services or qualified technicians.
- Authentication, authorization, and production-grade security controls are not yet implemented.
- The application requires a locally accessible Ollama service.


## Prompt-Injection Baseline Evaluation

EnergyOps AI was evaluated against five controlled
prompt-injection scenarios embedded in retrieved documents.

| Metric | Result |
|---|---|
| Attack scenarios | 5 |
| Observed attack success rate | 0% (0/5) |
| Legitimate-task success rate | 100% (5/5) |

The evaluation included direct instruction injection,
fake system messages, administrator impersonation,
safety-override instructions, and citation manipulation.

Attack success was measured by whether the model included
a specified attacker-controlled phrase in its response.
Legitimate-task success used a simple keyword-based check.

These results are limited to one customer question and
five controlled scenarios. They do not establish
comprehensive resistance to prompt injection.

### Reproduce the Evaluation

```powershell
python -m pytest security_tests/test_prompt_injection.py -v -s
python -m security_tests.evaluate_security
```

Results are saved in `security_tests/security_results.json`.



## Future Improvements

- Authentication and role-based access control
- Expanded end-to-end API integration and security testing
- Automated RAG answer-faithfulness scoring and citation verification
- Expanded adversarial prompt-injection testing and role-based access-control evaluation
- Monitoring and structured logging
- Improved safety classification and escalation policies
- Cloud deployment
- Integration with real customer-support platforms


## Project Purpose

This project demonstrates practical skills in AI agents, RAG, local LLM integration, workflow automation, API development, database operations, human-in-the-loop decision-making, and containerized deployment.

It was developed as an independent portfolio project focused on AI automation applications in the renewable-energy industry.

## License

No license has been selected yet.
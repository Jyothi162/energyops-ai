
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langgraph.types import Command

from agent import graph
from rag.rag_chain import generate_rag_answer


app = FastAPI(
    title="EnergyOps AI API",
    description="Solar support AI with LangGraph and RAG",
    version="1.1.0",
)


# ----------------------------------
# REQUEST MODELS
# ----------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    customer_id: Optional[int] = None


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


# ----------------------------------
# HELPER: FORMAT GRAPH OUTPUT
# ----------------------------------

def format_output(output, thread_id):

    interrupts = output.get("__interrupt__", [])

    if interrupts:
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "approval_request": [
                item.value for item in interrupts
            ],
        }

    return {
        "thread_id": thread_id,
        "status": "completed",
        "classification": output.get("classification"),
        "result": output.get("result"),
    }


# ----------------------------------
# BASIC ENDPOINTS
# ----------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to EnergyOps AI API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ----------------------------------
# DIRECT RAG ENDPOINT
# ----------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    return generate_rag_answer(
        request.question
    )


# ----------------------------------
# LANGGRAPH AGENT ENDPOINT
# ----------------------------------

@app.post("/agent")
def run_agent(request: AgentRequest):

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "message": request.message,
        "customer_id": request.customer_id,
        "classification": None,
        "result": None,
    }

    try:
        output = graph.invoke(
            initial_state,
            config=config,
        )

        return format_output(output, thread_id)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ----------------------------------
# HUMAN APPROVAL ENDPOINT
# ----------------------------------

@app.post("/agent/approve")
def approve_ticket(request: ApprovalRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    try:
        snapshot = graph.get_state(config)

        if not snapshot.tasks or not any(
            task.interrupts
            for task in snapshot.tasks
        ):
            raise HTTPException(
                status_code=409,
                detail="No pending approval for this thread.",
            )

        output = graph.invoke(
            Command(resume=request.approved),
            config=config,
        )

        return format_output(
            output,
            request.thread_id,
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

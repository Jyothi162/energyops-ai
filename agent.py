
import json
import uuid
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from main import (
    classify_request,
    apply_routing_rules,
    is_safety_issue,
)

from tools import (
    check_installation_status,
    create_support_ticket,
)

from rag.rag_chain import generate_rag_answer


# ==========================================
# 1. SHARED AGENT STATE
# ==========================================

class AgentState(TypedDict):
    message: str
    customer_id: Optional[int]
    classification: Optional[dict]
    result: Optional[dict]


# ==========================================
# 2. CLASSIFY CUSTOMER REQUEST
# ==========================================

def classify_node(state: AgentState):

    classification = classify_request(
        state["message"]
    )

    classification = apply_routing_rules(
        classification,
        state["message"]
    )

    return {
        "classification": classification.model_dump()
    }


# ==========================================
# 3. ROUTING DECISION
# ==========================================

def route_request(state: AgentState):

    message = state["message"].lower()

    # Safety always takes priority
    if is_safety_issue(message):
        return "human_review"

    action = state["classification"]["next_action"]
    category = state["classification"]["category"]

    # Installation status lookup
    if action == "check_installation_status":
        return "installation_lookup"

    # Technical problems requiring a ticket
    if action == "create_support_ticket":
        return "ticket_approval"

    # General information questions
    knowledge_phrases = [
        "what is",
        "what are",
        "how does",
        "how do",
        "how can",
        "explain",
        "why does",
        "why is",
        "what should",
    ]

    if any(
        phrase in message
        for phrase in knowledge_phrases
    ):
        return "rag_answer"

    # Billing and appointment questions
    # may be answered from the knowledge base,
    # but this is not account-specific verification.
    if category in ["billing", "appointment"]:
        return "rag_answer"

    return "human_review"


# ==========================================
# 4. INSTALLATION LOOKUP NODE
# ==========================================

def installation_lookup_node(state: AgentState):

    customer_id = state.get("customer_id")

    if customer_id is None:
        return {
            "result": {
                "error": "Customer ID is required"
            }
        }

    result = check_installation_status(
        customer_id
    )

    return {"result": result}


# ==========================================
# 5. SUPPORT TICKET APPROVAL NODE
# ==========================================

def ticket_approval_node(state: AgentState):

    customer_id = state.get("customer_id")

    if customer_id is None:
        return {
            "result": {
                "error": "Customer ID is required"
            }
        }

    customer = check_installation_status(
        customer_id
    )

    if "error" in customer:
        return {
            "result": {
                "error": "Customer not found"
            }
        }

    proposal = {
        "customer_id": customer_id,
        "customer_name": customer["customer_name"],
        "description": state["message"],
        "priority": state["classification"]["priority"],
    }

    # Pause execution until a human approves
    approval = interrupt({
        "type": "ticket_approval",
        "proposal": proposal,
        "question": "Approve support ticket creation?",
    })

    if approval is not True:
        return {
            "result": {
                "status": "Rejected",
                "message": "Ticket was not created.",
            }
        }

    # Safety check before database modification
    if is_safety_issue(state["message"]):
        return {
            "result": {
                "status": "Safety escalation",
                "message": "Automatic ticket creation blocked.",
            }
        }

    ticket = create_support_ticket(
        customer_id=customer_id,
        description=state["message"],
        priority=state["classification"]["priority"],
    )

    return {"result": ticket}


# ==========================================
# 6. RAG KNOWLEDGE ASSISTANT NODE
# ==========================================

def rag_answer_node(state: AgentState):

    result = generate_rag_answer(
        state["message"]
    )

    return {"result": result}


# ==========================================
# 7. HUMAN REVIEW NODE
# ==========================================

def human_review_node(state: AgentState):

    if is_safety_issue(state["message"]):
        return {
            "result": {
                "status": "Safety escalation",
                "priority": "high",
                "message": (
                    "Potential electrical danger. "
                    "Stay clear of unsafe equipment. "
                    "Contact emergency services if "
                    "there is immediate danger, or "
                    "qualified technical support."
                ),
            }
        }

    return {
        "result": {
            "status": "Human review required",
            "message": "No automatic action performed.",
        }
    }


# ==========================================
# 8. BUILD LANGGRAPH
# ==========================================

builder = StateGraph(AgentState)

builder.add_node("classify", classify_node)

builder.add_node(
    "installation_lookup",
    installation_lookup_node,
)

builder.add_node(
    "ticket_approval",
    ticket_approval_node,
)

builder.add_node(
    "rag_answer",
    rag_answer_node,
)

builder.add_node(
    "human_review",
    human_review_node,
)

builder.add_edge(START, "classify")

builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "installation_lookup": "installation_lookup",
        "ticket_approval": "ticket_approval",
        "rag_answer": "rag_answer",
        "human_review": "human_review",
    },
)

builder.add_edge("installation_lookup", END)
builder.add_edge("ticket_approval", END)
builder.add_edge("rag_answer", END)
builder.add_edge("human_review", END)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# ==========================================
# 9. RUN ENERGYOPS AI
# ==========================================

def main():

    print("\n===== ENERGYOPS AI AGENT =====")

    message = input(
        "Enter customer problem or question: "
    ).strip()

    if not message or message.isdigit():
        print("Please enter a valid question.")
        return

    customer_input = input(
        "Customer ID (101, 102, 103), or Enter to skip: "
    ).strip()

    if customer_input and not customer_input.isdigit():
        print("Customer ID must be numeric.")
        return

    customer_id = (
        int(customer_input)
        if customer_input
        else None
    )

    initial_state = {
        "message": message,
        "customer_id": customer_id,
        "classification": None,
        "result": None,
    }

    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

    try:
        output = graph.invoke(
            initial_state,
            config=config,
        )

        # Human approval workflow
        if "__interrupt__" in output:

            for pending in output["__interrupt__"]:
                print("\n===== APPROVAL REQUIRED =====")
                print(
                    json.dumps(
                        pending.value,
                        indent=4,
                    )
                )

            answer = input(
                "\nApprove ticket creation? (yes/no): "
            ).strip().lower()

            output = graph.invoke(
                Command(resume=answer == "yes"),
                config=config,
            )

        if output.get("__interrupt__"):
            print("Workflow is still awaiting approval.")
            return

        print("\nAI Classification:")
        print(
            json.dumps(
                output["classification"],
                indent=4,
            )
        )

        print("\nAgent Result:")
        print(
            json.dumps(
                output["result"],
                indent=4,
            )
        )

    except Exception as error:
        print("\nAgent error:", error)


if __name__ == "__main__":
    main()

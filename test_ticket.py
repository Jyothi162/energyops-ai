
import json

from ollama import chat
from pydantic import ValidationError

from schemas import CustomerRequest
from tools import (
    check_installation_status,
    create_support_ticket,
)

MODEL = "llama3.2"

SYSTEM_PROMPT = """
You are an AI operations assistant for a fictional
solar energy company.

Classify customer requests into:

Categories:
installation, billing, technical_support,
appointment, other

Priorities:
low, medium, high

Next actions:
check_installation_status,
review_billing,
create_support_ticket,
check_appointment,
human_review

Rules:
- Installation delays or status requests:
  check_installation_status
- Billing questions: review_billing
- Technical equipment problems: create_support_ticket
- Appointment requests: check_appointment
- Unclear requests: human_review

Priority:
- High: fire, smoke, sparks, electric shock,
  or other immediate safety risks
- Medium: installation delays, billing disputes,
  equipment faults without immediate danger
- Low: general information requests

Return JSON matching the provided schema.
Never invent customer records or claim actions were done.
"""


def classify_request(message):
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        format=CustomerRequest.model_json_schema(),
        options={"temperature": 0},
    )

    return CustomerRequest.model_validate_json(
        response.message.content
    )


def is_safety_issue(message):
    safety_words = [
        "fire",
        "smoke",
        "sparking",
        "sparks",
        "electric shock",
        "burning smell",
    ]

    message = message.lower()

    return any(word in message for word in safety_words)


def apply_routing_rules(result, message):
    text = message.lower()

    if is_safety_issue(message):
        result.priority = "high"
        result.next_action = "human_review"

    elif (
        result.category == "installation"
        and any(
            word in text
            for word in ["check", "status", "delay", "delayed"]
        )
    ):
        result.next_action = "check_installation_status"

    elif result.category == "technical_support":
        result.next_action = "create_support_ticket"

    return result


def request_customer_id():
    customer_id = input(
        "\nEnter fictional customer ID (101, 102, 103): "
    ).strip()

    if not customer_id.isdigit():
        raise ValueError("Customer ID must be a number.")

    return int(customer_id)


def handle_installation():
    customer_id = request_customer_id()

    result = check_installation_status(customer_id)

    print("\nInstallation Result:")
    print(json.dumps(result, indent=4))


def handle_ticket(message, priority):
    customer_id = request_customer_id()

    # Confirm that the fictional customer exists.
    customer = check_installation_status(customer_id)

    if "error" in customer:
        print("\nCustomer not found. Ticket not created.")
        return

    print("\nProposed Support Ticket:")
    print("Customer:", customer["customer_name"])
    print("Description:", message)
    print("Priority:", priority)

    approval = input(
        "\nApprove ticket creation? (yes/no): "
    ).strip().lower()

    if approval != "yes":
        print("\nTicket creation cancelled.")
        return

    ticket = create_support_ticket(
        customer_id=customer_id,
        description=message,
        priority=priority,
    )

    print("\nSupport Ticket Result:")
    print(json.dumps(ticket, indent=4))


def main():
    print("\n===== ENERGYOPS AI =====")

    message = input(
        "Enter customer problem (not customer ID): "
    ).strip()

    if not message:
        print("Please enter a customer request.")
        return

    if message.isdigit():
        print("Please describe the problem, not the customer ID.")
        return

    try:
        classification = classify_request(message)
        classification = apply_routing_rules(
            classification, message
        )

        print("\nAI Classification:")
        print(
            json.dumps(
                classification.model_dump(),
                indent=4,
            )
        )

        if is_safety_issue(message):
            print("\nSAFETY ALERT!")
            print(
                "Keep clear of dangerous electrical equipment. "
                "Contact emergency services if there is immediate "
                "danger, or qualified technical support."
            )
            print("Human review required.")
            print("No automatic action was performed.")
            return

        action = classification.next_action

        if action == "check_installation_status":
            handle_installation()

        elif action == "create_support_ticket":
            handle_ticket(message, classification.priority)

        elif action == "human_review":
            print("\nHuman review required.")

        else:
            print("\nSelected action:", action)
            print("Tool implementation coming soon.")

    except ValidationError as error:
        print("\nInvalid AI output:")
        print(error)

    except ValueError as error:
        print("\nInput error:", error)

    except Exception as error:
        print("\nApplication error:", error)


if __name__ == "__main__":
    main()

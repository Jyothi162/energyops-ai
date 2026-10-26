
import json

import os
from ollama import Client

ollama_client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://127.0.0.1:11434"
    )
)
from pydantic import ValidationError

from schemas import CustomerRequest
from tools import (
    check_installation_status,
    create_support_ticket,
)


# ==========================================
# 1. OLLAMA CONFIGURATION
# ==========================================

MODEL = "llama3.2"


# ==========================================
# 2. SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are an AI operations assistant for a fictional
solar energy company.

Your job is to classify customer requests.

CATEGORIES:
- installation: installation status or delays
- billing: electricity bills and payments
- technical_support: solar equipment problems
- appointment: scheduling and rescheduling
- other: anything else

PRIORITIES:
- high: fire, smoke, sparking, electric shock,
  or immediate electrical danger
- medium: installation delays, billing disputes,
  or equipment problems without immediate danger
- low: general questions and non-urgent requests

NEXT ACTIONS:
- check_installation_status: installation status
- review_billing: billing problems
- create_support_ticket: technical problems
- check_appointment: appointment requests
- human_review: unclear or sensitive requests

RULES:
1. Installation status requests should use
   check_installation_status.
2. Technical equipment problems should use
   create_support_ticket.
3. Billing requests should use review_billing.
4. Appointment requests should use check_appointment.
5. Unclear requests should use human_review.
6. Never invent customer information.
7. Never claim that an action has been completed.

Return JSON matching the provided schema.
"""


# ==========================================
# 3. CLASSIFY CUSTOMER REQUEST
# ==========================================

def classify_request(message):

    response = ollama_client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        format=CustomerRequest.model_json_schema(),
        options={"temperature": 0},
    )

    return CustomerRequest.model_validate_json(
        response.message.content
    )


# ==========================================
# 4. SAFETY DETECTION
# ==========================================

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

    return any(
        word in message
        for word in safety_words
    )


# ==========================================
# 5. WORKFLOW ROUTING
# ==========================================

def apply_routing_rules(result, message):

    text = message.lower()

    if is_safety_issue(message):
        result.priority = "high"
        result.next_action = "human_review"

    elif result.category == "installation":
        if any(
            word in text
            for word in [
                "check",
                "status",
                "delay",
                "delayed",
            ]
        ):
            result.next_action = "check_installation_status"

    elif result.category == "technical_support":
        result.next_action = "create_support_ticket"

    elif result.category == "billing":
        result.next_action = "review_billing"

    elif result.category == "appointment":
        result.next_action = "check_appointment"

    return result


# ==========================================
# 6. CUSTOMER ID INPUT
# ==========================================

def request_customer_id():

    customer_id = input(
        "\nEnter fictional customer ID (101, 102, 103): "
    ).strip()

    if not customer_id.isdigit():
        raise ValueError(
            "Customer ID must be a number."
        )

    return int(customer_id)


# ==========================================
# 7. INSTALLATION STATUS TOOL
# ==========================================

def handle_installation():

    customer_id = request_customer_id()

    result = check_installation_status(
        customer_id
    )

    print("\nInstallation Result:")
    print(
        json.dumps(
            result,
            indent=4
        )
    )


# ==========================================
# 8. SUPPORT TICKET CREATION
# ==========================================

def handle_ticket(message, priority):

    customer_id = request_customer_id()

    customer = check_installation_status(
        customer_id
    )

    if "error" in customer:
        print("\nCustomer not found.")
        print("Ticket was not created.")
        return

    print("\n===== PROPOSED SUPPORT TICKET =====")

    print("Customer ID:", customer_id)
    print("Customer Name:", customer["customer_name"])
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

    print("\n===== SUPPORT TICKET CREATED =====")

    print(
        json.dumps(
            ticket,
            indent=4
        )
    )


# ==========================================
# 9. MAIN APPLICATION
# ==========================================

def main():

    print("\n===== ENERGYOPS AI =====")

    message = input(
        "Enter customer problem (not customer ID): "
    ).strip()

    if not message:
        print("Please enter a customer request.")
        return

    if message.isdigit():
        print(
            "Please describe the problem, "
            "not the customer ID."
        )
        return

    try:

        # STEP 1: CLASSIFY USING OLLAMA

        classification = classify_request(
            message
        )

        # STEP 2: APPLY WORKFLOW RULES

        classification = apply_routing_rules(
            classification,
            message
        )

        # STEP 3: DISPLAY CLASSIFICATION

        print("\nAI Classification:")

        print(
            json.dumps(
                classification.model_dump(),
                indent=4
            )
        )

        # STEP 4: SAFETY CHECK

        if is_safety_issue(message):

            print("\n===== SAFETY ALERT =====")

            print(
                "Potential electrical danger detected."
            )

            print(
                "Stay clear of dangerous equipment. "
                "Contact emergency services if there "
                "is immediate danger, or contact "
                "qualified technical support."
            )

            print("Human review required.")
            print("No automatic action performed.")

            return

        # STEP 5: EXECUTE WORKFLOW

        action = classification.next_action

        if action == "check_installation_status":

            handle_installation()

        elif action == "create_support_ticket":

            handle_ticket(
                message,
                classification.priority
            )

        elif action == "review_billing":

            print("\nBilling review selected.")
            print("Billing tool coming soon.")

        elif action == "check_appointment":

            print("\nAppointment lookup selected.")
            print("Appointment tool coming soon.")

        elif action == "human_review":

            print("\nHuman review required.")

        else:

            print("\nUnknown action.")
            print("Human review required.")

    except ValidationError as error:

        print("\nInvalid AI output:")
        print(error)

    except ValueError as error:

        print("\nInput error:")
        print(error)

    except Exception as error:

        print("\nApplication error:")
        print(error)


# ==========================================
# 10. START APPLICATION
# ==========================================

if __name__ == "__main__":
    main()


from agent import route_request


def make_state(category, action, message):
    return {
        "message": message,
        "customer_id": None,
        "classification": {
            "category": category,
            "priority": "medium",
            "next_action": action,
        },
        "result": None,
    }


def test_installation_routing():
    state = make_state(
        "installation",
        "check_installation_status",
        "Check my installation status.",
    )

    assert route_request(state) == "installation_lookup"


def test_ticket_routing():
    state = make_state(
        "technical_support",
        "create_support_ticket",
        "My solar inverter is not working.",
    )

    assert route_request(state) == "ticket_approval"


def test_rag_routing():
    state = make_state(
        "other",
        "human_review",
        "What is a solar inverter?",
    )

    assert route_request(state) == "rag_answer"


def test_safety_routing():
    state = make_state(
        "technical_support",
        "create_support_ticket",
        "My inverter is sparking and there is smoke.",
    )

    assert route_request(state) == "human_review"

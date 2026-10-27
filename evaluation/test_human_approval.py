
import uuid
from unittest.mock import patch

import pytest

from langgraph.types import Command

from agent import (
    AgentState,
    ticket_approval_node,
    builder,
)
from langgraph.checkpoint.memory import MemorySaver


def make_state():
    return {
        "message": "My solar inverter is not working properly.",
        "customer_id": 101,
        "classification": {
            "category": "technical",
            "priority": "medium",
            "next_action": "create_support_ticket",
        },
        "result": None,
    }


@pytest.fixture
def approval_graph():
    """
    Build an isolated test graph using the existing
    approval node and a fresh in-memory checkpointer.
    """
    from langgraph.graph import StateGraph, START, END

    test_builder = StateGraph(AgentState)

    test_builder.add_node(
        "ticket_approval",
        ticket_approval_node,
    )

    test_builder.add_edge(
        START,
        "ticket_approval",
    )

    test_builder.add_edge(
        "ticket_approval",
        END,
    )

    return test_builder.compile(
        checkpointer=MemorySaver()
    )


def make_config():
    return {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }


def test_ticket_not_created_before_approval(
    approval_graph,
):
    with patch(
        "agent.check_installation_status",
        return_value={
            "customer_name": "Test Customer",
            "status": "Pending",
        },
    ), patch(
        "agent.create_support_ticket"
    ) as mock_create:

        config = make_config()

        result = approval_graph.invoke(
            make_state(),
            config=config,
        )

        assert "__interrupt__" in result
        assert len(result["__interrupt__"]) == 1

        mock_create.assert_not_called()


def test_ticket_created_after_approval(
    approval_graph,
):
    with patch(
        "agent.check_installation_status",
        return_value={
            "customer_name": "Test Customer",
            "status": "Pending",
        },
    ), patch(
        "agent.is_safety_issue",
        return_value=False,
    ), patch(
        "agent.create_support_ticket",
        return_value={
            "ticket_id": 999,
            "status": "Open",
        },
    ) as mock_create:

        config = make_config()

        first_result = approval_graph.invoke(
            make_state(),
            config=config,
        )

        assert "__interrupt__" in first_result

        mock_create.assert_not_called()

        final_result = approval_graph.invoke(
            Command(resume=True),
            config=config,
        )

        mock_create.assert_called_once_with(
            customer_id=101,
            description="My solar inverter is not working properly.",
            priority="medium",
        )

        assert final_result["result"]["status"] == "Open"


def test_ticket_rejected_without_creation(
    approval_graph,
):
    with patch(
        "agent.check_installation_status",
        return_value={
            "customer_name": "Test Customer",
            "status": "Pending",
        },
    ), patch(
        "agent.create_support_ticket"
    ) as mock_create:

        config = make_config()

        first_result = approval_graph.invoke(
            make_state(),
            config=config,
        )

        assert "__interrupt__" in first_result

        final_result = approval_graph.invoke(
            Command(resume=False),
            config=config,
        )

        mock_create.assert_not_called()

        assert (
            final_result["result"]["status"]
            == "Rejected"
        )

def test_approved_unsafe_ticket_is_blocked(
    approval_graph,
):
    unsafe_state = make_state()
    unsafe_state["message"] = (
        "My inverter is sparking and smoking."
    )

    with patch(
        "agent.check_installation_status",
        return_value={
            "customer_name": "Test Customer",
            "status": "Pending",
        },
    ), patch(
        "agent.create_support_ticket"
    ) as mock_create:

        config = make_config()

        first_result = approval_graph.invoke(
            unsafe_state,
            config=config,
        )

        assert "__interrupt__" in first_result

        final_result = approval_graph.invoke(
            Command(resume=True),
            config=config,
        )

        mock_create.assert_not_called()

        assert (
            final_result["result"]["status"]
            == "Safety escalation"
        )

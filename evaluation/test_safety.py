
import pytest

from rag.rag_chain import generate_rag_answer


@pytest.mark.parametrize(
    "question",
    [
        "My solar inverter is smoking.",
        "There are sparks coming from my inverter.",
        "My inverter has a burning smell.",
        "I received an electric shock.",
        "My solar equipment is on fire.",
    ],
)
def test_electrical_hazards_trigger_escalation(question):
    result = generate_rag_answer(question)

    assert result["status"] == "safety_escalation"
    assert result["sources"] == []

    answer = result["answer"].lower()

    assert "stay clear" in answer
    assert "do not attempt repairs" in answer


def test_normal_question_does_not_trigger_safety_escalation():
    result = generate_rag_answer(
        "Who should review an incorrect solar invoice?"
    )

    assert result["status"] == "answered"
    assert "billing_faq.txt" in result["sources"]

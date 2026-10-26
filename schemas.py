
from typing import Literal
from pydantic import BaseModel


class CustomerRequest(BaseModel):
    category: Literal[
        "installation",
        "billing",
        "technical_support",
        "appointment",
        "other",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    next_action: Literal[
        "check_installation_status",
        "review_billing",
        "create_support_ticket",
        "check_appointment",
        "human_review",
    ]

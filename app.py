
import os
import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="EnergyOps AI",
    page_icon="☀️",
    layout="centered",
)

st.title("☀️ EnergyOps AI")
st.caption(
    "AI-powered solar support assistant "
    "| Ollama + LangGraph + RAG"
)

st.info(
    "Portfolio demonstration using fictional "
    "customer records and support documents."
)

# Remember pending approval across Streamlit reruns
if "pending_thread_id" not in st.session_state:
    st.session_state.pending_thread_id = None

if "proposal" not in st.session_state:
    st.session_state.proposal = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ---------------------------------------
# API HELPER
# ---------------------------------------

def call_api(endpoint, payload):
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------
# CUSTOMER REQUEST FORM
# ---------------------------------------

st.subheader("Customer Support")

with st.form("customer_form"):
    message = st.text_area(
        "How can we help you?",
        placeholder=(
            "Example: My solar inverter "
            "is not working properly."
        ),
    )

    customer_id = st.selectbox(
        "Customer ID (optional)",
        options=["None", "101", "102", "103"],
    )

    submitted = st.form_submit_button(
        "Ask EnergyOps AI",
        use_container_width=True,
    )


if submitted:
    if not message.strip():
        st.warning("Please enter a question.")
    else:
        payload = {
            "message": message.strip(),
            "customer_id": (
                None
                if customer_id == "None"
                else int(customer_id)
            ),
        }

        # Clear any earlier approval workflow
        st.session_state.pending_thread_id = None
        st.session_state.proposal = None
        st.session_state.last_result = None

        try:
            with st.spinner("EnergyOps AI is processing..."):
                data = call_api("/agent", payload)

            if data["status"] == "awaiting_approval":
                st.session_state.pending_thread_id = (
                    data["thread_id"]
                )
                st.session_state.proposal = (
                    data["approval_request"][0]
                )
            else:
                st.session_state.last_result = data

        except requests.RequestException as error:
            st.error(f"API request failed: {error}")


# ---------------------------------------
# HUMAN APPROVAL
# ---------------------------------------

if st.session_state.pending_thread_id:

    st.subheader("Human Approval Required")

    st.warning(
        "The AI agent wants to create "
        "a support ticket."
    )

    st.json(st.session_state.proposal)

    col1, col2 = st.columns(2)

    with col1:
        approve = st.button(
            "Approve Ticket",
            use_container_width=True,
            type="primary",
        )

    with col2:
        reject = st.button(
            "Reject Ticket",
            use_container_width=True,
        )

    if approve or reject:
        payload = {
            "thread_id": (
                st.session_state.pending_thread_id
            ),
            "approved": approve,
        }

        try:
            with st.spinner("Processing approval..."):
                data = call_api(
                    "/agent/approve",
                    payload,
                )

            st.session_state.last_result = data
            st.session_state.pending_thread_id = None
            st.session_state.proposal = None

            st.rerun()

        except requests.RequestException as error:
            st.error(f"Approval failed: {error}")


# ---------------------------------------
# DISPLAY RESULT
# ---------------------------------------

if st.session_state.last_result:

    data = st.session_state.last_result
    result = data.get("result") or {}

    st.subheader("Agent Response")

    if result.get("status") in (
        "Safety escalation",
        "safety_escalation",
    ):
        st.error(
            result.get("message")
            or result.get("answer")
            or "Safety escalation required."
        )

    elif result.get("status") == "Rejected":
        st.warning("Ticket creation was rejected.")

    elif "answer" in result:
        st.write(result["answer"])

        if result.get("sources"):
            st.caption(
                "Retrieved sources: "
                + ", ".join(result["sources"])
            )

    elif "ticket_id" in result:
        st.success(
            f"Support ticket #{result['ticket_id']} "
            "created successfully."
        )
        st.json(result)

    else:
        st.json(result)

    with st.expander("View AI Classification"):
        st.json(data.get("classification"))

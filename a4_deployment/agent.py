"""A4: Deployment demo agent — FAQ bot extended with store-hours lookup.

This is the M8 FAQ agent with one extra tool added to show that the agent code
is unchanged regardless of deployment target (local, Docker, Cloud Run, Agent Engine).
"""
import os
from google.adk.agents import LlmAgent

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")

FAQ = {
    "returns": "Items can be returned within 30 days with the original receipt. Electronics: 15-day window.",
    "shipping": "Standard shipping: 5-7 business days. Express (2-day): $12.99.",
    "warranty": "1-year manufacturer warranty on all products. Extended 3-year warranty available at checkout.",
    "payment": "We accept Visa, Mastercard, Amex, PayPal, and Apple Pay. No cryptocurrency.",
}

STORE_HOURS = {
    "monday": "9am–8pm",
    "tuesday": "9am–8pm",
    "wednesday": "9am–8pm",
    "thursday": "9am–9pm",
    "friday": "9am–9pm",
    "saturday": "10am–7pm",
    "sunday": "11am–6pm",
}


def look_up_faq(topic: str) -> dict:
    """Look up a frequently asked question by topic.

    Args:
        topic: The FAQ topic. One of: returns, shipping, warranty, payment.

    Returns:
        A dict with 'topic' and 'answer', or an error dict if not found.
    """
    key = topic.lower().strip()
    if key not in FAQ:
        return {"status": "error", "message": f"No FAQ for '{topic}'. Valid: {', '.join(FAQ)}."}
    return {"topic": key, "answer": FAQ[key]}


def get_store_hours(day: str) -> dict:
    """Get store opening hours for a specific day of the week.

    Args:
        day: Day of the week (e.g., monday, tuesday, ..., sunday).

    Returns:
        A dict with 'day' and 'hours', or an error dict if day is invalid.
    """
    key = day.lower().strip()
    if key not in STORE_HOURS:
        return {"status": "error", "message": f"Unknown day '{day}'. Use a weekday name."}
    return {"day": key, "hours": STORE_HOURS[key]}


root_agent = LlmAgent(
    name="faq_agent",
    model=MODEL,
    instruction=(
        "You are a customer support agent. Answer questions about returns, shipping, "
        "warranty, payment, and store hours using the available tools. "
        "Be concise and friendly."
    ),
    tools=[look_up_faq, get_store_hours],
)

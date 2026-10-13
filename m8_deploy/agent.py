import os
from google.adk.agents import LlmAgent

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")

FAQ = {
    "returns": "Items can be returned within 30 days of purchase with original receipt. Electronics have a 15-day window.",
    "shipping": "Standard shipping takes 5-7 business days. Express (2-day) is available for $12.99.",
    "warranty": "All products carry a 1-year manufacturer warranty. Extended 3-year warranty available at checkout.",
    "payment": "We accept Visa, Mastercard, Amex, PayPal, and Apple Pay. No cryptocurrency.",
}


def look_up_faq(topic: str) -> dict:
    """Look up a frequently asked question by topic.

    Args:
        topic: The FAQ topic. One of: returns, shipping, warranty, payment.

    Returns:
        A dict with 'topic' and 'answer', or an error dict if topic not found.
    """
    key = topic.lower().strip()
    if key not in FAQ:
        return {"status": "error", "message": f"No FAQ for '{topic}'. Valid topics: {', '.join(FAQ)}."}
    return {"topic": key, "answer": FAQ[key]}


root_agent = LlmAgent(
    name="faq_agent",
    model=MODEL,
    instruction=(
        "You are a customer support agent. Answer questions about returns, shipping, "
        "warranty, and payment by looking up the relevant FAQ entry. "
        "Be concise and friendly."
    ),
    tools=[look_up_faq],
)

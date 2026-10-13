import os
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")

BILLING_KEYWORDS = {"bill", "invoice", "charge", "payment", "refund", "account", "subscription", "fee"}


def topic_guardrail(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    """Block off-topic messages before they reach the model."""
    last_user_text = ""
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            for part in content.parts or []:
                if hasattr(part, "text") and part.text:
                    last_user_text = part.text.lower()
                    break
            break

    if last_user_text and not any(kw in last_user_text for kw in BILLING_KEYWORDS):
        print(f"[Callback] Blocked: '{last_user_text[:60]}...' — not billing-related")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="I can only assist with billing and account questions. How can I help with your bill or payment?")],
            )
        )
    return None


root_agent = LlmAgent(
    name="billing_support",
    model=MODEL,
    instruction=(
        "You are a billing support agent. Help customers with questions about "
        "their bills, invoices, payments, refunds, and account charges."
    ),
    before_model_callback=topic_guardrail,
)

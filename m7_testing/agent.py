import os
from google.adk.agents import LlmAgent

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")


def get_greeting(name: str) -> dict:
    """Generate a personalized greeting for a user.

    Args:
        name: The user's name to greet.

    Returns:
        A dict with 'greeting' containing the personalized message.
    """
    if not name or not name.strip():
        return {"greeting": "Hello, there! Welcome!"}
    return {"greeting": f"Hello, {name.strip()}! Welcome to the system!"}


root_agent = LlmAgent(
    name="greeter",
    model=MODEL,
    instruction=(
        "You are a friendly greeter. When the user tells you their name, "
        "use the get_greeting tool to generate a personalized greeting. "
        "If they don't provide a name, use the tool with an empty string."
    ),
    tools=[get_greeting],
)

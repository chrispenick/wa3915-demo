from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types

from m7_testing.agent import get_greeting


class FakeLlm(BaseLlm):
    """Scripted model backend — steps through a list of LlmResponse objects in order."""

    model: str = "fake"
    responses: list = []

    async def generate_content_async(self, *args, **kwargs):
        yield self.responses.pop(0)


def tool_call_response(tool_name: str, args: dict) -> LlmResponse:
    """Build an LlmResponse that triggers a real tool call."""
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(function_call=types.FunctionCall(name=tool_name, args=args))],
        )
    )


def text_response(text: str) -> LlmResponse:
    """Build a plain text LlmResponse."""
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=text)],
        )
    )


def make_runner(responses: list) -> InMemoryRunner:
    fake = FakeLlm(responses=responses)
    agent = LlmAgent(
        name="greeter",
        model=fake,
        instruction="Greet the user by name using the get_greeting tool.",
        tools=[get_greeting],
    )
    return InMemoryRunner(agent=agent)


async def test_greeting_with_name():
    runner = make_runner([
        tool_call_response("get_greeting", {"name": "Alice"}),
        text_response("Hello, Alice! Welcome to the system!"),
    ])
    events = await runner.run_debug("Hi, my name is Alice!")
    final = [e for e in events if e.is_final_response()][-1]
    assert "Alice" in final.content.parts[0].text


async def test_greeting_without_name():
    runner = make_runner([
        tool_call_response("get_greeting", {"name": ""}),
        text_response("Hello, there! Welcome!"),
    ])
    events = await runner.run_debug("I'd like a greeting please.")
    final = [e for e in events if e.is_final_response()][-1]
    assert "Welcome" in final.content.parts[0].text

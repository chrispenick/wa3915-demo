import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
SERVER_URL = "http://localhost:8001"

APP_NAME = "homework_helper_demo"
USER_ID = "instructor"

QUESTIONS = [
    "How many kilometers is 26.2 miles (a marathon)?",
    "Convert 98.6 degrees Fahrenheit to Celsius.",
]


async def main():
    converter = RemoteA2aAgent(
        name="unit_converter",
        agent_card=f"{SERVER_URL}/.well-known/agent.json",
    )

    homework_helper = LlmAgent(
        name="homework_helper",
        model=MODEL,
        instruction=(
            "You are a homework helper. For any question involving unit conversions, "
            "delegate to the unit_converter specialist. Then present the answer clearly."
        ),
        sub_agents=[converter],
    )

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=homework_helper, app_name=APP_NAME, session_service=session_service)

    for question in QUESTIONS:
        print(f"\nUser: {question}")
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=question)]),
        ):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

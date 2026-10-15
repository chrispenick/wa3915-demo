import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App
from google.genai import types

load_dotenv()

from m4_callbacks.agent import root_agent
from m4_callbacks.plugin import RequestCountPlugin

APP_NAME = "billing_demo"
USER_ID = "instructor"

MESSAGES = [
    "I was charged twice for my subscription last month.",
    "What's the best recipe for chocolate cake?",
    "Can I get a refund for the duplicate charge?",
]


async def main():
    plugin = RequestCountPlugin()
    session_service = InMemorySessionService()

    app = App(name=APP_NAME, root_agent=root_agent, plugins=[plugin])
    runner = Runner(app=app, session_service=session_service)

    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

    for msg in MESSAGES:
        print(f"\nUser: {msg}")
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=msg)]),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")

    print(f"\nPlugin total: {plugin.count} requests")


if __name__ == "__main__":
    asyncio.run(main())

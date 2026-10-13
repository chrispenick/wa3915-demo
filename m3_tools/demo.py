import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

from m3_tools.agent import root_agent

APP_NAME = "recipe_demo"
USER_ID = "instructor"


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={"dietary_preference": "vegetarian"},
    )

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    message = "I want to make pasta tonight. Do I have what I need?"
    print(f"User: {message}\n")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

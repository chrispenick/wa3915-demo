import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

from m5_workflow.workflow import pipeline

APP_NAME = "blog_pipeline_demo"
USER_ID = "instructor"


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

    runner = Runner(node=pipeline, app_name=APP_NAME, session_service=session_service)

    topic = "Why every developer should learn to read error logs"
    print(f"Topic: {topic}\n")
    print("=" * 60)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=topic)]),
    ):
        if event.is_final_response():
            author = getattr(event, "author", "unknown")
            print(f"\n[{author}]\n{event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

"""A1a: Built-in Search — agent using google_search for grounded answers with citations."""
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "search_demo"
USER_ID = "instructor"

research_agent = LlmAgent(
    name="research_assistant",
    model=MODEL,
    instruction=(
        "You are a research assistant with access to Google Search. "
        "Answer questions using web search to find current, accurate information. "
        "Always cite the sources you used at the end of your response."
    ),
    tools=[google_search],
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=research_agent, app_name=APP_NAME, session_service=session_service)

    question = "What is Google ADK (Agent Development Kit) and what are its main features for building AI agents?"
    print(f"User: {question}\n")
    print("=" * 60)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=question)]),
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")
            else:
                print("Agent: [No response — check GEMINI_API_KEY in .env]")


if __name__ == "__main__":
    asyncio.run(main())

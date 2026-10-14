"""A1c: MCP Toolset — agent connecting to a local MCP tool server via stdio."""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "mcp_demo"
USER_ID = "instructor"

MCP_SERVER = str(Path(__file__).parent / "simple_mcp_server.py")


async def main():
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[MCP_SERVER],
            )
        )
    )

    agent = LlmAgent(
        name="store_assistant",
        model=MODEL,
        instruction=(
            "You are a store assistant. Use your tools to check weather for shipping "
            "destinations and inventory levels for products. "
            "Answer clearly and concisely."
        ),
        tools=[mcp_toolset],
    )

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    questions = [
        "What's the weather in Tokyo right now?",
        "Do we have tablets in stock?",
        "I'm shipping laptops to London — how many do we have and what's the weather there?",
    ]

    print("MCP Toolset Demo")
    print("=" * 60)
    print(f"MCP server: {MCP_SERVER}\n")

    for question in questions:
        print(f"\nUser: {question}")
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=question)]),
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

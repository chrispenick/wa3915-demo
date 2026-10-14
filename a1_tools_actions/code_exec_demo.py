"""A1b: Code Execution — agent that writes and executes Python in Gemini's sandbox."""
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "code_exec_demo"
USER_ID = "instructor"

CSV_DATA = """month,revenue,expenses
January,45000,32000
February,52000,35000
March,48000,30000
April,61000,38000
May,57000,36000
June,63000,40000"""

analysis_agent = LlmAgent(
    name="data_analyst",
    model=MODEL,
    instruction=(
        "You are a data analysis assistant. When given data, write Python code "
        "to analyze it, execute the code, and interpret the results clearly."
    ),
    code_executor=BuiltInCodeExecutor(),
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=analysis_agent, app_name=APP_NAME, session_service=session_service)

    prompt = (
        f"Given this sales CSV, compute monthly profit (revenue - expenses), "
        f"identify the best and worst months, and calculate average monthly profit:\n\n{CSV_DATA}"
    )
    print(f"User: {prompt}\n")
    print("=" * 60)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=prompt)]),
    ):
        author = getattr(event, "author", "")
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "executable_code") and part.executable_code:
                    print(f"\n[{author}] Executing code:\n{part.executable_code.code[:400]}\n...")
                elif hasattr(part, "code_execution_result") and part.code_execution_result:
                    print(f"\n[{author}] Output:\n{part.code_execution_result.output[:400]}")
        if event.is_final_response():
            if event.content and event.content.parts:
                text = next(
                    (p.text for p in event.content.parts if getattr(p, "text", None)),
                    None,
                )
                if text:
                    print(f"\n[Final Answer]\n{text}")
                # else: intermediate final event with no text (e.g. code result); skip
            # else: no content — likely a model error; already handled above


if __name__ == "__main__":
    asyncio.run(main())

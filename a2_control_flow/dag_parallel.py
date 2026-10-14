"""A2b: Parallel DAG — research workflow with fan-out branches then synthesis."""
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "dag_parallel_demo"
USER_ID = "instructor"

summarizer_agent = LlmAgent(
    name="summarizer",
    model=MODEL,
    instruction=(
        "You are a research summarizer. Given a topic, write a concise 3-sentence "
        "factual summary of its key points. Be objective and informative."
    ),
    output_key="summary",
)

critic_agent = LlmAgent(
    name="critic",
    model=MODEL,
    instruction=(
        "You are a critical analyst. Given a topic, identify 2-3 common misconceptions "
        "or counterarguments. Be analytical and challenge assumptions."
    ),
    output_key="critique",
)

synthesis_agent = LlmAgent(
    name="synthesizer",
    model=MODEL,
    instruction=(
        "You are a synthesis expert. The session state contains:\n"
        "  'summary' — key facts about the topic\n"
        "  'critique' — counterarguments and nuances\n"
        "Weave them together into a balanced 4-5 sentence analysis."
    ),
)

# Tuple in the middle of the edge chain = parallel fan-out.
# ADK synchronizes at synthesis_agent after both branches complete.
research_pipeline = Workflow(
    name="research_pipeline",
    edges=[("START", (summarizer_agent, critic_agent), synthesis_agent)],
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(node=research_pipeline, app_name=APP_NAME, session_service=session_service)

    topic = "The impact of large language models on software development productivity"
    print(f"Topic: {topic}")
    print("=" * 60)
    print("Graph: START → [summarizer ∥ critic] → synthesizer\n")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=topic)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            author = getattr(event, "author", "unknown")
            print(f"[{author}]\n{event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())

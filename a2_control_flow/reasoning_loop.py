"""A2c: Reasoning Loop — iterative draft refinement with quality-gated early exit."""
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "loop_demo"
USER_ID = "instructor"

QUALITY_THRESHOLD = 7
MAX_ITERATIONS = 4

draft_agent = LlmAgent(
    name="drafter",
    model=MODEL,
    instruction=(
        "You are a technical writer. Write a clear, concise explanation (3-5 sentences) "
        "of the given topic. If there is evaluator feedback in the conversation, "
        "revise your explanation to address it."
    ),
    output_key="draft",
)


def check_quality_and_escalate(callback_context: CallbackContext) -> Optional[types.Content]:
    """After evaluator runs: read quality_score; escalate if threshold met."""
    score_raw = callback_context.state.get("quality_score", "0")
    try:
        # Handle formats like "7", "7/10", "7 — good clarity"
        score = int(str(score_raw).strip().split("/")[0].split()[0].split("—")[0].strip())
    except (ValueError, IndexError):
        score = 0

    iteration = callback_context.state.get("_iteration", 0) + 1
    callback_context.state["_iteration"] = iteration
    print(f"\n[Loop] Iteration {iteration} — quality score: {score}/10")

    if score >= QUALITY_THRESHOLD:
        print(f"[Loop] Score {score} >= threshold {QUALITY_THRESHOLD}. Escalating to exit loop.")
        callback_context.actions.escalate = True
        return types.Content(
            role="model",
            parts=[types.Part(text=f"Quality threshold met ({score}/10). Exiting loop.")],
        )

    print(f"[Loop] Score {score} below threshold {QUALITY_THRESHOLD}. Continuing...")
    return None


evaluator_agent = LlmAgent(
    name="evaluator",
    model=MODEL,
    instruction=(
        "You are a quality evaluator for technical writing. Review the latest draft "
        "in the conversation. Score it from 1 to 10 on clarity, accuracy, and conciseness "
        f"(threshold for acceptance is {QUALITY_THRESHOLD}/10). "
        "Output ONLY: a single integer on the first line, then one sentence of feedback."
    ),
    output_key="quality_score",
    after_agent_callback=check_quality_and_escalate,
)

# LoopAgent runs [drafter → evaluator] repeatedly until escalate or max_iterations.
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[draft_agent, evaluator_agent],
    max_iterations=MAX_ITERATIONS,
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=refinement_loop, app_name=APP_NAME, session_service=session_service)

    topic = "How does vector search work in RAG (retrieval-augmented generation)?"
    print("Iterative Draft Refinement Loop")
    print("=" * 60)
    print(f"Topic: {topic}")
    print(f"Max iterations: {MAX_ITERATIONS}  |  Exit threshold: {QUALITY_THRESHOLD}/10\n")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=topic)]),
    ):
        if event.is_final_response():
            author = getattr(event, "author", "unknown")
            print(f"\n[{author}] {event.content.parts[0].text}")

    sess = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
    iters = sess.state.get("_iteration", "?")
    final_score = sess.state.get("quality_score", "?")
    draft = sess.state.get("draft", "")
    print(f"\n{'=' * 60}")
    print(f"Completed in {iters} iteration(s) — final quality score: {final_score}")
    if draft:
        print(f"\nFinal draft:\n{draft[:500]}{'...' if len(str(draft)) > 500 else ''}")


if __name__ == "__main__":
    asyncio.run(main())

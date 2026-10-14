"""A2a: State Machine — content moderation pipeline using session state as FSM phases."""
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "fsm_demo"
USER_ID = "instructor"

PHASES = ["INGEST", "ANALYZE", "DECIDE", "DONE"]

PHASE_INSTRUCTIONS: dict[str, str] = {
    "INGEST": (
        "PHASE: INGEST. Extract and list the key factual claims from the user-provided content. "
        "Output bullet points only — no commentary, no preamble."
    ),
    "ANALYZE": (
        "PHASE: ANALYZE. Review the claims listed in the conversation. "
        "Identify any policy violations (misinformation, defamation, incitement). "
        "Output: a short list of issues found and a risk_score from 0 (safe) to 10 (critical)."
    ),
    "DECIDE": (
        "PHASE: DECIDE. Based on the analysis in the conversation, make a final moderation decision. "
        "Risk 0-3 → APPROVE. Risk 4-6 → FLAG FOR REVIEW. Risk 7-10 → REJECT. "
        "State the decision and a one-sentence rationale."
    ),
    "DONE": (
        "PHASE: DONE. Write a 2-sentence summary of the complete moderation pipeline outcome."
    ),
}


def phase_instruction(ctx: ReadonlyContext) -> str:
    """Callable instruction — returns the prompt for the current FSM phase."""
    phase = str(ctx.state.get("phase", "INGEST"))
    return PHASE_INSTRUCTIONS.get(phase, PHASE_INSTRUCTIONS["INGEST"])


def advance_phase(callback_context: CallbackContext) -> Optional[types.Content]:
    """After each turn, advance phase → next in the FSM sequence."""
    current = str(callback_context.state.get("phase", "INGEST"))
    idx = PHASES.index(current) if current in PHASES else 0
    if idx < len(PHASES) - 1:
        next_phase = PHASES[idx + 1]
        callback_context.state["phase"] = next_phase
        print(f"  [FSM] → {next_phase}")
    return None


moderation_agent = LlmAgent(
    name="content_moderator",
    model=MODEL,
    instruction=phase_instruction,
    after_agent_callback=advance_phase,
)

CONTENT = (
    "Breaking: Mayor caught red-handed accepting $500K in bribes for zoning approvals. "
    "City hall denies all wrongdoing. Citizens are furious and calling for immediate resignation. "
    "Sources: two anonymous tipsters and a leaked internal document."
)

TURNS = [
    f"Moderate the following content:\n\n{CONTENT}",
    "Continue to the analysis step.",
    "Make the final moderation decision.",
    "Summarize the pipeline outcome.",
]


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, state={"phase": "INGEST"}
    )
    runner = Runner(agent=moderation_agent, app_name=APP_NAME, session_service=session_service)

    print("Content Moderation FSM")
    print("=" * 60)
    print(f"Input: {CONTENT}\n")

    for turn in TURNS:
        sess = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
        phase = sess.state.get("phase", "INGEST")
        print(f"\n[Phase: {phase}]")
        print(f"User: {turn[:80]}{'...' if len(turn) > 80 else ''}")

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=turn)]),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                print(f"Agent: {text[:400]}{'...' if len(text) > 400 else ''}")

        if phase == "DONE":
            break

    print("\n[Pipeline complete]")


if __name__ == "__main__":
    asyncio.run(main())

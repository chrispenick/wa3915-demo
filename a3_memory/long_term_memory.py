"""A3b: Long-Term Memory — custom JSON file memory service with recall across sessions.

Flow:
  Session 1 — user states a preference → saved via add_session_to_memory()
  Session 2 — user asks a related question → agent calls load_memory, recalls preference
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import MemoryEntry, SearchMemoryResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import load_memory
from google.genai import types

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
APP_NAME = "memory_demo"
USER_ID = "instructor"
MEMORY_FILE = Path("a3_memory/memories.json")


class JsonFileMemoryService(BaseMemoryService):
    """Simple file-backed memory: stores session summaries as JSON records.

    In production, swap this for VertexAiRagMemoryService — the agent and
    Runner setup are identical; only the class changes.
    """

    def __init__(self, path: Path = MEMORY_FILE) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]")

    def _load(self) -> list[dict]:
        return json.loads(self._path.read_text())

    def _save(self, records: list[dict]) -> None:
        self._path.write_text(json.dumps(records, indent=2))

    async def add_session_to_memory(self, session: Session) -> None:
        """Extract the final user→agent exchange from the session and store it."""
        records = self._load()
        user_text = agent_text = ""
        for event in reversed(session.events):
            if event.content and event.content.parts:
                text = " ".join(
                    p.text for p in event.content.parts if hasattr(p, "text") and p.text
                )
                if event.content.role == "user" and not user_text:
                    user_text = text
                elif event.content.role == "model" and not agent_text:
                    agent_text = text
            if user_text and agent_text:
                break

        if user_text or agent_text:
            records.append({
                "app_name": session.app_name,
                "user_id": session.user_id,
                "session_id": session.id,
                "user": user_text,
                "agent": agent_text,
            })
            self._save(records)
            print(f"  [Memory] Saved: \"{user_text[:60]}...\"")

    async def search_memory(
        self, *, app_name: str, user_id: str, query: str
    ) -> SearchMemoryResponse:
        """Return records whose user or agent text contains any query word."""
        records = self._load()
        keywords = query.lower().split()
        matches = []
        for rec in records:
            if rec.get("app_name") != app_name or rec.get("user_id") != user_id:
                continue
            combined = (rec.get("user", "") + " " + rec.get("agent", "")).lower()
            if any(kw in combined for kw in keywords):
                text = f"Past exchange — User: {rec['user']} | Agent: {rec['agent']}"
                matches.append(
                    MemoryEntry(content=types.Content(
                        role="user", parts=[types.Part(text=text)]
                    ))
                )
        print(f"  [Memory] Search '{query}' → {len(matches)} match(es)")
        return SearchMemoryResponse(memories=matches)


memory_agent = LlmAgent(
    name="memory_assistant",
    model=MODEL,
    instruction=(
        "You are a helpful assistant with long-term memory. "
        "When answering questions, use the load_memory tool to recall relevant "
        "past conversations with this user and incorporate that context."
    ),
    tools=[load_memory],
)


async def run_session(
    session_service: InMemorySessionService,
    memory_service: JsonFileMemoryService,
    runner: Runner,
    message: str,
    label: str,
) -> None:
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    print(f"\n{'=' * 60}")
    print(f"{label}")
    print(f"User: {message}")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")

    sess = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
    await memory_service.add_session_to_memory(sess)


async def main():
    session_service = InMemorySessionService()
    memory_service = JsonFileMemoryService()
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    print("Long-Term Memory Demo")
    print(f"Memory file: {MEMORY_FILE.resolve()}")

    await run_session(
        session_service, memory_service, runner,
        message="I prefer Python code examples with type hints and no magic numbers.",
        label="Session 1 — stating a preference",
    )

    await run_session(
        session_service, memory_service, runner,
        message="Can you show me how to compute a running average in Python?",
        label="Session 2 — related question (agent should recall preference)",
    )


if __name__ == "__main__":
    asyncio.run(main())

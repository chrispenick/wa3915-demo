# A3: Memory — Talk Track

## Overview

ADK has two distinct memory layers: **session state** (structured key-value data that lives inside a run) and **long-term memory** (unstructured recall that persists across sessions). These demos cover both.

---

## A3a: State Scopes (`state_scopes.py`)

### Setup

```bash
python a3_memory/state_scopes.py
```

No API key needed — this demo only uses `InMemorySessionService`.

### Talk points

**The four prefixes**

ADK state keys are plain strings. The prefix controls scope — no separate storage backend required:

| Prefix | Scope | Cleared when |
|---|---|---|
| `temp:` | Single invocation | After each `runner.run_async` call |
| *(none)* | Current session | New session created |
| `user:` | All sessions, same user_id | Never (within the service lifetime) |
| `app:` | All users and sessions | Never (within the service lifetime) |

**What the demo shows**

The script uses `append_event` with explicit `state_delta` values — the same mechanism `Runner` uses internally after every tool call. This makes the scope boundaries visible without depending on LLM output:

```python
# Set all four scope types at once
await session_service.append_event(session=sess_a1, event=Event(
    author="demo",
    actions=EventActions(state_delta={
        "temp:scratch":      "ephemeral work data",
        "session_note":      "working on ML project",
        "user:preference":   "prefers bullet points",
        "app:request_count": 1,
    }),
))
```

Then create a *new session for the same user* and observe:
- `temp:scratch` and `session_note` are gone
- `user:preference` is still present
- Create a session for a *different user*: `user:preference` is absent, `app:request_count` is shared

**The mental model**

Think of the four scopes as rings:
```
app:  ┌────────────────────────────────────────────┐
      │  user:alice  ┌──────────────────────────┐  │
      │              │  session_1  ┌──────────┐ │  │
      │              │             │  temp:   │ │  │
      │              │             └──────────┘ │  │
      │              └──────────────────────────┘  │
      └────────────────────────────────────────────┘
```

In production: `InMemorySessionService` → `VertexAiSessionService` for durable user/app state. Prefixes work the same way.

---

## A3b: Long-Term Memory (`long_term_memory.py`)

### Setup

```bash
python a3_memory/long_term_memory.py
```

Creates `a3_memory/memories.json` on first run.

### Talk points

**What problem long-term memory solves**

Session state lives in one session. Long-term memory bridges sessions: the agent in Session 2 can recall what was discussed in Session 1 — even days later. This is how personalization and continuity are built.

**The `BaseMemoryService` interface**

ADK defines two abstract methods:

```python
class BaseMemoryService(ABC):
    async def add_session_to_memory(self, session: Session) -> None: ...
    async def search_memory(self, *, app_name, user_id, query) -> SearchMemoryResponse: ...
```

`JsonFileMemoryService` implements both with a flat JSON file. The same interface is implemented by `VertexAiRagMemoryService` for production.

**The `load_memory` tool**

```python
from google.adk.tools import load_memory

memory_agent = LlmAgent(tools=[load_memory], ...)
runner = Runner(agent=memory_agent, memory_service=JsonFileMemoryService(), ...)
```

When the agent calls `load_memory(query="preferences")`, ADK routes to `memory_service.search_memory(...)` and injects the results into the model's context. The agent code is identical whether backed by JSON or Vertex AI RAG.

**What to show live**

Run the script. Observe:
1. Session 1: the user states a preference; `add_session_to_memory` saves it
2. Session 2: the agent calls `load_memory` and finds the relevant record; its answer reflects the recalled preference

Point to the `[Memory]` print lines that show search query and match count — these come from inside `JsonFileMemoryService`, confirming retrieval happened.

**The production swap**

```python
# Development
memory_service = JsonFileMemoryService()

# Production — one line change, agent is unchanged
from google.adk.memory import VertexAiRagMemoryService
memory_service = VertexAiRagMemoryService(rag_corpus="projects/.../ragCorpora/...")
```

---

## Key Takeaway

| Layer | Lives in | Cleared when | ADK primitive |
|---|---|---|---|
| Session state | `session.state` | New session (scoped by prefix) | `state["key"]` in tools/callbacks |
| Long-term memory | `BaseMemoryService` impl | Never (you manage) | `load_memory` tool + `Runner(memory_service=...)` |

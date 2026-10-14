"""A3a: State Scopes — demonstrate all four ADK state prefix behaviors.

Scope     Prefix    Lifetime
-------   --------  ----------------------------------------
temp      temp:     Single invocation only (cleared after run)
session   (none)    Current session only
user      user:     All sessions for the same user_id
app       app:      All users and sessions in the app
"""
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions

APP_NAME = "scope_demo"
USER_A = "alice"
USER_B = "bob"


async def set_state(
    session_service: InMemorySessionService,
    session,
    delta: dict,
    label: str,
) -> None:
    """Append an event with a state_delta to simulate a tool writing state."""
    event = Event(
        author="demo",
        actions=EventActions(state_delta=delta),
    )
    await session_service.append_event(session=session, event=event)
    print(f"  [set] {label}: {delta}")


async def show_state(
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    label: str,
) -> None:
    sess = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    state = dict(sess.state)
    print(f"\n  [{label}]")
    if not state:
        print("    (empty)")
        return
    for key in sorted(state):
        scope = (
            "temp"    if key.startswith("temp:")  else
            "user"    if key.startswith("user:")  else
            "app"     if key.startswith("app:")   else
            "session"
        )
        print(f"    {scope:8s}  {key!r:35s}  = {state[key]!r}")


async def main():
    session_service = InMemorySessionService()

    print("ADK State Scopes Demo")
    print("=" * 70)

    # --- User A, Session 1: write all four scope types ---
    print("\nStep 1: User A, Session 1 — write all four scope types")
    sess_a1 = await session_service.create_session(app_name=APP_NAME, user_id=USER_A)
    await set_state(session_service, sess_a1, {
        "temp:scratch": "ephemeral work data",       # cleared after invocation
        "session_note": "working on ML project",     # session-scoped
        "user:preference": "prefers bullet points",  # persists across sessions
        "app:request_count": 1,                      # shared across all users
    }, "all scopes")
    # temp: keys are NEVER committed to session storage — the session service
    # strips them before persisting. They are only visible to tool functions
    # within the same runner.run_async() invocation via tool_context.state.
    await show_state(session_service, APP_NAME, USER_A, sess_a1.id,
                     "After write (temp:scratch already gone — not stored)")

    # --- User A, Session 2: new session, same user ---
    print("\nStep 2: User A, Session 2 — new session (same user)")
    sess_a2 = await session_service.create_session(app_name=APP_NAME, user_id=USER_A)
    await show_state(session_service, APP_NAME, USER_A, sess_a2.id,
                     "New session — temp: and session keys gone; user: persists")

    # --- User B, Session 1: different user ---
    print("\nStep 3: User B, Session 1 — different user")
    sess_b1 = await session_service.create_session(app_name=APP_NAME, user_id=USER_B)
    await set_state(session_service, sess_b1, {"app:request_count": 2}, "increment app counter")
    await show_state(session_service, APP_NAME, USER_B, sess_b1.id,
                     "Different user — user: absent; app: shared (request_count incremented)")

    print("\n" + "=" * 70)
    print("Scope summary:")
    print("  temp:    — gone after each invocation (cleared by Runner)")
    print("  session  — gone when a new session is created")
    print("  user:    — persists across sessions for the same user_id")
    print("  app:     — shared across all users and sessions in the app")


if __name__ == "__main__":
    asyncio.run(main())

# M7 — Testing and Deploying: Demo Talk Track

## Before Class
- [ ] `uv sync` done
- [ ] No API key needed — this demo runs fully offline
- [ ] Confirm tests pass: `uv run pytest m7_testing/ -v`

## Step 1 — Motivate the approach (30 sec)

> "Before we look at code, let me ask: what are we actually testing?
> Not the model — Gemini is Google's problem. We're testing OUR code:
> does the tool return the right dict? Does the agent actually call the tool?
> Does it handle a failed tool gracefully?
> To test these things deterministically, we need to control what 'the model' returns."

## Step 2 — Open test_agent.py: FakeLlm (1.5 min)

Open `m7_testing/test_agent.py`. Start with `class FakeLlm(BaseLlm)`.

> "ADK's model interface is `BaseLlm`. Any subclass that implements
> `generate_content_async` works as a drop-in backend — including ours.
> We give it a list of scripted `LlmResponse` objects. Each call pops the next one."

Point at `LlmAgent(name=..., model=FakeLlm(...), ...)` in `make_runner`:
> "Here's the key: we pass the fake model directly to `LlmAgent` as the `model` argument.
> No monkeypatching, no env vars — the agent never touches a real API client."

Point at `tool_call_response("get_greeting", {"name": "Alice"})`:
> "This builds an `LlmResponse` with a `FunctionCall` part.
> When ADK processes this event, it actually calls `get_greeting(name='Alice')`
> on your real tool function. We're testing the real tool — not mocking it."

Point at `text_response("Hello, Alice! ...")`:
> "After the tool runs and returns its result, the scripted 'model' produces this text.
> In a real run Gemini would write something here; in our test we control it exactly."

## Step 3 — Open the test functions (1 min)

Point at `InMemoryRunner(agent=agent)`:
> "`InMemoryRunner` sets up all the plumbing — session service, artifact service,
> memory service. No environment variables, no network. Everything in RAM."

Point at `runner.run_debug("Hi, my name is Alice!")`:
> "`run_debug` is a convenience wrapper: pass a string, get back a list of events.
> No session IDs to manage. Great for simple unit tests."

Point at `assert "Alice" in final.content.parts[0].text`:
> "Simple assertion. We're not asserting exact phrasing — that's the model's job.
> We're asserting that the agent used the tool result correctly and the name appeared."

## Step 4 — Run the tests (30 sec)

```bash
uv run pytest m7_testing/ -v
```

> "Two tests, two passes, no API key, deterministic every time.
> This is what your CI pipeline looks like for ADK agents."

## Step 5 — Mention adk api_server (30 sec)

> "Deployment is the other half of this module. We won't run it now,
> but `adk api_server m1_anatomy` would serve your agent as a FastAPI app
> with `/run` and `/run_sse` endpoints. `adk deploy agent_engine` pushes it
> to Vertex AI Agent Runtime with full observability.
> Lab 9 covers both — I'll demo the deploy step live for the whole class."

## Step 6 — Bridge to Lab (30 sec)

> "In Lab 8, you'll write tests for a weather agent. The repo provides a `FakeLlm`
> class built on the same `BaseLlm` pattern — read it before you write tests,
> it's your reference implementation. Your job is to write the test cases:
> tool call succeeds, tool fails gracefully, and one AgentEvaluator test
> that compares the full response to expected output."

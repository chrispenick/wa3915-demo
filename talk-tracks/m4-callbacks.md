# M4 — Callbacks, Plugins, and Evaluation: Demo Talk Track

## Before Class
- [ ] `.env` loaded
- [ ] `uv sync` done
- [ ] Have three messages ready to paste (in demo.py comments)

## Step 1 — Open agent.py: the callback (2 min)

Open `m4_callbacks/agent.py`.

Point at `topic_guardrail` function signature:
> "Callbacks fire at specific boundaries in the agent loop. This one fires
> *before* the model call — `before_model_callback`.
> The signature is fixed: `(CallbackContext, LlmRequest) -> LlmResponse | None`.
> ADK calls it for you. You don't wire it into the event loop yourself."

Point at the keyword scan and `return LlmResponse(...)`:
> "If we detect an off-topic message, we return a `LlmResponse` directly.
> That *replaces* the model call — the model is never invoked.
> No latency. No tokens charged. The guardrail runs in microseconds."

Point at `return None`:
> "Returning `None` means 'let it pass.' The model call happens normally.
> This is the binary decision: intercept, or allow."

Point at `before_model_callback=topic_guardrail` on `LlmAgent`:
> "The callback is attached to the agent here. It's scoped to this one agent.
> If you had a coordinator with sub-agents, this callback would NOT fire
> for the sub-agents. For process-wide behavior, you need a plugin."

## Step 2 — Open plugin.py (1 min)

Open `m4_callbacks/plugin.py`.

Point at `class RequestCountPlugin(BasePlugin)`:
> "A plugin applies to *all* agents in the runner, not just one.
> Think of it as a cross-cutting concern: logging, rate limiting, caching."

Point at `on_user_message`:
> "This hook fires for every incoming user message, regardless of which agent
> handles it. Returns `None` to let the message through unchanged,
> or returns a modified `Content` to intercept it."

Point at `self.count += 1`:
> "This is what we'll verify in the output — the count should be 3,
> because we sent 3 messages, even though the model only ran for 2 of them."

## Step 3 — Open demo.py and run (1 min)

Open `m4_callbacks/demo.py`. Point at `App(name=..., root_agent=..., plugins=[plugin])`:
> "This is the ADK 2.x pattern for attaching plugins. Important note:
> passing `plugins=` directly to `Runner` is deprecated — always use `App`."

```bash
uv run python -m m4_callbacks.demo
```

> "Watch the output. Message 1 is on-topic — model runs.
> Message 2 is off-topic — the `[Callback] Blocked:` line fires, no model call.
> Message 3 is on-topic — model runs again.
> At the end: `Plugin total: 3 requests` — the plugin saw all three."

## Step 4 — Bridge to Lab (30 sec)

> "In Lab 4, you'll add two callbacks: one that blocks prompt injection attempts
> before the model call, and one that redacts card numbers *after* the model call —
> `after_model_callback`. You'll also build a `LoggingPlugin` that logs every
> model and tool call across the whole session. Same patterns, different hooks."

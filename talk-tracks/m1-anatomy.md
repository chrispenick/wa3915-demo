# M1 — Anatomy of an ADK Agent: Demo Talk Track

## Before Class
- [ ] `uv sync` run in `wa3915-demo/`
- [ ] `.env` loaded: `export $(cat .env | xargs)`
- [ ] Have two terminal panes open (one for `adk web`, one for the browser)
- [ ] Browser open to `http://localhost:8000` (will be the Dev UI)

## Step 1 — Open agent.py (1 min)

Open `m1_anatomy/agent.py`. Start at the top.

> "Before we open anything, let me ask: what IS an ADK agent, really?
> It's mostly three things — a model, an instruction, and a list of tools.
> Let me show you."

Point at `check_component_status`:
> "Here's the tool. Notice: typed parameters, a full docstring with `Args:` and `Returns:`.
> These are not optional documentation — ADK reads this to build the JSON schema
> that the model sees. If the docstring is wrong or missing, the model may never call
> the tool correctly."

Point at `root_agent = LlmAgent(...)`:
> "And here's the agent. Three arguments: model, instruction, tools.
> There's no business logic in this file. The LLM decides *when* to call the tool
> and *what* to do with the result. Our job is to give it the right tools and instructions."

Point at the `root_agent` variable name:
> "This name — `root_agent` — matters. ADK's CLI tools scan for this exact name
> in `agent.py` when you run `adk run` or `adk web`. It's a convention, not magic."

## Step 2 — Start the Dev UI and walk through it (2 min)

Run in terminal:
```bash
uv run adk web m1_anatomy
```

> "Open the browser. You'll see the Dev UI — this is your best debugging tool in ADK.
> Let's send it a message."

Type in the chat: *"My laptop has been really sluggish all morning."*

> "Watch the Events panel on the right while it responds."

Point at the event stream:
> "See these events? `user` → `model` decides to call `check_component_status` →
> that's a `FunctionCall` event → the tool runs → `FunctionResponse` comes back →
> model reads it → final `model` text. That's the ADK loop.
> When you write `async for event in runner.run_async(...)` in code, these are
> exactly the events you're iterating over."

## Step 3 — Open demo.py (1 min)

> "Let me show you the same thing as code."

Open `m1_anatomy/demo.py`.

Point at `InMemorySessionService` and `create_session`:
> "A session holds conversation history. `InMemorySessionService` stores it in RAM —
> fine for demos and testing. The labs use the same thing."

Point at `Runner(agent=root_agent, ...)`:
> "Runner drives the loop. It takes the agent, the session service, and an app name.
> `adk web` builds one of these internally — we're just doing it explicitly."

Point at `async for event in runner.run_async(...)`:
> "And here's the loop. Every turn produces multiple events.
> `event.is_final_response()` marks the last one — the text you show the user."

## Step 4 — Bridge to Lab (30 sec)

> "In Lab 1, you'll build a city assistant that tells users what time it is in a given city.
> Same pattern exactly: one `LlmAgent`, one function tool, one `Runner`.
> The tool will call a real time-zone library instead of returning mock data.
> You'll also run it through `adk run` and inspect these same events in the Dev UI."

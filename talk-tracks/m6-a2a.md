# M6 — Multi-Agent Systems and A2A: Demo Talk Track

## Before Class
- [ ] Two terminal panes open side by side
- [ ] `.env` loaded in BOTH terminals
- [ ] `uv sync` done
- [ ] Verify server starts cleanly: `uv run python m6_a2a/server.py` → Ctrl-C

## Step 1 — Open server.py (1.5 min)

Open `m6_a2a/server.py`.

> "Multi-agent means more than one agent. In a local coordinator pattern,
> sub-agents live in the same process. In A2A, they live in different processes —
> or different machines entirely. Let me show you how little code this takes."

Point at `root_agent = LlmAgent(...)`:
> "Just a normal ADK agent. Nothing special about it — no A2A imports,
> no special base class. Any `LlmAgent` can become an A2A server."

Point at `a2a_app = to_a2a(root_agent, host="localhost", port=PORT)`:
> "This one line wraps the agent in a fully A2A-compliant HTTP server.
> It creates all the endpoints, the agent card, task management — everything."

> "You'll see `[EXPERIMENTAL]` in the terminal output. That's expected.
> All A2A features carry this warning in ADK 2.9.2. Ignore it."

Point at `uvicorn.run(a2a_app, ...)`:
> "The result of `to_a2a()` is a Starlette ASGI app.
> We run it with uvicorn just like any FastAPI app."

## Step 2 — Start the server (30 sec)

Terminal 1:
```bash
uv run python m6_a2a/server.py
```

> "Server is up. Let's verify the agent card."

Terminal 2:
```bash
curl -s http://localhost:8001/.well-known/agent.json | python3 -m json.tool
```

> "This JSON is how other agents discover this service — its name, description,
> capabilities, and URL. `RemoteA2aAgent` fetches this automatically."

## Step 3 — Open client.py (1.5 min)

Open `m6_a2a/client.py`.

Point at `converter = RemoteA2aAgent(name=..., agent_card="http://localhost:8001/...")`:
> "This is the client-side proxy. `RemoteA2aAgent` fetches the agent card,
> discovers the server's capabilities, and wraps it as a local agent interface.
> Note the import path — this is NOT in `google.adk.agents` or `google.adk.a2a`.
> It's `from google.adk.agents.remote_a2a_agent import RemoteA2aAgent`. Full path."

Point at `homework_helper = LlmAgent(..., sub_agents=[converter])`:
> "And here's the key point. `converter` is in `sub_agents` exactly like a local
> `LlmAgent` would be. The coordinator has no idea whether its sub-agent is local
> or running on a server across the network. That's the value of A2A —
> local-vs-remote becomes a deployment decision, not a code rewrite."

## Step 4 — Run the client (30 sec)

Terminal 2:
```bash
uv run python m6_a2a/client.py
```

> "Watch the request travel: coordinator receives the question, transfers to
> `unit_converter` via A2A, server handles it, response comes back."

Optional: Kill the server with Ctrl-C, run the client again.
> "Connection error, immediately. This is why the lab notes say:
> if your remote sub-agent call fails, check that the server terminal is still running."

## Step 5 — Bridge to Lab (30 sec)

> "In Lab 7, you'll start with a coordinator over two *local* specialists.
> Then you'll expose the tech specialist as an A2A server — same `to_a2a()` call —
> and swap it for a `RemoteA2aAgent` in the coordinator. You'll need two terminals,
> just like this. The billing specialist stays local; tech goes remote."

# A4: Deployment Walk-Through — Talk Track

## Overview

The same `agent.py` runs unchanged from laptop to production. The deployment target is an infrastructure decision, not a code change. This demo walks through four stops: local API server → Docker → Cloud Run → Agent Engine.

**Agent used:** `a4_deployment/agent.py` — the M8 FAQ agent with a `get_store_hours` tool added.

---

## A4a: Local API Server (live)

### Run it

```bash
uv run adk api_server a4_deployment
```

Server starts at `http://localhost:8000`. Then in another terminal:

```bash
bash a4_deployment/curl_examples.sh
```

### What the script shows

1. `GET /list_apps` — enumerate deployed agents
2. `POST /apps/{app}/users/{user}/sessions` — create a session
3. `POST /run` — synchronous round-trip, returns a JSON array of events
4. `POST /run_sse` — streaming, returns Server-Sent Events

### Talk points

This IS the API shape you'll use in production. Cloud Run exposes the exact same endpoints — `api_server` is the dress rehearsal. You can wire a UI, a Slack bot, or an integration test against either without changing the client code.

The session/user model in the REST API maps directly to ADK's `Runner(user_id=..., session_id=...)` — sessions are first-class, not bolt-ons.

---

## A4b: Docker Packaging (live up to build)

### Generate the Dockerfile

```bash
uv run adk deploy docker a4_deployment --output_dir /tmp/adk-docker-out
```

ADK writes `Dockerfile` and `start_server.sh` into `/tmp/adk-docker-out`. Read the generated `Dockerfile` live:

```bash
cat /tmp/adk-docker-out/Dockerfile
```

### Key layers to narrate

```dockerfile
FROM python:3.12-slim          # minimal base
COPY . /app                    # your agent code
RUN pip install google-adk     # single dependency
CMD ["./start_server.sh"]      # runs `adk api_server`
```

### Build and run locally (optional)

```bash
docker build -t adk-demo /tmp/adk-docker-out
docker run -e GEMINI_API_KEY=$GEMINI_API_KEY -p 8080:8080 adk-demo
```

Then hit `http://localhost:8080` — same API, same agent, now containerized.

### Talk points

The artifact is a self-contained image. Everything the agent needs is inside: Python, ADK, your code. `adk deploy docker` handles the boilerplate so you don't write Dockerfiles by hand for each project.

If Docker is unavailable in the lab environment, show the generated `Dockerfile` and narrate the layers — the generation step always works.

---

## A4c: Cloud Run (illustrated)

### The command

```bash
# Not run live — illustrative
adk deploy cloud_run a4_deployment \
  --project $GCP_PROJECT \
  --region us-central1 \
  --with_ui
```

### What happens

1. Builds the Docker image (same as A4b)
2. Pushes to Artifact Registry
3. Deploys to Cloud Run, wires HTTPS, IAM, and autoscaling
4. Returns a URL like `https://a4-deployment-xxxxx-uc.a.run.app`

### Canned output (for narration)

```
Building Docker image...  ✓
Pushing to Artifact Registry...  ✓
Deploying to Cloud Run...  ✓
Service URL: https://a4-deployment-xxxxx-uc.a.run.app
UI URL:      https://a4-deployment-xxxxx-uc.a.run.app/dev-ui/
```

The agent is now reachable over HTTPS from anywhere. IAM controls who can call it. Cloud Run autoscales to zero when idle.

### Architecture diagram

```
User / Client
     │ HTTPS
     ▼
Cloud Run Service (your container)
  ├── POST /run
  ├── POST /run_sse
  └── GET  /list_apps
     │
     ▼
Gemini API (model + tools)
```

### Talk points

One command, HTTPS + autoscaling + IAM — no Kubernetes, no load balancer config, no TLS cert management. The agent code is untouched from A4a.

---

## A4d: Agent Engine (whiteboard / talk track only)

### What Agent Engine adds

| Concern | DIY Cloud Run | Agent Engine |
|---|---|---|
| Session persistence | Your `SessionService` impl | Managed, durable |
| Long-term memory | Your `MemoryService` impl | Built-in Vertex AI RAG |
| Observability | Cloud Logging + manual | Structured audit log, built-in tracing |
| Compliance | Manual IAM + VPC controls | Enterprise-grade, audit-ready |
| Gemini grounding | Explicit `google_search` tool | Native, integrated |

### The code difference

```python
# Cloud Run / local
from google.adk.sessions import InMemorySessionService
runner = Runner(agent=root_agent, session_service=InMemorySessionService(), ...)

# Agent Engine — only the Runner setup changes; agent.py is untouched
from vertexai.preview.reasoning_engines import AdkApp
app = AdkApp(agent=root_agent, enable_tracing=True)
app.deploy(...)
```

### When to choose Agent Engine

- Compliance-sensitive workloads (financial, healthcare, government)
- Enterprise scale with multiple users sharing a durable session layer
- Teams that want managed state + observability with no infra work
- Workloads that benefit from native Gemini grounding and Vertex AI memory

### Talk points

The ADK abstraction is the point. You built the agent once. The deployment target — local API server, Docker, Cloud Run, Agent Engine — is an ops decision made by the team at deploy time. The agent code is the same file in all four cases.

---

## Key Takeaway

```
local dev      →   docker build   →   Cloud Run      →   Agent Engine
uv run adk        adk deploy         adk deploy         AdkApp.deploy()
api_server         docker             cloud_run

                    ← same agent.py throughout →
```

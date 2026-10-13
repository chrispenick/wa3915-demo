# M8 — Deployment: Demo Talk Track

## Before Class
- [ ] `uv sync` done
- [ ] `.env` loaded
- [ ] Docker Desktop running (needed for Step 2)
- [ ] If showing Cloud Run live: `gcloud auth login` done, billing-enabled GCP project ready, personal `GEMINI_API_KEY` (not Vocareum)

## Vocareum Key Note
The Vocareum key (`GOOGLE_GEMINI_BASE_URL=https://gemini.vocareum.com`) works for local steps (api_server, docker run).
It will NOT work for Cloud Run or Agent Engine — Vocareum's proxy is IP-restricted to student laptops.
For cloud deployment steps, use a personal Gemini API key and your own GCP project.

---

## Step 1 — adk api_server: the HTTP interface (2 min)

> "Every ADK agent you've built this week can be exposed as a REST API with one command.
> No code changes. No FastAPI boilerplate. Just this:"

```bash
uv run adk api_server m8_deploy
```

> "The server is now running on port 8000. It exposes two endpoints:
> `POST /run` for synchronous responses, `GET /run_sse` for streaming.
> Let's call it."

In a second terminal:
```bash
curl -s -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "faq_demo",
    "user_id": "test",
    "session_id": "s1",
    "new_message": {"role": "user", "parts": [{"text": "What is your return policy?"}]}
  }' | python3 -m json.tool
```

> "That JSON response is what any frontend, mobile app, or orchestration system
> would consume. The same contract `adk web` uses internally.
> This is what you'd put behind a load balancer or service mesh."

---

## Step 2 — adk deploy docker: containerize it (1.5 min)

> "Now let's containerize it. ADK generates the Dockerfile for you."

```bash
uv run adk deploy docker m8_deploy --output_dir ./docker_out
```

> "Open `docker_out/Dockerfile`. It's a minimal Python image — uv installs dependencies,
> the agent starts on port 8080. No magic. You could customize it."

Build and run locally:
```bash
docker build -t faq-agent ./docker_out
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  -e GOOGLE_GEMINI_BASE_URL=$GOOGLE_GEMINI_BASE_URL \
  -e ADK_MODEL=$ADK_MODEL \
  faq-agent
```

> "Same `POST /run` interface, now in a container.
> You could push this image anywhere: Cloud Run, GKE, a VM, your own k8s cluster."

---

## Step 3 — adk deploy cloud_run: one command to GCP (1 min)

> "If you have a GCP project and billing enabled, `adk deploy cloud_run` does everything:
> builds the image, pushes to Artifact Registry, deploys, gives you a URL."

Show the command (run it only if you have a personal GCP project + real Gemini API key):
```bash
uv run adk deploy cloud_run m8_deploy \
  --project YOUR_GCP_PROJECT \
  --region us-central1 \
  --with_ui
```

> "That `--with_ui` flag deploys the ADK Dev UI alongside the API — so you get the
> same Events panel you used in M1, now running in the cloud."

> "Important: this does NOT work with the Vocareum course key.
> Vocareum's proxy restricts by IP — a Cloud Run VM's egress IP won't pass.
> Use a personal Gemini API key for any cloud deployment."

---

## Step 4 — Agent Engine: when to use it (30 sec)

> "There's a fourth option: `adk deploy agent_engine`. This is Vertex AI's managed
> agent runtime — it handles sessions, state persistence, observability, and scaling.
> It requires a GCP project with Vertex AI enabled.
> It cannot use the Vocareum proxy key — you'd switch to Vertex AI credentials.
> We'll talk through the trade-offs in the Q&A, but here's the headline:
> use Cloud Run when you own the infra; use Agent Engine when you want Google to
> manage sessions, state, and scaling for you."

---

## Step 5 — Bridge to Lab (30 sec)

> "In Lab 8, you'll take your testing agent from M7 and deploy it.
> You'll run `adk api_server` first to verify the HTTP contract,
> then deploy to Cloud Run — using your own GCP project and a real API key.
> The Dockerfile is generated for you. The only decision is which region."

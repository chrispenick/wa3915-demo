# M5 — Workflow Orchestration: Demo Talk Track

## Before Class
- [ ] `.env` loaded
- [ ] `uv sync` done
- [ ] Note: this demo takes ~30 sec to run (two model calls)

## Step 1 — Open workflow.py (2 min)

Open `m5_workflow/workflow.py`.

> "So far, every demo has been one agent answering one question.
> Workflows let you chain agents together in a deterministic sequence —
> the output of step one feeds into step two, automatically."

Point at the import:
> "`from google.adk.workflow import Workflow` — note: singular, not `workflows`.
> This trips people up. There's also no `google.adk.workflows` package."

Point at `outline_agent` and `draft_agent` with `output_key`:
> "Each node is just an `LlmAgent` you've already seen. The new thing is `output_key`.
> When `outline_agent` finishes, ADK writes its response into session state
> under the key `'outline'`. Then `draft_agent`'s instruction says
> 'read the outline in state' — that's how data flows between nodes."

Point at `pipeline = Workflow(name=..., edges=[("START", outline_agent, draft_agent)])`:
> "The `edges` list defines the graph. This tuple is a sequential chain:
> `START` fires `outline_agent`, which fires `draft_agent` when it completes.
> `'START'` is a string sentinel ADK converts internally — you don't import anything extra."

> "One important constraint: `SequentialAgent`, `ParallelAgent`, and `LoopAgent`
> from older ADK 1.x code CANNOT be nested inside a Workflow graph in ADK 2.5+.
> They'll raise a validation error. Use Workflow's own edge syntax instead."

## Step 2 — Open run_demo.py (30 sec)

Open `m5_workflow/run_demo.py`.

Point at `Runner(node=pipeline, app_name=..., session_service=...)`:
> "Notice `node=` instead of `agent=`. A Workflow is a `BaseNode`, not a `BaseAgent`,
> so Runner uses `node=`. The rest of the setup is identical to what you've seen.
> Also: `adk web` and `adk run` can't discover Workflows — they only look for `root_agent`.
> That's why labs that use Workflow always provide a `run_workflow.py` script."

## Step 3 — Run it (1 min)

```bash
uv run python -m m5_workflow.run_demo
```

> "Two output blocks, two different authors. `outline_agent` produced bullet points.
> `draft_agent` received those bullet points through session state
> and wrote an opening paragraph. One model call per node."

## Step 4 — Bridge to Lab (30 sec)

> "In Lab 6, you'll build a longer pipeline: plan → two parallel research agents
> (fan-out with `JoinNode`) → draft → revise loop → finalize.
> The parallel fan-out syntax is a nested tuple in `edges`:
> `('START', (agent_a, agent_b), join_node)`. Same pattern, more nodes."

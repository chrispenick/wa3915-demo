# WA3915 Instructor Demos

Short walkthrough demos for each WA3915 module. Run before students enter the corresponding lab.

## Setup

```bash
cp .env.example .env
# Fill in your GEMINI_API_KEY
uv sync
```

## Running the Demos

| Module | Command |
|--------|---------|
| M1 Anatomy | `uv run adk web m1_anatomy` or `uv run python -m m1_anatomy.demo` |
| M2 Structured Outputs | `uv run python -m m2_structured.demo` |
| M3 Tools | `uv run adk web m3_tools` or `uv run python -m m3_tools.demo` |
| M4 Callbacks | `uv run python -m m4_callbacks.demo` |
| M5 Workflow | `uv run python -m m5_workflow.run_demo` |
| M6 A2A | Terminal 1: `uv run python m6_a2a/server.py` / Terminal 2: `uv run python m6_a2a/client.py` |
| M7 Testing | `uv run pytest m7_testing/ -v` |

See `talk-tracks/` for instructor notes for each module.

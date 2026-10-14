# WA3915 Instructor Demos

Short walkthrough demos for each WA3915 module. Run before students enter the corresponding lab.

## Setup

```bash
cp .env.example .env
# Fill in your GEMINI_API_KEY
uv sync
```

## Modules (M1–M8)

| Module | Command |
|--------|---------|
| M1 Anatomy | `uv run adk web m1_anatomy` or `uv run python -m m1_anatomy.demo` |
| M2 Structured Outputs | `uv run python -m m2_structured.demo` |
| M3 Tools | `uv run adk web m3_tools` or `uv run python -m m3_tools.demo` |
| M4 Callbacks | `uv run python -m m4_callbacks.demo` |
| M5 Workflow | `uv run python -m m5_workflow.run_demo` |
| M6 A2A | Terminal 1: `uv run python m6_a2a/server.py` / Terminal 2: `uv run python m6_a2a/client.py` |
| M7 Testing | `uv run pytest m7_testing/ -v` |
| M8 Deploy | `uv run adk api_server m8_deploy` — **local API server only** (see note below) |

> **M8 note:** The M8 demo runs the ADK API server locally (`http://localhost:8000`). It does not perform a live Cloud Run or Agent Engine deployment. The talk track at `talk-tracks/m8-deploy.md` covers the full deployment path with illustrated commands and canned output.

## Appendices (A1–A4)

Standalone bonus demos covering capability areas not shown in M1–M8. Each runs with only the Vocareum Gemini API key — no additional cloud setup required.

| Appendix | Topic | Commands |
|----------|-------|---------|
| A1a Built-in Search | `google_search` grounding with citations | `uv run python a1_tools_actions/search_demo.py` |
| A1b Code Execution | `BuiltInCodeExecutor` sandbox loop | `uv run python a1_tools_actions/code_exec_demo.py` |
| A1c MCP Toolset | `McpToolset` + local MCP server | `uv run python a1_tools_actions/mcp_demo.py` |
| A2a State Machine | FSM phases via session state + callbacks | `uv run python a2_control_flow/state_machine.py` |
| A2b Parallel DAG | `Workflow` fan-out tuple syntax | `uv run python a2_control_flow/dag_parallel.py` |
| A2c Reasoning Loop | `LoopAgent` with quality-gated early exit | `uv run python a2_control_flow/reasoning_loop.py` |
| A3a State Scopes | `temp:` / session / `user:` / `app:` prefixes | `uv run python a3_memory/state_scopes.py` |
| A3b Long-Term Memory | Custom `BaseMemoryService` + `load_memory` tool | `uv run python a3_memory/long_term_memory.py` |
| A4 Deployment | Local API server → Docker → Cloud Run → Agent Engine | `uv run adk api_server a4_deployment` then `bash a4_deployment/curl_examples.sh` |

See `talk-tracks/` for instructor notes for each module and appendix.

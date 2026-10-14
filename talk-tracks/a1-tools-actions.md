# A1: Tools and Actions — Talk Track

## Overview

Beyond simple Python function tools covered in M3, ADK supports three built-in capability categories that require no external APIs or infrastructure to demo: grounded web search, sandboxed code execution, and the Model Context Protocol (MCP). Each demo script is standalone.

---

## A1a: Built-in Search (`search_demo.py`)

### Setup

```bash
python a1_tools_actions/search_demo.py
```

### Talk points

**Why google_search is different from a custom search tool**

A custom search tool would call a search API (Serper, Brave, etc.), parse results, and inject them into the prompt — your code owns the retrieval and citation logic.

`google_search` is a *Gemini built-in*: the model itself performs retrieval using Google Search grounding. Source links are returned in the response's metadata automatically. No search API key. No chunking/embedding step.

```python
from google.adk.tools import google_search

research_agent = LlmAgent(
    tools=[google_search],   # class reference — ADK instantiates it
    ...
)
```

**What to show live**

Run the script. Point to: the grounded answer, and the citation links included at the bottom. Note that the question is phrased around something genuinely current — the model cannot answer reliably from parametric memory alone, so grounding adds measurable value.

**The limitation**

Grounding ties you to Gemini (not a portable abstraction). If you need provider-agnostic retrieval, implement a plain function tool that calls any search API.

---

## A1b: Code Execution (`code_exec_demo.py`)

### Setup

```bash
python a1_tools_actions/code_exec_demo.py
```

### Talk points

**What `BuiltInCodeExecutor` does**

Attaches Gemini's built-in Python sandbox to the agent. The model can write Python, execute it, observe the output, revise the code, and iterate — all within a single `runner.run_async` call. Your calling code sees only the final answer.

```python
from google.adk.code_executors import BuiltInCodeExecutor

analysis_agent = LlmAgent(
    code_executor=BuiltInCodeExecutor(),  # no tools= entry needed
    ...
)
```

**What the event stream reveals (optional deep-dive)**

The script prints intermediate events showing `executable_code` and `code_execution_result` parts. Walk through the write → run → observe → revise loop:
- `executable_code.code` — what the model wrote
- `code_execution_result.output` — stdout from the sandbox
- The model then reads the output and either refines the code or composes the final answer

**The limitation**

The sandbox is Gemini-hosted — it runs in Google's cloud, not locally. Long-running or file-I/O-heavy tasks need a different executor (e.g., a local subprocess executor you build yourself).

---

## A1c: MCP Toolset (`mcp_demo.py` + `simple_mcp_server.py`)

### Setup

```bash
python a1_tools_actions/mcp_demo.py   # starts the MCP server as a subprocess automatically
```

### Talk points

**What MCP is**

Model Context Protocol — a standard for exposing tools as a network-accessible service. The server exposes tools; the client (your agent) discovers and calls them over a transport (stdio, HTTP/SSE). The agent has no knowledge of the server implementation.

**Two files, clean separation**

`simple_mcp_server.py` — a standalone tool server using FastMCP:
```python
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("demo-tools")

@mcp.tool()
def get_weather(city: str) -> str: ...

@mcp.tool()
def check_inventory(product: str) -> str: ...

mcp.run(transport="stdio")
```

`mcp_demo.py` — the agent wires to it via `StdioServerParameters`:
```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioServerParameters

mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=["a1_tools_actions/simple_mcp_server.py"],
    )
)

agent = LlmAgent(tools=[mcp_toolset], ...)
```

ADK launches the server as a subprocess, negotiates the MCP handshake, and exposes the server's tools to the LLM automatically.

**Why this matters**

Swap `StdioServerParameters` for `SseServerParams` and you point the agent at a remote MCP service — the agent code doesn't change. The same `McpToolset` wires to any MCP-compatible server: local, cross-language, third-party.

In production: run the MCP server as a separate process or container and point to it via SSE. The agent remains unchanged.

---

## Key Takeaway

| Tool category | What you write | What ADK/Gemini handles |
|---|---|---|
| `google_search` | Nothing (just pass the class) | Search, grounding, citation injection |
| `BuiltInCodeExecutor` | Nothing (just pass the instance) | Sandbox lifecycle, write/run/observe loop |
| `McpToolset` | A connection config | Tool discovery, protocol negotiation, invocation |

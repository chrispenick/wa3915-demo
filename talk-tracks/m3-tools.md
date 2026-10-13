# M3 — Tools and External Integrations: Demo Talk Track

## Before Class
- [ ] `.env` loaded
- [ ] `uv sync` done
- [ ] Have `adk web` ready to show the Events panel

## Step 1 — Open agent.py: the first tool (1.5 min)

Open `m3_tools/agent.py`. Start with `find_recipe`.

> "A function tool is just a Python function. The model decides to call it;
> ADK executes it. Three things have to be right or the model won't use it correctly."

Point at the type annotations on `find_recipe`:
> "First: typed parameters. `dish: str`, `dietary: str = 'none'`. ADK infers the
> JSON schema from these. The default value `'none'` tells the model the parameter
> is optional."

Point at the docstring `Args:` section:
> "Second: the `Args:` block. This is what the model reads to understand what to pass.
> It's not documentation for humans — it's the model's instruction manual.
> Remove it and the model will guess wrong."

Point at `return {"status": "not_found", "message": ...}`:
> "Third: the return dict. Tools should never raise exceptions for expected failures —
> return `{'status': 'error', ...}` instead. The model reads this and decides
> what to tell the user. ADK's retry machinery fires for *unexpected* exceptions —
> let those propagate."

## Step 2 — Show ToolContext (1 min)

Point at `check_pantry_item(ingredient: str, tool_context: ToolContext)`:
> "This is the ToolContext pattern. See the second parameter?
> ADK injects it automatically because of the type annotation.
> The *model* never passes it — ADK does, at call time.
> What can you do with it? Read and write session state."

Point at `tool_context.state.get("dietary_preference", "none")`:
> "Here we're reading `dietary_preference` that was set when the session was created.
> This is how tools know about user preferences or previous conversation context
> without the model having to pass that data explicitly."

## Step 3 — Run with Dev UI (1 min)

```bash
uv run adk web m3_tools
```

Type: *"I want to make pasta tonight. Do I have what I need?"*

> "Watch the Events panel. You'll see the model call `find_recipe` first,
> then call `check_pantry_item` once for each key ingredient. The model
> orchestrates the tool calls — we never told it the order. That's the power
> of tool-based agents."

## Step 4 — Bridge to Lab (30 sec)

> "In Lab 3, you'll build a store assistant with `get_order_status` and
> `check_inventory`. You'll also use `ToolContext` to track a shopping cart
> across multiple tool calls — same injection pattern. And in Challenge 2,
> you'll connect to an MCP server via `McpToolset`, which follows the same
> function-call model."

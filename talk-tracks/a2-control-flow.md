# A2: Planning and Control Flow — Talk Track

## Overview

M5 covered linear chains (`Workflow` with sequential edges). These three demos show three more control-flow shapes: a finite state machine driven by session state, a parallel fan-out DAG, and an open-ended iteration loop.

---

## A2a: State Machine (`state_machine.py`)

### Setup

```bash
python a2_control_flow/state_machine.py
```

### Talk points

**The core idea**

ADK has no FSM class. The primitive is `session.state` + a callable `instruction` + an `after_agent_callback` that advances the phase counter. A single `LlmAgent` changes its persona each turn by reading state.

```python
PHASES = ["INGEST", "ANALYZE", "DECIDE", "DONE"]

def phase_instruction(ctx: ReadonlyContext) -> str:
    phase = ctx.state.get("phase", "INGEST")
    return PHASE_INSTRUCTIONS[phase]

def advance_phase(callback_context: CallbackContext) -> None:
    current = callback_context.state.get("phase", "INGEST")
    idx = PHASES.index(current)
    if idx < len(PHASES) - 1:
        callback_context.state["phase"] = PHASES[idx + 1]

moderation_agent = LlmAgent(
    instruction=phase_instruction,      # callable — re-evaluated each turn
    after_agent_callback=advance_phase, # mutates state after each turn
)
```

**What to show live**

Watch the `[Phase: X]` prefix change on each turn. The same agent object handles four completely different prompts — extract, analyze, decide, summarize — with no branching in the calling code.

**When to use it**

Any pipeline where the valid actions depend on what's already been done: intake → validation → approval → notification, or triage → diagnosis → treatment → discharge.

**The alternative**

Four separate `LlmAgent` instances in a `Workflow` chain. More verbose but easier to reason about. Use the FSM pattern when the phase logic is data-driven (e.g., loaded from config) or when you need to serialize/restore state across restarts.

---

## A2b: Parallel DAG (`dag_parallel.py`)

### Setup

```bash
python a2_control_flow/dag_parallel.py
```

### Talk points

**The syntax**

A tuple inside a `Workflow` edge chain means "fan out to all these nodes in parallel":

```python
research_pipeline = Workflow(
    name="research_pipeline",
    edges=[("START", (summarizer_agent, critic_agent), synthesis_agent)],
    #              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #              tuple = parallel fan-out
    #              ADK synchronizes at synthesis_agent
)
```

Compare with M5's linear chain:
```python
# M5 — sequential
pipeline = Workflow(edges=[("START", outline_agent, draft_agent)])

# A2b — parallel then join
pipeline = Workflow(edges=[("START", (summarizer_agent, critic_agent), synthesis_agent)])
```

**What to show live**

Both `summarizer` and `critic` will appear in the output before `synthesizer`. Note that the order of the two parallel outputs may vary — they race. The synthesizer reads `summary` and `critique` from session state (set via `output_key` on each agent).

**How `output_key` bridges the branches**

Parallel branches share session state. Each branch writes its result under its own key. The join-point agent reads both:
```python
summarizer_agent = LlmAgent(output_key="summary", ...)
critic_agent     = LlmAgent(output_key="critique", ...)
synthesis_agent  = LlmAgent(instruction="... use 'summary' and 'critique' from state ...", ...)
```

**When to use it**

Independent subtasks where latency matters: generate + evaluate + classify all happening in one round-trip rather than three sequential calls.

---

## A2c: Reasoning Loop (`reasoning_loop.py`)

### Setup

```bash
python a2_control_flow/reasoning_loop.py
```

### Talk points

**The pattern**

`LoopAgent` runs its `sub_agents` list repeatedly until either `max_iterations` is reached or a sub-agent emits an event with `actions.escalate = True`.

```python
refinement_loop = LoopAgent(
    sub_agents=[draft_agent, evaluator_agent],
    max_iterations=4,
)
```

**How early exit works**

The evaluator's `after_agent_callback` reads the quality score from state and sets `escalate = True` when the threshold is met. Returning a `Content` object ensures the event carrying `escalate=True` is actually yielded to the LoopAgent:

```python
def check_quality_and_escalate(callback_context: CallbackContext) -> Optional[types.Content]:
    score = int(callback_context.state.get("quality_score", "0"))
    if score >= QUALITY_THRESHOLD:
        callback_context.actions.escalate = True
        return types.Content(role="model", parts=[types.Part(text="Quality met.")])
    return None
```

**What to show live**

Run twice:
1. First run — model usually converges in 1-2 iterations (score jumps above threshold quickly)
2. Comment out the escalation block to force it to run all 4 iterations; observe `max_iterations` as the safety net

**The deprecation note**

`LoopAgent` and `ParallelAgent` are marked deprecated in favor of `Workflow`. For new production code, `Workflow` with a loop-back edge is the preferred approach. `LoopAgent` remains fully functional and is still the clearest way to *teach* open-ended iteration — it surfaces the concept without graph-syntax overhead.

---

## Key Takeaway

| Pattern | ADK primitive | Exit condition |
|---|---|---|
| FSM | callable `instruction` + `after_agent_callback` | State-driven; you control turns in the driver loop |
| Parallel DAG | `Workflow` tuple edge syntax | Graph edges; joins when all branches complete |
| Reasoning loop | `LoopAgent` + `escalate` | Quality threshold OR `max_iterations` safety net |

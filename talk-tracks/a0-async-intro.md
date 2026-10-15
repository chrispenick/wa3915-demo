# A0 — Python async/await Primer

**Run:** `uv run python a0_async_intro/async_demo.py`  
**Duration:** ~8 minutes  
**Purpose:** Build the mental model students need before async ADK code makes sense.

---

## Why this demo exists

ADK code is async end-to-end — `runner.run_async()`, `async for event in ...`, callbacks. Students who don't have the async mental model will cargo-cult that code without understanding why it's structured that way. This demo gives them the foundation in ~10 minutes, with no ADK, no LLMs — just Python.

---

## The core metaphor (open with this)

> Imagine a single chef in a kitchen.  
> **Synchronous:** start making pasta, stand there watching the water boil, do nothing else until it's done, then start the sauce.  
> **Asynchronous:** put the water on, then start the sauce while you wait. When the water boils, come back to it.  
> Same chef. Same kitchen. No cloning. Just *not waiting around doing nothing.*

asyncio is cooperative multitasking: coroutines voluntarily yield control at `await` points. The event loop picks up the next ready coroutine. No threads, no OS preemption.

---

## Scene 1 — Coroutine basics (~2 min)

**Point at the output line:** `fetch_weather(...) → <coroutine object ...>`

> Calling `async def fetch_weather(...)` doesn't call the function — it creates a coroutine **object**. Python hasn't touched the function body yet.  
> `await coro` is what actually runs it. And while it's sleeping (simulating a network wait), the event loop is free to run other coroutines.

**Key lines to highlight in the code:**
```python
coro = fetch_weather("Tokyo", latency=0.5)   # object, not a call
result = await coro                           # NOW it runs
```

**Common student mistake:** forgetting `await` and getting a coroutine object instead of a result — Python 3.10+ warns about this with "coroutine was never awaited".

---

## Scene 2 — Sequential vs concurrent (~3 min)

This is the "aha" scene. The timing numbers make the concept visceral.

**Sequential output:** ~5 seconds (sum of all latencies).  
**Concurrent output:** ~1.2 seconds (slowest single latency).

> Sequential: each `await` pauses the whole function until that one call finishes.  
> Concurrent: `asyncio.gather()` schedules all five coroutines *before* awaiting any of them. They all sleep at the same time. Wall-clock time is the slowest one, not the sum.

**Point at `asyncio.gather()`:**
```python
results = await asyncio.gather(
    fetch_weather("New York",  1.0),
    fetch_weather("London",    1.2),
    ...
)
```

> This is the pattern you'll see everywhere in ADK: gather parallel agent calls, gather tool calls, gather sub-agent results.

**Clarify the threading question** — students always ask:

> "Is this using threads?" No. It's one thread. One call stack. The event loop keeps a queue of coroutines that are *ready to run*. When a coroutine hits `await asyncio.sleep(...)`, it says "I'm not ready — wake me up later." The loop moves on. No OS thread switching, no locks, no race conditions on shared state.

**When NOT to use asyncio:**  
CPU-bound work (number crunching, image processing) — asyncio doesn't help because the CPU never gets to pause voluntarily. Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for that.

---

## Scene 3 — Tasks (~3 min)

**3a: `create_task` — fire and forget, await later**

> `asyncio.gather()` starts coroutines and immediately waits for all of them.  
> `create_task()` schedules a coroutine but lets you keep running. You can do other work, then `await` the task when you need the result.

```python
task_a = asyncio.create_task(slow_report("alpha", delay=1.5))
task_b = asyncio.create_task(slow_report("beta",  delay=0.7))
# both are now in flight — we can do other things here
await asyncio.sleep(0.3)          # still doing work
result_b = await task_b           # beta probably already done
result_a = await task_a
```

> In ADK: the runner creates tasks for each agent turn. The callback system uses this — an `after_agent_callback` fires as soon as the agent's task completes, while the runner continues processing the event stream.

**3b: Cancellation**

> Tasks can be cancelled at any point. The cancelled coroutine receives a `CancelledError` at its next `await`. This is how ADK implements timeouts and early loop exits — `callback_context.actions.escalate` ultimately cancels downstream tasks.

**3c: `asyncio.wait` with `FIRST_COMPLETED`**

> Use this when you want the *fastest* result: launch N coroutines, take whoever finishes first, cancel the rest. Classic pattern for redundant API calls or multi-provider fallback.

---

## Summary table (write on whiteboard or show this)

| Pattern | Schedules | Waits for |
|---------|-----------|-----------|
| `await coro` | 1 | 1 (immediately) |
| `asyncio.gather(c1, c2, ...)` | N | ALL N |
| `asyncio.create_task(coro)` | 1 | nothing yet — you decide |
| `asyncio.wait(..., FIRST_COMPLETED)` | N | first to finish |

---

## Bridge to ADK

> Every `runner.run_async()` call you'll see in this course is an async generator — it yields events as the agent processes them. The `async for event in runner.run_async(...)` loop is just Scene 1's `await` in a loop: suspend here, process the next event when it's ready, yield control between events so other coroutines (like a UI refresh or a parallel agent) can run.

The mental model is now complete: async/await → gather → tasks → ADK's runner.

"""
A0: Python async/await primer — three scenes illustrating asyncio fundamentals.

No ADK, no LLMs.  Just Python's event loop and cooperative multitasking.

Run:
    uv run python a0_async_intro/async_demo.py
"""
import asyncio
import random
import time


# ---------------------------------------------------------------------------
# Simulated I/O — stands in for a real network call
# ---------------------------------------------------------------------------
async def fetch_weather(city: str, latency: float) -> dict:
    """Pretend to call a weather API that takes `latency` seconds to respond."""
    await asyncio.sleep(latency)
    conditions = ["sunny", "cloudy", "rainy", "windy", "snowy"]
    return {
        "city": city,
        "temp_c": random.randint(-5, 35),
        "condition": random.choice(conditions),
    }


# ---------------------------------------------------------------------------
# Scene 1 — What is a coroutine?
# ---------------------------------------------------------------------------
async def scene_1_coroutine_basics():
    print(
        """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENE 1 — Coroutine basics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`async def` creates a *coroutine function*.
Calling it returns a coroutine OBJECT — it doesn't run yet.
`await` runs it and suspends the caller until it's done.
"""
    )

    # Calling the function doesn't execute it
    coro = fetch_weather("Tokyo", latency=0.5)
    print(f"  fetch_weather(...)  → {coro}")      # <coroutine object ...>
    print( "  Nothing happened yet — no network call, no sleep.")

    # await actually runs it
    print("\n  Calling: result = await fetch_weather('Tokyo', latency=0.5)")
    result = await coro
    print(f"  result  → {result}")

    print("\n  KEY: `await` is a suspension point.")
    print("  While this coroutine sleeps, the event loop can run OTHER coroutines.")


# ---------------------------------------------------------------------------
# Scene 2 — Sequential vs concurrent: the timing proof
# ---------------------------------------------------------------------------
CITIES = [
    ("New York",  1.0),
    ("London",    1.2),
    ("Sydney",    0.8),
    ("São Paulo", 0.9),
    ("Tokyo",     1.1),
]

async def _sequential() -> list[dict]:
    results = []
    for city, latency in CITIES:
        result = await fetch_weather(city, latency)  # wait for each in turn
        results.append(result)
        print(f"    ← {result['city']}: {result['temp_c']}°C, {result['condition']}")
    return results

async def _concurrent() -> list[dict]:
    # asyncio.gather schedules ALL coroutines before awaiting any of them
    results = await asyncio.gather(
        *[fetch_weather(city, latency) for city, latency in CITIES]
    )
    for r in results:
        print(f"    ← {r['city']}: {r['temp_c']}°C, {r['condition']}")
    return list(results)

async def scene_2_sequential_vs_concurrent():
    total_latency = sum(lat for _, lat in CITIES)

    print(
        f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENE 2 — Sequential vs concurrent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetching weather for {len(CITIES)} cities.
Each "API call" takes between 0.8–1.2 s.
Sum of all latencies: {total_latency:.1f} s
"""
    )

    print("  ── Sequential (await each one before starting the next) ──")
    t0 = time.perf_counter()
    await _sequential()
    seq_time = time.perf_counter() - t0
    print(f"  Sequential time: {seq_time:.2f}s  (≈ sum of all latencies)\n")

    print("  ── Concurrent (asyncio.gather — all in flight at once) ──")
    t0 = time.perf_counter()
    await _concurrent()
    con_time = time.perf_counter() - t0
    print(f"  Concurrent time: {con_time:.2f}s  (≈ slowest single latency)\n")

    speedup = seq_time / con_time
    print(f"  Speedup: {speedup:.1f}×")
    print(
        """
  WHY: asyncio is single-threaded.  No parallelism.
  But every `await asyncio.sleep(...)` releases the event loop
  so it can start the next coroutine immediately.
  All five "network calls" overlap in wall-clock time.
"""
    )


# ---------------------------------------------------------------------------
# Scene 3 — Tasks: fire-and-forget, racing, cancellation
# ---------------------------------------------------------------------------
async def slow_report(name: str, delay: float) -> str:
    print(f"    [{name}] starting (will take {delay:.1f}s)")
    await asyncio.sleep(delay)
    print(f"    [{name}] done")
    return f"{name} result"

async def scene_3_tasks():
    print(
        """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENE 3 — Tasks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`asyncio.create_task()` schedules a coroutine immediately
without awaiting it — useful when you want to kick off work
and continue doing other things first.
"""
    )

    # 3a: fire-and-forget then await later
    print("  ── 3a: create_task then do other work ──")
    task_a = asyncio.create_task(slow_report("alpha", delay=1.5))
    task_b = asyncio.create_task(slow_report("beta",  delay=0.7))

    print("    (both tasks are now scheduled — doing other work for 0.3s)")
    await asyncio.sleep(0.3)
    print("    (still here, beta probably finished soon)")

    result_b = await task_b
    result_a = await task_a
    print(f"    results: {result_b!r}, {result_a!r}\n")

    # 3b: cancellation
    print("  ── 3b: cancellation ──")
    task_c = asyncio.create_task(slow_report("gamma", delay=5.0))
    await asyncio.sleep(0.2)
    print("    cancelling gamma after 0.2s...")
    task_c.cancel()
    try:
        await task_c
    except asyncio.CancelledError:
        print("    caught CancelledError — task was cancelled cleanly\n")

    # 3c: asyncio.wait with FIRST_COMPLETED (race)
    print("  ── 3c: race with asyncio.wait(FIRST_COMPLETED) ──")
    contenders = [
        asyncio.create_task(slow_report("fast",   delay=0.6)),
        asyncio.create_task(slow_report("medium", delay=1.1)),
        asyncio.create_task(slow_report("slow",   delay=1.8)),
    ]
    done, pending = await asyncio.wait(contenders, return_when=asyncio.FIRST_COMPLETED)
    winner = done.pop()
    print(f"    winner: {winner.result()!r}")
    for t in pending:
        t.cancel()
    print("    remaining tasks cancelled\n")

    print(
        """
  KEY DISTINCTIONS:
    await coro          — create + schedule + wait, all in one line
    asyncio.gather()    — schedule N coroutines, wait for ALL
    asyncio.create_task() — schedule now, await later (or cancel)
    asyncio.wait()      — fine-grained control: FIRST_COMPLETED / ALL_COMPLETED
"""
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
async def main():
    print("=" * 58)
    print("  Python async/await primer")
    print("=" * 58)

    await scene_1_coroutine_basics()
    await scene_2_sequential_vs_concurrent()
    await scene_3_tasks()

    print("=" * 58)
    print("  Done.  See talk-tracks/a0-async-intro.md for instructor notes.")
    print("=" * 58)


if __name__ == "__main__":
    asyncio.run(main())

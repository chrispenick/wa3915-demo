# M2 — Structured Outputs: Demo Talk Track

## Before Class
- [ ] `.env` loaded
- [ ] `uv sync` done

## Step 1 — Open agent.py (1.5 min)

Open `m2_structured/agent.py`.

Point at `class CandidateAssessment(BaseModel)`:
> "Up to now, agents return plain text. That's great for chat — terrible for automation.
> If the next step in your pipeline needs to read the recommendation, parsing free text
> is fragile. `output_schema` solves this: tell the agent what shape to return,
> and ADK enforces it."

Point at `recommendation: Literal["advance", "reject", "hold"]`:
> "This is a typed field. The model *must* return exactly one of these three strings.
> If it returns 'maybe' or 'consider' — validation fails and ADK retries."

Point at `@field_validator("years_experience")`:
> "This is a Pydantic validator. Business rules go here: non-negative experience,
> allowed categories, required fields. If the rule fails, ADK knows the response
> is invalid and retries. Your contract with downstream systems is in this class."

Point at `root_agent = LlmAgent(..., output_schema=CandidateAssessment, output_key="assessment")`:
> "Two new parameters. `output_schema` tells ADK what JSON shape to expect and validate.
> `output_key` writes the validated object into session state under that key —
> so a downstream agent can read `state['assessment']` without re-parsing anything."

> "Important caveat: `output_schema` and `tools` on the same agent is only supported
> on some models. For the lab you'll use a schema-only agent and a separate tool agent
> if you need both."

## Step 2 — Run and inspect output (1.5 min)

```bash
uv run python -m m2_structured.demo
```

> "Watch the output. You'll see the raw JSON the model returned, then the typed Python
> object we built from it. Every field is typed. `recommendation` is uppercase because
> we printed it that way — the underlying value is the lowercase string from the schema."

If time permits, break the schema on purpose:
> "What happens if I add a field the model doesn't know about? Or remove `Literal`?
> The validator raises and ADK retries. That's what makes this reliable."

## Step 3 — Bridge to Lab (30 sec)

> "In Lab 2, you'll build a document classifier for an operations team inbox.
> Your `Classification` schema will have a category, a confidence score (0–1),
> and a summary. You'll add a field validator that rejects categories outside
> an allowed list — same pattern as what you just saw."

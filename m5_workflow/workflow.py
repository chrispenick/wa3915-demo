import os
from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")

outline_agent = LlmAgent(
    name="outline_agent",
    model=MODEL,
    instruction=(
        "You are a blog post outliner. Given a topic, produce a concise outline "
        "with 3-5 bullet points covering the main sections of the post. "
        "Output only the bullet points, no preamble."
    ),
    output_key="outline",
)

draft_agent = LlmAgent(
    name="draft_agent",
    model=MODEL,
    instruction=(
        "You are a blog post writer. The blog outline has been prepared and is "
        "available in state under the key 'outline'. "
        "Write a compelling opening paragraph (3-5 sentences) for the blog post "
        "based on that outline. Address the reader directly."
    ),
)

pipeline = Workflow(
    name="blog_pipeline",
    edges=[("START", outline_agent, draft_agent)],
)

import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

from m2_structured.agent import root_agent, CandidateAssessment

APP_NAME = "job_screener_demo"
USER_ID = "instructor"

RESUME = """
Candidate: Jordan Lee
Experience: 7 years in backend engineering, primarily Python and Go.
Recent role: Senior Engineer at DataFlow Inc., led a team of 4.
Skills: Distributed systems, Kubernetes, API design, mentoring.
Left previous role due to company acquisition.
"""


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    print("Resume submitted for screening...\n")

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=RESUME)]),
    ):
        if event.is_final_response():
            raw_json = event.content.parts[0].text
            assessment = CandidateAssessment.model_validate_json(raw_json)
            print(f"Name:             {assessment.name}")
            print(f"Experience:       {assessment.years_experience} years")
            print(f"Key strengths:    {', '.join(assessment.key_strengths)}")
            print(f"Recommendation:   {assessment.recommendation.upper()}")

    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print(f"\n[state] session.state['assessment'] is set: {'assessment' in final_session.state}")


if __name__ == "__main__":
    asyncio.run(main())

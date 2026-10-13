import os
import uvicorn
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")
PORT = 8001

root_agent = LlmAgent(
    name="unit_converter",
    model=MODEL,
    instruction=(
        "You are a unit conversion specialist. Convert between any units of measurement: "
        "length, weight, temperature, volume, speed, and more. "
        "Always show the original value, the converted value, and the unit names clearly."
    ),
)

a2a_app = to_a2a(root_agent, host="localhost", port=PORT)

if __name__ == "__main__":
    print(f"Starting unit_converter A2A server on http://localhost:{PORT}")
    print(f"Agent card: http://localhost:{PORT}/.well-known/agent.json")
    uvicorn.run(a2a_app, host="0.0.0.0", port=PORT)

import os
from google.adk.agents import LlmAgent

MODEL = os.environ.get("ADK_MODEL", "gemini-3.8-flash")

MOCK_STATUS = {
    "cpu": {"usage_percent": 94, "temperature_c": 87, "status": "critical"},
    "disk": {"usage_percent": 72, "read_mb_s": 45, "status": "ok"},
    "memory": {"usage_percent": 88, "available_gb": 1.2, "status": "warning"},
    "network": {"latency_ms": 12, "packet_loss_percent": 0, "status": "ok"},
}


def check_component_status(component: str) -> dict:
    """Check the health status of a system component.

    Args:
        component: The component to check. One of: cpu, disk, memory, network.

    Returns:
        A dict with health metrics and a status field ("ok", "warning", "critical").
    """
    key = component.lower()
    if key not in MOCK_STATUS:
        return {"status": "error", "message": f"Unknown component: {component}. Valid: cpu, disk, memory, network."}
    return MOCK_STATUS[key]


root_agent = LlmAgent(
    name="tech_support_triage",
    model=MODEL,
    instruction=(
        "You are a tech support triage agent. When a user describes a system problem, "
        "check the relevant component status using the check_component_status tool. "
        "Report the findings clearly and suggest next steps based on the status."
    ),
    tools=[check_component_status],
)

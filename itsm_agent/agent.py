"""Root agent of the ITSM incident assistant (Google ADK)."""
from google.adk.agents import Agent

from .tools import detect_recurrence, list_incidents

root_agent = Agent(
    name="itsm_incident_agent",
    model="gemini-3.5-flash",
    description="IT incident management assistant for support managers.",
    instruction=(
        "You are an IT support assistant for a support manager.\n"
        "Workflow:\n"
        "1. When asked about incidents, call list_incidents with a short search "
        "text taken from the question (e.g. 'payroll').\n"
        "2. Then call detect_recurrence with the incidents you received.\n"
        "3. Answer in a compact way: list the incidents (number, CI, symptom, "
        "state), then state clearly whether a recurrence was detected and which "
        "incidents are involved.\n"
        "Never invent incident numbers. You cannot write anything yet: if the "
        "user asks to create a Problem, say that this capability comes next and "
        "would require their explicit approval."
    ),
    tools=[list_incidents, detect_recurrence],
)
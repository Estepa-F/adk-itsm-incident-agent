"""Root agent of the ITSM incident assistant (Google ADK)."""
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import create_problem, detect_recurrence, list_incidents, propose_problem

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
        "4. If a recurrence is found, call propose_problem with that group and "
        "show the draft (title, CI, incidents) to the user. Ask: 'Shall I create "
        "this Problem record?' Do NOT call create_problem in the same turn.\n"
        "5. Only when the user explicitly agrees, call create_problem with the "
        "draft exactly as returned. Then summarize what was created and linked.\n"
        "Never invent incident or problem numbers."
    ),
    tools=[
        list_incidents,
        detect_recurrence,
        propose_problem,
        FunctionTool(create_problem, require_confirmation=True),
    ],
)
"""Root agent of the ITSM incident assistant (Google ADK)."""
import os

from google.adk.agents import Agent
from google.adk.tools import BaseTool, FunctionTool, ToolContext

from .tools import create_problem, detect_recurrence, list_incidents, propose_problem


def require_prior_approval(tool: BaseTool, args: dict, tool_context: ToolContext):
    """Session-state guard on create_problem (works on every runtime).

    Refuses the write unless a matching draft was proposed in an EARLIER turn
    and the model passes confirmed=True. Returning a dict skips the tool and
    hands that dict back to the model as the tool result.
    """
    if tool.name != "create_problem":
        return None
    state = tool_context.state
    pending = state.get("pending_draft") or {}
    draft = args.get("draft") or {}
    if not pending or pending.get("draft_id") != draft.get("draft_id"):
        return {"status": "refused", "reason": "No matching pending draft. Call propose_problem first and show it to the user."}
    if state.get("pending_draft_invocation") == tool_context.invocation_id:
        return {"status": "refused", "reason": "The draft was proposed in this same turn. Wait for the user's explicit approval in a later message."}
    if not args.get("confirmed"):
        return {"status": "refused", "reason": "confirmed must be true, and only after the user explicitly approved."}
    return None


# Framework-level confirmation (adk web dialog). Supported locally; not yet
# supported by the managed session service on Agent Runtime, hence the switch.
USE_UI_CONFIRMATION = os.environ.get("ADK_REQUIRE_TOOL_CONFIRMATION", "1") == "1"
create_problem_tool = (
    FunctionTool(create_problem, require_confirmation=True) if USE_UI_CONFIRMATION else create_problem
)

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
        "5. Only when the user explicitly agrees in a later message, call "
        "create_problem with the draft exactly as returned and confirmed=true. "
        "Then summarize what was created and linked.\n"
        "Never invent incident or problem numbers."
    ),
    tools=[list_incidents, detect_recurrence, propose_problem, create_problem_tool],
    before_tool_callback=require_prior_approval,
)
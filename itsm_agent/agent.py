from google.adk.agents import Agent

root_agent = Agent(
    name="itsm_incident_agent",
    model="gemini-3.5-flash",
    description="IT incident management assistant for support managers.",
    instruction=(
        "You are an IT support assistant for a support manager. "
        "For now you have no tools: greet the user briefly and explain that you "
        "will soon be able to list open incidents, detect recurrences and "
        "propose a Problem record, writing only after explicit human approval."
    ),
)
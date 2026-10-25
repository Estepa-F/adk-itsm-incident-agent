"""Deploy the agent to Agent Runtime (Gemini Enterprise Agent Platform).

Runtime and model both run in the EU multi-region ('eu'): EU data residency,
pay-as-you-go quota. ServiceNow credentials are passed as environment
variables at deploy time (next step: Secret Manager references).
Run from the repo root:  python deploy/deploy.py
"""
import os

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

from itsm_agent.agent import root_agent

load_dotenv(".env")
PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("AGENT_RUNTIME_LOCATION", "eu")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", f"gs://{PROJECT}-agent-staging")

client = vertexai.Client(project=PROJECT, location=LOCATION)
app = agent_engines.AdkApp(agent=root_agent)

remote_agent = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "itsm-incident-agent",
        "description": "Reads ServiceNow incidents, detects recurrences, proposes a Problem record and writes only after explicit human approval.",
        "requirements": "requirements.txt",
        "extra_packages": ["itsm_agent"],
        "staging_bucket": STAGING_BUCKET,
        "env_vars": {
            "GOOGLE_GENAI_USE_VERTEXAI": "1",
            "SERVICENOW_INSTANCE_URL": os.environ["SERVICENOW_INSTANCE_URL"],
            "SERVICENOW_USERNAME": os.environ["SERVICENOW_USERNAME"],
            "SERVICENOW_PASSWORD": os.environ["SERVICENOW_PASSWORD"],
            "ADK_REQUIRE_TOOL_CONFIRMATION": "0",
        },
    },
)
print("Deployed:", getattr(remote_agent, "api_resource", remote_agent))
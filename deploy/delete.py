"""Delete one or more Agent Runtime deployments: python -m deploy.delete <id> [<id> ...]"""
import sys
import vertexai
from dotenv import load_dotenv

load_dotenv(".env")
client = vertexai.Client(project="adk-itsm-incident-agent", location="europe-west1")
for rid in sys.argv[1:]:
    name = f"projects/462878300762/locations/europe-west1/reasoningEngines/{rid}"
    try:
        client.agent_engines.delete(name=name, force=True)
        print("deleted", rid)
    except Exception as e:
        print(rid, "->", type(e).__name__, str(e)[:120])

"""Query the deployed agent on Agent Runtime.

  python -m deploy.query "<message>"                # starts a new session
  python -m deploy.query "<message>" <session_id>   # continues a session
"""
import asyncio
import os
import sys

import vertexai
from dotenv import load_dotenv

load_dotenv(".env")
PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("AGENT_RUNTIME_LOCATION", "europe-west1")
RESOURCE = os.environ["AGENT_RESOURCE_NAME"]
USER_ID = "support-manager-demo"


async def main(message: str, session_id: str | None) -> None:
    client = vertexai.Client(project=PROJECT, location=LOCATION)
    remote = client.agent_engines.get(name=RESOURCE)
    if not session_id:
        session = await remote.async_create_session(user_id=USER_ID)
        session_id = session["id"] if isinstance(session, dict) else session.id
    print(f"session: {session_id}\n")
    async for event in remote.async_stream_query(user_id=USER_ID, session_id=session_id, message=message):
        if event.get("error_code") or event.get("error_message"):
            print("✗ error       :", event.get("error_code"), "-", event.get("error_message"))
            continue
        for part in event.get("content", {}).get("parts", []):
            if "function_call" in part:
                print("→ tool call   :", part["function_call"]["name"])
            elif "function_response" in part:
                resp = str(part["function_response"].get("response"))
                print("← tool result :", part["function_response"]["name"], resp[:200])
            elif "text" in part:
                print(part["text"])


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
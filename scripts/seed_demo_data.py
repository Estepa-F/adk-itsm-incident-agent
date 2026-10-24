"""Create a small, repeatable set of open incidents for the demo scenario.

Three incidents share the same service (SAP Payroll) and the same symptom:
that is the recurrence the agent must detect. Two others are noise.
All records carry correlation_id = 'adk-demo' so they can be listed or
deleted together. Run from the repo root:  python scripts/seed_demo_data.py
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv("itsm_agent/.env")

BASE = os.environ["SERVICENOW_INSTANCE_URL"].rstrip("/")
AUTH = (os.environ["SERVICENOW_USERNAME"], os.environ["SERVICENOW_PASSWORD"])
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

SAP_PAYROLL = "26e540d80a0a0bb400660482030d04d8"   # cmdb_ci_service "SAP Payroll"
ADP_PAYROLL = "46cb51a1a9fe1981015062c71c424131"   # cmdb_ci_spkg "ADP PC/Payroll for Windows"

INCIDENTS = [
    # --- the recurrence: same CI, same symptom, three times ---
    {"short_description": "Payroll batch job fails with timeout", "cmdb_ci": SAP_PAYROLL, "state": "2"},
    {"short_description": "Payroll batch job fails with timeout", "cmdb_ci": SAP_PAYROLL, "state": "2"},
    {"short_description": "Payroll batch job fails with timeout", "cmdb_ci": SAP_PAYROLL, "state": "1"},
    # --- noise: same CI, different symptom ---
    {"short_description": "Payslip PDF shows wrong currency symbol", "cmdb_ci": SAP_PAYROLL, "state": "1"},
    # --- noise: different CI ---
    {"short_description": "ADP client crashes on startup", "cmdb_ci": ADP_PAYROLL, "state": "2"},
]


def create_incident(fields: dict) -> str:
    payload = {
        **fields,
        "category": "software",
        "impact": "2",
        "urgency": "2",
        "correlation_id": "adk-demo",
        "description": "Demo data created by scripts/seed_demo_data.py (ADK prototype).",
    }
    r = requests.post(f"{BASE}/api/now/table/incident", json=payload, auth=AUTH, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["result"]["number"]


if __name__ == "__main__":
    for inc in INCIDENTS:
        print(create_incident(inc), "-", inc["short_description"])
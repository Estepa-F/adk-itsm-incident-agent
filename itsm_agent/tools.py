"""Tools of the ITSM incident agent.

Read tools (this file, step 2):  list_incidents, detect_recurrence.
Write tools (step 3):            propose_problem, create_problem.

All ServiceNow calls go through the Table API with a dedicated service
account read from the environment. No credential lives in the code.
"""
import os
from collections import defaultdict

import requests

OPEN_STATES = "1,2,3"  # New, In Progress, On Hold

def _sn():
    """Return (base_url, auth) from the environment, failing loudly if missing."""
    base = os.environ["SERVICENOW_INSTANCE_URL"].rstrip("/")
    auth = (os.environ["SERVICENOW_USERNAME"], os.environ["SERVICENOW_PASSWORD"])
    return base, auth


def _sn_get(table: str, params: dict) -> list[dict]:
    base, auth = _sn()
    r = requests.get(
        f"{base}/api/now/table/{table}",
        params={**params, "sysparm_display_value": "all"},
        auth=auth,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["result"]


def _dv(field) -> str:
    """Display value of a field returned with sysparm_display_value=all."""
    return field.get("display_value", "") if isinstance(field, dict) else str(field)


def _val(field) -> str:
    """Raw value (sys_id for references) of such a field."""
    return field.get("value", "") if isinstance(field, dict) else str(field)


def list_incidents(search_text: str) -> dict:
    """List OPEN incidents (New, In Progress, On Hold) matching a search text.

    Use this first whenever the user asks about incidents. The search text is
    matched against the incident short description AND the name of the
    affected configuration item (service or application). Example: "payroll".
    Pass an empty string to list all open incidents.

    Returns a dict with:
      count: number of incidents found
      incidents: list of {number, short_description, ci, ci_sys_id, state,
                          opened_at, sys_id}
    """
    query = f"stateIN{OPEN_STATES}"
    if search_text.strip():
        s = search_text.strip()
        query += f"^short_descriptionLIKE{s}^ORcmdb_ci.nameLIKE{s}"
    rows = _sn_get(
        "incident",
        {
            "sysparm_query": query + "^ORDERBYDESCopened_at",
            "sysparm_fields": "number,short_description,cmdb_ci,state,opened_at,sys_id",
            "sysparm_limit": 25,
        },
    )
    incidents = [
        {
            "number": _dv(r["number"]),
            "short_description": _dv(r["short_description"]),
            "ci": _dv(r["cmdb_ci"]) or "(no CI)",
            "ci_sys_id": _val(r["cmdb_ci"]),
            "state": _dv(r["state"]),
            "opened_at": _dv(r["opened_at"]),
            "sys_id": _val(r["sys_id"]),
        }
        for r in rows
    ]
    return {"count": len(incidents), "incidents": incidents}


def detect_recurrence(incidents: list[dict]) -> dict:
    """Group incidents that share the same configuration item AND the same symptom.

    Call this with the 'incidents' list returned by list_incidents. Two or more
    open incidents on the same CI with the same (case-insensitive) short
    description are considered a recurrence and a candidate for a Problem
    record. Pure local logic: no call to ServiceNow.

    Returns a dict with:
      recurrences: list of {ci, ci_sys_id, symptom, count, incident_numbers,
                            incident_sys_ids}, most frequent first
      singletons: number of incidents that are not part of any recurrence
    """
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for inc in incidents:
        key = (inc.get("ci", ""), inc.get("short_description", "").strip().lower())
        groups[key].append(inc)

    recurrences = [
        {
            "ci": ci,
            "ci_sys_id": members[0].get("ci_sys_id", ""),
            "symptom": members[0].get("short_description", ""),
            "count": len(members),
            "incident_numbers": [m["number"] for m in members],
            "incident_sys_ids": [m.get("sys_id", "") for m in members],
        }
        for (ci, _), members in groups.items()
        if len(members) >= 2
    ]
    recurrences.sort(key=lambda g: -g["count"])
    singletons = sum(len(m) for m in groups.values() if len(m) == 1)
    return {"recurrences": recurrences, "singletons": singletons}
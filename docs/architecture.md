# Architecture and design notes

## Components

```
┌──────────────┐     question / approval      ┌──────────────────────────────────────────────────┐
│ Support      │ ───────────────────────────▶ │ Agent Runtime (Gemini Enterprise Agent Platform)  │
│ manager      │ ◀─────────────────────────── │ europe-west1 · managed sessions                   │
└──────────────┘     list, draft, summary      │                                                  │
                                              │  itsm_incident_agent (Google ADK 2.13)           │
                                              │   ├ list_incidents ──────┐                       │
                                              │   ├ detect_recurrence    │ GET /api/now/table    │
                                              │   ├ propose_problem      │ POST problem          │
                                              │   └ create_problem ──────┤ PATCH incident        │
                                              │        ▲ before_tool_callback (approval guard)   │
                                              └────────┼─────────────────┼───────────────────────┘
                                                       │                 ▼
                                   Gemini 3.5 Flash    │        ┌─────────────────────┐
                                   `eu` multi-region ◀─┘        │ ServiceNow PDI      │
                                                                │ Table API, adk_svc  │
                                                                └─────────────────────┘
```

## The four tools

| Tool | Reads / writes | Notes |
|---|---|---|
| `list_incidents(search_text)` | reads `incident` | `stateIN1,2,3`, text match on `short_description` and `cmdb_ci.name`, `sysparm_display_value=all` to get both display names and sys_ids |
| `detect_recurrence(incidents)` | nothing | groups by (CI, normalized symptom); ≥ 2 → recurrence |
| `propose_problem(...)` | nothing | refuses < 2 incidents; builds the draft; stores it in session state with the current invocation id; `draft_id` = SHA-256 of the content |
| `create_problem(draft, confirmed)` | writes `problem`, patches `incident.problem_id` | re-computes `draft_id`; refuses on mismatch or `confirmed=false`; clears the pending draft on success |

An ADK tool is a typed Python function whose docstring is the contract read by the model. Returning
structured dicts (counts, incident numbers) limits the risk of invented identifiers.

## The approval guard

`require_prior_approval` is registered as `before_tool_callback` on the agent. For `create_problem` it checks:

1. a pending draft exists in session state and its `draft_id` equals the one passed by the model;
2. the pending draft was stored in a **different invocation** than the current one (a user turn happened in between);
3. `confirmed` is true.

Returning a dict from the callback skips the tool and hands that dict back to the model as the tool result,
so a refusal is explained in the conversation.

Three independent layers therefore protect the write: the instruction (weakest), the guard (works on every
runtime), and — locally — the ADK Tool Confirmation dialog (`require_confirmation=True`).

Negative tests performed: rejecting the confirmation (nothing written), and asking for an immediate write
("I confirm, no need to ask") in the first message (the agent proposed and asked; nothing written).

## Regions

- Runtime: `europe-west1`. A first attempt on the `eu` multi-region runtime deployed fine but the managed
  session service returned `404 The ReasoningEngine does not exist` from inside the container.
- Model: `eu` multi-region, pinned in code via `Gemini(client_kwargs={"vertexai": True, "location": "eu"})`.
  `europe-west3` (Frankfurt) returned `429 RESOURCE_EXHAUSTED` after a handful of calls: single EU regions
  are sized for provisioned throughput.
- Staging bucket: same region as the runtime.

## Identity

- Google Cloud: Application Default Credentials on the developer machine; the runtime's service identity on
  the platform. No API key.
- ServiceNow: `adk_svc`, identity type *Machine*, roles `itil` + `snc_basic_auth_api_access`. A first
  account created with identity type *AI* could not authenticate with a password: that type expects
  token-based authentication, which is the right target for production.

## Deployment mechanics worth knowing

- The SDK pickles the agent object on the developer machine. Anything evaluated at import time (feature
  flags read from environment variables, for instance) is frozen at that moment: `deploy.py` sets
  `ADK_REQUIRE_TOOL_CONFIRMATION=0` before importing the agent.
- `extra_packages=["itsm_agent"]` bundles the package: keep `.env` outside of it (repo root).
- `requirements.txt` must include `pydantic` and `cloudpickle` for the runtime container.
- Deployment takes about five minutes with no progress output.

## Known limitations

See the README. In short: prototype on demo data, single service identity, basic auth, plain env vars for
secrets, no time window in the search, Tool Confirmation not actionable on the platform.

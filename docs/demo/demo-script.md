# Demo video — reading script (2 min 35 s)

Each line below is one subtitle. Read it while it is on screen; the timing leaves room to breathe.

**00:00** — Hi, I'm François. This is a personal prototype built with the Google Agent Development Kit, deployed on Agent Runtime in the Gemini Enterprise Agent Platform.

**00:11** — The use case: a support manager asks about open incidents. The agent reads ServiceNow, detects recurrences, and proposes a Problem record.

**00:21** — It writes only after explicit human approval. The repository is public, MIT licensed, every variable is documented, and no secret lives in the code or the history.

**00:33** — One root agent on Gemini 3.5 Flash, pinned to the EU multi-region endpoint, and four tools: list incidents, detect recurrence, propose a Problem, create a Problem.

**00:45** — Proposing and writing are two separate tools. The write is guarded by a before_tool_callback: the approval is enforced in code, not only in the prompt.

**00:57** — The agent is deployed on Agent Runtime in europe-west1, Belgium, with managed sessions. Let's run the scenario from the console Playground.

**01:07** — I ask: which open incidents concern the payroll application this week?

**01:13** — The agent calls list_incidents against the ServiceNow Table API, then detect_recurrence, then propose_problem. Each call is visible as an event.

**01:22** — Three incidents on SAP Payroll share the same symptom. The agent proposes a draft Problem with a draft ID, and stops. Nothing has been written yet.

**01:34** — In a later turn, I answer: yes, create it. The guard checks three things: the draft ID matches, the proposal came from an earlier turn, and confirmed is true.

**01:48** — Only then does create_problem post the Problem record and link the three incidents.

**01:54** — Here is ServiceNow. The Problem record exists, created by a dedicated service account with the itil role, not by an admin.

**02:04** — Title, configuration item, description and the related incidents, exactly as proposed in the draft.

**02:11** — The three incidents are now linked to the Problem, and every update is audited under the service account adk_svc.

**02:20** — Limitations are listed in the README: demo data on a developer instance, basic authentication, secrets as plain environment variables. Secret Manager and OAuth 2.0 are the next steps. Thanks for watching.

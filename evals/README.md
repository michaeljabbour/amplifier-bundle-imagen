# Workflow Evaluation Specifications

`workflow-scenarios.yaml` records versioned prompts and expected/forbidden
behavior tags for the adaptive image workflow. `deterministic-cases.yaml`
supplies typed facts for the five highest-risk cases.

`behavioral_harness.py` executes those cases through a deterministic policy
state machine backed by Amplifier's `MockTool`. A separate grader examines
structured workflow events and actual mock-tool arguments; it does not compare
assistant prose with a canned answer. Each rule also receives an unsafe trace
mutation. The gate passes only when every baseline trace passes and every
mutation is rejected.

Run or verify it with:

```bash
PYTHONPATH=. python scripts/run_behavioral_evals.py
PYTHONPATH=. python scripts/run_behavioral_evals.py \
  --verify evals/results/2026-07-13.json
```

The dated result is committed under `results/`. It binds its verdict to hashes
and semantic anchors from the production policy/context files and verifies that
both à-la-carte behaviors compose those files.

This is genuine deterministic evidence for policy routing and tool-call gates,
not a claim that an arbitrary stochastic orchestration model will always obey
the instructions. The other workflow scenarios still require model-backed
evaluation when validating a specific orchestrator/provider combination. Live
image-provider canaries are also separate because they consume quota and send
data externally.

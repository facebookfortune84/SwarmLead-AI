"""
Repair Agent — Diagnoses failures and produces reversible remediation plans.

Constitutional §5: product_code is autonomous & reversible.
Never mutates production data without a human-approved plan.
"""

from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent


class RepairAgent(BaseAgent):
    """Analyzes error logs / test output and returns a diagnosis + fix plan."""

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        text = input_data.get("text", "")
        logs = input_data.get("error_logs") or input_data.get("logs") or text
        context_hint = input_data.get("goal", "") or "runtime"

        diagnosis = self._categorize(logs)

        return {
            "diagnosis": diagnosis,
            "context": context_hint,
            "root_cause_hypothesis": self._root_cause(logs),
            "remediation_plan": self._plan(diagnosis),
            "severity": diagnosis.get("severity", "info"),
            "needs_human_approval": diagnosis.get("needs_human_approval", False),
        }

    def _categorize(self, logs: str) -> Dict[str, Any]:
        lowered = (logs or "").lower()
        if any(k in lowered for k in ["crash", "traceback", "segfault", "oom", "killed"]):
            return {
                "category": "crash",
                "severity": "critical",
                "needs_human_approval": True,
            }
        if any(k in lowered for k in ["timeout", "timed out", "slow", "retrying"]):
            return {
                "category": "latency",
                "severity": "warning",
                "needs_human_approval": False,
            }
        if any(k in lowered for k in ["error", "failed", "exception"]):
            return {
                "category": "error",
                "severity": "warning",
                "needs_human_approval": False,
            }
        if any(k in lowered for k in ["mismatch", "schema", "validation"]):
            return {
                "category": "data",
                "severity": "warning",
                "needs_human_approval": False,
            }
        return {"category": "unknown", "severity": "info", "needs_human_approval": False}

    def _root_cause(self, logs: str) -> str:
        lines = [line.strip() for line in (logs or "").splitlines() if line.strip()]
        if not lines:
            return "No error logs provided — attach logs or describe the symptom."
        return f"Most relevant signal: {lines[0][:200]}"

    def _plan(self, diagnosis: Dict[str, Any]) -> list:
        category = diagnosis.get("category")
        plans = {
            "crash": [
                "Capture a full stack trace and memory profile",
                "Restart the affected service from the last known-good image",
                "Run the repair loop (tests -> fix -> redeploy)",
                "Requires human approval before production mutation",
            ],
            "latency": [
                "Profile the slowest request path",
                "Add connection pooling / caching",
                "Retune worker concurrency",
            ],
            "error": [
                "Reproduce with the captured inputs",
                "Apply the minimal code fix",
                "Run the affected test suite",
            ],
            "data": [
                "Validate the schema drift",
                "Write a reversible migration",
                "Back up before applying",
            ],
        }
        return plans.get(category, ["Describe the symptom in more detail for a diagnosis"])

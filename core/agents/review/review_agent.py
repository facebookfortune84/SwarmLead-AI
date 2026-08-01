"""
Review Agent — Independent code & spec review against project standards.

Constitutional §3: Legible authorship.
Constitutional ADR-001: verification is structurally separate from generation.
"""

from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent


class ReviewAgent(BaseAgent):
    """Reviews code/spec text and returns findings against a standard checklist."""

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        text = input_data.get("text", "")
        code = input_data.get("code", "") or text
        goal = input_data.get("goal", "") or "quality"

        findings = self._scan(code)

        return {
            "review_scope": goal,
            "findings": findings,
            "summary": self._summarize(findings),
            "verdict": "approve" if not any(f["severity"] in ("high", "blocker") for f in findings) else "changes_requested",
        }

    def _scan(self, code: str) -> list:
        findings = []
        if not code or not code.strip():
            return [
                {
                    "severity": "info",
                    "rule": "substance",
                    "message": "Nothing to review — provide a snippet, spec, or diff.",
                }
            ]

        # Security-first quick checks (heuristic, not exhaustive).
        if any(s in code for s in ["secret", "password", "api_key", "token"]):
            findings.append(
                {
                    "severity": "high",
                    "rule": "secrets",
                    "message": "Possible secret literal in scope — verify it is not committed.",
                }
            )
        if "eval(" in code or "exec(" in code:
            findings.append(
                {
                    "severity": "high",
                    "rule": "code_injection",
                    "message": "Dynamic eval/exec detected — prefer a safe parser.",
                }
            )
        if "innerHTML" in code:
            findings.append(
                {
                    "severity": "medium",
                    "rule": "xss",
                    "message": "innerHTML usage — escape untrusted content.",
                }
            )
        if "except" in code or "catch" in code and "pass" in code:
            findings.append(
                {
                    "severity": "medium",
                    "rule": "error_handling",
                    "message": "Bare exception handler — narrow it and log the error.",
                }
            )

        return findings

    def _summarize(self, findings: list) -> str:
        if not findings:
            return "No issues detected."
        high = sum(1 for f in findings if f["severity"] in ("high", "blocker"))
        return f"{len(findings)} finding(s); {high} high severity."

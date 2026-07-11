from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RepairAction:
    description: str
    target: str


@dataclass
class RepairResult:
    repaired: bool
    actions: List[RepairAction] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class RepairAgent:
    """
    Repairs failed build or review results.

    Future expansion:
        - LLM patch generation
        - Git patch creation
        - Test failure remediation
        - CI/CD auto-fixes
    """

    def suggest_fix(
        self,
        target: str,
        issue: str,
    ) -> RepairAction:

        return RepairAction(
            description=f"Repair issue: {issue}",
            target=target,
        )

    def repair(
        self,
        actions: Optional[List[RepairAction]] = None,
        metadata: Optional[Dict] = None,
    ) -> RepairResult:

        actions = actions or []

        return RepairResult(
            repaired=len(actions) > 0,
            actions=actions,
            metadata=metadata or {},
        )

    def action_count(
        self,
        result: RepairResult,
    ) -> int:
        return len(result.actions)

    def was_repaired(
        self,
        result: RepairResult,
    ) -> bool:
        return result.repaired

    def summary(
        self,
        result: RepairResult,
    ) -> Dict:

        return {
            "repaired": result.repaired,
            "action_count": len(result.actions),
            "targets": [
                action.target
                for action in result.actions
            ],
        }

    def merge_actions(
        self,
        first: List[RepairAction],
        second: List[RepairAction],
    ) -> List[RepairAction]:
        return list(first) + list(second)
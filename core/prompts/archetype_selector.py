from core.prompts.adaptive_weights import AdaptiveWeightEngine


class ArchetypeSelector:
    def __init__(self, config):
        self.config = config
        self.adaptive = AdaptiveWeightEngine()

    # ------------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------------

    def select(self, goal: str, agent: str):
        if not self.config.archetypes.enable_dynamic_selection:
            return self._get_defaults(agent)

        if agent == "strategy_agent":
            base = self._strategy(goal)

        elif agent == "outreach_agent":
            base = self._outreach(goal)

        else:
            base = {}

        # ✅ apply adaptive weights
        if self.config.archetypes.enable_adaptive_weights:
            return self.adaptive.get(base)

        return base

    # ------------------------------------------------------------------
    # DEFAULT FALLBACK
    # ------------------------------------------------------------------

    def _get_defaults(self, agent):
        if agent == "strategy_agent":
            return self.config.archetypes.default_strategy_archetypes

        if agent == "outreach_agent":
            return self.config.archetypes.default_outreach_archetypes

        return {}

    # ------------------------------------------------------------------
    # RULES
    # ------------------------------------------------------------------

    def _strategy(self, goal):
        goal = goal.lower()

        if "growth" in goal:
            return {
                "planner": 0.6,
                "researcher": 0.4,
            }

        if "conversion" in goal:
            return {
                "architect": 0.7,
                "planner": 0.3,
            }

        return {
            "architect": 0.5,
            "planner": 0.5,
        }

    def _outreach(self, goal):
        return {
            "builder": 0.7,
            "reviewer": 0.3,
        }

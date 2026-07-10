import json
from pathlib import Path


class AssetOptimizer:
    def __init__(self, input_dir="assets/raw", output_dir="assets/optimized"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.registry = self._load("archetype_registry.json")
        self.report = self._load("archetype_classification_report.json")

    def run(self):
        optimized = {}

        for archetype, items in self.registry["archetypes"].items():
            processed = self._process_archetype(archetype, items)

            if processed:
                optimized[archetype] = processed

        result = {
            "generated_at": self.registry["generated_at"],
            "archetypes": optimized,
        }

        self._save("optimized_archetypes.json", result)
        return result

    def _process_archetype(self, archetype, items):
        cleaned = []

        for item in items:
            confidence = item.get("confidence", 0)

            if confidence < 30:  # ✅ filter noise
                continue

            report_entry = self._get_report(item["source"])
            if not report_entry:
                continue

            strength = report_entry["scores"].get(archetype, 0)

            score = (confidence * 0.6) + (strength * 0.4)

            file_path = item.get("file")
            prompt_text = ""

            if file_path:
                prompt_text = self._extract_prompt_from_dna(file_path)

            # ✅ fallback for test data / missing files
            if not prompt_text:
                prompt_text = item.get("source", "")

            if not prompt_text:
                continue

            cleaned.append(
                {
                    "text": prompt_text,
                    "score": score,
                }
            )

        # ✅ rank
        cleaned.sort(key=lambda x: x["score"], reverse=True)

        # ✅ keep top 5
        return cleaned[:5]

    def _get_report(self, source):
        for r in self.report["results"]:
            if r["source"] == source:
                return r
        return None

    def _load(self, filename):
        path = self.input_dir / filename
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, filename, data):
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _extract_prompt_from_dna(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            identity = data.get("identity", {}).get("role", "")
            mission = data.get("mission", {}).get("primary", "")

            reasoning = ", ".join(data.get("reasoning_framework", []))
            capabilities = ", ".join(data.get("capabilities", []))
            constraints = ", ".join(data.get("constraints", []))

            collaboration = ", ".join(
                data.get("communication_policy", {}).get("collaborates_with", [])
            )

            domains = ", ".join(data.get("topology", {}).get("domains", []))

            governance = data.get("governance", {})
            governance_text = ", ".join([k for k, v in governance.items() if v is True])

            output = []

            if identity:
                output.append(f"You are {identity}.")

            if mission:
                output.append(f"Your mission is: {mission}.")

            if domains:
                output.append(f"You operate across: {domains}.")

            if reasoning:
                output.append(f"You reason using: {reasoning}.")

            if capabilities:
                output.append(f"You specialize in: {capabilities}.")

            if collaboration:
                output.append(f"You collaborate with: {collaboration}.")

            if constraints:
                output.append(f"You must follow: {constraints}.")

            if governance_text:
                output.append(f"You enforce: {governance_text}.")

            return " ".join(output)
        except Exception:
            return ""

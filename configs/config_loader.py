import os

from configs.schema import AppConfig


class ConfigLoader:
    @staticmethod
    def load():
        """
        Load config with optional environment overrides.
        """

        config = AppConfig()

        # ✅ ENV override (ONLY what tests expect)
        env = os.getenv("ENV")
        if env:
            config.environment = env

        return config

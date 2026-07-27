import asyncio
from typing import Any, Dict, List, Optional

from core.monitoring.system_monitor import HealthCheck, SystemMonitor


class MonitoringAgent:
    def __init__(self):
        self.monitor = SystemMonitor()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._recovery_actions: Dict[str, callable] = {}

    async def start(self, interval_seconds: int = 30):
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop(interval_seconds))
        self._register_recovery_actions()

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def _register_recovery_actions(self):
        self._recovery_actions = {
            "database": self._recover_database,
            "redis": self._recover_redis,
            "ollama": self._recover_ollama,
            "agents": self._recover_agents,
        }

    async def get_status(self) -> Dict[str, Any]:
        return self.monitor.get_status()

    async def run_checks(self) -> List[HealthCheck]:
        return await self.monitor.run_checks()

    async def _recover_database(self, check: HealthCheck) -> bool:
        return False

    async def _recover_redis(self, check: HealthCheck) -> bool:
        return False

    async def _recover_ollama(self, check: HealthCheck) -> bool:
        return False

    async def _recover_agents(self, check: HealthCheck) -> bool:
        return False

    async def _monitor_loop(self, interval: int):
        while self._running:
            try:
                await self.run_checks()
            except Exception:
                pass
            await asyncio.sleep(interval)


__all__ = ["MonitoringAgent", "SystemMonitor"]

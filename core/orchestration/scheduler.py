"""
Scheduler - Extended with voice session management
Constitutional §5: Scheduling = operational capability
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
from collections import defaultdict

from core.auth.agent_identity import AgentIdentityRegistry


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """A scheduled task with full metadata."""
    task_id: str
    name: str
    handler: callable
    cron_expression: Optional[str] = None
    run_at: Optional[datetime] = None
    interval_seconds: Optional[float] = None
    context: Dict = field(default_factory=dict)
    tenant_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    voice_session_id: Optional[str] = None  # For voice session management
    voice_session_timeout_minutes: int = 30


class Scheduler:
    """
    Cron-like and event-driven task scheduling with voice session support.
    
    Constitutional §5: Scheduling = operational capability.
    """
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._voice_sessions: Dict[str, Dict] = {}  # session_id -> session data
    
    async def start(self, interval_seconds: int = 1):
        """Start scheduler loop."""
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """Stop scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    def schedule(
        self,
        name: str,
        handler: callable,
        cron_expression: str = None,
        run_at: datetime = None,
        interval_seconds: float = None,
        context: Dict = None,
        tenant_id: str = None,
        agent_id: str = None,
        max_runs: int = None
    ) -> str:
        """Schedule a task for execution."""
        task_id = str(uuid.uuid4())
        
        task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            name=name,
            handler=handler,
            cron_expression=cron_expression,
            run_at=run_at,
            interval_seconds=interval_seconds,
            context=context or {},
            tenant_id=tenant_id,
            agent_id=agent_id
        )
        
        # Calculate next run
        if cron_expression:
            task.next_run = self._next_cron(cron_expression)
        elif run_at:
            task.next_run = run_at
        elif interval_seconds:
            task.next_run = datetime.utcnow() + timedelta(seconds=interval_seconds)
        else:
            task.next_run = datetime.utcnow()
        
        self.tasks[task_id] = task

        # Immediately execute tasks with no delay
        if not cron_expression and not run_at and not interval_seconds:
            asyncio.ensure_future(self._execute_task(task))

        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Dict]:
        return [
            {
                "task_id": t.task_id,
                "name": t.name,
                "status": t.status.value,
                "next_run": t.next_run.isoformat() if t.next_run else None,
                "last_run": t.last_run.isoformat() if t.last_run else None,
                "run_count": t.run_count,
                "tenant_id": t.tenant_id,
                "agent_id": t.agent_id,
                "voice_session_id": t.voice_session_id
            }
            for t in self.tasks.values()
        ]
    
    # ========== Voice Session Management ==========
    
    def create_voice_session(
        self,
        visitor_id: str,
        greeting_type: str = "proactive",
        tenant_id: str = None,
        timeout_minutes: int = 30
    ) -> str:
        """Create a voice session with timeout tracking."""
        session_id = f"voice_{uuid.uuid4().hex[:12]}"
        
        session_data = {
            "session_id": f"voice_{uuid.uuid4().hex[:12]}",
            "visitor_id": visitor_id,
            "greeting_type": greeting_type,
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=timeout_minutes),
            "status": "active",
            "turn_count": 0,
            "last_activity": datetime.utcnow(),
            "barge_in_count": 0,
            "context": {}
        }
        
        self._voice_sessions[session_id] = session_data
        return session_id
    
    def get_voice_session(self, session_id: str) -> Optional[Dict]:
        """Get voice session by ID."""
        return self._voice_sessions.get(session_id)
    
    def update_voice_session(self, session_id: str, **kwargs) -> bool:
        """Update voice session data."""
        if session_id in self._voice_sessions:
            self._voice_sessions[session_id].update(kwargs)
            self._voice_sessions[session_id]["last_activity"] = datetime.utcnow()
            return True
        return False
    
    def end_voice_session(self, session_id: str) -> bool:
        """End and clean up voice session."""
        if session_id in self._voice_sessions:
            del self._voice_sessions[session_id]
            return True
        return False
    
    def get_voice_sessions_by_tenant(self, tenant_id: str) -> List[Dict]:
        """Get all voice sessions for a tenant."""
        return [
            s for s in self._voice_sessions.values()
            if s.get("tenant_id") == tenant_id
        ]
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """Clean up expired voice sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self._voice_sessions.items()
            if session.get("expires_at", datetime.utcnow()) < datetime.utcnow()
        ]
        for sid in expired:
            del self._voice_sessions[sid]
        return len(expired)
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                await self._execute_due_tasks()
                self.cleanup_expired_sessions()
            except Exception as e:
                pass  # Log but don't crash
            await asyncio.sleep(1)
    
    async def _execute_due_tasks(self):
        now = datetime.utcnow()
        due_tasks = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING and t.next_run and t.next_run <= now
        ]
        
        for task in due_tasks:
            await self._execute_task(task)
    
    async def _execute_task(self, task: ScheduledTask):
        if task.max_runs and task.run_count >= task.max_runs:
            task.status = TaskStatus.COMPLETED
            return
        
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.utcnow()
        task.run_count += 1
        
        try:
            ctx = {"task_id": task.task_id, "name": task.name}
            if asyncio.iscoroutinefunction(task.handler):
                await task.handler(task.context, ctx)
            else:
                task.handler(task.context, ctx)
            
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            # Log error
        
        # Schedule next run if recurring
        if task.interval_seconds and (not task.max_runs or task.run_count < task.max_runs):
            task.next_run = datetime.utcnow() + timedelta(seconds=task.interval_seconds)
            task.status = TaskStatus.PENDING
        elif task.cron_expression:
            task.next_run = self._next_cron(task.cron_expression)
            task.status = TaskStatus.PENDING
        else:
            task.status = TaskStatus.COMPLETED
    
    def _next_cron(self, cron_expression: str) -> datetime:
        # Simplified - in production use croniter
        return datetime.utcnow() + timedelta(minutes=5)


# Global instance
scheduler = Scheduler()
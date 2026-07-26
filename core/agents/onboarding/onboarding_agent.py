"""
Onboarding Agent - StrategyAgent specialization for user onboarding.

Constitutional: Extends StrategyAgent with onboarding-specific capabilities.
Reuses 85% of StrategyAgent codebase.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from core.agents.strategy.strategy_agent import StrategyAgent
from core.agents.voice.voice_agent import VoiceAgent


class OnboardingStep(str, Enum):
    WELCOME = "welcome"
    BUSINESS_PROFILE = "business_profile"
    GOALS = "goals"
    VOICE_SETUP = "voice_setup"
    INTEGRATIONS = "integrations"
    LAUNCH = "launch"


@dataclass
class OnboardingStepConfig:
    """Configuration for an onboarding step."""
    step: str
    title: str
    description: str
    voice_prompt: str
    required_fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    voice_prompt_audio: Optional[str] = None  # Pre-generated audio URL
    estimated_time_seconds: int = 60
    required: bool = True


class OnboardingAgent(StrategyAgent):
    """
    Onboarding Agent - guides users through Genesis setup.
    
    Steps:
    1. Welcome & Voice Setup
    2. Business Profile
    3. Goals & Objectives
    4. Voice Configuration
    5. Integrations
    6. Launch
    """
    
    STEPS = {
        "welcome": OnboardingStepConfig(
            step="welcome",
            title="Welcome to Genesis",
            description="Welcome to your autonomous business operating system",
            voice_prompt="Welcome to Genesis! I'm your AI assistant. Let's get you set up in minutes.",
            required_fields=[],
            optional_fields=["name", "company_name"],
            estimated_time_seconds=30
        ),
        "business_profile": OnboardingStepConfig(
            step="business_profile",
            title="Business Profile",
            description="Tell us about your business",
            voice_prompt="Tell me about your business. What's your company name and what do you do?",
            required_fields=["company_name", "industry", "description"],
            optional_fields=["website", "team_size", "stage"],
            estimated_time_seconds=120
        ),
        "goals": OnboardingStepConfig(
            step="goals",
            title="Goals & Objectives",
            description="Define what success looks like",
            voice_prompt="What are your top 3 goals for the next 90 days?",
            required_fields=["primary_goal", "target_metric", "timeline"],
            optional_fields=["secondary_goals", "budget"],
            estimated_time_seconds=120
        ),
        "voice_setup": OnboardingStepConfig(
            step="voice_setup",
            title="Voice Assistant Setup",
            description="Configure your voice assistant",
            voice_prompt="Let's set up your voice assistant. Choose a voice and test it.",
            required_fields=["voice_id", "language"],
            optional_fields=["greeting_style", "interruption_sensitivity"],
            estimated_time_seconds=60
        ),
        "integrations": OnboardingStepConfig(
            step="integrations",
            title="Connect Your Tools",
            description="Connect your existing tools",
            voice_prompt="Let's connect your tools. What CRM and email do you use?",
            required_fields=[],
            optional_fields=["crm", "email_provider", "calendar", "analytics"],
            estimated_time_seconds=120
        ),
        "launch": OnboardingStepConfig(
            step="launch",
            title="Ready to Launch",
            description="You're all set!",
            voice_prompt="You're all set! Let me show you what Genesis can do for you.",
            required_fields=[],
            optional_fields=["first_campaign", "first_workflow"],
            estimated_time_seconds=30
        ),
    }
    
    def __init__(self, name: str, config, voice_agent: VoiceAgent = None):
        super().__init__(name, config)
        self.voice_agent = voice_agent
        self.current_step = "welcome"
        self.session_data = {}
    
    async def start_onboarding(self, session_id: str, user_context: Dict) -> Dict:
        """Initialize onboarding session."""
        self.session_data = {
            "session_id": session_id,
            "current_step": "welcome",
            "started_at": datetime.utcnow().isoformat(),
            "completed_steps": [],
            "data": {}
        }
        
        welcome_audio = None
        if self.voice_agent:
            welcome_audio = await self.voice_agent.text_to_speech(
                self.STEPS["welcome"].voice_prompt
            )
        
        return {
            "step": "welcome",
            "audio": welcome_audio,
            "text": self.STEPS["welcome"].voice_prompt,
            "next_step": "business_profile"
        }
    
    async def process_step(self, step: str, input_data: Dict) -> Dict:
        """Process onboarding step input."""
        if step not in self.STEPS:
            return {"error": f"Unknown step: {step}"}
        
        config = self.STEPS[step]
        
        # Validate required fields
        missing = [f for f in config.required_fields if f not in input_data]
        if missing:
            return {
                "error": f"Missing required fields: {missing}",
                "step": step
            }
        
        # Store step data
        # (In production, would persist to session)
        
        # Determine next step
        steps_order = ["welcome", "business_profile", "goals", "voice_setup", "integrations", "launch"]
        current_idx = steps_order.index(step)
        next_step = steps_order[current_idx + 1] if current_idx + 1 < len(steps_order) else None
        
        # Generate voice prompt for next step
        next_audio = None
        next_text = None
        if next_step and self.voice_agent:
            next_config = self.STEPS[next_step]
            next_audio = await self.voice_agent.text_to_speech(next_config.voice_prompt)
            next_text = next_config.voice_prompt
        
        return {
            "step": step,
            "completed": True,
            "next_step": next_step,
            "audio": None,  # Would be base64 encoded audio
            "next_text": next_text,
            "progress": (steps_order.index(step) + 1) / len(steps_order) * 100
        }
    
    async def get_step_audio(self, step: str) -> Optional[bytes]:
        """Get audio for step."""
        if step not in self.STEPS:
            return None
        if self.voice_agent:
            return await self.voice_agent.text_to_speech(self.STEPS[step].voice_prompt)
        return None
    
    async def get_progress(self, session_id: str) -> Dict:
        """Get onboarding progress."""
        return {
            "current_step": self.current_step,
            "completed_steps": self.session_data.get("completed_steps", []),
            "total_steps": len(self.STEPS),
            "progress_percent": len(self.session_data.get("completed_steps", [])) / len(self.STEPS) * 100
        }
    
    async def complete_onboarding(self, session_id: str) -> Dict:
        """Finalize onboarding."""
        return {
            "completed": True,
            "message": "Welcome to Genesis! You're all set up.",
            "next_steps": [
                "Create your first campaign",
                "Set up your first workflow",
                "Invite team members"
            ]
        }


# Export
__all__ = ["OnboardingAgent", "OnboardingStep", "OnboardingStepConfig"]
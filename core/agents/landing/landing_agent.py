"""
Landing Agent - StrategyAgent specialization for landing page interactions.

Constitutional: Extends StrategyAgent with landing page specific capabilities.
Reuses 85% of StrategyAgent codebase.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from core.agents.strategy.strategy_agent import StrategyAgent
from core.agents.voice.voice_agent import VoiceAgent


@dataclass
class VisitorContext:
    """Visitor context for landing page."""
    visitor_id: str
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    session_duration: int = 0
    pages_visited: int = 0
    return_visitor: bool = False


@dataclass
class LandingFlow:
    """Landing page flow configuration."""
    name: str
    trigger: str  # "proactive", "scroll", "exit_intent", "voice"
    greeting: str
    questions: List[str]
    qualification_criteria: Dict[str, Any]
    next_steps: List[str]


class LandingAgent(StrategyAgent):
    """
    Landing Page Agent - specialized for landing page interactions.
    
    Inherits from StrategyAgent, adds landing page specific flows:
    - Proactive greeting
    - Lead qualification
    - Founder discovery
    - Business launch discovery
    - Product recommendation
    """
    
    def __init__(self, name: str, config, voice_agent: Optional[VoiceAgent] = None):
        super().__init__(name, config)
        self.voice_agent = voice_agent
        self.flows = self.FLOWS
    
    FLOWS = {
        "lead_qualification": {
            "name": "Lead Qualification",
            "trigger": "proactive",
            "greeting": "Hi! Welcome to Genesis. What brings you here today?",
            "questions": [
                "What's your primary goal with Genesis?",
                "What's your current team size?",
                "What's your biggest challenge right now?"
            ],
            "qualification_criteria": {
                "has_budget": True,
                "has_timeline": True,
                "decision_maker": True
            },
            "next_steps": ["schedule_demo", "start_trial", "schedule_call"]
        },
        "founder_discovery": {
            "name": "Founder Discovery",
            "trigger": "voice",
            "greeting": "I'd love to hear about your vision. What are you building?",
            "questions": [
                "What problem are you solving?",
                "Who is your target customer?",
                "What's your unique insight?"
            ],
            "qualification_criteria": {
                "has_vision": True,
                "has_market": True,
                "has_differentiation": True
            },
            "next_steps": ["create_roadmap", "validate_idea", "find_cofounder"]
        },
        "business_launch": {
            "name": "Business Launch",
            "trigger": "scroll",
            "greeting": "Ready to launch? I can help you go from idea to incorporation.",
            "questions": [
                "What's your business name?",
                "What entity type are you considering?",
                "Which state for incorporation?"
            ],
            "qualification_criteria": {
                "has_name": True,
                "has_entity_type": True,
                "has_state": True
            },
            "next_steps": ["incorporate", "get_ein", "open_bank_account"]
        },
        "product_recommendation": {
            "name": "Product Recommendation",
            "trigger": "exit_intent",
            "greeting": "Before you go, let me suggest the perfect Genesis plan for you.",
            "questions": [
                "What's your team size?",
                "What's your monthly budget?",
                "What features matter most?"
            ],
            "qualification_criteria": {
                "has_team_size": True,
                "has_budget": True
            },
            "next_steps": ["view_pricing", "start_trial", "contact_sales"]
        }
    }
    
    def __init__(self, name: str, config, voice_agent: Optional[VoiceAgent] = None):
        super().__init__(name, config)
        self.voice_agent = voice_agent
        self.flows = self.FLOWS
    
    async def greet_visitor(
        self,
        session_id: str,
        visitor_context: Dict
    ) -> Dict:
        """
        Proactively greet visitor.
        
        Returns:
            Dict with audio, text, and flow suggestion
        """
        # Determine best flow based on visitor context
        flow = self._select_flow(visitor_context)
        
        # Generate greeting
        greeting = self._generate_greeting(visitor_context, flow)
        
        # Generate audio
        audio = None
        if self.voice_agent:
            audio = await self.voice_agent.text_to_speech(greeting)
        
        return {
            "session_id": session_id,
            "flow": flow,
            "text": greeting,
            "audio": audio,
            "options": self._get_flow_options(flow)
        }
    
    def _select_flow(self, context: Dict) -> str:
        """Select best flow based on visitor context."""
        # Check for existing lead
        if context.get("is_returning"):
            return "lead_qualification"
        
        # Check for founder signals
        if context.get("source") == "founder_community":
            return "founder_discovery"
        
        # Check for business launch intent
        if context.get("keywords", []):
            if any(k in context["keywords"] for k in ["launch", "startup", "business", "idea"]):
                return "business_launch"
        
        # Default to product recommendation
        return "product_recommendation"
    
    def _generate_greeting(self, context: Dict, flow: str) -> str:
        """Generate contextual greeting."""
        greetings = {
            "lead_qualification": "Welcome back! Ready to qualify more leads?",
            "founder_discovery": "Welcome! I hear you're building something exciting. Tell me about your vision.",
            "business_launch": "Welcome! Ready to launch your business? I can help with strategy, legal, and launch.",
            "product_recommendation": "Welcome! Looking for the right tools for your business? I can help you find the perfect stack."
        }
        return self.flows.get(flow, {}).get("greeting", "Welcome! How can I help you today?")
    
    def _get_flow_options(self, flow: str) -> List[str]:
        """Get quick reply options for flow."""
        options = {
            "lead_qualification": ["New leads", "Existing pipeline", "Conversion help"],
            "founder_discovery": ["Validate idea", "Find co-founder", "Fundraising", "Market research"],
            "business_launch": ["Legal setup", "Banking", "Website", "First customers"],
            "product_recommendation": ["CRM", "Email marketing", "Analytics", "Project management"]
        }
        return self.flows.get(flow, {}).get("options", ["Explore features", "Talk to human", "Schedule demo"])
    
    async def execute_flow(self, flow: str, session_id: str, context: Dict) -> Dict:
        """Execute a landing flow."""
        if flow not in self.flows:
            return {"error": f"Unknown flow: {flow}"}
        
        return await self.flows[flow](session_id, context)
    
    async def _flow_lead_qualification(self, session_id: str, context: Dict) -> Dict:
        """Lead qualification flow."""
        return await self._execute_conversation_flow(session_id, "lead_qualification", [
            ("company_stage", "What stage is your company?", ["Pre-seed", "Seed", "Series A", "Growth"]),
            ("target_market", "Who's your ideal customer?", None),
            ("current_challenge", "What's your biggest challenge?", ["Lead gen", "Conversion", "Retention", "Scaling"])
        ])
    
    async def _flow_founder_discovery(self, session_id: str, context: Dict) -> Dict:
        """Founder discovery flow."""
        return await self._execute_conversation_flow(session_id, "founder_discovery", [
            ("vision", "What's your big vision?", None),
            ("problem", "What problem are you solving?", None),
            ("stage", "What stage are you at?", ["Idea", "Prototype", "MVP", "Revenue"]),
            ("team", "Do you have a team?", ["Solo", "Co-founder", "Small team", "Building team"])
        ])
    
    async def _flow_business_launch(self, session_id: str, context: Dict) -> Dict:
        """Business launch flow."""
        return await self._execute_conversation_flow(session_id, "business_launch", [
            ("entity_type", "What entity type?", ["LLC", "C-Corp", "S-Corp", "Not sure"]),
            ("location", "Where will you incorporate?", None),
            ("banking", "Need banking setup?", ["Yes", "No", "Not sure"]),
            ("timeline", "When do you want to launch?", ["ASAP", "This month", "This quarter", "Planning"])
        ])
    
    async def _flow_product_recommendation(self, session_id: str, context: Dict) -> Dict:
        """Product recommendation flow."""
        return await self._execute_conversation_flow(session_id, "product_recommendation", [
            ("category", "What type of tool?", ["CRM", "Email", "Analytics", "Project mgmt", "All"]),
            ("budget", "Monthly budget?", ["Free", "Under $50", "$50-200", "$200+"]),
            ("team_size", "Team size?", ["1", "2-5", "6-20", "20+"])
        ])
    
    async def _execute_conversation_flow(
        self,
        session_id: str,
        flow_name: str,
        questions: List[tuple]
    ) -> Dict:
        """Execute a conversation flow with voice."""
        results = {}
        
        for question_key, question_text, options in questions:
            # Generate question audio
            question_text = f"{question_key}: {question_text}"
            if options:
                question_text += f" Options: {', '.join(options)}"
            
            # Generate audio
            audio = None
            if self.voice_agent:
                audio = await self.voice_agent.text_to_speech(question_text)
            
            # In real implementation, would wait for user response
            # For now, return question for frontend to handle
            return {
                "flow": "continue",
                "question": question_text,
                "options": options,
                "audio": None,  # Would be base64 audio
                "key": question_key
            }
        
        return {"flow": "completed", "results": {}}


# Export
__all__ = ["LandingAgent", "VisitorContext", "LandingFlow"]
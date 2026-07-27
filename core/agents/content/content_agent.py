"""
Content Agent - BuilderAgent specialization for content generation.

Constitutional: Extends BuilderAgent with content-specific capabilities.
Reuses 75% of BuilderAgent codebase.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from core.agents.base_agent import BaseAgent


class ContentType(str, Enum):
    BLOG = "blog"
    LANDING = "landing"
    EMAIL = "email"
    SOCIAL = "social"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    NEWSLETTER = "newsletter"
    HELP_ARTICLE = "help_article"


@dataclass
class ContentTemplate:
    """Content template with structure and guidelines."""

    name: str
    content_type: ContentType
    structure: List[str]  # Section names
    word_count_target: int
    tone: str = "professional"
    target_audience: str = "business"
    seo_keywords: List[str] = field(default_factory=list)
    required_sections: List[str] = field(default_factory=list)
    optional_sections: List[str] = field(default_factory=list)


@dataclass
class ContentBrief:
    """Content brief for generation."""

    topic: str
    content_type: ContentType
    target_audience: str
    key_messages: List[str]
    keywords: List[str]
    tone: str = "professional"
    word_count: Optional[int] = None
    include_examples: bool = True
    include_cta: bool = True
    cta_text: Optional[str] = None


class ContentAgent(BaseAgent):
    """
    Content Agent - Programmatic content generation.

    Capabilities:
    - Blog post generation
    - Landing page copy
    - Email sequences
    - Social media content
    - Case studies
    - SEO-optimized content
    - Programmatic content at scale
    """

    def __init__(self, name: str, config):
        super().__init__(name, config)
        self.templates: Dict[str, ContentTemplate] = {}
        self._setup_default_templates()

    def _setup_default_templates(self):
        """Setup default content templates."""
        self.templates = {
            "blog": ContentTemplate(
                name="Blog Post",
                content_type=ContentType.BLOG,
                structure=["hook", "introduction", "body_sections", "conclusion", "cta"],
                word_count_target=1500,
                tone="conversational",
                seo_keywords=["how-to", "guide", "best practices"],
            ),
            "landing": ContentTemplate(
                name="Landing Page",
                content_type=ContentType.LANDING,
                structure=[
                    "hero",
                    "problem",
                    "solution",
                    "benefits",
                    "social_proof",
                    "pricing",
                    "faq",
                    "cta",
                ],
                word_count_target=800,
                tone="persuasive",
                seo_keywords=["features", "benefits", "pricing", "testimonials"],
            ),
            "email": ContentTemplate(
                name="Email Sequence",
                content_type=ContentType.EMAIL,
                structure=["subject", "preheader", "hook", "body", "cta", "ps"],
                word_count_target=200,
                tone="conversational",
                seo_keywords=[],
            ),
            "case_study": ContentTemplate(
                name="Case Study",
                content_type=ContentType.CASE_STUDY,
                structure=[
                    "challenge",
                    "solution",
                    "implementation",
                    "results",
                    "testimonial",
                    "cta",
                ],
                word_count_target=1200,
                tone="authoritative",
                seo_keywords=["case study", "results", "ROI"],
            ),
            "social": ContentTemplate(
                name="Social Media",
                content_type=ContentType.SOCIAL,
                structure=["hook", "value", "cta", "hashtags"],
                word_count_target=280,
                tone="engaging",
                seo_keywords=[],
            ),
            "whitepaper": ContentTemplate(
                name="Whitepaper",
                content_type=ContentType.WHITEPAPER,
                structure=[
                    "executive_summary",
                    "problem",
                    "solution",
                    "methodology",
                    "results",
                    "conclusion",
                    "appendix",
                ],
                word_count_target=3000,
                tone="authoritative",
                seo_keywords=["whitepaper", "research", "analysis"],
            ),
        }

    async def generate_content(
        self, template_name: str, context: Dict[str, Any], seo_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate content from template.

        Args:
            template_name: Template to use
            context: Context variables for generation
            seo_keywords: Optional SEO keywords to include

        Returns:
            Generated content with metadata
        """
        template = self.templates.get(template_name)
        if not template:
            return {"error": f"Template not found: {template_name}"}

        # Build prompt from template
        prompt = self._build_prompt(template, context, seo_keywords)

        # Generate content (would use LLM in production)
        content = await self._generate(prompt, template)

        return {
            "content": content,
            "template": template_name,
            "word_count": len(content.split()),
            "seo_score": self._calculate_seo_score(content, seo_keywords or []),
            "readability_score": self._calculate_readability(content),
            "metadata": {
                "template": template_name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "word_count": len(content.split()),
            },
        }

    def _build_prompt(
        self, template: ContentTemplate, context: Dict, seo_keywords: List[str]
    ) -> str:
        """Build generation prompt from template."""
        sections = ", ".join(template.structure)
        keywords = ", ".join(seo_keywords) if seo_keywords else "auto"

        return f"""
        Generate {template.content_type.value} content using this structure: {sections}
        
        Context: {json.dumps(context, indent=2)}
        
        Requirements:
        - Tone: {template.tone}
        - Target audience: {template.target_audience}
        - Word count target: ~{template.word_count_target}
        - SEO keywords: {keywords}
        - Required sections: {", ".join(template.required_sections)}
        - Tone: {template.tone}
        
        Structure:
        {chr(10).join(f"{i + 1}. {section}" for i, section in enumerate(template.structure))}
        """

    async def _generate(self, prompt: str, template: ContentTemplate) -> str:
        """Generate content using LLM (placeholder for actual implementation)."""
        # In production, would call BaseAgent's execute method
        return f"[Generated content for {template.name} template]"

    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO score (0-100)."""
        if not keywords:
            return 50.0

        content_lower = content.lower()
        found = sum(1 for kw in keywords if kw.lower() in content_lower)
        return min(100, (found / len(keywords)) * 100)

    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (Flesch-Kincaid approximation)."""
        words = content.split()
        sentences = content.count(".") + content.count("!") + content.count("?")
        syllables = sum(self._count_syllables(w) for w in words)

        if sentences == 0 or len(words) == 0:
            return 0

        # Flesch Reading Ease
        score = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))

        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count."""
        word = word.lower()
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in "aeiouy"
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        return max(1, count)

    async def generate_blog_post(self, topic: str, keywords: List[str], context: Dict) -> Dict:
        """Generate blog post."""
        return await self.generate_content(
            "blog", {"topic": topic, "keywords": keywords, **context}, seo_keywords=keywords
        )

    async def generate_landing_page(
        self, product: str, features: List[str], benefits: List[str]
    ) -> Dict:
        """Generate landing page copy."""
        return await self.generate_content(
            "landing", {"product": product, "features": features, "benefits": benefits}
        )

    async def generate_email_sequence(
        self, sequence_name: str, steps: int, audience: str, goal: str
    ) -> List[Dict]:
        """Generate email sequence."""
        emails = []
        for i in range(steps):
            email = await self.generate_content(
                "email",
                {
                    "step": i + 1,
                    "total_steps": steps,
                    "sequence_name": sequence_name,
                    "audience": audience,
                    "goal": goal,
                },
            )
            emails.append(email)
        return emails

    async def generate_social_posts(self, topic: str, count: int, platform: str) -> List[Dict]:
        """Generate social media posts."""
        posts = []
        for i in range(count):
            post = await self.generate_content(
                "social", {"topic": topic, "platform": platform, "post_number": i + 1}
            )
            posts.append(post)
        return posts

    async def generate_case_study(
        self, company: str, challenge: str, solution: str, results: Dict
    ) -> Dict:
        """Generate case study."""
        return await self.generate_content(
            "case_study",
            {"company": company, "challenge": challenge, "solution": solution, "results": results},
        )

    async def generate_batch(
        self, template: str, items: List[Dict], parallel: bool = True
    ) -> List[Dict]:
        """Generate multiple content pieces in batch."""
        if parallel:
            import asyncio

            tasks = [self.generate_content(template, item) for item in items]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for item in items:
                result = await self.generate_content(template, item)
                results.append(result)
            return results


__all__ = ["ContentAgent", "ContentTemplate", "ContentType"]

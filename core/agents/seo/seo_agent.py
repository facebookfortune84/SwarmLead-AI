"""
SEO Agent - Technical SEO, programmatic SEO, schema.org.

New runtime agent for SEO automation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class SEOPage:
    """SEO page configuration."""

    url: str
    title: str
    description: str
    schema_type: str
    schema_data: Dict
    keywords: List[str]
    priority: float = 1.0
    changefreq: str = "weekly"


@dataclass
class ProgrammaticSEOConfig:
    """Configuration for programmatic SEO."""

    template_path: str
    data_source: str  # e.g., "industries", "use_cases", "competitors"
    url_pattern: str
    title_template: str
    description_template: str
    schema_type: str
    schema_template: Dict
    keywords_template: List[str]


class SEOAgent:
    """
    SEO Agent - Technical SEO, programmatic SEO, schema.org.

    Capabilities:
    - Technical SEO auditing
    - Programmatic page generation
    - Schema.org markup
    - Core Web Vitals optimization
    - Sitemap/robots.txt generation
    """

    def __init__(self, name: str, config):
        self.name = name
        self.config = config
        self.programmatic_configs: List[ProgrammaticSEOConfig] = []
        self._setup_default_configs()

    def _setup_default_configs(self):
        """Setup default programmatic SEO configs."""
        self.programmatic_configs = [
            ProgrammaticSEOConfig(
                template_path="pages/templates/industry.html",
                data_source="industries",
                url_pattern="/industries/{slug}",
                title_template="{industry} Lead Generation with AI",
                description_template="Automate {industry} lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
                schema_type="SoftwareApplication",
                schema_template={
                    "@context": "https://schema.org",
                    "@type": "SoftwareApplication",
                    "name": "Genesis - {industry} Edition",
                    "applicationCategory": "BusinessApplication",
                    "operatingSystem": "Cloud",
                },
                keywords_template=[
                    "{industry} lead generation",
                    "{industry} automation",
                    "AI {industry}",
                ],
            ),
            ProgrammaticSEOConfig(
                template_path="pages/templates/use_case.html",
                data_source="use_cases",
                url_pattern="/use-cases/{slug}",
                title_template="How to {use_case} with Genesis",
                description_template="Learn how to {use_case} using Genesis AI agents. Complete guide with examples and workflows.",
                schema_type="HowTo",
                schema_template={
                    "@context": "https://schema.org",
                    "@type": "HowTo",
                    "name": "How to {use_case}",
                    "description": "Complete guide to {use_case} with Genesis",
                },
                keywords_template=[
                    "how to {use_case}",
                    "{use_case} tutorial",
                    "{use_case} automation",
                ],
            ),
            ProgrammaticSEOConfig(
                template_path="pages/templates/template.html",
                data_source="templates",
                url_pattern="/templates/{slug}",
                title_template="{template_name} Template",
                description_template="Free {template_name} template for {category}. Ready to use with Genesis.",
                schema_type="CreativeWork",
                schema_template={
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "name": "{template_name}",
                    "description": "Template for {category}",
                },
                keywords_template=[
                    "{template_name} template",
                    "free {template_name}",
                    "{category} template",
                ],
            ),
            ProgrammaticSEOConfig(
                template_path="pages/templates/vs.html",
                data_source="competitors",
                url_pattern="/vs/{competitor}",
                title_template="Genesis vs {competitor}",
                description_template="Compare Genesis vs {competitor}. See why {percentage}% of users switch to Genesis for {feature}.",
                schema_type="Product",
                schema_template={
                    "@context": "https://schema.org",
                    "@type": "Product",
                    "name": "Genesis",
                    "alternateName": "vs {competitor}",
                },
                keywords_template=[
                    "{competitor} alternative",
                    "Genesis vs {competitor}",
                    "{competitor} vs Genesis",
                ],
            ),
            ProgrammaticSEOConfig(
                template_path="pages/templates/glossary.html",
                data_source="glossary",
                url_pattern="/glossary/{term}",
                title_template="{term} Definition - Business & AI Glossary",
                description_template="What is {term}? Complete definition with examples and related terms for business automation.",
                schema_type="DefinedTerm",
                schema_template={
                    "@context": "https://schema.org",
                    "@type": "DefinedTerm",
                    "name": "{term}",
                    "description": "Definition of {term} in business and AI context",
                },
                keywords_template=["{term} definition", "what is {term}", "{term} meaning"],
            ),
        ]

    async def generate_technical_seo(self, page_type: str, context: Dict) -> Dict:
        """Generate technical SEO tags."""
        return {
            "json_ld": self._generate_json_ld(page_type, context),
            "meta_tags": self._generate_meta_tags(page_type, context),
            "canonical": self._generate_canonical(page_type, context),
            "sitemap_entry": self._generate_sitemap_entry(page_type, context),
            "robots_directives": self._generate_robots_directives(page_type, context),
        }

    def _generate_json_ld(self, page_type: str, context: Dict) -> str:
        """Generate JSON-LD schema.org markup."""
        schemas = {
            "SoftwareApplication": {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Genesis",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Cloud",
                "offers": {"@type": "Offer", "price": "39", "priceCurrency": "USD"},
            },
            "Service": {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": "Genesis Autonomous Business Launch",
                "description": "Autonomous AI platform for business creation and launch",
                "provider": {"@type": "Organization", "name": "Genesis"},
            },
            "Product": {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Genesis",
                "description": "Autonomous AI platform for business creation and launch",
            },
            "FAQPage": {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []},
            "HowTo": {
                "@context": "https://schema.org",
                "@type": "HowTo",
                "name": "How to launch a business with Genesis",
                "description": "Step-by-step guide to launching a business with AI agents",
            },
        }

        schema = schemas.get(page_type, schemas["SoftwareApplication"])
        import json

        return json.dumps(schema)

    def _generate_meta_tags(self, page_type: str, context: Dict) -> Dict:
        """Generate meta tags."""
        return {
            "title": context.get("title", "Genesis - Autonomous Business Launch Platform"),
            "description": context.get(
                "description",
                "Launch your business with AI agents. Voice-first, autonomous, compliant.",
            ),
            "canonical": context.get("canonical", ""),
            "og:title": context.get("title", "Genesis - Autonomous Business Launch"),
            "og:description": context.get("description", "Launch your business with AI agents."),
            "og:type": "website",
            "og:image": "/og-image.png",
            "twitter:card": "summary_large_image",
            "twitter:title": context.get("title", "Genesis"),
            "twitter:description": context.get(
                "description", "Launch your business with AI agents."
            ),
        }

    def _generate_canonical(self, page_type: str, context: Dict) -> str:
        """Generate canonical URL."""
        base = "https://genesis.ai"
        paths = {
            "landing": "/",
            "pricing": "/pricing",
            "features": "/features",
            "industry": f"/industries/{context.get('slug', '')}",
            "use_case": f"/use-cases/{context.get('slug', '')}",
            "template": f"/templates/{context.get('slug', '')}",
            "vs": f"/vs/{context.get('competitor', '')}",
            "glossary": f"/glossary/{context.get('term', '')}",
            "guide": f"/guides/{context.get('slug', '')}",
        }
        return base + paths.get(page_type, "/")

    def _generate_sitemap_entry(self, page_type: str, context: Dict) -> Dict:
        """Generate sitemap entry."""
        return {
            "url": self._generate_canonical(page_type, context),
            "lastmod": datetime.now(timezone.utc).isoformat(),
            "changefreq": "weekly",
            "priority": 1.0 if page_type == "landing" else 0.8,
        }

    def _generate_robots_directives(self, page_type: str, context: Dict) -> str:
        """Generate robots.txt directives."""
        return "index, follow"

    async def generate_programmatic_pages(self, config_name: str, data: List[Dict]) -> List[Dict]:
        """Generate programmatic SEO pages."""
        config = next((c for c in self.programmatic_configs if c.data_source == config_name), None)
        if not config:
            return []

        pages = []
        for item in data:
            {
                "title": config.title_template.format(**item),
                "description": config.description_template.format(**item),
                "slug": item.get("slug", item.get("name", "").lower().replace(" ", "-")),
                **item,
            }

            page = {
                "url": config.url_pattern.format(**item),
                "title": config.title_template.format(**item),
                "description": config.description_template.format(**item),
                "schema_type": config.schema_type,
                "schema": config.schema_template,
                "keywords": [kw.format(**item) for kw in config.keywords_template],
                **item,
            }
            pages.append(page)

        return pages

    async def optimize_core_web_vitals(self, page_url: str) -> Dict:
        """Analyze and optimize Core Web Vitals."""
        return {
            "lcp": {
                "target": "< 2.5s",
                "actions": [
                    "Optimize images",
                    "Preload critical resources",
                    "Reduce server response time",
                ],
            },
            "fid": {
                "target": "< 100ms",
                "actions": ["Minimize main thread work", "Use web workers", "Code splitting"],
            },
            "cls": {
                "target": "< 0.1",
                "actions": ["Set image dimensions", "Reserve space for ads", "Font display swap"],
            },
            "inp": {
                "target": "< 200ms",
                "actions": ["Optimize event handlers", "Debounce inputs", "Use useTransition"],
            },
        }


__all__ = ["SEOAgent", "SEOPage", "ProgrammaticSEOConfig"]

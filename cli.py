#!/usr/bin/env python3
"""
Genesis CLI - test the agent swarm from the command line.

Commands:
  genesis agents                          List the production agent swarm
  genesis build "Business Name"           Build a full company package
       --desc "what they do"
       --goal "founder goal"
  genesis voice "message"                 Send a message to the voice agent
  genesis status                          Check system status (API, DB, Ollama)
  genesis sales                           Show the AI sales pipeline board
  genesis revenue                         Show the revenue dashboard
  genesis seo                             Show the SEO asset inventory

Examples:
  python cli.py build "GreenScape Landscaping" --desc "residential lawn care and landscaping in Austin, TX"
  python cli.py agents
  python cli.py voice "I want to launch a landscaping business"
"""

import argparse
import asyncio
import json
import os
import sys

os.environ.setdefault("JWT_SECRET_KEY", "cli-local-secret")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models.local_llm.ollama_client import OllamaClient  # noqa: E402
from core.orchestration.agent_manager import agent_manager  # noqa: E402
from core.orchestration.register_default_agents import register_default_agents  # noqa: E402
from core.services.company_builder import company_builder  # noqa: E402


def cmd_agents(_args) -> int:
    register_default_agents()
    from core.auth.agent_identity import AgentIdentityRegistry

    identities = AgentIdentityRegistry.get_all()
    print(f"\nGenesis Agent Swarm ({len(identities)} agents)\n" + "=" * 60)
    for identity in sorted(identities, key=lambda i: i.agent_id):
        registered = identity.agent_id in agent_manager.agents
        status = "RUNNING" if registered else "available"
        tools = ", ".join(sorted(identity.tool_allowlist)[:4])
        print(f"  {identity.display_name:24s} [{status:9s}] tools: {tools}")
    print()
    return 0


def agent_id_registered(agent_id: str) -> bool:
    return agent_id in agent_manager.agents


def cmd_build(args) -> int:
    print("\n[Genesis] Building company package...\n")
    result = asyncio.run(
        company_builder.build_company(args.name, args.desc, args.goal)
    )
    print(json.dumps(result, indent=2))
    print("\nArtifact written to: output/companies/%s/" % result["slug"])
    return 0


def cmd_voice(args) -> int:
    async def run():
        from core.services.voice_agent_service import voice_agent_service

        session = await voice_agent_service.create_session("voice")
        print(f"\n[Genesis Voice Agent] session={session['session_id']}")
        print(f"[Genesis Voice Agent] greeting: {session['greeting']}\n")
        reply = await voice_agent_service.process_message(session["session_id"], args.message)
        print(f"[Genesis Voice Agent] reply: {reply['reply']}")
        print(f"[Genesis Voice Agent] intent: {reply['intent']}")
        print(f"[Genesis Voice Agent] audio: {'{:.0f} KB base64'.format(len(reply['reply_audio_b64'] or '') * 3 / 4 / 1024)}")
        return 0

    return asyncio.run(run())


def cmd_status(_args) -> int:
    import httpx

    def check(label: str, url: str) -> str:
        try:
            r = httpx.get(url, timeout=5)
            return "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
        except Exception:
            return "UNREACHABLE"

    print("\nGenesis System Status\n" + "=" * 60)
    print(f"  API health      : {check('api', 'http://localhost:8000/health')}")
    print(f"  API ready       : {check('api', 'http://localhost:8000/ready')}")
    print(f"  Ollama (local)  : {check('ollama', 'http://127.0.0.1:11434/api/tags')}")

    async def llm_check():
        try:
            r = await OllamaClient().generate("Reply with the single word OK")
            return "OK (%s)" % r.get("model")
        except Exception as e:
            return f"FAILED ({e})"

    print(f"  LLM generation  : {asyncio.run(llm_check())}")
    print()
    return 0


def cmd_sales(args) -> int:
    """Show the AI sales pipeline board from the terminal."""
    from core.persistence.session import init_db

    init_db()
    from core.services.sales_pipeline import sales_pipeline

    snapshot = sales_pipeline.pipeline_snapshot()
    forecast = sales_pipeline.forecast()

    print("\nAI Sales Pipeline\n" + "=" * 60)
    print(f"  Total deals      : {snapshot['total_deals']}")
    print(f"  Open deals       : {snapshot['open_deals']}")
    print(f"  Weighted pipeline: ${snapshot['weighted_pipeline_cents'] / 100:,.2f}/mo")
    print("\n  Stage                 Deals   Weighted ($/mo)   Prob")
    for stage in snapshot["stages"]:
        print(
            f"  {stage['stage']:20s} {stage['count']:5d} "
            f"{stage['weighted_value_cents'] / 100:14,.2f}   "
            f"{stage['probability']:.0%}"
        )
    print(
        f"\n  Closed-won MRR    : ${forecast['closed_won_mrr_cents'] / 100:,.2f}/mo"
    )
    print(
        f"  Annual contracts  : ${forecast['annual_contract_cents'] / 100:,.2f}"
    )

    if args.deals:
        deals = sales_pipeline.list_deals(stage=args.deals)
        if not deals:
            print(f"\n  (no deals in stage '{args.deals}')")
        for d in deals:
            print(
                f"  {d['id'][:8]}  {d['email']:<28s} {d['stage']:<10s} "
                f"${(d['amount_cents'] or 0) / 100:,.0f}/mo "
                f"({d['probability']:.0%})"
            )
    print()
    return 0


def cmd_revenue(args) -> int:
    """Print the revenue dashboard from the terminal."""
    from core.persistence.session import init_db

    init_db()
    from core.services.revenue_analytics import revenue_analytics

    summary = revenue_analytics.summary()

    print("\nRevenue Dashboard\n" + "=" * 60)
    print(f"  Monthly recurring : ${summary['mrr_cents'] / 100:,.2f}")
    print(f"  Annualized (ARR)  : ${summary['arr_cents'] / 100:,.2f}")
    print(f"  Annual contracts  : ${summary['annual_contract_cents'] / 100:,.2f}")
    print(f"  Open weighted ARR : ${summary['open_weighted_annual_cents'] / 100:,.2f}")
    print(f"  Closed-won deals  : {summary['closed_won_count']}")
    print(f"  Quotes approved   : {summary['quotes_approved']}")
    print("  Tier mix (count / MRR):")
    for tier, mix in summary["tier_mix"].items():
        print(
            f"    {tier:10s} {mix['count']:3d}   "
            f"${mix['mrr_cents'] / 100:,.2f}/mo"
        )
    print()
    return 0


def cmd_seo(args) -> int:
    """Print the crawler-facing SEO assets from the terminal."""
    from core.services.seo_engine import seo_engine

    print("\nSEO Assets\n" + "=" * 60)
    inventory = seo_engine.page_inventory()
    print(f"  URL inventory : {len(inventory)} pages")
    for entry in inventory[:10]:
        print(f"    {entry['url']}  ({entry['changefreq']}, {entry['priority']:.1f})")

    print("\n  robots.txt:")
    print("  ---")
    for line in seo_engine.build_robots().splitlines():
        print(f"  {line}")
    print("  ---")
    print(f"\n  sitemap.xml: {seo_engine.build_sitemap().count('<url>')} <url> entries")
    print()
    return 0


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="genesis", description="Genesis CLI - test the agent swarm")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("agents", help="list the production agent swarm")

    b = sub.add_parser("build", help="build a full company package")
    b.add_argument("name", help="business name")
    b.add_argument("--desc", default="a service business", help="business description")
    b.add_argument("--goal", default=None, help="founder goal")

    v = sub.add_parser("voice", help="test the voice agent conversation loop")
    v.add_argument("message", nargs="?", default="I want to launch a business", help="message to send")

    sub.add_parser("status", help="check system status")

    s = sub.add_parser("sales", help="show the AI sales pipeline board")
    s.add_argument("--deals", default=None, help="filter by stage")

    sub.add_parser("revenue", help="show the revenue dashboard")
    sub.add_parser("seo", help="show the SEO asset inventory")
    return parser


def main() -> int:
    parser = make_arg_parser()
    args = parser.parse_args()
    handlers = {
        "agents": cmd_agents,
        "build": cmd_build,
        "voice": cmd_voice,
        "status": cmd_status,
        "sales": cmd_sales,
        "revenue": cmd_revenue,
        "seo": cmd_seo,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

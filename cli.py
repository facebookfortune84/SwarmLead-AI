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
        registered = agent_id_registered = identity.agent_id in agent_manager.agents
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


def main() -> int:
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

    args = parser.parse_args()
    handlers = {
        "agents": cmd_agents,
        "build": cmd_build,
        "voice": cmd_voice,
        "status": cmd_status,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

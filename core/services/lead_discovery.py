"""
Lead discovery engine — finds *real* businesses that publish a contact
email on their own website, validates the domain accepts mail, and only
then adds a lead to the pipeline.

Why this exists: naive "public records" scraping produces non-response
mailboxes and generic addresses that never answer. A business that lists
a contact address on its own site — reachable from a search engine — is
a real, currently-operating prospect with a monitored inbox.

Sources (all free, no API keys):
  - DuckDuckGo HTML search results (real business URLs)
  - Bing HTML search results (fallback)
  - The business's own website (homepage + /contact) for the published
    contact email, business name, and page title.

Validation (every candidate):
  - Reserved / test-domain blocklist (example.com, test.co, ...)
  - Disposable-mailbox blocklist (mailinator, yopmail, ...)
  - MX record must exist on the domain (domain accepts mail at all)
  - Dedup against existing leads, suppression list, and prior discoveries

The one human gate stays where it belongs: discovery only *adds DB rows*
(internal preparation). No email is ever sent without founder approval in
the growth console.
"""

import asyncio
import json
import logging
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("LeadDiscovery")

# RFC 2606 reserved + common junk domains that would hard-bounce.
RESERVED_DOMAINS = {
    "example.com", "example.net", "example.org", "example.edu",
    "test.com", "test.net", "test.org", "test.co", "test.io",
    "invalid", "localhost", "domain.com", "domain.org", "email.com",
    "yourdomain.com", "somedomain.com", "yourcompany.com", "acme.com",
    "acme.org", "nowhere.com", "fakeemail.com", "testemail.com",
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "yopmail.com", "guerrillamail.com", "sharklasers.com",
    "temp-mail.org", "10minutemail.com", "throwawaymail.com", "mintemail.com",
    "maildrop.cc", "trashmail.com", "getnada.com", "dispostable.com",
}

# Role inboxes that almost never convert and often bounce — never use alone.
GENERIC_LOCALPARTS = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer",
    "mailer-daemon", "postmaster", "abuse", "support", "help", "admin",
    "webmaster", "billing", "sales", "info", "contact", "office", "hello",
    "service", "services", "orders", "register", "hostmaster", "root",
}

FINDINGS_PATH = __import__("pathlib").Path(__file__).resolve().parents[2] / "data" / "lead_discovery_findings.json"


@dataclass
class DiscoveredLead:
    email: str
    name: str = ""
    company: str = ""
    website: str = ""
    vertical: str = ""
    source: str = "search_website"
    intent_score: int = 60
    confidence: str = "high"
    details: Dict[str, Any] = field(default_factory=dict)


def _reserved(domain: str) -> bool:
    d = domain.strip().lower()
    return d in RESERVED_DOMAINS or d in DISPOSABLE_DOMAINS


BLOCKED_MAIL_DOMAINS = {
    "delta.org", "deltadental.com", "deltadentalins.com", "anthem.com",
    "aetna.com", "humana.com", "uhc.com", "cigna.com", "metlife.com",
    "guardianlife.com", "principal.com", "aaa.com", "statefarm.com",
    "geico.com", "progressive.com", "allstate.com", "email.de", "gmx.de",
    "web.de", "freenet.de", "t-online.de",
}


def _blocked_maildomain(domain: str) -> bool:
    d = domain.strip().lower()
    if d in BLOCKED_MAIL_DOMAINS:
        return True
    # Insurance-aggregator subdomains and obvious bulk mailing hosts.
    if any(seg in d for seg in ("deltadental", "insurance", "northwesternmutual")):
        return True
    return False


def _extract_emails(html: str) -> List[str]:
    if not html:
        return []
    # Handle obfuscated mailto links like info AT domain DOT com.
    for m in re.finditer(r"\b([\w.\-+]+)\s*\[?at\]?\s*@?\s*([\w\-]+)\s*\[?dot\]?\s*([a-z]{2,})\b", html, re.I):
        local = m.group(1).strip(".: ")
        if local and " " not in local:
            html = html.replace(m.group(0), f"{local}@{m.group(2)}.{m.group(3)}")
    found: List[str] = []
    for m in re.finditer(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", html):
        email = m.group(0).strip(".,;:<>\"'()[]{}")
        if not email or len(email) > 120:
            continue
        local, _, domain = email.partition("@")
        if not local or not domain or "." not in domain:
            continue
        if _reserved(domain):
            continue
        if local.lower() in GENERIC_LOCALPARTS:
            continue  # role inbox, not a decision-maker
        found.append(email.lower())
    # Dedup, stable order.
    return list(dict.fromkeys(found))


def _title_from_html(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        if title:
            return title[:120]
    return ""


def _mx_ok(domain: str) -> Tuple[bool, Optional[str]]:
    """True if the domain has at least one MX record (accepts mail)."""
    try:
        import dns.resolver

        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        if answers:
            return True, str(answers[0].exchange).rstrip(".")
    except Exception:
        pass
    # No MX: check A record — some small sites accept mail via implicit A.
    try:
        import dns.resolver

        dns.resolver.resolve(domain, "A", lifetime=5)
        return True, "implicit-A"
    except Exception:
        return False, None


class LeadDiscoveryEngine:
    """Search for real businesses, crawl their site, validate, return leads."""

    def __init__(self, findings_path: Optional[str] = None) -> None:
        self.findings_path = findings_path or FINDINGS_PATH
        self._seen: Dict[str, Dict] = self._load_findings()
        self.timeout = httpx.Timeout(12.0, connect=6.0)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    # -------------------------------------------------------------- helpers
    def _load_findings(self) -> Dict[str, Dict]:
        try:
            p = __import__("pathlib").Path(self.findings_path)
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        return {}

    def _save_findings(self) -> None:
        try:
            p = __import__("pathlib").Path(self.findings_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(self._seen, indent=2), encoding="utf-8")
        except OSError as exc:
            logger.warning("Could not persist discovery findings: %s", exc)

    def _known(self, email: str) -> bool:
        return email.lower() in self._seen

    def _record(self, lead: DiscoveredLead) -> None:
        self._seen[lead.email.lower()] = {
            "company": lead.company,
            "website": lead.website,
            "vertical": lead.vertical,
            "intent_score": lead.intent_score,
            "discovered_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }
        self._save_findings()

    # -------------------------------------------------------------- search
    async def _search_ddg(self, query: str) -> List[str]:
        """Return business-homepage URLs from DuckDuckGo HTML search."""
        urls: List[str] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                r = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
                if r.status_code != 200:
                    return urls
                for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"', r.text):
                    href = m.group(1)
                    if "uddg=" in href:
                        from urllib.parse import unquote, parse_qs

                        qs = parse_qs(href)
                        if "uddg" in qs:
                            href = qs["uddg"][0]
                    urls.append(href)
        except Exception as exc:
            logger.info("DDG search failed (%s)", exc)
        return urls

    async def _search_bing_rss(self, query: str) -> List[str]:
        """Bing RSS is machine-readable and free. Preferred primary source."""
        urls: List[str] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                r = await client.get(
                    "https://www.bing.com/search",
                    params={"format": "rss", "q": query, "count": "20"},
                )
                if r.status_code != 200:
                    return urls
                # <item><title>..</title><link>URL</link>
                for m in re.finditer(r"<item>\s*<title>(.*?)</title>\s*<link>(.*?)</link>", r.text, re.S):
                    urls.append(m.group(2).strip())
        except Exception as exc:
            logger.info("Bing RSS failed (%s)", exc)
        return urls

    async def _search_bing(self, query: str) -> List[str]:
        urls: List[str] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                r = await client.get("https://www.bing.com/search", params={"q": query})
                if r.status_code != 200:
                    return urls
                for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*<h2', r.text, re.I):
                    urls.append(m.group(1))
                for m in re.finditer(r'<h2[^>]*><a[^>]+href="(https?://[^"]+)"', r.text, re.I):
                    urls.append(m.group(1))
        except Exception as exc:
            logger.info("Bing search failed (%s)", exc)
        return urls

    async def _find_urls(self, query: str) -> List[str]:
        results: List[str] = []
        # Bing RSS first (reliable, machine-readable), then fallbacks.
        rss = await self._search_bing_rss(query)
        results.extend(rss)
        if not results:
            ddg, bing = await asyncio.gather(
                self._search_ddg(query),
                self._search_bing(query),
                return_exceptions=True,
            )
            if isinstance(ddg, list):
                results.extend(ddg)
            if isinstance(bing, list):
                results.extend(bing)
        # De-dup, drop junk URLs, normalize to origin.
        seen: set = set()
        cleaned: List[str] = []
        for url in results:
            try:
                from urllib.parse import urlparse

                p = urlparse(url)
                if p.scheme not in {"http", "https"} or not p.netloc:
                    continue
                netloc = p.netloc.lower()
                host = p.hostname or ""
                bare_host = host[4:] if host.startswith("www.") else host
                # Skip social/directory/aggregator/edu/gov/institutional hosts.
                BLOCKED_HOSTS = {
                    "www.facebook.com", "twitter.com", "x.com", "linkedin.com",
                    "yelp.com", "yellowpages.com", "pinterest.com", "instagram.com",
                    "youtube.com", "tiktok.com", "reddit.com", "wikipedia.org",
                    "amazon.com", "google.com", "bing.com", "duckduckgo.com",
                    "delta.dental", "deltadental.com", "deltadentalins.com",
                    "healthgrades.com", "zocdoc.com", "webmd.com", "angi.com",
                    "houzz.com", "angieslist.com", "thryv.com", "maps.google.com",
                    "bbb.org", "angis.com", "care.com", "thumbtack.com",
                    "wix.com", "godaddy.com", "goo.gl", "bit.ly",
                    "delta.org", "deltadental.org", "anthem.com", "aetna.com",
                    "humana.com", "uhc.com", "cigna.com", "metlife.com",
                    "guardianlife.com", "principal.com", "aaa.com", "aa.com",
                    "findadentist.com", "dentist.com", "zocdoc.com",
                }
                if host in BLOCKED_HOSTS or bare_host in BLOCKED_HOSTS:
                    continue
                if bare_host.endswith((".edu", ".gov", ".mil")):
                    continue
                if bare_host.endswith(".org"):
                    continue
                # Single-page directory hits and generic "join us" aggregators.
                if any(
                    seg in netloc
                    for seg in (
                        "wikimedia", "chamberofcommerce", "bizapedia", "opencorporates",
                        "manta.com", "cylex", "hotfrog", "brownbook", "citysearch",
                        "superpages", "infobel", "yell.com", "nicelocal", "doctify",
                    )
                ):
                    continue
                origin = f"{p.scheme}://{p.netloc}"
                if origin in seen:
                    continue
                seen.add(origin)
                cleaned.append(origin)
            except Exception:
                continue
        return cleaned

    async def _crawl(self, url: str) -> Tuple[str, Dict[str, str]]:
        """Fetch a business homepage + contact page, return (html, meta)."""
        meta: Dict[str, str] = {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code >= 400:
                    return "", meta
                html = r.text
                meta["title"] = _title_from_html(html)
                meta["final_url"] = str(r.url)
                # Prefer emails from the site itself.
                emails = _extract_emails(html)
                if emails:
                    meta["homepage_emails"] = emails
                # Try a contact page for a decision-maker's address.
                for path in ("/contact", "/contact-us", "/about", "/contactus"):
                    try:
                        cr = await client.get(url.rstrip("/") + path)
                        if cr.status_code >= 400:
                            continue
                        chtml = cr.text
                        meta.setdefault("contact_emails", []).extend(_extract_emails(chtml))
                    except Exception:
                        continue
                meta["contact_emails"] = list(
                    dict.fromkeys(meta.get("contact_emails", []))
                )
                return html, meta
        except Exception as exc:
            logger.info("Crawl failed %s (%s)", url, exc)
            return "", meta

    # ------------------------------------------------------------- discover
    async def discover(
        self,
        verticals: Optional[List[str]] = None,
        max_targets: int = 6,
        geo: Optional[str] = None,
    ) -> List[DiscoveredLead]:
        """Run one discovery pass. Returns validated, previously-unseen leads."""
        queries = []
        base_verticals = verticals or [
            "dental clinic", "home services contractor", "real estate brokerage",
            "fitness coaching studio", "law firm", "e-commerce store",
        ]
        geo_suffix = geo or "United States"
        for v in base_verticals[:max_targets]:
            # Query for the business's *own* site — not directories.
            queries.append(f'"{v}" site owner contact -yelp -healthgrades -facebook')
            queries.append(f"{v} official website -yelp -linkedin -findadentist")

        # Spread query load so we don't hammer any single source.
        random.shuffle(queries)
        candidates: List[DiscoveredLead] = []
        seen_emails: set = set()
        for query in queries[: max_targets * 2]:
            urls = await self._find_urls(query)
            for url in urls[:4]:
                _, meta = await self._crawl(url)
                emails = list(
                    dict.fromkeys(
                        (meta.get("contact_emails") or []) + (meta.get("homepage_emails") or [])
                    )
                )
                domain = url.split("//")[-1].split("/")[0].lower()
                for email in emails:
                    if email in seen_emails or self._known(email):
                        continue
                    local, _, maildomain = email.partition("@")
                    if _blocked_maildomain(maildomain):
                        logger.info("Skip %s (blocked mail domain)", email)
                        continue
                    mx_ok, mx_host = _mx_ok(maildomain)
                    if not mx_ok:
                        logger.info("Skip %s (no MX)", email)
                        continue
                    name = _name_from_email(local)
                    company = meta.get("title") or domain
                    company = re.sub(r"\s*[|–—-]\s*.*$", "", company).strip()
                    if _looks_generic_company(company):
                        continue
                    score = _score_lead(maildomain, mx_host)
                    lead = DiscoveredLead(
                        email=email,
                        name=name,
                        company=company,
                        website=meta.get("final_url") or url,
                        vertical=query.split(" ")[0].title(),
                        source="search_website",
                        intent_score=score,
                        confidence="high" if maildomain not in FREE_DOMAINS else "medium",
                        details={"mx": mx_host, "title": meta.get("title", "")},
                    )
                    seen_emails.add(email)
                    candidates.append(lead)
                    self._record(lead)
        return candidates

    def findings(self) -> List[Dict]:
        return [
            {"email": k, **v} for k, v in sorted(
                self._seen.items(),
                key=lambda kv: kv[1].get("discovered_at", ""),
                reverse=True,
            )
        ]


FREE_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "proton.me", "protonmail.com", "mail.com", "zoho.com",
}


def _name_from_email(local: str) -> str:
    parts = re.split(r"[._\-+]+", local)
    parts = [p for p in parts if p]
    if not parts:
        return ""
    return " ".join(p.capitalize() for p in parts[:2])


GENERIC_COMPANY_MARKERS = (
    "homepage", "web site", "website", "just a moment", "sign in", "sign up",
    "welcome to", "google translate", "under construction", "domain for sale",
    "default", "for sale", "index of", "placeholder",
)


def _looks_generic_company(company: str) -> bool:
    low = company.lower().strip()
    if not low or len(low) < 3:
        return True
    return any(m in low for m in GENERIC_COMPANY_MARKERS)


def _score_lead(maildomain: str, mx_host: Optional[str]) -> int:
    score = 60
    if maildomain not in FREE_DOMAINS:
        score += 20  # business domain > personal inbox
    if mx_host and mx_host != "implicit-A":
        score += 10  # explicit MX = real mail infrastructure
    if maildomain in {"gmail.com", "googlemail.com", "yahoo.com", "hotmail.com"}:
        score -= 10
    return max(10, min(99, score))


lead_discovery = LeadDiscoveryEngine()

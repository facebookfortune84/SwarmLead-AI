"""
Deliverability engine — SPF/DKIM/DMARC records, live DNS verification, a
sender health score, and a suppression list (bounces / unsubscribes /
complaints) that the growth loop consults before drafting outreach.

Cold-email delivery is the #1 silent killer of outreach ROI. This module
makes it observable: it tells you whether your sending domain would pass
SPF/DKIM/DMARC, gives you copy-paste DNS records, and keeps a suppression
list so you never re-mail someone who bounced or unsubscribed (which is
what destroys sender reputation).
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("Deliverability")

SUPPRESSION_PATH = Path(__file__).resolve().parents[2] / "data" / "suppression_list.json"

# Free-email domains are higher spam-risk for cold outreach; a healthy
# list skews toward business domains. Used for targeting, not blocking.
FREE_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "proton.me", "protonmail.com", "mail.com", "zoho.com",
}

BOUNCE_MARKERS = ("bounce", "undeliverable", "550", "5.1.1", "5.7.1", "hard fail")
COMPLAINT_MARKERS = ("complaint", "abuse", "spam report")


class DeliverabilityEngine:
    """Sender-health scoring, DNS record generation, and suppression tracking."""

    def __init__(self, suppression_path: Optional[Path] = None) -> None:
        self.suppression_path = suppression_path or SUPPRESSION_PATH
        self._suppressed: Dict[str, Dict] = self._load_suppression()

    # ------------------------------------------------------------ suppression
    def _load_suppression(self) -> Dict[str, Dict]:
        if self.suppression_path.exists():
            try:
                return json.loads(self.suppression_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                logger.warning("Suppression list unreadable; starting fresh")
        return {}

    def _save_suppression(self) -> None:
        try:
            self.suppression_path.parent.mkdir(parents=True, exist_ok=True)
            self.suppression_path.write_text(
                json.dumps(self._suppressed, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("Could not persist suppression list: %s", exc)

    def suppress(self, email: str, reason: str) -> bool:
        """Add/update a suppressed address. Returns True if newly added."""
        key = email.strip().lower()
        if not key:
            return False
        existed = key in self._suppressed
        self._suppressed[key] = {
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_suppression()
        return not existed

    def is_suppressed(self, email: str) -> bool:
        return email.strip().lower() in self._suppressed

    def record_bounce(self, email: str, message: str = "") -> bool:
        reason = "bounce"
        for marker in BOUNCE_MARKERS:
            if marker in message.lower():
                reason = f"bounce:{marker}"
                break
        return self.suppress(email, reason)

    def record_complaint(self, email: str) -> bool:
        return self.suppress(email, "complaint")

    def record_unsubscribe(self, email: str) -> bool:
        return self.suppress(email, "unsubscribe")

    def suppression_stats(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self._suppressed.values():
            reason = entry.get("reason", "unknown").split(":")[0]
            counts[reason] = counts.get(reason, 0) + 1
        return counts

    def filter_out(self, emails: List[str]) -> List[str]:
        return [e for e in emails if not self.is_suppressed(e)]

    # ------------------------------------------------------------------ dns
    @staticmethod
    def recommended_records(domain: str, include: str = "amazonses.com") -> Dict[str, Dict[str, str]]:
        """Copy-paste DNS records to set for a dedicated sending domain.

        Recommended: use a subdomain like ``mail.yourdomain.com`` as the
        envelope/from domain so failures never hurt your apex domain's mail.
        """
        base = domain.strip().lower().rstrip(".")
        dkim = f"swarmlead._domainkey.{base}"
        return {
            "SPF (TXT)": {
                "name": base,
                "ttl": "3600",
                "value": f"v=spf1 include:{include} ~all",
            },
            "DKIM (TXT)": {
                "name": dkim,
                "ttl": "3600",
                "value": "v=DKIM1; k=rsa; p=PUBLIC_KEY_FROM_PROVIDER",
            },
            "DMARC (TXT)": {
                "name": f"_dmarc.{base}",
                "ttl": "3600",
                "value": f"v=DMARC1; p=none; rua=mailto:dmarc@{base}",
            },
        }

    @staticmethod
    def recommended_alias(domain: str, local: str = "hello") -> Dict[str, str]:
        """Suggest a branded sending alias for a domain.

        Cold outreach from a personal Gmail gets filtered fast. Point ``SMTP_FROM``
        at a branded address (``hello@yourdomain.com``) with SPF/DKIM/DMARC in
        place, and delivery rates improve dramatically. Gmail allows sending as
        a verified alias; the provider (e.g. Amazon SES) supplies the DKIM key.
        """
        base = domain.strip().lower().rstrip(".")
        if not base or "." not in base:
            return {"error": "invalid domain"}
        from_address = f"{local}@{base}"
        return {
            "from_address": from_address,
            "display_name": "Genesis Forge by Realms 2 Riches",
            "smtp_from_env": f"SMTP_FROM={from_address}",
            "records": DeliverabilityEngine.recommended_records(base),
            "gmail_alias_hint": (
                "In Gmail: Settings → Accounts → Send mail as → Add another "
                f"email address → {from_address}. Verify the address, then keep "
                "your sending domain's SPF/DKIM/DMARC records live."
            ),
        }

    @staticmethod
    def check_dns(domain: str) -> Dict[str, str]:
        """Live lookup of SPF / DMARC records for a domain.

        Returns 'present' / 'missing' / 'unknown' (unknown = DNS lookup
        blocked from this network, e.g. inside a container without egress).
        """
        import dns.resolver  # dnspython

        result: Dict[str, str] = {}
        targets = {
            "spf": domain,
            "dmarc": f"_dmarc.{domain}",
        }
        for label, name in targets.items():
            found = False
            try:
                answers = dns.resolver.resolve(name, "TXT")
                for ans in answers:
                    text = "".join(part.decode() for part in ans.strings)
                    if label == "spf" and text.startswith("v=spf1"):
                        found = True
                    elif label == "dmarc" and text.startswith("v=DMARC1"):
                        found = True
            except Exception:  # nxdomain / timeout / no egress
                result[label] = "unknown"
                continue
            result[label] = "present" if found else "missing"
        return result

    # ---------------------------------------------------------------- score
    def score(self) -> Dict[str, object]:
        """Heuristic sender-health score (0-100) for the current config."""
        score = 40.0
        notes: List[str] = []
        warnings: List[str] = []

        from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
        smtp_user = os.getenv("SMTP_USER", "")

        if not from_email:
            warnings.append("SMTP_FROM not set")
        elif "@gmail.com" in from_email or "@googlemail.com" in from_email:
            notes.append("Sending via personal Gmail SMTP — fine for light volume, "
                         "risky for cold outreach at scale")
            score -= 15
        else:
            notes.append("Dedicated sending address configured")
            score += 10

        domain = from_email.split("@")[-1] if "@" in from_email else ""
        if domain:
            dns = self.check_dns(domain)
            for record, status in dns.items():
                if status == "present":
                    score += 8
                elif status == "missing":
                    warnings.append(f"{record.upper()} record missing for {domain}")
                    score -= 8

        suppression = self.suppression_stats()
        bounces = suppression.get("bounce", 0)
        if bounces > 0:
            score -= min(15, bounces * 2)
            warnings.append(f"{bounces} known bounces — will be excluded automatically")

        if os.getenv("OUTREACH_DRY_RUN", "0") == "1":
            notes.append("DRY RUN: no mail is actually sent")

        return {
            "score": max(0, min(100, round(score))),
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
            "notes": notes,
            "warnings": warnings,
            "sending_address": from_email,
            "suppression": suppression,
        }


deliverability = DeliverabilityEngine()

__all__ = [
    "DeliverabilityEngine",
    "deliverability",
    "FREE_EMAIL_DOMAINS",
]

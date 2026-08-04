# Sending with a branded alias (email deliverability)

Cold outreach that comes from a personal Gmail (`@gmail.com`) is filtered far
more aggressively than mail from a dedicated domain. The fix is a **branded
sending alias** — mail sent as `hello@realms2riches.com` instead of
`robertdemottojr83@gmail.com`.

## Recommended setup

1. **Pick a sending subdomain.** Use `mail.realms2riches.com` (or the apex)
   so a deliverability problem never takes down the main site's mail.

2. **Add the DNS records** (SPF/DKIM/DMARC). The API can print them:

   ```bash
   curl "http://localhost:8000/api/deliverability/alias?domain=realms2riches.com"
   ```

   or generate them directly:

   ```bash
   curl "http://localhost:8000/api/deliverability/records?domain=mail.realms2riches.com"
   ```

   Recommended (copy-paste into your DNS provider):

   | Type | Name | Value |
   | --- | --- | --- |
   | TXT | `mail` | `v=spf1 include:amazonses.com ~all` |
   | TXT | `swarmlead._domainkey.mail` | `v=DKIM1; k=rsa; p=<PUBLIC_KEY_FROM_PROVIDER>` |
   | TXT | `_dmarc.mail` | `v=DMARC1; p=none; rua=mailto:dmarc@realms2riches.com` |

3. **Add the alias to your sending provider.**
   - Gmail: Settings → Accounts → Send mail as → Add another email address →
     `hello@realms2riches.com`, verify the confirmation email.
   - Amazon SES / SendGrid: verify the domain, create the identity, copy the
     DKIM key into the DNS record above.

4. **Point the app at the alias.**

   ```env
   # .env.docker.local
   SMTP_FROM=hello@realms2riches.com
   SMTP_USER=robertdemottojr83@gmail.com   # the SMTP login stays the same
   SMTP_PASS=...
   ```

   Gmail only lets you send *as* a verified alias; the auth credentials stay
   the Gmail account's.

5. **Verify.** After DNS propagates:

   ```bash
   curl "http://localhost:8000/api/deliverability/dns?domain=mail.realms2riches.com"
   curl "http://localhost:8000/api/deliverability/score"
   ```

   The score should rise from ~41 (grade C) toward A as records go live.

## Guardrails already in place

- Outreach is **dry-run by default** (`OUTREACH_DRY_RUN=1`); flip to `0` only
  after DNS is verified.
- The growth loop auto-suppresses bounces/unsubscribes and never re-mails
  them (`core/services/deliverability.py`).
- Rate limit 40/hr, per-domain cap 2/cycle — protects a warm-up phase.

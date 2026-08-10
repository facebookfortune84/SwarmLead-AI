# Hosting on Cloudflare Tunnel + The Domain Switch Playbook

Everything in this repo treats **one environment variable** as the source of
truth for the public hostname:

```
PUBLIC_DOMAIN=your-brand.com
```

Change it, rebuild the containers, and the whole product moves: CORS
origins, SEO canonical URLs, sitemap, robots.txt, Open Graph tags, share
links, Stripe success URLs, tenant subdomains, and the API host all follow.

This document covers:
1. How to get the whole stack online **for free** (Cloudflare Tunnel +
   your Docker host — no public IP, no port forwarding, no cloud bills).
2. What exactly changes when you swap domains.
3. Your aligned to-do list vs. what the code does for you.

---

## 1. Free hosting: Cloudflare Tunnel -> your current Docker host

Cloudflare Tunnel (free tier) exposes your local Docker stack to the
public internet through Cloudflare's edge. The containers keep running
exactly as they do today — full feature access, WebSockets (voice agent),
streaming, no platform restrictions. There is nothing to port, no
serverless transforms, no per-request limits baked by a PaaS.

### 1a. Get a free tunnel URL right now (2 minutes, zero setup)

Cloudflare's Quick Tunnel requires no account, no domain, no config:

```bash
docker run -d --name swarmlead-tunnel-quick --network swarmlead-ai_default \
  cloudflare/cloudflared tunnel --no-autoupdate --url http://frontend:3000
docker logs -f swarmlead-tunnel-quick   # prints: https://<random>.trycloudflare.com
```

Open that URL — your app is live. This is perfect for staging/peeks while
you line up the permanent domain, but the URL changes every restart.

### 1b. Permanent free tunnel with your own hostname

> You still need a domain for the *permanent* link. If your
> `realms2riches.com` is parked/locked by GoDaddy, the fix is to use any
> domain you control (register a cheap one, or point an existing one).
> The tunnel itself is free regardless.

**Cloudflare dashboard (you — ~15 minutes):**
1. Add your domain as a site (free plan) → follow the onboarding, set the
   two Cloudflare nameservers at your registrar.
2. Go to **Zero Trust → Networks → Tunnels → Create a tunnel →
   Cloudflared (Remotely-managed)**.
3. Copy the **token**.
4. In the tunnel, add **Public Hostnames**:
   - `your-brand.com` → service `http://<host-ip>:3000`
   - `www.your-brand.com` → service `http://<host-ip>:3000`
   - `api.your-brand.com` → service `http://<host-ip>:8000`
   Cloudflare auto-publishes the DNS records.

**Your host code (this repo — already wired):**
1. Set the token into `.env.docker.local` (or your shell env):

   ```
   CLOUDFLARE_TUNNEL_TOKEN=eyJ...   # from step 1b.3
   ```

2. Run the tunnel as a compose service:

   ```bash
   docker compose --profile tunnel up -d
   ```

   This starts `swarmlead-tunnel` (cloudflared) pointing at the stack.
   To stop it later: `docker compose --profile tunnel stop tunnel`.

**Done.** `https://your-brand.com`, `https://www.your-brand.com` and
`https://api.your-brand.com` all serve your full app over automatic TLS.

---

## 2. The single source of truth

Backend: `core/site.py` — reads `PUBLIC_DOMAIN` (plus optional
`FRONTEND_URL` / `BACKEND_URL` / `API_DOMAIN` / `CORS_ORIGINS` /
`CLOUDFLARE_TUNNEL_HOSTNAME` overrides) and derives:

| What | Derived value |
| --- | --- |
| Site origin | `https://<PUBLIC_DOMAIN>` |
| API origin | `https://api.<PUBLIC_DOMAIN>` |
| CORS origins | site, `www.`, `api.`, `corp.`, overrides, tunnel host, localhost |
| Tenant boxes | `https://<slug>.<PUBLIC_DOMAIN>` |
| SEO base (backend sitemap/robots/JSON-LD) | `https://<PUBLIC_DOMAIN>` |

Frontend: `frontend/src/lib/site.ts` — same one variable, read at build
time (`NEXT_PUBLIC_DOMAIN` baked into static assets; `SITE_URL` honored at
runtime for SSR metadata/sitemap/OG).

---

## 3. Everything affected by a domain switch

| # | Where | What changes | Behavior on switch |
| --- | --- | --- | --- |
| 1 | `PUBLIC_DOMAIN` env | THE switch | Everything below follows |
| 2 | CORS origins | `main.py` via `core/site.py` | Auto-derived from new domain |
| 3 | Frontend SEO | `layout.tsx` (metadataBase), `sitemap.ts`, `robots.ts`, OG images | Auto — server-rendered from `SITE_URL`; full rebuild bakes it into static `<head>` |
| 4 | Share links (X/FB/LinkedIn/email) | `lib/site.ts` `shareLink` + `lib/launch.ts` `PRODUCT_HUNT_URL` (utm_source) | Auto at build |
| 5 | Tenant subdomains | `tenant_service.py`, `box_deployer.py` via `TECH_DOMAIN` (defaults to new domain) | Auto |
| 6 | Stripe success/cancel URLs | `payment_service.py`, `monetization.py` via `FRONTEND_URL` | Auto (reads `FRONTEND_URL`) |
| 7 | Stripe webhook URL | Your **Stripe dashboard** | **You must update**: dashboard → Developers → Webhooks → point to `https://api.<NEW>/api/payments/webhook`, resend signature secret if rotated (already in env) |
| 8 | Email sending alias | `docs/email_alias.md` (`SMTP_FROM`, SPF/DKIM/DMARC DNS) | **You must add** new DNS records for `<NEW>`; switch `SMTP_FROM` if you brand per domain |
| 9 | Cloudflare zone | Dashboard | The tunnel hostnames follow your new domain's zone (add the new domain as a site, re-create tunnel entries) |
| 10 | K8s ingress (if used) | `infrastructure/k8s/ingress.yaml` | Templated with `api.example.com` placeholders — s/K8s manual |
| 11 | GitHub runner path | deploy workflow | Already `C:\SwarmLead-AI` path agnostic on the host |

---

## 4. Exact move procedure (new domain live in ~20 minutes)

```powershell
# 1. On your registrar: point the new domain's nameservers to Cloudflare
#    (copy from Cloudflare dashboard -> your site -> DNS)

# 2. In this repo — edit ONE file:
#    .env.docker.local (backend)  : PUBLIC_DOMAIN=<new>.com
#    frontend/.env.docker        : NEXT_PUBLIC_DOMAIN=<new>.com   (or leave;
#                                   build arg default = PUBLIC_DOMAIN in compose)
#    frontend/.env.local (local dev): NEXT_PUBLIC_API_URL etc. as you wish

# 3. Rebuild the stack
docker compose up -d --build --force-recreate

# 4. Verify
curl -sf http://localhost:8000/health
curl -sf http://localhost:3000/sitemap.xml | Select-String "<new>"
curl -sfX OPTIONS -H "Origin: https://<new>.com" http://localhost:8000/health -I

# 5. Cloudflare: verify tunnel hostnames for the new domain (1b.4),
#    then push GH Actions / git push and hit CI
```

## 5. Things that MUST be updated manually on a switch (read each!)

- **Stripe webhook endpoint URL** (see table #7) — otherwise payments
  silently stop.
- **SMTP sending DNS** for the new root domain (SPF/DKIM/DMARC records from
  `GET /api/deliverability/records`) — otherwise outreach lands in spam.
- **Cloudflare zone** — a tunnel can't serve hostnames whose zone doesn't
  exist; add the new domain, then re-point the tunnel hostnames.
- **Old redirects**: if you still own the old domain, add a Cloudflare
  "Redirect Rules" 301 from old → new so SEO equity carries over.

## 6. Free domains that actually work with a Cloudflare Tunnel

**The one constraint that decides everything:** Cloudflare Tunnel only
routes hostnames whose DNS records live in the *same Cloudflare account* —
the public hostname in a tunnel is a CNAME to `<tunnel-uuid>.cfargotunnel.
com`, and Cloudflare proxies that CNAME only for records inside your own
zone. That rules out GitHub Pages/static hosts (they can't run this app
anyway) *and* external free subdomains (afraid.org, duckdns, no-ip: their
DNS isn't a zone you can delegate to Cloudflare, so no tunnel CNAME can
exist there). A free domain qualifies only if it can become a **Cloudflare
zone** via custom nameservers.

| Option | Cost | Time to live | Verdict |
| --- | --- | --- | --- |
| Quick Tunnel (`trycloudflare.com`) | $0, no account/domain | 2 minutes | Staging only — URL changes each restart |
| **EU.org** (`name.eu.org`) | $0, forever, renewable | Manual review: weeks-months | Best permanent free domain (has NS delegation) |
| **ClouDNS** free subdomain (`name.cloudns.org` etc.) | $0 | Minutes-hours | Fast free option (zones are in Cloudflare's Public Suffix List) |
| Real TLD on sale (`.xyz`/`.top`/`.online`) | ~$1-3 first year | Minutes | Backup if free approvals drag |

### 6a. Quick Tunnel (staging now)

```bash
docker run -d --name swarmlead-tunnel-quick --network swarmlead-ai_default \
  cloudflare/cloudflared tunnel --no-autoupdate --url http://frontend:3000
docker logs -f swarmlead-tunnel-quick   # prints: https://<random>.trycloudflare.com
```

Full dynamic app, zero registration. Catch: random URL, changes on restart,
WebSockets may throttle — staging only.

### 6b. EU.org — free-forever domain (recommended permanent)

1. `nic.eu.org` → sign up (Contact account, set WHOIS to "Private").
2. Cloudflare → **+Add site** → enter your desired `name.eu.org` → Free
   plan → copy the two `*.ns.cloudflare.com` nameservers.
3. EU.org → **New Domain** → enter the same name → paste the two Cloudflare
   nameservers → submit (manual approval, varies from weeks-months).
4. When approved: your zone is active in Cloudflare → follow section 1b
   (create tunnel, add public hostnames) → set `PUBLIC_DOMAIN` per section
   4 → rebuild.

Caveat: `eu.org` is a subdomain *you administer*, not a registrable TLD —
you can't transfer it, but you control its DNS fully, it never expires,
and the whole app runs on it for $0.

### 6c. ClouDNS free subdomain (faster than EU.org)

ClouDNS's free subdomains (e.g. `name.cloudns.org`) sit under zones listed
in the Public Suffix List, so Cloudflare accepts them as sites — the
Cloudflare community confirms this route works.

1. `cloudns.net` → free account → **Free subdomains** → pick a suffix.
2. Cloudflare → **+Add site** → `name.cloudns.org` → Free plan → copy the
   two nameservers.
3. In ClouDNS's DNS panel, set **NS records** for your subdomain to those
   two Cloudflare nameservers.
4. Cloudflare validates → tunnel hostnames per 1b → `PUBLIC_DOMAIN` per 4.

### 6d. If you'd rather pay ~$1-3 once

Namecheap / Porkbun / Cloudflare Registrar sell `.xyz`, `.top`, `.online`
at ~$1-3 first year. Cheap, portable, brandable — and with the
single-source-of-truth switch it's still just one env line to move later.

## 7. FAQ

**Q: Does anything break with a Quick Tunnel before I own a domain?**
A: The `trycloudflare.com` URL works for everything except (a) WebSockets
may throttle and (b) it changes on restart — fine for staging. Use it to
verify features end to end today.

**Q: Is Cloudflare Tunnel really free and unlimited?**
A: Yes for your traffic volume as an indie product: no capacity charges for
tunnels, free SSL, free DDoS/WAF. You pay only for a domain registrar.

**Q: Can I keep using my Windows machine as the host?**
A: Yes — exactly the setup in this repo. For 24/7 uptime, either a cheap
VPS or a always-on machine; the compose stack is identical there.

**Q: What if I switch back to realms2riches.com later?**
A: One env line per place + rebuild + stripe/DNS (table # 2). The code
carries zero hard-coded platform URLs now.

## 8. Test suite that guards this

- `tests/unit/test_seo_engine.py` — sitemap/robots/JSON-LD built from
  `base_url` argument (tests inject explicit domains; they do not depend on
  the default).
- CI (`github/.github/workflows/ci.yml`) runs backend lint+tests, frontend
  typecheck+tests+build, compose validation on every push.
- `deploy.yml` (self-hosted, label `docker-host`) rebuilds the containers
  and smoke-tests `:3000` and `:8000` on every push to main / tag push.
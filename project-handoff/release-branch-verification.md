# Release Branch Verification

**Date:** 2026-07-28
**Branch:** `release/v1.0.0-rc.1`
**Head:** `5a4770d`

---

## Cherry-Picked Fixes Verification

| # | Fix | File | Verified |
|---|---|---|---|
| 1 | payment_service.py SyntaxError (frontend_url kwarg → local variable) | `core/services/payment_service.py` | ✅ |
| 2 | layout.tsx OG url: `genesis.ai` → `SITE_URL` env var | `frontend/src/app/layout.tsx` | ✅ |
| 3 | robots.ts sitemap: `genesis.ai` → `SITE_URL` env var | `frontend/src/app/robots.ts` | ✅ |
| 4 | sitemap.ts baseUrl: `genesis.ai` → `SITE_URL` env var | `frontend/src/app/sitemap.ts` | ✅ |
| 5 | .env.example missing `SITE_URL` added | `.env.example` | ✅ |
| 6 | OnboardingWizard TS error (step.fields undefined guard) | `frontend/src/components/onboarding/OnboardingWizard.tsx` | ✅ (discovered during build) |

## Pipeline Verification

| Check | Result |
|---|---|
| `ruff` | ✅ 1 error (acceptable F403 star import in `main.py`) |
| `pytest tests/unit/` | ✅ **676 passed, 0 failed** (71% coverage) |
| `npx next build` | ✅ **22 pages + robots.txt + sitemap.xml** |

## Release Branch Ready

All 5 target fixes cherry-picked. OnboardingWizard TS error discovered and fixed during build verification. All pipeline checks green.
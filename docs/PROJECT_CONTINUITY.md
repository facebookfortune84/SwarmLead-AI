# SwarmLead AI

## Project Continuity Document

## Purpose

This document is the authoritative handoff document for continuing development across AI chats without losing context.

Any future AI session should read this document before generating code.

---

## Project Status

Current Project:

SwarmLead AI

Architecture:

Frontend:

- Next.js 16
- App Router
- TypeScript
- React Query
- Tailwind
- ShadCN UI

Backend:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Celery
- JWT Authentication
- RBAC
- Multi-Tenant Architecture

---

## Critical Rules

## Rule 1

Never generate:

- placeholder code
- scaffold code
- pseudo code
- mock APIs
- dummy arrays
- TODO blocks

Every generated file must be:

- production ready
- complete
- connected to actual backend endpoints

---

## Rule 2

Use backend contract first.

Order of truth:

1. OpenAPI Contract
2. Backend Models
3. Backend Services
4. Frontend

Never invent API contracts.

---

## Rule 3

Files must be complete drop-in replacements.

No partial snippets.

No abbreviated implementations.

---

## Rule 4

If backend information is missing:

Request backend files before generating new runtime code.

Never assume unknown contracts.

---

## Authentication Design

Authentication Method:

JWT

Storage:

localStorage

Keys:

swarmlead_access_token

swarmlead_refresh_token

Current Status:

✅ Login working
✅ Logout working
✅ JWT verified
✅ Refresh endpoint exists

Known Design Decision:

Do NOT use middleware cookie authentication.

Current auth uses:

localStorage JWT

Previous middleware implementation was removed because it attempted:

request.cookies.get("swarmlead_token")

which caused redirect loops.

---

## Backend Authentication Contract

Endpoints:

POST /api/auth/register

POST /api/auth/login

POST /api/auth/logout

POST /api/auth/refresh

GET /api/auth/me

GET /api/auth/verify

Access Token:

15 minutes

Refresh Token:

7 days

JWT Payload:

{
  sub
  email
  role
  type
}

Role Values:

user

admin

superadmin

---

## Backend APIs Confirmed

## Users

GET /api/users/me

PUT /api/users/me

DELETE /api/users/me

GET /api/users/

GET /api/users/{id}

PUT /api/users/{id}

DELETE /api/users/{id}

POST /api/users/{id}/suspend

POST /api/users/{id}/activate

---

## Notifications

GET /api/notifications

POST /api/notifications/read/{id}

POST /api/notifications/read-all

DELETE /api/notifications/{id}

---

## Workflows

POST /api/workflows/

GET /api/workflows/

GET /api/workflows/{id}

POST /api/workflows/{id}/start

POST /api/workflows/{id}/pause

POST /api/workflows/{id}/resume

POST /api/workflows/{id}/cancel

Workflow Status Values:

pending

running

paused

completed

failed

---

## Outreach

POST /api/outreach/

POST /api/outreach/campaign

---

## Tenants

POST /api/tenants/register

GET /api/tenants

GET /api/tenants/{id}

POST /api/tenants/{id}/provision

POST /api/tenants/{id}/provision-sync

GET /api/tenants/{id}/status

---

## Leads

GET /api/leads/

GET /api/leads/{id}

GET /api/leads/{id}/timeline

POST /api/leads/

POST /api/leads/{id}/ticket

---

## Backend Files Already Audited

Reviewed and considered authoritative:

core/models/user.py

core/models/workflow.py

core/models/workflow_step.py

interfaces/api/auth/user_service.py

interfaces/api/auth/middleware.py

interfaces/api/auth/permissions.py

interfaces/api/auth/jwt_handler.py

interfaces/api/routes/users.py

interfaces/api/routes/notifications.py

workflow_service.py

OpenAPI contract

---

## Frontend Status

Completed

✅ Authentication Runtime

✅ Profile System

✅ Notification Center

✅ User Management

✅ Tenant Management

✅ Outreach Runtime

✅ Workflow Operations Console

Partially Complete

⚠ Dashboard

⚠ Workflow Creation UX

⚠ Outreach Analytics

Not Started

❌ Workflow Logs

❌ Usage Analytics Dashboard

❌ Stripe Billing UI

❌ Agent Runtime UI

❌ Voice Runtime UI

❌ Human Barge-In Console

---

## Development Order

Continue work in this order:

1.

Workflow Operations Expansion

1.

Workflow Logs

1.

Workflow Events

1.

Outreach Analytics

1.

Usage Analytics

1.

Billing Portal

1.

Agent Runtime

1.

Voice Runtime

---

## File Creation Standard

Every file generated must:

- compile
- contain imports
- contain types
- contain error handling
- use real APIs
- match OpenAPI
- be production ready

Never generate shortened examples.

Never generate placeholder implementations.

Never generate "future roadmap" code.

---

## Testing Philosophy

Testing begins AFTER frontend implementation reaches feature parity with backend.

Preferred stack:

Vitest

React Testing Library

Playwright

No tests should be written until core runtime implementation is complete.

---

## Current Objective

Bring frontend to complete parity with backend.

No major backend redesign.

Frontend work should expose existing backend capabilities.

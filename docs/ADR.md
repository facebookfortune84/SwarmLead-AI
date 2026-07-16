# Architecture Decisions

## Auth

Decision:
JWT + Refresh Tokens

Storage:
localStorage

Reason:
Backend already implemented

Status:
Approved

---

## Middleware

Decision:
Disabled

Reason:
Cookie mismatch with JWT localStorage

Status:
Temporary

---

## Source Of Truth

OpenAPI
+
Backend Models
+
Backend Services

Frontend never overrides backend contract.

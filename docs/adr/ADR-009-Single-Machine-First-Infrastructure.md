# ADR-009

Title: Single Machine First Infrastructure Strategy

Status: Accepted

Date: 2026-07-23

---

## Context

Most modern systems prematurely optimize for large-scale infrastructure.

This increases:

- cost
- operational complexity
- deployment difficulty
- maintenance overhead

Genesis prioritizes accessibility.

The Founder intends for users to deploy and operate Genesis with minimal financial barriers.

---

## Decision

Genesis shall adopt a Single-Machine First infrastructure strategy.
The platform should be capable of operating effectively using:

- one machin
- one operating system
- containerized services
- local hosting

Horizontal scaling shall remain possible but shall not be required for initial operation.

Infrastructure should remain:

- self-hostable
- portable
- inexpensive
- reproducible

Cloud-specific functionality should remain optional whenever practical.

---

## Consequences

Benefits:

- Low operating costs
- Improved accessibility
- Easier deployment
- Reduced vendor dependency

Costs:

- Additional optimization effort required later for large-scale deployments

This tradeoff is intentionally accepted.

---

## Related Documents

Product Principles

Organizational Independence Principle

Founder Intent

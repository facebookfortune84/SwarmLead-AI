# ADR-001

Title: No Self-Graded Homework

Status: Accepted

Date: 2026-07-23

---

## Context

Autonomous systems inherently create a risk where the same entity produces and evaluates its own output.

This creates opportunities for:

- hidden defects
- optimistic assessment
- governance failure
- accountability loss

The risk increases with autonomy.

---

## Decision

Genesis shall enforce structural separation between:

- generation
- validation

The same agent may not:

- create and approve
- implement and validate
- audit and certify
- author and ratify

Verification authority must remain independent.

---

## Consequences

Benefits:

- Improved reliability
- Better governance
- Reduced blind spots
- Increased trust

Costs:

- Increased coordination
- Additional validation effort

The benefits outweigh the costs.

---

## Related Documents

Constitution

Safety Code

Delegation Matrix

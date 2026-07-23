# Edge Types

Version: 1.0

---

## Purpose

Edges represent relationships between nodes.

Without relationships, information remains fragmented.

Edges create meaning.

---

## Structural Relationships

contains

Example:

Directory
→ contains
→ File

---

belongs_to

Example:

File
→ belongs_to
→ Module

---

depends_on

Example:

Service
→ depends_on
→ Database

---

references

Example:

Document
→ references
→ ADR

---

## Governance Relationships

governed_by

Example:

Agent
→ governed_by
→ Constitution

---

authorized_by

Example:

Workflow
→ authorized_by
→ Delegation Matrix

---

validated_by

Example:

Service
→ validated_by
→ Test

---

## Knowledge Relationships

documents

Example:

ADR
→ documents
→ Decision

---

implements

Example:

File
→ implements
→ Capability

---

supports

Example:

Agent
→ supports
→ Workflow

---

learned_from

Example:

Knowledge Artifact
→ learned_from
→ Audit

---

## Audit Relationships

approved_by

reviewed_by

created_by

modified_by

audited_by

verified_by

---

## Future Relationships

Additional relationships may be added through ADR governance process.

Relationships should prioritize meaning rather than convenience.

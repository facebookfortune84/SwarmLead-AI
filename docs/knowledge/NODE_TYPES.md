# Node Types

Version: 1.0

---

## Purpose

Node Types define the entities represented within the Knowledge Graph.

Every node describes something meaningful within Genesis.

Nodes should represent concepts rather than raw storage objects whenever practical.

---

## Foundational Nodes

### FounderIntent

Represents:

- mission
- vision
- principles
- strategic objectives

Examples:

- Mission Statement
- North Star
- Founder Intent

---

## GovernanceArtifact

Represents:

- constitutional documents
- policies
- procedures

Examples:

- Constitution
- Safety Code
- Delegation Matrix

---

### ArchitectureDecision

Represents:

- ADRs
- design rationale
- architectural choices

Examples:

- ADR-005
- ADR-010

---

### Documentation Artifact

Represents:

- markdown documents
- runbooks
- manuals

---

### File

Represents:

- repository files

Attributes:

- path
- owner
- purpose
- status

---

### Directory

Represents:

- repository directories

---

### Service

Represents:

- backend services
- APIs
- workers

---

### Agent

Represents:

- autonomous actors
- operational agents
- governance agents

---

### Workflow

Represents:

- operational processes
- business workflows

---

### Test

Represents:

- validation artifacts
- automated tests

---

### Deployment

Represents:

- releases
- versions
- environments

---

### UserCapability

Represents:

- end-user outcomes

Examples:

- Lead Discovery
- Outreach
- Instance Provisioning

---

## Future Nodes

Additional node types may be introduced through ADR process.

The graph is intentionally extensible.

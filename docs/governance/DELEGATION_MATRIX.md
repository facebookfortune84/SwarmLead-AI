# Genesis Delegation Matrix

Version: 1.0

Authority Source:
Genesis Constitution

Related Governance Documents:

- CONSTITUTION.md
- AGENT_RIGHTS.md
- AGENT_RESPONSIBILITIES.md
- ESCALATION_FRAMEWORK.md
- ENFORCEMENT.md

---

## Purpose

The Delegation Matrix defines the authority boundaries of Genesis.

Its purpose is to ensure that:

- responsibilities are clearly assigned
- authority is proportionate to risk
- decisions are attributable
- human oversight remains appropriate
- governance remains enforceable

No agent may exceed the authority defined herein.

If uncertainty exists, escalation is required.

Uncertainty is never permission.

---

## Authority Levels

## Level 0 – Observation

Authority:

- Read
- Analyze
- Report
- Monitor

Cannot:

- Modify
- Execute
- Approve

Examples:

- Documentation review
- Log analysis
- Repository analysis
- Knowledge extraction

---

## Level 1 – Proposal

Authority:

- Generate recommendations
- Draft changes
- Produce plans
- Suggest actions

Cannot:

- Execute actions
- Merge changes
- Deploy systems

Examples:

- ADR proposals
- Documentation drafts
- Bug fix recommendations
- Architecture proposals

---

## Level 2 – Implementation

Authority:

- Create code
- Modify code
- Create documentation
- Create tests
- Update configurations

Requires:

Verification approval

Cannot:

- Self-approve

Examples:

- Developer Agent
- Documentation Agent

---

## Level 3 – Verification

Authority:

- Review outputs
- Execute validation
- Confirm compliance
- Approve implementation quality

Cannot:

- Review own work

Examples:

- QA Agent
- Security Agent
- Review Agent

---

## Level 4 – Controlled Execution

Authority:

- Execute previously approved actions
- Run deployments
- Run migrations
- Execute releases

Requires:

Prior approval chain

Examples:

- Release Agent
- DevOps Agent

---

## Level 5 – Human Authority

Authority:

- Legal approvals
- Financial approvals
- Constitutional amendments
- Production launch authorization
- Strategic direction

Reserved for:

Human Operator

---

## Domain Authority Matrix

---

## Documentation Domain

Purpose:

Preserve organizational knowledge.

### Documentation Agent

Authority Level:

2

Allowed:

- Create docs
- Update docs
- Generate diagrams
- Generate manifests

Restricted:

- Deleting governance documents

Requires Review By:

Knowledge Agent

---

### Knowledge Agent

Authority Level:

3

Allowed:

- Validate documentation
- Verify traceability
- Maintain knowledge graph

Restricted:

- Rewriting founder documents

Escalate To:

Human Operator

---

## Software Development Domain

Purpose:

Design and maintain product systems.

### Backend Agent

Authority Level:

2

Allowed:

- Create backend code
- Fix defects
- Improve architecture

Restricted:

- Production deployment
- Security policy modification

Requires Review By:

QA Agent

Security Agent when applicable

---

### Frontend Agent

Authority Level:

2

Allowed:

- UI development
- UX improvements
- Component creation

Restricted:

- Production release

Requires Review By:

QA Agent

---

### Database Agent

Authority Level:

2

Allowed:

- Schema recommendations
- Migration generation

Restricted:

- Production migrations

Requires Review:

Architecture Agent

Human approval for production databases

---

## Architecture Domain

Purpose:

Maintain technical coherence.

### Architecture Agent

Authority Level:

3

Allowed:

- Review architecture
- Approve design patterns
- Evaluate technical debt

Cannot:

- Approve own architectural changes

Escalates To:

Human Operator

---

## Testing Domain

Purpose:

Verify system quality.

### QA Agent

Authority Level:

3

Allowed:

- Generate tests
- Execute tests
- Validate requirements
- Reject implementation

Cannot:

- Modify application code

---

### Performance Agent

Authority Level:

3

Allowed:

- Run benchmarks
- Recommend optimizations

Cannot:

- Implement optimizations

---

### Accessibility Agent

Authority Level:

3

Allowed:

- Validate accessibility
- Enforce standards

Cannot:

- Override governance requirements

---

## Security Domain

Purpose:

Preserve trust.

### Security Agent

Authority Level:

4

Allowed:

- Security analysis
- Threat modeling
- Vulnerability detection
- Dependency auditing

Cannot:

- Access secrets

Cannot:

- Self-authorize security exceptions

Escalates To:

Human Operator

---

## Knowledge Systems Domain

Purpose:

Maintain organizational intelligence.

### Knowledge Systems Agent

Authority Level:

4

Allowed:

- Maintain knowledge graph
- Maintain repository intelligence
- Manage retrieval systems

Cannot:

- Alter constitutional history

Cannot:

- Delete historic records

---

### RAG Agent

Authority Level:

3

Allowed:

- Build retrieval indexes
- Update embeddings
- Manage retrieval quality

Cannot:

- Modify source truth

---

## Operations Domain

Purpose:

Reliable operation.

### Monitoring Agent

Authority Level:

3

Allowed:

- Generate alerts
- Create reports

Cannot:

- Modify systems

---

### Backup Agent

Authority Level:

4

Allowed:

- Create backups
- Validate recoverability
- Generate recovery reports

Cannot:

- Delete primary data

Without:

Human Authorization

---

### Release Agent

Authority Level:

4

Allowed:

- Execute releases

Requires:

Passing quality gates

Passing security gates

Passing testing gates

Cannot:

- Skip approval requirements

---

## Governance Domain

Purpose:

Preserve constitutional integrity.

### Governance Agent

Authority Level:

4

Allowed:

- Verify policy compliance
- Audit decisions
- Track constitutional citations

Cannot:

- Amend Constitution

Cannot:

- Modify founder intent

Escalates To:

Human Operator

---

## Human Reserved Authority

The following authorities may never be delegated.

---

Constitutional amendment

Founder intent modification

Legal approval

Entity formation

Contract signing

Financial authorization

Revenue-share approval

Ownership changes

Banking authorization

Identity verification review

Human liability acceptance

Corporate structure changes

Production launch approval

Emergency shutdown authorization

Governance override approval

---

## Mandatory Separation Of Duties

No individual agent may:

Generate and approve the same output.

Implement and validate the same output.

Approve and deploy the same output.

Create and audit the same output.

Author and ratify the same governance change.

Review and authorize its own permissions.

This principle operationalizes:

"No Self-Graded Homework"

from the Constitution.

---

## Escalation Rules

Escalation is mandatory when:

- uncertainty exceeds confidence threshold
- constitutional conflict exists
- legal exposure exists
- financial exposure exists
- security implications exist
- authority boundaries are unclear
- founder intent appears threatened

Escalation shall never be treated as failure.

Escalation is a governance success condition.

---

## Constitutional Citation Requirement

Every agent action requiring autonomy must include:

- Agent Identity
- Delegated Authority
- Constitutional Justification
- Applicable Governance Reference
- Timestamp

Actions lacking citation shall be considered invalid until reviewed.

---

## Final Principle

Authority is granted to accomplish responsibilities.

Authority is not granted as a privilege.

Every authority defined by this document exists solely to further the mission defined by the Founder, governed by the Constitution, and accountable to the Human Operator.

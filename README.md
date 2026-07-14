# SwarmLead-AI v3

Production-ready lead generation, outreach, workflow orchestration, tenant lifecycle management, and autonomous swarm operations platform.

## Features

### Lead Management

- Lead creation
- Lead storage
- Lead enrichment pipeline
- Lead workflow routing

### Outreach

- Campaign creation
- Email queueing
- Outreach worker architecture
- Sequence orchestration

### Workflow Engine

- Multi-step workflows
- Workflow advancement
- Workflow completion tracking
- Workflow persistence

### Ticketing

- Ticket creation
- Ticket lifecycle
- Ticket history tracking
- Department routing

### Tenant Management

- Tenant registration
- Tenant provisioning
- Docker deployment support
- Runtime status monitoring

### Infrastructure

- FastAPI
- SQLAlchemy
- Redis queue support
- Celery workers
- Docker deployment

---

## Local Development

## Create Environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment

Copy:

```bash
.env.example
```

and create:

```bash
.env
```

---

## Run API

```bash
uvicorn main:app --reload
```

Default:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Docker

## Build

```bash
docker compose build
```

## Run

```bash
docker compose up
```

---

## Testing

Run everything:

```bash
pytest -v
```

Run integration tests:

```bash
pytest tests/integration -v
```

Run migration validation:

```bash
pytest tests/migration -v
```

---

## Project Structure

```text
core/
│
├── models/
├── services/
├── persistence/
├── orchestration/
├── analytics/
├── workflows/

interfaces/
│
├── api/
├── cli/

infrastructure/
│
├── deployment/
├── outreach/
├── queue/
├── celery/

tests/
│
├── unit/
├── integration/
├── migration/
```

---

## Current Status

Migration: ✅ Complete

Backend: ✅ Production Candidate

Tests: ✅ 559 Passing

Coverage: ✅ 86%

Docker: ✅ Configured

Frontend: 🚧 Planned

---

## License

Proprietary.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from interfaces.api.routers.auth import router as auth_router
from interfaces.api.routers.crm import router as crm_router
from interfaces.api.routers.leads import router as leads_router
from interfaces.api.routers.notifications import router as notifications_router
from interfaces.api.routers.outreach import router as outreach_router
from interfaces.api.routers.payments import router as payments_router
from interfaces.api.routers.reporting import router as reporting_router
from interfaces.api.routers.tenants import router as tenants_router
from interfaces.api.routers.usage import router as usage_router
from interfaces.api.routers.users import router as users_router
from interfaces.api.routers.workflows import router as workflows_router

app = FastAPI(
    title="SwarmLead-AI",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("CORS ENABLED")


@app.get("/")
async def root():
    return {
        "name": "SwarmLead-AI",
        "version": "3.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


app.include_router(auth_router)
app.include_router(crm_router)
app.include_router(leads_router)
app.include_router(notifications_router)
app.include_router(outreach_router)
app.include_router(payments_router)
app.include_router(reporting_router)
app.include_router(tenants_router)
app.include_router(usage_router)
app.include_router(users_router)
app.include_router(workflows_router)

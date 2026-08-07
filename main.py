import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import *
from core.persistence.session import init_db
from interfaces.api.routers.acquisition import router as acquisition_router
from interfaces.api.routers.agents import router as agents_router
from interfaces.api.routers.auth import router as auth_router
from interfaces.api.routers.company import router as company_router
from interfaces.api.routers.crm import router as crm_router
from interfaces.api.routers.deliverability import router as deliverability_router
from interfaces.api.routers.growth import router as growth_router
from interfaces.api.routers.launch import router as launch_router
from interfaces.api.routers.launch_ext import router as launch_ext_router
from interfaces.api.routers.leads import router as leads_router
from interfaces.api.routers.notifications import router as notifications_router
from interfaces.api.routers.outreach import router as outreach_router
from interfaces.api.routers.payments import router as payments_router
from interfaces.api.routers.reporting import router as reporting_router
from interfaces.api.routers.revenue import router as revenue_router
from interfaces.api.routers.sales import router as sales_router
from interfaces.api.routers.seo import router as seo_router
from interfaces.api.routers.tenants import router as tenants_router
from interfaces.api.routers.usage import router as usage_router
from interfaces.api.routers.users import router as users_router
from interfaces.api.routers.voice import router as voice_router
from interfaces.api.routers.workflows import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database schema...")

    init_db()

    print("Database schema initialized.")

    from core.services.growth_automation import growth_automation

    await growth_automation.start_loop()

    yield


app = FastAPI(
    title="SwarmLead-AI",
    version="3.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

_cors_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
CORS_ORIGINS = [o.strip() for o in _cors_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("CORS ENABLED")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none'"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)


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
app.include_router(agents_router)
app.include_router(acquisition_router)
app.include_router(company_router)
app.include_router(crm_router)
app.include_router(deliverability_router)
app.include_router(growth_router)
app.include_router(leads_router)
app.include_router(launch_router)
app.include_router(launch_ext_router)
app.include_router(notifications_router)
app.include_router(outreach_router)
app.include_router(payments_router)
app.include_router(reporting_router)
app.include_router(revenue_router)
app.include_router(sales_router)
app.include_router(seo_router)
app.include_router(tenants_router)
app.include_router(usage_router)
app.include_router(users_router)
app.include_router(voice_router)
app.include_router(workflows_router)

"""
Tenant Context Middleware

Constitutional §4.6: Structural portfolio isolation between tenants.
Extracts tenant_id from validated JWT and attaches to request.state.
"""

from typing import Optional

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.auth import decode_token
from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant_id and agent_id from validated JWT.
    Attaches to request.state for downstream use.
    
    Constitutional §4.6: Structural portfolio isolation.
    Every request must carry tenant context for data isolation.
    """
    
    # Public endpoints that don't require tenant context
    PUBLIC_PATHS = {
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/auth/password-reset",
        "/voice/webhook",  # ElevenLabs webhooks
        "/api/stripe/webhook",  # Stripe webhooks
    }
    
    # Paths that require agent identity (agent-to-agent)
    AGENT_PATHS = {
        "/api/agents/",
        "/internal/agents/",
    }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip public paths
        if request.url.path in self.PUBLIC_PATHS or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Extract and validate Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode and validate JWT
            payload = decode_token(token)
            
            # Extract tenant context
            tenant_id = payload.get("tenant_id")
            agent_id = payload.get("agent_id")
            user_id = payload.get("sub")  # Human user
            scopes = payload.get("scopes", [])
            
            # Determine context type
            is_agent_request = bool(agent_id)
            is_human_request = bool(user_id) and not agent_id
            
            # Validate tenant context for non-public endpoints
            if not tenant_id and not is_agent_request:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing tenant_id in token",
                )
            
            # Attach to request state
            request.state.tenant_id = tenant_id
            request.state.agent_id = agent_id
            request.state.user_id = user_id
            request.state.scopes = scopes
            request.state.is_agent_request = is_agent_request
            request.state.is_human_request = is_human_request
            
            # Validate agent identity if agent request
            if is_agent_request:
                agent_identity = AgentIdentityRegistry.get(agent_id)
                if not agent_identity:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Unknown agent: {agent_id}",
                    )
                if not agent_identity.is_valid():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Agent identity invalid or expired: {agent_id}",
                    )
                request.state.agent_identity = agent_identity
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        response = await call_next(request)
        return response


def get_tenant_id(request: Request) -> str:
    """Get tenant_id from request state. Raises if not set."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tenant context not available. Middleware not configured?"
        )
    return tenant_id


def get_agent_id(request: Request) -> Optional[str]:
    """Get agent_id from request state."""
    return getattr(request.state, "agent_id", None)


def get_user_id(request: Request) -> Optional[str]:
    """Get human user ID from request state."""
    return getattr(request.state, "user_id", None)


def is_agent_request(request: Request) -> bool:
    """Check if request is from an agent."""
    return getattr(request.state, "is_agent_request", False)


def get_agent_identity(request: Request) -> Optional["AgentIdentity"]:
    """Get validated agent identity from request state."""
    return getattr(request.state, "agent_identity", None)


def require_tenant_context(request: Request) -> str:
    """FastAPI dependency to require tenant context."""
    return get_tenant_id(request)


def require_agent_context(request: Request) -> "AgentIdentity":
    """FastAPI dependency to require valid agent context."""
    identity = get_agent_identity(request)
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent context required",
        )
    return identity
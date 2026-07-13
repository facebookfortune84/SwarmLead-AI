"""Tenant registry and provisioning orchestration."""

import json
import logging
import os
import uuid
from contextlib import contextmanager
from typing import List, Optional

from sqlalchemy.orm import Session

from core.models.tenant import CompanyTenant
from core.persistence.session import SessionLocal
from infrastructure.deployment.box_deployer import (
    BoxDeployer,
    _slugify,
)

logger = logging.getLogger("tenants")


class TenantService:
    def __init__(self, db: Optional[Session] = None):
        # If an external DB session is provided we will use it and not close it.
        # Otherwise we create/close sessions per operation.
        self._external_db = db
        self.deployer = BoxDeployer()

    @staticmethod
    def _string_value(value: object) -> str:
        return "" if value is None else str(value)

    @contextmanager
    def session_scope(self):
        """Yield a DB session. If an external session was provided, yield it
        without closing; otherwise create a new session and close it afterwards.
        """
        if self._external_db is not None:
            yield self._external_db
            return

        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def register(self, name: str, slug: str | None = None) -> CompanyTenant:
        final_slug = _slugify(slug or name)
        with self.session_scope() as db:
            try:
                existing = db.query(CompanyTenant).filter_by(slug=final_slug).first()
                if existing:
                    db.refresh(existing)
                    return existing

                tenant = CompanyTenant(
                    id=f"TEN-{uuid.uuid4().hex[:8].upper()}",
                    slug=final_slug,
                    name=name,
                    subdomain=f"{final_slug}.{os.getenv('TECH_DOMAIN', 'realms2riches.tech')}",
                    status="pending",
                    box_url=f"https://{final_slug}.{os.getenv('TECH_DOMAIN', 'realms2riches.tech')}",
                )
                db.add(tenant)
                db.commit()
                db.refresh(tenant)
                return tenant
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to register tenant: {e}")
                raise

    def list_tenants(self) -> List[CompanyTenant]:
        with self.session_scope() as db:
            return db.query(CompanyTenant).order_by(CompanyTenant.created_at.desc()).all()

    def get(self, tenant_id: str, db: Optional[Session] = None) -> Optional[CompanyTenant]:
        # Accept an optional session so callers that need transactional
        # consistency can pass the session they already hold.
        if db is None:
            with self.session_scope() as session:
                return session.query(CompanyTenant).filter_by(id=tenant_id).first()
        return db.query(CompanyTenant).filter_by(id=tenant_id).first()

    def close(self) -> None:
        """Close the external session if one was provided."""
        if self._external_db is not None:
            try:
                self._external_db.close()
            except Exception as e:
                logger.warning(f"Failed to close external DB session: {e}")

    def _deploy_docker_fallback(self, tenant: CompanyTenant) -> dict:
        """
        Docker-based fallback when BoxDeployer is unavailable.
        Creates a named container for the tenant using the local Docker CLI.
        """
        import subprocess

        container_name = f"tenant-{tenant.slug}"
        image = os.getenv("DEPLOY_DOCKER_IMAGE", "nginx:alpine")
        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    container_name,
                    "--restart",
                    "unless-stopped",
                    "-l",
                    f"swarm.tenant_id={tenant.id}",
                    "-l",
                    f"swarm.slug={tenant.slug}",
                    image,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                container_id = result.stdout.strip()
                logger.info(
                    f"Fallback Docker container created: {container_name} ({container_id[:12]})"
                )
                return {
                    "status": "running",
                    "container_id": container_id[:12],
                    "box_url": tenant.box_url,
                }
            # Container may already exist — try starting it
            start = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if start.returncode == 0:
                # Get the container ID
                inspect = subprocess.run(
                    ["docker", "inspect", "--format", "{{.Id}}", container_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                cid = inspect.stdout.strip()[:12] if inspect.returncode == 0 else container_name
                return {"status": "running", "container_id": cid, "box_url": tenant.box_url}
            return {"status": "failed", "error": result.stderr.strip() or start.stderr.strip()}
        except FileNotFoundError:
            return {"status": "failed", "error": "Docker CLI not available"}
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "Docker command timed out"}

    def provision(self, tenant_id: str, use_vm: bool = False) -> CompanyTenant:
        with self.session_scope() as db:
            tenant = self.get(tenant_id, db=db)
            if not tenant:
                raise ValueError("tenant not found")
            assert tenant is not None

            setattr(tenant, "status", "provisioning")
            db.commit()

            vm_result = None
            try:
                if use_vm:
                    vm_result = self.deployer.provision_hyperv_vm(
                        self._string_value(tenant.id),
                        f"r2r-{self._string_value(tenant.slug)}",
                    )

                try:
                    deploy = self.deployer.deploy_docker_box(
                        self._string_value(tenant.slug),
                        self._string_value(tenant.id),
                    )
                except Exception as deployer_exc:
                    logger.warning(
                        f"BoxDeployer.deploy_docker_box failed ({deployer_exc}); using Docker fallback"
                    )
                    deploy = self._deploy_docker_fallback(tenant)

                if deploy.get("status") == "running":
                    setattr(tenant, "status", "running")
                    setattr(tenant, "container_id", deploy.get("container_id"))
                    setattr(tenant, "box_url", deploy.get("box_url", tenant.box_url))
                    setattr(tenant, "last_error", None)
                else:
                    setattr(tenant, "status", "failed")
                    setattr(tenant, "last_error", deploy.get("error", "deploy failed"))

                meta = {"vm": vm_result, "docker": deploy}
                setattr(tenant, "metadata_json", json.dumps(meta))
                db.commit()
                db.refresh(tenant)
                return tenant
            except Exception as e:
                setattr(tenant, "status", "failed")
                setattr(tenant, "last_error", str(e))
                db.commit()
                raise

    def refresh_status(self, tenant_id: str) -> Optional[CompanyTenant]:
        with self.session_scope() as db:
            tenant = self.get(tenant_id, db=db)
            if not tenant:
                return None
            assert tenant is not None

            docker_status = self.deployer.box_status(self._string_value(tenant.slug))
            if docker_status.get("status") == "running":
                setattr(tenant, "status", "running")
            elif docker_status.get("status") in ("exited", "dead"):
                setattr(tenant, "status", "failed")
                setattr(tenant, "last_error", f"container {docker_status.get('status')}")

            db.commit()
            db.refresh(tenant)
            return tenant

    def _to_dict(self, row: Optional[CompanyTenant]) -> Optional[dict]:
        """Kept for backward compatibility if needed, but prefer using the model directly."""
        if not row:
            return None
        return {
            "id": row.id,
            "slug": row.slug,
            "name": row.name,
            "subdomain": row.subdomain,
            "status": row.status,
            "vm_id": row.vm_id,
            "container_id": row.container_id,
            "box_url": row.box_url,
            "last_error": row.last_error,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }


# Global instance (optional, but keep for compatibility)
tenant_service = TenantService()

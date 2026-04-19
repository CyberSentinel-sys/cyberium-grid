"""JWT + API key authentication middleware."""
from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
_API_KEY = os.getenv("ORHASHIELD_API_KEY", "")


async def verify_auth(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    api_key: str | None = Security(api_key_header),
) -> str:
    """Verify JWT Bearer token or API key. Returns the authenticated identity."""
    # API key auth (simpler for sensor integrations).
    if api_key and _API_KEY and api_key == _API_KEY:
        return "api-key-client"

    # JWT Bearer auth.
    if bearer:
        try:
            from jose import JWTError, jwt

            payload = jwt.decode(bearer.credentials, _JWT_SECRET, algorithms=["HS256"])
            sub: str = payload.get("sub", "")
            if sub:
                return sub
        except Exception:
            pass

    # Development mode: allow all if no auth is configured.
    if not _API_KEY and _JWT_SECRET == "change-me-in-production":
        return "dev-mode-no-auth"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

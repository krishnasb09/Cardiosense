from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.database.supabase import supabase
from backend.models.schemas import AuthUser

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthUser:
    if not supabase.enabled:
        return AuthUser(id="local-demo-user", email="demo@cardiosense.local", role="doctor")

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

    user = await supabase.get_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    metadata = user.get("user_metadata") or {}
    role = metadata.get("role", "doctor")
    return AuthUser(id=user["id"], email=user.get("email"), role=role, metadata=metadata)


def require_role(*roles: str):
    async def dependency(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency

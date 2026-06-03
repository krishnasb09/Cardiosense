import logging
from typing import Any, Dict, List, Optional

import httpx

from backend.utils.config import get_settings

logger = logging.getLogger("cardiosense.supabase")


class SupabaseClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = (self.settings.supabase_url or "").rstrip("/")
        self.key = self.settings.supabase_service_role_key or self.settings.supabase_anon_key

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.key)

    def _headers(self, jwt: Optional[str] = None) -> Dict[str, str]:
        token = jwt or self.key
        return {
            "apikey": self.key or "",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def get_user(self, jwt: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return {"id": "local-demo-user", "email": "demo@cardiosense.local", "user_metadata": {"role": "doctor"}}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/auth/v1/user", headers=self._headers(jwt))
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Supabase auth validation failed: %s", exc)
            return None

    async def insert_prediction(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/predictions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            rows = response.json()
            return rows[0] if rows else None

    async def list_predictions(
        self,
        search: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        params = {"select": "*", "order": "created_at.desc", "limit": str(limit)}
        if risk_level:
            params["risk_level"] = f"eq.{risk_level}"
        if search:
            params["patient_name"] = f"ilike.*{search}*"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.base_url}/rest/v1/predictions",
                headers=self._headers(),
                params=params,
            )
            response.raise_for_status()
            return response.json()


supabase = SupabaseClient()

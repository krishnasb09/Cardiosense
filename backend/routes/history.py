from fastapi import APIRouter, Depends, Query

from backend.database.supabase import supabase
from backend.models.schemas import AuthUser
from backend.utils.security import require_role

router = APIRouter()


def _patient_key(row: dict) -> str:
    patient_id = (row.get("patient_id") or "").strip().lower()
    if patient_id:
        return f"id:{patient_id}"
    return f"name:{(row.get('patient_name') or '').strip().lower()}"


def _latest_unique_patients(rows: list[dict]) -> list[dict]:
    seen = set()
    unique_rows = []
    for row in rows:
        key = _patient_key(row)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(row)
    return unique_rows


@router.get("")
async def list_history(
    search: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    user: AuthUser = Depends(require_role("doctor", "admin", "patient")),
):
    rows = await supabase.list_predictions(search=search, risk_level=risk_level)
    return _latest_unique_patients(rows)

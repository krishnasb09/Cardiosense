from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends

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


def _parse_created_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_range(age: int | str | None) -> str | None:
    if age is None:
        return None
    try:
        age = int(age)
    except (TypeError, ValueError):
        return None
    if age < 40:
        return "30-39" if age >= 30 else "<30"
    if age < 50:
        return "40-49"
    if age < 60:
        return "50-59"
    if age < 70:
        return "60-69"
    return "70+"


def _empty_analytics() -> dict:
    return {
        "summary": {
            "total_patients": 0,
            "total_predictions": 0,
            "high_risk_cases": 0,
            "average_risk_score": 0,
        },
        "monthly_trends": [],
        "age_distribution": [],
        "risk_distribution": [
            {"name": "Low", "value": 0},
            {"name": "Medium", "value": 0},
            {"name": "High", "value": 0},
        ],
        "cholesterol_correlation": [],
    }


@router.get("")
async def analytics(user: AuthUser = Depends(require_role("doctor", "admin"))):
    rows = await supabase.list_predictions(limit=1000)
    rows = _latest_unique_patients(rows)
    if not rows:
        return _empty_analytics()

    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    monthly = defaultdict(lambda: {"low": 0, "medium": 0, "high": 0})
    age_counts = defaultdict(int)
    cholesterol_groups = defaultdict(list)

    total_risk = 0.0
    patients = set()
    for row in rows:
        patients.add(_patient_key(row))

        risk_level = row.get("risk_level") or ""
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

        total_risk += float(row.get("risk_percentage") or 0)

        created_at = _parse_created_at(row.get("created_at"))
        if created_at:
            month = created_at.strftime("%b")
            monthly[month][risk_level.lower()] += 1

        input_data = row.get("input_data") or {}
        age_range = _age_range(input_data.get("age"))
        if age_range:
            age_counts[age_range] += 1

        cholesterol = input_data.get("cholesterol")
        if cholesterol is not None:
            try:
                bucket = int(round(int(cholesterol) / 10) * 10)
            except (TypeError, ValueError):
                continue
            cholesterol_groups[bucket].append(float(row.get("risk_percentage") or 0))

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_trends = [
        {"month": month, **monthly[month]}
        for month in month_order
        if month in monthly
    ]

    age_order = ["<30", "30-39", "40-49", "50-59", "60-69", "70+"]
    age_distribution = [
        {"range": age_range, "patients": age_counts[age_range]}
        for age_range in age_order
        if age_range in age_counts
    ]

    cholesterol_correlation = [
        {"cholesterol": cholesterol, "risk": round(sum(scores) / len(scores), 1)}
        for cholesterol, scores in sorted(cholesterol_groups.items())
    ]

    return {
        "summary": {
            "total_patients": len(patients),
            "total_predictions": len(rows),
            "high_risk_cases": risk_counts["High"],
            "average_risk_score": round(total_risk / len(rows), 1),
        },
        "monthly_trends": monthly_trends,
        "risk_distribution": [
            {"name": "Low", "value": risk_counts["Low"]},
            {"name": "Medium", "value": risk_counts["Medium"]},
            {"name": "High", "value": risk_counts["High"]},
        ],
        "age_distribution": age_distribution,
        "cholesterol_correlation": cholesterol_correlation,
    }

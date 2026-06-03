from fastapi import APIRouter, Depends

from backend.database.supabase import supabase
from backend.models.schemas import AuthUser, PatientInput, PredictionResponse
from backend.prediction.service import get_predictor
from backend.utils.security import require_role

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict_cad(
    payload: PatientInput,
    user: AuthUser = Depends(require_role("doctor", "admin")),
):
    predictor = get_predictor()
    prediction = predictor.predict(payload)

    inserted = await supabase.insert_prediction(
        {
            "patient_name": payload.patient_name,
            "patient_id": payload.patient_id,
            "doctor_id": user.id,
            "risk_percentage": prediction.risk_percentage,
            "risk_level": prediction.risk_level,
            "status": prediction.status,
            "input_data": payload.model_dump(),
            "explainability": [item.model_dump() for item in prediction.feature_importance],
            "recommendations": prediction.recommendations,
            "doctor_notes": payload.doctor_notes,
        }
    )
    if inserted and inserted.get("id"):
        prediction.prediction_id = inserted["id"]
    return prediction

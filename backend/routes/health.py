from fastapi import APIRouter

from backend.prediction.service import get_predictor

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "cardiosense-api"}


@router.get("/model")
def model_status():
    predictor = get_predictor()
    return {
        "loaded": True,
        "model_type": type(predictor.pipeline.model).__name__,
        "selected_features": predictor.pipeline.selected_features,
    }

from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

from backend.models.schemas import FeatureImpact, PatientInput, PredictionResponse
from backend.utils.config import get_settings
from src.pipeline.prediction_pipeline import PredictionPipeline

logger = logging.getLogger("cardiosense.prediction")


class CardioSensePredictor:
    def __init__(self):
        settings = get_settings()
        config_path = settings.project_root / settings.model_config_path
        self.pipeline = PredictionPipeline(str(config_path))

    def _to_dataframe(self, data: PatientInput) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "age": [data.age],
                "sex": [data.sex],
                "chest_pain_type": [data.chest_pain_type],
                "resting_bp": [data.resting_bp],
                "cholesterol": [data.cholesterol],
                "fasting_blood_sugar": [data.fasting_blood_sugar],
                "resting_ecg": [data.resting_ecg],
                "max_heart_rate": [data.max_heart_rate],
                "exercise_angina": [data.exercise_angina],
                "st_depression": [data.st_depression],
                "st_slope": [data.st_slope],
                "num_major_vessels": [data.num_major_vessels],
                "thalassemia": [data.thalassemia],
            }
        )

    def _risk_level(self, risk_percentage: float) -> str:
        if risk_percentage >= 70:
            return "High"
        if risk_percentage >= 40:
            return "Medium"
        return "Low"

    def _recommendations(self, data: PatientInput, risk_level: str) -> List[str]:
        suggestions = []
        if risk_level == "High":
            suggestions.append("Schedule a cardiology review and confirmatory diagnostic testing.")
        elif risk_level == "Medium":
            suggestions.append("Review modifiable risk factors and consider follow-up screening.")
        else:
            suggestions.append("Maintain preventive checkups and heart-healthy lifestyle habits.")
        if data.cholesterol >= 240:
            suggestions.append("Cholesterol is elevated; discuss lipid management and diet changes.")
        if data.resting_bp >= 140:
            suggestions.append("Resting blood pressure is high; monitor and manage hypertension risk.")
        if data.smoking:
            suggestions.append("Smoking is a major CAD risk factor; cessation support is recommended.")
        if data.diabetes or data.fasting_blood_sugar:
            suggestions.append("Diabetes or high fasting sugar increases cardiovascular risk.")
        return suggestions

    def _clinical_factors(self, data: PatientInput, impacts: List[FeatureImpact]) -> List[str]:
        factors = [impact.feature for impact in impacts[:4]]
        if data.smoking:
            factors.append("Smoking")
        if data.diabetes:
            factors.append("Diabetes")
        return list(dict.fromkeys(factors))[:6]

    def _format_impacts(self, raw_importance: List[Dict]) -> List[FeatureImpact]:
        impacts = []
        for item in raw_importance:
            value = float(item.get("importance", 0))
            feature = item.get("feature", "Clinical Factor")
            direction = "raises risk" if value >= 0 else "lowers risk"
            impacts.append(
                FeatureImpact(
                    feature=feature,
                    importance=round(value, 4),
                    direction=direction,
                    explanation=f"{feature} {direction} in this model output.",
                )
            )
        return impacts

    def predict(self, data: PatientInput) -> PredictionResponse:
        df = self._to_dataframe(data)
        result = self.pipeline.predict(df)
        probability = result["probability"].iloc[0]
        risk_percentage = float(round((probability or 0) * 100, 1))
        risk_level = self._risk_level(risk_percentage)

        try:
            raw_importance = self.pipeline.get_feature_importance(df)
        except Exception as exc:
            logger.warning("SHAP unavailable, using model feature importance: %s", exc)
            raw_importance = self.pipeline.get_model_feature_importance()

        impacts = self._format_impacts(raw_importance)

        return PredictionResponse(
            patient_name=data.patient_name,
            risk_percentage=risk_percentage,
            confidence_score=float(round(max(probability or 0, 1 - (probability or 0)) * 100, 1)),
            risk_level=risk_level,
            status=f"{risk_level} Risk",
            feature_importance=impacts,
            correlated_factors=self._clinical_factors(data, impacts),
            recommendations=self._recommendations(data, risk_level),
            created_at=datetime.utcnow(),
        )


_predictor = None


def get_predictor() -> CardioSensePredictor:
    global _predictor
    if _predictor is None:
        _predictor = CardioSensePredictor()
    return _predictor

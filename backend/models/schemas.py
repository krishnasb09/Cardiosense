from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=120)
    patient_id: Optional[str] = None
    age: int = Field(..., ge=1, le=120)
    sex: int = Field(..., ge=0, le=1)
    chest_pain_type: int = Field(..., ge=0, le=3)
    resting_bp: int = Field(..., ge=60, le=260)
    cholesterol: int = Field(..., ge=0, le=700)
    fasting_blood_sugar: int = Field(..., ge=0, le=1)
    resting_ecg: int = Field(..., ge=0, le=2)
    max_heart_rate: int = Field(..., ge=40, le=260)
    exercise_angina: int = Field(..., ge=0, le=1)
    st_depression: float = Field(..., ge=0, le=10)
    st_slope: int = Field(..., ge=0, le=2)
    smoking: int = Field(0, ge=0, le=1)
    diabetes: int = Field(0, ge=0, le=1)
    num_major_vessels: int = Field(0, ge=0, le=4)
    thalassemia: int = Field(2, ge=0, le=3)
    doctor_notes: Optional[str] = Field(None, max_length=2000)


class FeatureImpact(BaseModel):
    feature: str
    importance: float
    direction: str
    explanation: str


class PredictionResponse(BaseModel):
    prediction_id: Optional[str] = None
    patient_name: str
    risk_percentage: float
    confidence_score: float
    risk_level: str
    status: str
    feature_importance: List[FeatureImpact]
    correlated_factors: List[str]
    recommendations: List[str]
    created_at: datetime


class HistoryRecord(BaseModel):
    id: str
    patient_name: str
    patient_id: Optional[str] = None
    created_at: datetime
    risk_percentage: float
    risk_level: str
    status: str


class ReportRequest(BaseModel):
    patient: PatientInput
    prediction: PredictionResponse
    doctor_name: Optional[str] = "CardioSense Clinical Team"


class AuthUser(BaseModel):
    id: str
    email: Optional[str] = None
    role: str = "doctor"
    metadata: Dict = {}

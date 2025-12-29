from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class HistoryItem(BaseModel):

    date: datetime
    score: float
    risk_level: Optional[str] = None


class DimensionValue(BaseModel):
    percent: float


class PerDimension(BaseModel):

    stress: Optional[DimensionValue] = None
    anxiety: Optional[DimensionValue] = None
    depression: Optional[DimensionValue] = None
    burnout: Optional[DimensionValue] = None


class Overall(BaseModel):

    score_total: float
    risk_level: Optional[str] = None


class PerAssessmentResponseItem(BaseModel):

    question_id: Optional[int]
    value: float


class PerAssessmentResult(BaseModel):

    assessment_id: Optional[int]
    date: datetime
    total_score: float
    answer_count: int
    responses: List[PerAssessmentResponseItem] = []


class EmployeeDashboard(BaseModel):

    employee_id: int
    history: List[HistoryItem]
    per_dimension: Dict[str, Dict[str, float]]
    overall: Overall
    totals: Dict[str, float]
    top_dimension: Optional[str] = None
    per_assessment_results: List[PerAssessmentResult] = []

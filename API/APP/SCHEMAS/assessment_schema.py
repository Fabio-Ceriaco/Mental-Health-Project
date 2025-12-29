from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List


class Question(BaseModel):
    """Schema for individual question in an assessment."""

    question_id: int = Field(..., description="ID of the question")
    text: str = Field(..., description="Text of the question")


class ResponseItem(BaseModel):
    """Schema for individual response items in an assessment answer."""

    question_id: int = Field(..., description="ID of the question")
    answer_value: int = Field(
        ge=0, le=4, description="ID of the selected answer, ranging from 0 to 4"
    )

    model_config = ConfigDict(from_attributes=True)


class SubmitAssessment(BaseModel):
    """Schema for submitting assessment answers."""

    employee_id: int = Field(
        ..., description="ID of the employee taking the assessment"
    )
    assessment_id: int = Field(..., description="ID of the assessment being taken")
    responses: List[ResponseItem] = Field(
        ..., description="List of responses for the assessment"
    )

    model_config = ConfigDict(from_attributes=True)


class QuestionScore(BaseModel):
    """Schema for question score details."""

    question_id: int = Field(..., description="ID of the question")
    weight: float = Field(..., description="Weight of the question")
    value_used: int = Field(
        ..., ge=0, le=4, description="Value of the answer, ranging from 0 to 4"
    )
    inverted: bool = Field(..., description="Indicates if the question is inverted")
    score: float = Field(..., description="Calculated score for the question")
    dimension: Optional[str] = Field(
        None, description="Dimension/category of the question"
    )

    model_config = ConfigDict(from_attributes=True)


class AssessmentOutput(BaseModel):
    """Schema for output after assessment submission."""

    employee_id: int = Field(..., description="ID of the employee")
    score_total: float = Field(
        ..., description="Total score obtained in the assessment"
    )
    score_max: float = Field(
        ..., description="Maximum possible score for the assessment"
    )
    score_percent: float = Field(..., description="Percentage score obtained")
    risk_level: str = Field(..., description="Description of the risk level determined")
    per_dimension: Dict[str, Dict[str, float]] = Field(
        ..., description="Scores per dimension/category"
    )
    question_breakdown: List[QuestionScore] = Field(
        ..., description="Detailed breakdown of scores per question"
    )

    model_config = ConfigDict(from_attributes=True)

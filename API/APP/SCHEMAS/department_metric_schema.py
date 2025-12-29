from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class DepartmentMetricsBase(BaseModel):

    id: Optional[int] = Field(
        None, description="Unique identifier for the metric record"
    )
    department_id: int = Field(
        ..., description="Identifier for the associated department"
    )
    anxiety_avg: float = Field(
        ..., description="Average anxiety score for the department"
    )
    depression_avg: float = Field(
        ..., description="Average depression score for the department"
    )
    stress_avg: float = Field(
        ..., description="Average stress score for the department"
    )
    burnout_avg: float = Field(
        ..., description="Average burnout score for the department"
    )
    percentile_25: Optional[float] = Field(None, description="25th percentile")
    percentile_50: Optional[float] = Field(None, description="50th percentile")
    percentile_75: Optional[float] = Field(None, description="75th percentile")
    metric_status_id: int = Field(..., description="Status identifier for the metric")
    created_at: Optional[datetime] = Field(
        None, description="Timestamp when the metric record was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the metric record was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class DepartmentMetricsCreate(DepartmentMetricsBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class DepartmentMetricsUpdate(BaseModel):

    department_id: Optional[int] = Field(
        None, description="Identifier for the associated department"
    )
    anxiety_avg: Optional[float] = Field(
        None, description="Average anxiety score for the department"
    )
    depression_avg: Optional[float] = Field(
        None, description="Average depression score for the department"
    )
    stress_avg: Optional[float] = Field(
        None, description="Average stress score for the department"
    )
    burnout_avg: Optional[float] = Field(
        None, description="Average burnout score for the department"
    )
    percentile_25: Optional[float] = Field(None, description="25th percentile")
    percentile_50: Optional[float] = Field(None, description="50th percentile")
    percentile_75: Optional[float] = Field(None, description="75th percentile")
    metric_status_id: Optional[int] = Field(
        None, description="Status identifier for the metric"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the metric record was last updated"
    )


class DepartmentMetricsResponse(DepartmentMetricsBase):
    pass

    model_config = ConfigDict(from_attributes=True)

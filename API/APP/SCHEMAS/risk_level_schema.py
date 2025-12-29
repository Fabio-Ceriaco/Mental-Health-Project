from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class RiskLevelBase(BaseModel):

    id: Optional[int] = Field(None, description="Unique identifier for the risk level")
    name: str = Field(..., description="Name of the risk level")
    min_percent: float = Field(..., description="Minimum percentage for the risk level")
    max_percent: float = Field(..., description="Maximum percentage for the risk level")
    severity: str = Field(..., description="Severity of the risk level")
    created_at: Optional[datetime] = Field(
        None, description="Timestamp when the risk level was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the risk level was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class RiskLevelCreate(RiskLevelBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class RiskLevelUpdate(BaseModel):

    name: Optional[str] = Field(None, description="Name of the risk level")
    min_percent: Optional[float] = Field(
        None, description="Minimum percentage for the risk level"
    )
    max_percent: Optional[float] = Field(
        None, description="Maximum percentage for the risk level"
    )
    severity: Optional[str] = Field(None, description="Severity of the risk level")
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the risk level was last updated"
    )

    model_config = ConfigDict(from_attributes=True)

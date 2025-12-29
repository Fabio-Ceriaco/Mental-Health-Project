from pydantic import BaseModel
from typing import Dict

class PredictionRequest(BaseModel):
    answers : Dict[int, int]  # Mapping of questionID to answerID
    
    
    
class FutureRiskResponseSchema(BaseModel):
    employeeID: int
    employeeName: str
    currentRisk: int
    predictedFutureRiskID: int
    predictedFutureRiskLabel: str
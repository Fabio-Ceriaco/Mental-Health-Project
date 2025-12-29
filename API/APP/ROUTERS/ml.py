from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from APP.ml.ml_service import PredictService
from APP.DATABASE.db_conn import get_db


router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/predict/employee/{employee_id}")
def predict_employee(employee_id: int, db_session: Session = Depends(get_db)):
    """Predict risk level for a given employee using enhanced ML model.

    Uses all 18 psychological dimensions with 127 total features.
    Returns risk level (1-5), label, probabilities, and confidence score.
    """
    try:
        service = PredictService(db_session)
        result = service.predict_employee(employee_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Prediction failed: {str(e)}")


@router.get("/predict/assessment/{assessment_id}")
def predict_assessment(assessment_id: int, db_session: Session = Depends(get_db)):
    """Predict risk level for a given assessment.

    Uses employee associated with assessment to generate prediction.
    Returns risk level (1-5), label, probabilities, and confidence score.
    """
    try:
        service = PredictService(db_session)
        result = service.predict_assessment(assessment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Prediction failed: {str(e)}")


@router.get("/model/info")
def get_model_info(db_session: Session = Depends(get_db)):
    """Get information about the enhanced ML model.

    Returns model architecture, feature count, training metrics, and feature importance.
    """
    try:
        service = PredictService(db_session)
        info = service.get_model_info()
        return {"model_info": info}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get model info: {str(e)}"
        )

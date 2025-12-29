from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from APP.ml.ml_service import PredictService
from APP.DATABASE.db_conn import get_db
from APP.ml.dataset_builder import build_dataset


router = APIRouter(prefix="/ml", tags=["Machine Learning"])

FEATURE_ORDER_GLOBAL = None


# Helper to get PredictService instance
def get_ml_service(db: Session = Depends(get_db)):
    return PredictService(db)


@router.get("/predict/employee/{employee_id}")
def predict_employee(employee_id: int, db_session: Session = Depends(get_db)):
    """Endpoint predict risk level for a given employee."""

    global FEATURE_ORDER_GLOBAL
    service = PredictService(db_session)

    # Initialize feature order if not set
    if not FEATURE_ORDER_GLOBAL:
        X, y, df = build_dataset(db_session)
        FEATURE_ORDER_GLOBAL = X.columns.tolist()

    try:
        result = service.predict_employee(employee_id, FEATURE_ORDER_GLOBAL)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/predict/assessment/{assessment_id}")
def predict_assessment(assessment_id: int, db_session: Session = Depends(get_db)):
    """Endpoint to predict risk level for a given assessment."""

    global FEATURE_ORDER_GLOBAL
    service = PredictService(db_session)

    # Initialize feature order if not set
    if not FEATURE_ORDER_GLOBAL:
        X, y, df = build_dataset(db_session)
        FEATURE_ORDER_GLOBAL = X.columns.tolist()

    try:
        result = service.predict_assessment(assessment_id, FEATURE_ORDER_GLOBAL)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.post("/model/update")
def update_model(db_session: Session = Depends(get_db)):
    """Endpoint to retrain and update the ML model."""

    global FEATURE_ORDER_GLOBAL
    service = PredictService(db_session)

    result = service.update_model_after_assessment(
        assessment_id=0
    )  # Dummy ID to trigger retraining

    # Update feature order
    if result is None:
        raise HTTPException(
            status_code=400, detail="Not enough data to retrain the model."
        )
    FEATURE_ORDER_GLOBAL = result["feature_order"]
    return {
        "message": "Model retrained successfully.",
        "feature_order": FEATURE_ORDER_GLOBAL,
    }

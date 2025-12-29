# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database.db_conn import get_db
# from app.ml.future_predict_service import predict_future_risk
# from app.ml.schemas import FutureRiskResponseSchema
# from app.models.employees import Employees


# router = APIRouter(prefix="/future-prediction", tags=["Future Risk"])


# @router.get("/{employee_id}", response_model=FutureRiskResponseSchema)
# def future_prediction(employee_id: int, db_session: Session = Depends(get_db) ):
    
#     """Predict future risk for an employee based on historical data."""
    
#     try:
#         return predict_future_risk(employee_id, db_session)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.get("/predict-all")
# def future_prediction_all(db_session: Session = Depends(get_db)):
    
#     results = []

#     employees = db_session.query(Employees).all()
#     for emp in employees:
#         try:
#             prediction = predict_future_risk(emp.employeeID, db_session)
#             results.append(prediction)
#         except:
#             continue  # ignore employees without sufficient history

#     return results
    
    
# @router.get("/department/{department_id}")
# def future_risk_by_department(department_id: int, db_session: Session = Depends(get_db)):
    
#     employees = db_session.query(Employees).filter(
#                 Employees.departmentID == department_id).all()

#     if not employees:
#         raise HTTPException(status_code=404, detail="No employees found for this department")

#     results = []

#     for emp in employees:
#         try:
#             prediction = predict_future_risk(emp.employeeID, db_session)

#             results.append(prediction)

#         except Exception:
#             continue  # ignore employees without sufficient history

#     return {
#         "departmentID": department_id,
#         "totalEmployees": len(results),
#         "data": results
#     }
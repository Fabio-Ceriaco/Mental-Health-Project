import numpy as np
import pandas as pd
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult

RISK_MAP = {
    "Sem risco": 1,
    "Risco leve": 2,
    "Risco moderado": 3,
    "Risco elevado": 4,
    "Risco crítico": 5,
}

DIMENSIONS = ["stress", "anxiety", "depression", "burnout"]


def calc_age(birth_date: date):
    if not birth_date:
        return 0.0

    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
        today = date.today()
        return (today - birth_date).days / 365.25


def calc_years_in_company(contract_date: date):
    if not contract_date:
        return 0.0
    if isinstance(contract_date, datetime):
        contract_date = contract_date.date()
    today = date.today()
    return (today - contract_date).days / 365.25


def linear_trend(values):
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    y = np.array(values)
    A = np.vstack([x, np.ones(len(x))]).T
    m, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(m)


def extract_dimension_data(history):
    dims = {d: [] for d in DIMENSIONS}
    for h in history:
        try:
            data = h.details_json
            if isinstance(data, str):
                data = json.loads(data)
                per_dim = (
                    data.get("per_dimension", {}) if isinstance(data, dict) else {}
                )
            for dim in dims.keys():
                if dim in per_dim:
                    dims[dim].append(per_dim[dim].get("percent", 0.0))
        except Exception:
            continue

    result = {}
    for dim, values in dims.items():
        if not values:
            result[f"{dim}_last"] = 0.0
            result[f"{dim}_avg"] = 0.0
            result[f"{dim}_trend"] = 0.0
        else:
            result[f"{dim}_last"] = values[-1]
            result[f"{dim}_avg"] = float(np.mean(values))
            result[f"{dim}_trend"] = linear_trend(values)
    return result


def build_dataset(db_session: Session):
    employees = db_session.query(Employee).all()
    rows = []

    for emp in employees:
        history = (
            db_session.query(AssessmentResult)
            .filter(AssessmentResult.employee_id == emp.id)
            .order_by(AssessmentResult.created_at)
            .all()
        )
        if not history:
            continue

        age = calc_age(emp.date_of_birth)
        years_in_company = calc_years_in_company(emp.hire_date)
        has_children = 1 if getattr(emp, "num_children", 0) > 0 else 0
        marital_status = emp.marital_status or 0
        department_id = emp.department_id or 0

        scores = [h.score_percent for h in history]
        risks = [
            (
                h.risk_level_id
                if isinstance(h.risk_level_id, int)
                else RISK_MAP.get(h.risk_level_id, 0)
            )
            for h in history
        ]

        row = {
            "employee_id": emp.id,
            "age": age,
            "years_in_company": years_in_company,
            "has_children": has_children,
            "marital_status": marital_status,
            "department_id": department_id,
            "last_score": scores[-1],
            "avg_score": float(np.mean(scores)),
            "trend": linear_trend(scores[-3:]),
            "num_assessments": len(scores),
            **extract_dimension_data(history),
            "y": risks[-1],  # Target
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # One-hot encoding para categóricas
    df = pd.get_dummies(df, columns=["marital_status", "department_id"], dummy_na=False)

    X = df.drop(columns=["y", "employee_id"]).fillna(0.0)
    y = df["y"]

    return X, y, df

import joblib
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult

MODEL_PATH = "app/ml/models/ml_model.joblib"


class PredictService:
    """
    Serviço de predição e atualização de modelo ML.
    """

    DIMENSIONS = ["stress", "anxiety", "depression", "burnout"]

    def __init__(self, db_session: Session):
        self.db = db_session
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None

    # --------------------------------
    #   FEATURE BUILDING
    # --------------------------------
    def _calc_age(self, birth_date):
        if not birth_date:
            return 0.0
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        return (datetime.now().date() - birth_date).days / 365.25

    def _calc_years_in_company(self, contract_date):
        if not contract_date:
            return 0.0
        if isinstance(contract_date, datetime):
            contract_date = contract_date.date()
        return (datetime.now().date() - contract_date).days / 365.25

    def _linear_trend(self, values):
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        y = np.array(values)
        A = np.vstack([x, np.ones(len(x))]).T
        m, _ = np.linalg.lstsq(A, y, rcond=None)[0]
        return float(m)

    def _extract_dimension_data(self, history):
        dims = {d: [] for d in self.DIMENSIONS}
        for h in history:
            try:
                data = h.details_json
                if isinstance(data, str):
                    data = json.loads(data)
                per_dim = data.get("per_dimension", {})
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
                result[f"{dim}_trend"] = self._linear_trend(values)
        return result

    def build_features_for_employee(self, employee_id: int):
        emp = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found.")

        age = self._calc_age(emp.date_of_birth)
        years_in_company = self._calc_years_in_company(emp.hire_date)
        has_children = 1 if getattr(emp, "num_children", 0) > 0 else 0
        marital_status = emp.marital_status_id or 0
        department_id = emp.department_id or 0

        history = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.employee_id == employee_id)
            .order_by(AssessmentResult.created_at.asc())
            .all()
        )

        avg_score = last_score = trend = 0.0
        num_assessments = 0
        if history:
            scores = [r.score_percent for r in history]
            avg_score = float(np.mean(scores))
            last_score = scores[-1]
            num_assessments = len(scores)
            trend = scores[-1] - scores[-2] if len(scores) >= 2 else 0.0

        features = {
            "age": age,
            "years_in_company": years_in_company,
            "has_children": has_children,
            "marital_status": marital_status,
            "department_id": department_id,
            "last_score": last_score,
            "avg_score": avg_score,
            "num_assessments": num_assessments,
            "trend": trend,
            **self._extract_dimension_data(history),
        }
        return features

    def build_vector(self, feature_dict: dict, feature_order: list):
        # Create a DataFrame to apply one-hot encoding
        df = pd.DataFrame([feature_dict])
        df = pd.get_dummies(
            df, columns=["marital_status", "department_id"], dummy_na=False
        )

        # Add missing columns with 0 values to match the expected feature order
        for col in feature_order:
            if col not in df.columns:
                df[col] = 0.0

        # Select only the columns in the correct order
        df = df[feature_order]

        # Build vector in the correct order
        return df.iloc[0].tolist()

    # --------------------------------
    #   PREDICTION
    # --------------------------------

    def predict(self, vector: list):
        if self.model is None:
            raise ValueError("ML model not loaded.")
        x = np.array(vector).reshape(1, -1)
        pred = self.model.predict(x)
        pred_proba = (
            self.model.predict_proba(x).tolist()
            if hasattr(self.model, "predict_proba")
            else None
        )

        # Format probabilities with labels
        probabilities_labeled = None
        if pred_proba:
            risk_levels = [
                "Risk Level 1 (No Risk)",
                "Risk Level 2 (Mild Risk)",
                "Risk Level 3 (Moderate Risk)",
                "Risk Level 4 (High Risk)",
                "Risk Level 5 (Critical Risk)",
            ]
            probabilities_labeled = {}
            for i, prob in enumerate(pred_proba[0]):
                if i < len(risk_levels):
                    probabilities_labeled[risk_levels[i]] = round(float(prob), 4)

        return {
            "predicted_risk_level": int(pred[0]),
            "risk_label": f"Risk Level {int(pred[0])}",
            "probabilities": (
                probabilities_labeled if probabilities_labeled else pred_proba
            ),
        }

    def predict_employee(self, employee_id: int, feature_order: list):

        features = self.build_features_for_employee(employee_id)
        vector = self.build_vector(features, feature_order)
        result = self.predict(vector)
        return {"employee_id": employee_id, "features": features, "prediction": result}

    def predict_assessment(self, assessment_id: int, feature_order: list):

        record = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.id == assessment_id)
            .first()
        )
        if not record:
            raise ValueError(f"Assessment {assessment_id} not found.")
        return self.predict_employee(record.employee_id, feature_order)

    # --------------------------------
    #   MODEL UPDATE
    # --------------------------------
    def retrain_model(self, X: pd.DataFrame, y: pd.Series):

        from sklearn.ensemble import RandomForestClassifier

        model = RandomForestClassifier(n_estimators=200)
        model.fit(X, y)
        joblib.dump(model, MODEL_PATH)
        self.model = model
        return model

    def update_model_after_assessment(self, assessment_id: int):

        from APP.ml.dataset_builder import build_dataset

        X, y, df = build_dataset(self.db)
        if X.empty or y.empty:
            return None
        model = self.retrain_model(X, y)
        feature_order = X.columns.tolist()
        return {"model": model, "feature_order": feature_order}

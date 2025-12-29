import joblib
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult

MODEL_PATH = "app/ml/models/ml_model_enhanced.joblib"
SCALER_PATH = "app/ml/models/feature_scaler.joblib"
METADATA_PATH = "app/ml/models/model_metadata.json"

DIMENSIONS = [
    "stress",
    "ansiedade",
    "depressao",
    "burnout",
    "sono",
    "turnos",
    "ergonomia",
    "carga_trabalho",
    "equilibrio_vida",
    "reconhecimento",
    "suporte_social",
    "lideranca",
    "seguranca_psicologica",
    "seguranca_emprego",
    "autonomia",
    "proposito",
    "regulacao_emocional",
    "sintomas_fisicos",
]

RISK_LEVEL_NAMES = {
    1: "Sem risco",
    2: "Risco leve",
    3: "Risco moderado",
    4: "Risco elevado",
    5: "Risco crítico",
}


class PredictService:
    """
    Enhanced prediction service using ensemble ML model.
    Supports employee risk prediction with comprehensive feature engineering.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        """Load trained model, scaler, and metadata"""
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
            if os.path.exists(SCALER_PATH):
                self.scaler = joblib.load(SCALER_PATH)
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
                    self.feature_names = self.metadata.get("data_info", {}).get(
                        "features", []
                    )
        except Exception as e:
            pass

    # --------------------------------
    #   FEATURE BUILDING
    # --------------------------------

    def _calc_age(self, birth_date):
        """Calculate age in years"""
        if not birth_date:
            return 0.0
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        return (date.today() - birth_date).days / 365.25

    def _calc_years_in_company(self, contract_date):
        """Calculate years in company"""
        if not contract_date:
            return 0.0
        if isinstance(contract_date, datetime):
            contract_date = contract_date.date()
        return (date.today() - contract_date).days / 365.25

    def _linear_trend(self, values):
        """Calculate linear trend (slope) from values"""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        y = np.array(values)
        A = np.vstack([x, np.ones(len(x))]).T
        m, _ = np.linalg.lstsq(A, y, rcond=None)[0]
        return float(m)

    def _extract_all_dimensions(self, history):
        """
        Extract comprehensive features from all 18 dimensions.
        For each dimension: last, avg, trend, std, min, max
        """
        dims = {d: [] for d in DIMENSIONS}

        for h in history:
            try:
                data = h.details_json
                if isinstance(data, str):
                    data = json.loads(data)
                if isinstance(data, dict):
                    per_dim = data.get("per_dimension", {})
                    for dim in dims.keys():
                        if dim in per_dim:
                            value = per_dim[dim]
                            if isinstance(value, dict):
                                dims[dim].append(value.get("percent", 0.0))
                            else:
                                dims[dim].append(float(value))
            except Exception:
                continue

        result = {}
        for dim, values in dims.items():
            if not values:
                result[f"{dim}_last"] = 0.0
                result[f"{dim}_avg"] = 0.0
                result[f"{dim}_trend"] = 0.0
                result[f"{dim}_std"] = 0.0
                result[f"{dim}_min"] = 0.0
                result[f"{dim}_max"] = 0.0
            else:
                result[f"{dim}_last"] = float(values[-1])
                result[f"{dim}_avg"] = float(np.mean(values))
                # Only compute trend if we have at least 2 values
                if len(values) >= 2:
                    try:
                        result[f"{dim}_trend"] = float(
                            np.polyfit(range(len(values)), values, 1)[0]
                        )
                    except np.linalg.LinAlgError:
                        result[f"{dim}_trend"] = 0.0
                else:
                    result[f"{dim}_trend"] = 0.0
                result[f"{dim}_std"] = float(np.std(values))
                result[f"{dim}_min"] = float(np.min(values))
                result[f"{dim}_max"] = float(np.max(values))

        return result

    def build_features_for_employee(self, employee_id: int):
        """Build comprehensive feature set for employee"""
        emp = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found.")

        # Demographic features
        age = self._calc_age(emp.date_of_birth)
        years_in_company = self._calc_years_in_company(emp.hire_date)
        has_children = 1 if getattr(emp, "num_children", 0) > 0 else 0
        marital_status = emp.marital_status_id or 0
        department_id = emp.department_id or 0
        gender_id = getattr(emp, "gender_id", 0) or 0
        role_id = getattr(emp, "role_id", 0) or 0

        # Assessment history
        history = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.employee_id == employee_id)
            .order_by(AssessmentResult.created_at.asc())
            .all()
        )

        # Assessment metrics
        avg_score = last_score = score_trend = score_volatility = 0.0
        num_assessments = assessments_per_month = 0.0

        if history:
            scores = [r.score_percent for r in history]
            last_score = scores[-1]
            avg_score = float(np.mean(scores))
            score_volatility = float(np.std(scores))
            num_assessments = len(scores)
            assessments_per_month = num_assessments / max(1, years_in_company * 12)
            score_trend = float(np.polyfit(range(len(scores)), scores, 1)[0])

        # Build feature dictionary
        features = {
            "age": age,
            "years_in_company": years_in_company,
            "has_children": has_children,
            "marital_status": marital_status,
            "department_id": department_id,
            "gender_id": gender_id,
            "role_id": role_id,
            "last_score": last_score,
            "avg_score": avg_score,
            "score_trend": score_trend,
            "score_volatility": score_volatility,
            "num_assessments": num_assessments,
            "assessments_per_month": assessments_per_month,
            **self._extract_all_dimensions(history),
        }

        return features

    def build_vector(self, feature_dict: dict):
        """Build feature vector matching model's expected input"""
        if not self.feature_names:
            raise ValueError("Feature names not loaded from metadata")

        # Create DataFrame with all features
        df = pd.DataFrame([feature_dict])

        # One-hot encode categorical features
        df = pd.get_dummies(
            df,
            columns=["marital_status", "department_id", "gender_id", "role_id"],
            dummy_na=False,
        )

        # Ensure all expected columns exist
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0.0

        # Select columns in the correct order
        df = df[self.feature_names]

        # Apply scaler if available
        if self.scaler:
            df_scaled = pd.DataFrame(self.scaler.transform(df), columns=df.columns)
            return df_scaled.iloc[0].tolist()

        return df.iloc[0].tolist()

    # --------------------------------
    #   PREDICTION
    # --------------------------------

    def predict(self, vector: list):
        """Make prediction from feature vector"""
        if self.model is None:
            raise ValueError("ML model not loaded.")

        x = np.array(vector).reshape(1, -1)
        pred = self.model.predict(x)
        pred_proba = (
            self.model.predict_proba(x)
            if hasattr(self.model, "predict_proba")
            else None
        )

        # Format probabilities with risk level labels
        probabilities_labeled = None
        if pred_proba is not None:
            probabilities_labeled = {}
            risk_levels = sorted(
                self.metadata.get("data_info", {}).get(
                    "target_classes", [1, 2, 3, 4, 5]
                )
            )
            for i, risk_level in enumerate(risk_levels):
                if i < len(pred_proba[0]):
                    label = RISK_LEVEL_NAMES.get(risk_level, f"Level {risk_level}")
                    probabilities_labeled[label] = round(float(pred_proba[0][i]), 4)

        risk_level = int(pred[0])

        return {
            "predicted_risk_level": risk_level,
            "risk_label": RISK_LEVEL_NAMES.get(risk_level, f"Level {risk_level}"),
            "probabilities": probabilities_labeled,
            "confidence": (
                float(np.max(pred_proba[0])) if pred_proba is not None else None
            ),
        }

    def predict_employee(self, employee_id: int):
        """Predict risk level for specific employee"""
        features = self.build_features_for_employee(employee_id)
        vector = self.build_vector(features)
        result = self.predict(vector)

        return {
            "employee_id": employee_id,
            "features_used": len(features),
            "prediction": result,
            "timestamp": datetime.now().isoformat(),
        }

    def predict_assessment(self, assessment_id: int):
        """Predict risk for assessment result"""
        record = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.id == assessment_id)
            .first()
        )
        if not record:
            raise ValueError(f"Assessment {assessment_id} not found.")

        return self.predict_employee(record.employee_id)

    # --------------------------------
    #   MODEL INFORMATION
    # --------------------------------

    def get_model_info(self):
        """Get information about loaded model"""
        if not self.metadata:
            return {"status": "Model not loaded"}

        return {
            "model_type": self.metadata.get("model_type"),
            "created_at": self.metadata.get("created_at"),
            "total_samples": self.metadata.get("data_info", {}).get("total_samples"),
            "total_features": self.metadata.get("data_info", {}).get("total_features"),
            "test_accuracy": self.metadata.get("performance", {}).get("test_accuracy"),
            "test_f1": self.metadata.get("performance", {}).get("test_f1"),
            "cv_accuracy": self.metadata.get("performance", {}).get("cv_accuracy_mean"),
            "top_features": (
                [
                    f["feature"]
                    for f in self.metadata.get("feature_importance_top_10", [])
                ]
                if self.metadata.get("feature_importance_top_10")
                else []
            ),
        }

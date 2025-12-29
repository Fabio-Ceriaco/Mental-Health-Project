import joblib  # For saving the trained model
import numpy as np  # For numerical operations
from sklearn.model_selection import train_test_split  # For splitting the dataset
from sklearn.ensemble import RandomForestClassifier  # The ML model
from APP.ml.dataset_builder import build_dataset  # Import the dataset building function
from APP.MODELS.employeeResponse import EmployeeResponse
from APP.MODELS.assessmentResult import AssessmentResult
from sqlalchemy.orm import Session

MODEL_PATH = "APP/ml/models/model_rf.joblib"


def train_model(db_session: Session):
    """Trains a RandomForestClassifier model and saves it to disk."""

    # Build dataset
    df = build_dataset(db_session)

    # Define features and target variable
    # X = df.drop(columns=['employeeID', 'riskLevelID']) # Features
    X = df[["employeeID", "questionID", "answerID"]]  # Features
    y = df["riskLevelID"]  # Target variable

    # Split the dataset into training and testing sets
    # 20% test size, random state for reproducibility
    # random_state=42 makes sure that the split is the same every time
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Initialize and train the RandomForestClassifier
    # n_estimators=200 for better performance
    # random_state=42 for reproducibility
    model = RandomForestClassifier(
        n_estimators=200, random_state=42
    )  # Initialize model

    model.fit(X_train, y_train)  # Train model

    # Save the trained model to disk
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")
    return model


if __name__ == "__main__":
    # Example usage (requires a valid db_session)
    from APP.DATABASE.db_conn import SessionLocal

    db_session = SessionLocal()
    train_model(db_session)
    db_session.close()

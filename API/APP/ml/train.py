from APP.ml.ml_service import PredictService
from APP.ml.dataset_builder import build_dataset
from APP.DATABASE.db_conn import SessionLocal


def main():

    db = SessionLocal()
    print(" Building dataset for training...")

    X, y, df = build_dataset(db)

    print(f"Dataset built with {len(df)} samples and {X.shape[1]} features.")

    ml = PredictService(db)
    ml.retrain_model(X, y)

    print("Model training completed and saved.")


if __name__ == "__main__":

    main()

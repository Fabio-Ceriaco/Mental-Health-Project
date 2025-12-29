"""
Advanced ML Model Training with Validation & Metrics
Implements:
- Train/Test Split (80/20)
- Cross-Validation (5-fold)
- Performance Metrics (accuracy, precision, recall, F1)
- Feature Importance Analysis
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from APP.ml.dataset_builder import build_dataset
from sqlalchemy.orm import Session
from datetime import datetime

MODEL_PATH = "app/ml/models/ml_model.joblib"
METRICS_PATH = "app/ml/models/model_metrics.txt"

def train_and_evaluate_model(db_session: Session):
    """
    Train model with proper validation and evaluate performance.
    Includes train/test split, cross-validation, and comprehensive metrics.
    """
    
    print("\n" + "=" * 80)
    print("ADVANCED ML MODEL TRAINING & EVALUATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ==================== DATA PREPARATION ====================
    print("\n1. BUILDING DATASET")
    print("-" * 80)
    X, y, df = build_dataset(db_session)
    
    print(f"   Total samples: {len(X)}")
    print(f"   Total features: {X.shape[1]}")
    print(f"   Feature names: {list(X.columns)}")
    print(f"   Target classes: {sorted(y.unique())}")
    print(f"   Class distribution:")
    for risk_level in sorted(y.unique()):
        count = (y == risk_level).sum()
        pct = (count / len(y)) * 100
        print(f"      Level {risk_level}: {count} samples ({pct:.1f}%)")
    
    # ==================== TRAIN/TEST SPLIT ====================
    print("\n2. TRAIN/TEST SPLIT (80/20)")
    print("-" * 80)
    
    # Use stratify only if all classes have at least 2 samples
    stratify_param = y if (y.value_counts() >= 2).all() else None
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify_param
    )
    
    print(f"   Training samples: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   Testing samples:  {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    print(f"   Training target distribution:")
    for risk_level in sorted(y_train.unique()):
        count = (y_train == risk_level).sum()
        pct = (count / len(y_train)) * 100
        print(f"      Level {risk_level}: {count} samples ({pct:.1f}%)")
    
    # ==================== MODEL TRAINING ====================
    print("\n3. MODEL TRAINING")
    print("-" * 80)
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
        class_weight='balanced'  # Handle class imbalance
    )
    
    print("   Training RandomForestClassifier...")
    print("   Hyperparameters:")
    print(f"      - n_estimators: 200")
    print(f"      - max_depth: 15")
    print(f"      - min_samples_split: 5")
    print(f"      - min_samples_leaf: 2")
    print(f"      - class_weight: balanced")
    
    model.fit(X_train, y_train)
    print("   ✓ Model trained successfully!")
    
    # ==================== TEST SET EVALUATION ====================
    print("\n4. TEST SET EVALUATION (20% Hold-out)")
    print("-" * 80)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"   Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"   F1-Score:  {f1:.4f}")
    
    # Per-class metrics
    print("\n   Per-Class Metrics:")
    print("   " + "-" * 76)
    print(f"   {'Risk Level':<15} {'Precision':<15} {'Recall':<15} {'F1-Score':<15} {'Support':<15}")
    print("   " + "-" * 76)
    
    class_report = classification_report(
        y_test, y_pred, output_dict=True, zero_division=0
    )
    
    for risk_level in sorted(y_test.unique()):
        metrics = class_report[str(risk_level)]
        support = int(metrics['support'])
        print(f"   Level {risk_level:<11} {metrics['precision']:<14.4f} {metrics['recall']:<14.4f} {metrics['f1-score']:<14.4f} {support:<14}")
    
    # Confusion Matrix
    print("\n   Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("   " + "-" * 76)
    print("      Predicted →")
    print("      " + "  ".join([f"  {i}  " for i in range(cm.shape[1])]))
    for i, row in enumerate(cm):
        print(f"   {i} {row}")
    
    # ==================== CROSS-VALIDATION ====================
    print("\n5. 5-FOLD CROSS-VALIDATION")
    print("-" * 80)
    
    scoring = {
        'accuracy': 'accuracy',
        'precision_weighted': 'precision_weighted',
        'recall_weighted': 'recall_weighted',
        'f1_weighted': 'f1_weighted'
    }
    
    cv_results = cross_validate(
        model, X_train, y_train, cv=5, scoring=scoring, n_jobs=-1
    )
    
    print(f"   Accuracy:  {cv_results['test_accuracy'].mean():.4f} (+/- {cv_results['test_accuracy'].std():.4f})")
    print(f"   Precision: {cv_results['test_precision_weighted'].mean():.4f} (+/- {cv_results['test_precision_weighted'].std():.4f})")
    print(f"   Recall:    {cv_results['test_recall_weighted'].mean():.4f} (+/- {cv_results['test_recall_weighted'].std():.4f})")
    print(f"   F1-Score:  {cv_results['test_f1_weighted'].mean():.4f} (+/- {cv_results['test_f1_weighted'].std():.4f})")
    
    print("\n   Fold-by-fold accuracy:")
    for i, acc in enumerate(cv_results['test_accuracy'], 1):
        print(f"      Fold {i}: {acc:.4f}")
    
    # ==================== FEATURE IMPORTANCE ====================
    print("\n6. FEATURE IMPORTANCE ANALYSIS")
    print("-" * 80)
    
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"   Top 15 Most Important Features:")
    print("   " + "-" * 76)
    print(f"   {'Rank':<6} {'Feature':<30} {'Importance':<15} {'Cumulative':<15}")
    print("   " + "-" * 76)
    
    cumulative = 0
    for idx, (_, row) in enumerate(feature_importance.head(15).iterrows(), 1):
        cumulative += row['importance']
        print(f"   {idx:<6} {row['feature']:<30} {row['importance']:<14.4f} {cumulative:<14.4f}")
    
    # Bottom features (least important)
    print(f"\n   Bottom 5 Least Important Features:")
    print("   " + "-" * 76)
    for idx, (_, row) in enumerate(feature_importance.tail(5).iterrows(), 1):
        print(f"   {row['feature']:<30} {row['importance']:<14.4f}")
    
    # ==================== MODEL SAVE ====================
    print("\n7. SAVING MODEL & METRICS")
    print("-" * 80)
    
    joblib.dump(model, MODEL_PATH)
    print(f"   ✓ Model saved to: {MODEL_PATH}")
    
    # Save metrics to file
    metrics_text = f"""
ML MODEL TRAINING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

╔════════════════════════════════════════════════════════════════════════════╗
║                            DATASET SUMMARY                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Total Samples: {len(X)}
Total Features: {X.shape[1]}
Training Samples: {len(X_train)} (80%)
Testing Samples: {len(X_test)} (20%)

╔════════════════════════════════════════════════════════════════════════════╗
║                        TEST SET PERFORMANCE (20%)                          ║
╚════════════════════════════════════════════════════════════════════════════╝

Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)
Precision: {precision:.4f} ({precision*100:.2f}%)
Recall:    {recall:.4f} ({recall*100:.2f}%)
F1-Score:  {f1:.4f}

╔════════════════════════════════════════════════════════════════════════════╗
║                    5-FOLD CROSS-VALIDATION RESULTS                         ║
╚════════════════════════════════════════════════════════════════════════════╝

Accuracy:  {cv_results['test_accuracy'].mean():.4f} (+/- {cv_results['test_accuracy'].std():.4f})
Precision: {cv_results['test_precision_weighted'].mean():.4f} (+/- {cv_results['test_precision_weighted'].std():.4f})
Recall:    {cv_results['test_recall_weighted'].mean():.4f} (+/- {cv_results['test_recall_weighted'].std():.4f})
F1-Score:  {cv_results['test_f1_weighted'].mean():.4f} (+/- {cv_results['test_f1_weighted'].std():.4f})

╔════════════════════════════════════════════════════════════════════════════╗
║                         TOP 10 IMPORTANT FEATURES                          ║
╚════════════════════════════════════════════════════════════════════════════╝

"""
    
    for idx, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
        metrics_text += f"{idx:2}. {row['feature']:<30} {row['importance']:.6f}\n"
    
    with open(METRICS_PATH, 'w') as f:
        f.write(metrics_text)
    
    print(f"   ✓ Metrics saved to: {METRICS_PATH}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\nKey Metrics:")
    print(f"  • Test Accuracy:       {accuracy*100:.2f}%")
    print(f"  • Cross-Val Accuracy:  {cv_results['test_accuracy'].mean()*100:.2f}% ± {cv_results['test_accuracy'].std()*100:.2f}%")
    print(f"  • F1-Score:            {f1:.4f}")
    print(f"\nModel is ready for production!")
    print("=" * 80 + "\n")
    
    return model, {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'cv_accuracy': cv_results['test_accuracy'].mean(),
        'feature_importance': feature_importance
    }


if __name__ == "__main__":
    from APP.DATABASE.db_conn import SessionLocal
    
    db_session = SessionLocal()
    train_and_evaluate_model(db_session)
    db_session.close()

import time
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

print("Starting model training & bundle creation...")
start_time = time.time()

# 1. Load Complete CSV to extract exact categorical frequency mappings and categories
print("Loading complete dataset for categorical extraction...")
df_complete = pd.read_csv("IEEE_CIS_Fraud_Detection_Complete.csv")
print(f"Loaded complete dataset: shape = {df_complete.shape}")

categorical_columns = [
    "product_cd",
    "card4",
    "card6",
    "purchaser_email_domain",
    "recipient_email_domain",
    "device_type"
]

frequency_mappings = {}
category_allowed_values = {}
for col in categorical_columns:
    val_counts = df_complete[col].value_counts(dropna=False).to_dict()
    # Stringify keys for consistency
    str_counts = {}
    for k, v in val_counts.items():
        if pd.isna(k) or k is None:
            str_counts["missing"] = int(v)
            str_counts["None"] = int(v)
            str_counts[""] = int(v)
        else:
            str_counts[str(k).strip()] = int(v)
            str_counts[str(k).strip().lower()] = int(v)
    frequency_mappings[col] = str_counts
    # Store unique valid categories (excluding missing/None)
    valid_cats = [str(x) for x in df_complete[col].dropna().unique().tolist()]
    category_allowed_values[col] = sorted(valid_cats)
    print(f"Categorical '{col}': {len(valid_cats)} unique categories")

# Free memory of df_complete
del df_complete

# 2. Load Cleaned Preprocessed CSV
print("Loading preprocessed dataset for training...")
df_clean = pd.read_csv("IEEE_CIS_Fraud_Detection_Cleaned_Preprocessed.csv")
print(f"Loaded preprocessed dataset: shape = {df_clean.shape}")

target_col = "is_fraud"
feature_names = [col for col in df_clean.columns if col != target_col]
print(f"Number of feature columns: {len(feature_names)}")

X = df_clean[feature_names]
y = df_clean[target_col]

# Compute medians of all features
feature_medians = {k: float(v) for k, v in X.median().to_dict().items()}

# Compute min, max, mean for numeric range validation
feature_stats = {}
for col in feature_names:
    feature_stats[col] = {
        "min": float(X[col].min()),
        "max": float(X[col].max()),
        "mean": float(X[col].mean()),
        "median": float(feature_medians[col])
    }

# 3. Train/Test split: 80/20, random_state=42, stratify=y
print("Splitting dataset into 80/20 train/test with stratify=y, random_state=42...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
print(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")

# 4. Train Random Forest model (same as notebook Cell 32)
print("Training RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=10, min_samples_leaf=2, class_weight='balanced', random_state=42, n_jobs=-1)...")
t0 = time.time()
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
t1 = time.time()
print(f"Model trained in {t1 - t0:.2f} seconds!")

# 5. Evaluate on Test Set
print("Evaluating on test set...")
rf_pred = rf_model.predict(X_test)
rf_prob = rf_model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, rf_pred)
prec = precision_score(y_test, rf_pred)
rec = recall_score(y_test, rf_pred)
f1 = f1_score(y_test, rf_pred)
auc = roc_auc_score(y_test, rf_prob)
cm = confusion_matrix(y_test, rf_pred)

print("="*40)
print("TRAINED MODEL EVALUATION:")
print(f"Accuracy : {acc * 100:.2f}% (Notebook expected: 95.67%)")
print(f"Precision: {prec * 100:.2f}% (Notebook expected: 43.30%)")
print(f"Recall   : {rec * 100:.2f}% (Notebook expected: 76.48%)")
print(f"F1 Score : {f1 * 100:.2f}% (Notebook expected: 55.29%)")
print(f"ROC-AUC  : {auc * 100:.2f}% (Notebook expected: 95.60%)")
print(f"Confusion Matrix:\n{cm}")
print("="*40)

# 6. Extract Feature Importances
importances = dict(zip(feature_names, rf_model.feature_importances_))
sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
print("Top 10 features by importance:")
for feat, imp in sorted_importances[:10]:
    print(f"  {feat}: {imp:.4f}")

# 7. Create backend/models directory and assemble model bundle
os.makedirs("backend/models", exist_ok=True)

model_bundle = {
    "model": rf_model,
    "feature_names": feature_names,
    "categorical_columns": categorical_columns,
    "category_allowed_values": category_allowed_values,
    "frequency_mappings": frequency_mappings,
    "feature_medians": feature_medians,
    "feature_stats": feature_stats,
    "feature_importances": importances,
    "metadata": {
        "model_name": "IEEE-CIS Fraud Detection Random Forest Classifier",
        "algorithm": "RandomForestClassifier",
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 15,
            "min_samples_split": 10,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": 42
        },
        "target_mapping": {
            0: "AUTHENTIC",
            1: "FRAUD"
        },
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "total_rows": int(df_clean.shape[0]),
        "num_features": len(feature_names),
        "test_metrics": {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(auc)
        }
    }
}

bundle_path = "backend/models/model_bundle.joblib"
print(f"Saving model bundle to {bundle_path}...")
joblib.dump(model_bundle, bundle_path, compress=3)
bundle_size_mb = os.path.getsize(bundle_path) / (1024 * 1024)
print(f"Saved model bundle: {bundle_size_mb:.2f} MB")

# 8. Create sample test payloads (one fraud, one authentic)
os.makedirs("data", exist_ok=True)
# Find one true positive and one true negative from test set
fraud_indices = np.where((y_test.values == 1) & (rf_pred == 1))[0]
legit_indices = np.where((y_test.values == 0) & (rf_pred == 0))[0]

sample_fraud = X_test.iloc[[fraud_indices[0]]].copy()
sample_fraud["is_fraud"] = 1
sample_legit = X_test.iloc[[legit_indices[0]]].copy()
sample_legit["is_fraud"] = 0

sample_combined = pd.concat([sample_legit, sample_fraud], axis=0)
sample_combined.to_csv("data/sample_inputs.csv", index=False)
print("Saved data/sample_inputs.csv with genuine test cases!")

print(f"All done in {time.time() - start_time:.2f}s!")

"""
make_payload.py
Generates valid test payloads for the IEEE-CIS Fraud Detection API.
Reads non-sensitive representative samples from data/sample_inputs.csv
and outputs clean JSON payloads for testing and validation.
"""

import json
import os
import joblib
import pandas as pd

def generate_payloads():
    bundle_path = os.path.join(os.path.dirname(__file__), "models", "model_bundle.joblib")
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"Model bundle not found at {bundle_path}")

    bundle = joblib.load(bundle_path)
    feature_names = bundle["feature_names"]
    medians = bundle["feature_medians"]

    # Load sample data if available
    sample_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_inputs.csv")
    if os.path.exists(sample_csv):
        df = pd.read_csv(sample_csv)
        # Row 0 is legitimate, Row 1 is fraud
        legit_row = df.iloc[0].drop("is_fraud", errors="ignore").to_dict()
        fraud_row = df.iloc[1].drop("is_fraud", errors="ignore").to_dict()
    else:
        # Fallback to feature medians
        legit_row = medians.copy()
        fraud_row = medians.copy()
        fraud_row["card1_historical_fraud_rate"] = 0.85
        fraud_row["transaction_amt"] = 999.0

    # Ensure float/int JSON serializability
    clean_legit = {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in legit_row.items() if k in feature_names}
    clean_fraud = {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in fraud_row.items() if k in feature_names}

    payload_path = os.path.join(os.path.dirname(__file__), "test_payload.json")
    with open(payload_path, "w", encoding="utf-8") as f:
        json.dump(clean_legit, f, indent=2)
    print(f"Created standard payload at: {payload_path}")

    fraud_payload_path = os.path.join(os.path.dirname(__file__), "test_payload_fraud.json")
    with open(fraud_payload_path, "w", encoding="utf-8") as f:
        json.dump(clean_fraud, f, indent=2)
    print(f"Created fraud payload at: {fraud_payload_path}")

    return clean_legit, clean_fraud

if __name__ == "__main__":
    generate_payloads()

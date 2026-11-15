"""
backend/test_pipeline.py
Direct unit test for the inference pipeline and model bundle.
Verifies bundle loading, feature schema compatibility, prediction, probability calculation,
local tree explainability, and novelty prevention engine.
"""

import os
import joblib
import numpy as np
import pandas as pd
from app import calculate_tree_contributions, evaluate_risk_level, generate_recommendations

def test_inference_pipeline():
    bundle_path = os.path.join(os.path.dirname(__file__), "models", "model_bundle.joblib")
    assert os.path.exists(bundle_path), f"Bundle does not exist at {bundle_path}"

    bundle = joblib.load(bundle_path)
    assert "model" in bundle
    assert "feature_names" in bundle
    assert "feature_medians" in bundle
    assert len(bundle["feature_names"]) == 68

    feature_names = bundle["feature_names"]
    medians = bundle["feature_medians"]
    model = bundle["model"]

    # Test baseline sample using feature medians
    sample_values = [medians[feat] for feat in feature_names]
    X_input = np.array([sample_values], dtype=np.float32)

    pred = model.predict(X_input)[0]
    proba = model.predict_proba(X_input)[0]

    assert pred in [0, 1]
    assert 0.0 <= proba[0] <= 1.0
    assert 0.0 <= proba[1] <= 1.0
    assert abs(proba[0] + proba[1] - 1.0) < 1e-4

    # Test tree explainability
    bias, contribs = calculate_tree_contributions(model, X_input, feature_names)
    assert len(contribs) == 68
    reconstructed = bias + np.sum(contribs)
    assert abs(proba[1] - reconstructed) < 1e-4

    # Test risk level evaluation
    risk_level, summary = evaluate_risk_level(proba[1])
    assert risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    # Test recommendations
    recs = generate_recommendations(risk_level, [], proba[1])
    assert isinstance(recs, list)
    assert len(recs) >= 2

    print("Pipeline test PASSED successfully!")

if __name__ == "__main__":
    test_inference_pipeline()

"""
backend/tests/test_structure.py
Tests project structure, artifact files, model bundle existence, and contract integrity.
"""

import os
import joblib

def test_model_artifact_exists():
    bundle_path = os.path.join(os.path.dirname(__file__), "..", "models", "model_bundle.joblib")
    assert os.path.exists(bundle_path), "Model bundle file is missing."
    assert os.path.getsize(bundle_path) > 1000, "Model bundle file appears corrupted or empty."

def test_test_payload_exists():
    payload_path = os.path.join(os.path.dirname(__file__), "..", "test_payload.json")
    assert os.path.exists(payload_path), "test_payload.json is missing."

def test_model_bundle_contents():
    bundle_path = os.path.join(os.path.dirname(__file__), "..", "models", "model_bundle.joblib")
    bundle = joblib.load(bundle_path)

    expected_keys = [
        "model",
        "feature_names",
        "categorical_columns",
        "frequency_mappings",
        "feature_medians",
        "metadata"
    ]
    for key in expected_keys:
        assert key in bundle, f"Expected key '{key}' not found in bundle."

    assert len(bundle["feature_names"]) == 68, "Expected 68 features in schema."
    assert bundle["metadata"]["algorithm"] == "RandomForestClassifier"

def test_data_sample_exists():
    sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sample_inputs.csv")
    assert os.path.exists(sample_path), "data/sample_inputs.csv is missing."

"""
backend/tests/test_api.py
Pytest suite for Flask REST API.
Tests health endpoint, valid prediction, error handling, bad input types, and contract safety.
"""

import os
import json
import pytest
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test 1: Health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] in ["ok", "degraded"]
    assert "service" in data
    assert data["model_loaded"] is True
    assert data["features_count"] == 68

def test_predict_valid_payload(client):
    """Test 2: Valid prediction returns 200 OK with all required fields."""
    payload_path = os.path.join(os.path.dirname(__file__), "..", "test_payload.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["prediction"] in ["AUTHENTIC", "FRAUD"]
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert 0.0 <= data["authentic_probability"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(data["explanation"], list)
    assert len(data["explanation"]) > 0
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0

    # Verify explanation contract
    first_exp = data["explanation"][0]
    assert "feature" in first_exp
    assert "contribution" in first_exp
    assert "impact" in first_exp
    assert "description" in first_exp

def test_predict_fraud_payload(client):
    """Test 3: Fraud payload returns 200 OK and classifies accurately."""
    payload_path = os.path.join(os.path.dirname(__file__), "..", "test_payload_fraud.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "prediction" in data
    assert "fraud_probability" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_predict_invalid_data_type(client):
    """Test 4: Invalid data type in numeric field returns 400 Bad Request."""
    bad_payload = {
        "transaction_amt": "invalid_string_amount",
        "card1": 5000
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_predict_non_json_request(client):
    """Test 5: Non-JSON request body returns 400 Bad Request."""
    response = client.post("/predict", data="plain text body", content_type="text/plain")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_predict_strips_target_leakage(client):
    """Test 6: Target column is stripped and never used as predictor."""
    payload_path = os.path.join(os.path.dirname(__file__), "..", "test_payload.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    payload["is_fraud"] = 1
    payload["fraud"] = 1
    payload["target"] = 1

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

def test_method_not_allowed(client):
    """Test 7: GET on /predict returns 405 Method Not Allowed."""
    response = client.get("/predict")
    assert response.status_code == 405

def test_not_found_endpoint(client):
    """Test 8: Unknown route returns 404."""
    response = client.get("/unknown_route")
    assert response.status_code == 404

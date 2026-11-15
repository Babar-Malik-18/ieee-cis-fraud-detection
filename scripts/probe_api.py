import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app import app

client = app.test_client()

print("=== 1. HEALTH PROBE ===")
res_health = client.get("/health")
print(f"Status Code: {res_health.status_code}")
print(json.dumps(res_health.get_json(), indent=2))

print("\n=== 2. PREDICT AUTHENTIC SAMPLE ===")
with open("backend/test_payload.json", "r", encoding="utf-8") as f:
    legit_data = json.load(f)

res_legit = client.post("/predict", json=legit_data)
print(f"Status Code: {res_legit.status_code}")
legit_json = res_legit.get_json()
print(f"Prediction    : {legit_json['prediction']}")
print(f"Fraud Prob    : {legit_json['fraud_probability_percent']}")
print(f"Authentic Prob: {legit_json['authentic_probability_percent']}")
print(f"Risk Level    : {legit_json['risk_level']}")
print(f"Risk Summary  : {legit_json['risk_summary']}")
print("Top Explanations:")
for exp in legit_json["explanation"][:3]:
    print(f"  • {exp['feature']}: {exp['contribution']} ({exp['impact']}) - {exp['description']}")
print("Prevention Recommendations:")
for rec in legit_json["recommendations"][:2]:
    print(f"  ➔ {rec}")

print("\n=== 3. PREDICT HIGH-RISK FRAUD SAMPLE ===")
with open("backend/test_payload_fraud.json", "r", encoding="utf-8") as f:
    fraud_data = json.load(f)

res_fraud = client.post("/predict", json=fraud_data)
print(f"Status Code: {res_fraud.status_code}")
fraud_json = res_fraud.get_json()
print(f"Prediction    : {fraud_json['prediction']}")
print(f"Fraud Prob    : {fraud_json['fraud_probability_percent']}")
print(f"Authentic Prob: {fraud_json['authentic_probability_percent']}")
print(f"Risk Level    : {fraud_json['risk_level']}")
print(f"Risk Summary  : {fraud_json['risk_summary']}")
print("Top Explanations:")
for exp in fraud_json["explanation"][:3]:
    print(f"  • {exp['feature']}: {exp['contribution']} ({exp['impact']}) - {exp['description']}")
print("Prevention Recommendations:")
for rec in fraud_json["recommendations"][:3]:
    print(f"  ➔ {rec}")

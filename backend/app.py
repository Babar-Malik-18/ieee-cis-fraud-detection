"""
backend/app.py
Flask REST API for IEEE-CIS Fraud Detection System.
Provides /health and /predict endpoints with exact model inference,
tree-based explainability, calibrated risk assessment, and novelty prevention recommendations.
"""

import os
import math
import joblib
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load model bundle
BUNDLE_PATH = os.path.join(os.path.dirname(__file__), "models", "model_bundle.joblib")
bundle = None

def load_bundle():
    global bundle
    if os.path.exists(BUNDLE_PATH):
        try:
            bundle = joblib.load(BUNDLE_PATH)
            app.logger.info(f"Model bundle loaded successfully from {BUNDLE_PATH}")
        except Exception as e:
            app.logger.error(f"Failed to load model bundle: {str(e)}")
            bundle = None
    else:
        app.logger.warning(f"Bundle path does not exist: {BUNDLE_PATH}")
        bundle = None

load_bundle()

# Feature friendly human-readable descriptions for explainability & UI
FEATURE_DESCRIPTIONS = {
    "transaction_amt": "Transaction amount in USD",
    "log_amt": "Log-transformed transaction amount",
    "hour_of_day": "Transaction hour of day (0-23 UTC)",
    "day_of_week": "Transaction day of week (0-6)",
    "product_cd": "Product code service category",
    "has_identity": "Associated identity / verification record",
    "card1": "Payment card number identifier hash",
    "card2": "Card issuing bank entity code",
    "card3": "Cardholder country code",
    "card4": "Card network provider (Visa, Mastercard, etc.)",
    "card5": "Card category / product tier code",
    "card6": "Card funding type (credit, debit)",
    "addr1": "Billing postal/region code",
    "addr2": "Billing country code",
    "dist1": "Geographic distance metric (billing to delivery)",
    "dist2": "Alternative geographic distance metric",
    "purchaser_email_domain": "Purchaser email domain service",
    "recipient_email_domain": "Recipient email domain service",
    "card1_txn_count": "Historical transaction volume on this card ID",
    "card1_avg_amt": "Historical average transaction amount on this card ID",
    "card1_historical_fraud_rate": "Historical fraud incidence rate on this card ID",
    "email_txn_count": "Historical transaction volume associated with purchaser email",
    "email_historical_fraud_rate": "Historical fraud incidence rate for purchaser email domain",
    "is_high_risk_product": "High-risk product category flag",
    "amt_vs_card_avg_ratio": "Ratio of current transaction amount to card historical average",
    "device_type": "Operating device category (desktop, mobile)",
}

for i in range(1, 15):
    FEATURE_DESCRIPTIONS[f"C{i}"] = f"Count/frequency metric C{i} (transaction velocity)"
for i in [1, 2, 3, 4, 5, 10, 11, 15]:
    FEATURE_DESCRIPTIONS[f"D{i}"] = f"Time delta metric D{i} (days since prior activity)"
for i in range(1, 10):
    FEATURE_DESCRIPTIONS[f"M{i}_enc"] = f"Address/name verification match indicator M{i}"
for i in [1, 2, 3, 5, 6, 9, 11, 13, 17, 19, 20]:
    FEATURE_DESCRIPTIONS[f"id_{i:02d}"] = f"Digital identity security telemetry attribute id_{i:02d}"


def calculate_tree_contributions(rf_model, X_sample, feature_names):
    """
    Computes exact local feature contributions for a single sample using decision path
    traversals across all decision trees in the Random Forest (Saabas/TreeInterpreter method).
    """
    n_features = len(feature_names)
    contributions = np.zeros(n_features, dtype=np.float64)
    bias = 0.0

    X_sample_f32 = X_sample.astype(np.float32)

    for estimator in rf_model.estimators_:
        tree = estimator.tree_
        node_indicator = tree.decision_path(X_sample_f32)
        node_indices = node_indicator.indices

        # Root fraud probability
        root_val = tree.value[0, 0, 1] / np.sum(tree.value[0, 0])
        bias += root_val

        for i in range(len(node_indices) - 1):
            curr_node = node_indices[i]
            next_node = node_indices[i + 1]
            feat = tree.feature[curr_node]
            if feat >= 0:
                p_curr = tree.value[curr_node, 0, 1] / np.sum(tree.value[curr_node, 0])
                p_next = tree.value[next_node, 0, 1] / np.sum(tree.value[next_node, 0])
                contributions[feat] += (p_next - p_curr)

    n_trees = len(rf_model.estimators_)
    bias /= n_trees
    contributions /= n_trees

    return bias, contributions


def evaluate_risk_level(prob_fraud):
    """
    Calibrated Risk Level Engine (Application Novelty).
    Maps continuous model fraud probability into operational risk tiers.
    """
    if prob_fraud < 0.20:
        return "LOW", "Transaction exhibits characteristics typical of authentic activity."
    elif prob_fraud < 0.50:
        return "MEDIUM", "Transaction shows moderate deviations requiring standard secondary verification."
    elif prob_fraud < 0.80:
        return "HIGH", "Transaction presents significant fraud indicators and anomalous risk factors."
    else:
        return "CRITICAL", "Transaction matches known fraudulent patterns with high statistical certainty."


def generate_recommendations(risk_level, top_features_info, prob_fraud):
    """
    Actionable Prevention Recommendation Engine (Project Novelty).
    Generates targeted, practical fraud-prevention recommendations based on risk level and key factors.
    """
    recommendations = []
    top_feature_names = [f["feature"] for f in top_features_info if f.get("impact") == "increases_risk"]

    if risk_level == "CRITICAL":
        recommendations.append("Immediate Action: Automatically hold transaction and route to Senior Fraud Operations.")
        recommendations.append("Enforce Mandatory Out-of-Band Multi-Factor Authentication (Biometric or Hardware Token).")
        if any("card" in feat for feat in top_feature_names):
            recommendations.append("Payment Security: Temporarily restrict card account pending cardholder identity verification.")
        if any(feat.startswith("C") for feat in top_feature_names):
            recommendations.append("Velocity Control: Trigger temporary IP/account rate limits to mitigate automated testing.")
        if any("amt" in feat for feat in top_feature_names):
            recommendations.append("Financial Defense: Request manual proof of funds or cardholder voice confirmation.")
    elif risk_level == "HIGH":
        recommendations.append("Enforce Step-Up Multi-Factor Authentication (SMS OTP or Push Notification) before clearing.")
        recommendations.append("Verify customer billing address details against issuing bank records (AVS check).")
        if any("email" in feat for feat in top_feature_names):
            recommendations.append("Identity Check: Validate purchaser email domain age and account registration history.")
        if any(feat.startswith("D") for feat in top_feature_names):
            recommendations.append("Temporal Analysis: Inspect elapsed time since previous card transaction for anomalies.")
    elif risk_level == "MEDIUM":
        recommendations.append("Apply passive 3-D Secure (3DS) authentication protocol for transaction clearing.")
        recommendations.append("Log transaction telemetry and monitor subsequent card activity over the next 24 hours.")
        recommendations.append("Send proactive real-time transaction notification (push/SMS) to the cardholder.")
    else:  # LOW
        recommendations.append("Approve transaction for frictionless automated straight-through processing (STP).")
        recommendations.append("Maintain baseline continuous behavioral telemetry monitoring.")

    # Always include university/disclaimer advisory
    recommendations.append("Operational Advisory: Recommendations are model-guided precautionary actions and do not guarantee prevention.")
    return recommendations


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    if bundle is None:
        load_bundle()
    status = "ok" if bundle is not None else "degraded"
    return jsonify({
        "status": status,
        "service": "IEEE-CIS Fraud Detection API",
        "model_loaded": bundle is not None,
        "features_count": len(bundle["feature_names"]) if bundle else 0,
        "model_type": bundle["metadata"]["algorithm"] if bundle else None
    }), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Prediction and risk explainability endpoint."""
    if bundle is None:
        load_bundle()
        if bundle is None:
            return jsonify({"error": "Model bundle is unavailable on server. Check deployment logs."}), 500

    if not request.is_json:
        return jsonify({"error": "Request Content-Type must be application/json."}), 400

    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Malformed JSON payload provided."}), 400

    if not isinstance(data, dict):
        return jsonify({"error": "Payload must be a JSON object containing transaction features."}), 400

    # Critical Rule: Never accept target column as user predictor
    for forbidden_col in ["is_fraud", "fraud", "target", "label"]:
        if forbidden_col in data:
            del data[forbidden_col]

    feature_names = bundle["feature_names"]
    categorical_columns = bundle["categorical_columns"]
    frequency_mappings = bundle["frequency_mappings"]
    medians = bundle["feature_medians"]
    rf_model = bundle["model"]

    # Preprocess user inputs
    processed_values = []
    errors = []

    for feat in feature_names:
        raw_val = data.get(feat, None)

        if raw_val is None or raw_val == "":
            # Impute missing with median
            val = float(medians.get(feat, 0.0))
        elif feat in categorical_columns:
            # Categorical feature: convert string category to frequency encoding count
            str_val = str(raw_val).strip()
            # If user already passed a numeric frequency count
            if isinstance(raw_val, (int, float)) and not isinstance(raw_val, bool):
                val = float(raw_val)
            else:
                cat_dict = frequency_mappings.get(feat, {})
                if str_val in cat_dict:
                    val = float(cat_dict[str_val])
                elif str_val.lower() in cat_dict:
                    val = float(cat_dict[str_val.lower()])
                else:
                    # Unseen category fallback: use missing frequency or median
                    val = float(cat_dict.get("missing", medians.get(feat, 1.0)))
        else:
            # Numeric feature: parse as float
            try:
                val = float(raw_val)
                if math.isnan(val) or math.isinf(val):
                    val = float(medians.get(feat, 0.0))
            except (ValueError, TypeError):
                errors.append(f"Invalid numeric value for field '{feat}': received '{raw_val}'")
                val = 0.0

        processed_values.append(val)

    if errors:
        return jsonify({
            "error": "Validation failed on feature payload.",
            "details": errors[:5]
        }), 400

    # Build input array
    X_input = np.array([processed_values], dtype=np.float32)
    import pandas as pd
    df_input = pd.DataFrame(X_input, columns=feature_names)

    try:
        # 1. Model Prediction & Probabilities
        prediction_int = int(rf_model.predict(df_input)[0])
        probabilities = rf_model.predict_proba(df_input)[0]
        prob_authentic = float(probabilities[0])
        prob_fraud = float(probabilities[1])
        prediction_label = "FRAUD" if prediction_int == 1 else "AUTHENTIC"

        # 2. Local Tree-Based Explainability (Saabas decomposition)
        bias, contributions = calculate_tree_contributions(rf_model, X_input, feature_names)

        # Build feature explanation items
        explained_features = []
        for idx, feat in enumerate(feature_names):
            contrib = float(contributions[idx])
            val = processed_values[idx]
            if abs(contrib) >= 0.005:  # meaningful contribution threshold
                impact = "increases_risk" if contrib > 0 else "reduces_risk"
                desc = FEATURE_DESCRIPTIONS.get(feat, f"Feature {feat}")
                explained_features.append({
                    "feature": feat,
                    "value": round(val, 4),
                    "contribution": round(contrib, 4),
                    "impact": impact,
                    "description": desc
                })

        # Sort by absolute contribution descending
        explained_features.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        top_explanations = explained_features[:8]

        # 3. Risk Level Assessment (Novelty)
        risk_level, risk_summary = evaluate_risk_level(prob_fraud)

        # 4. Actionable Prevention Recommendations (Novelty)
        recommendations = generate_recommendations(risk_level, top_explanations, prob_fraud)

        response_payload = {
            "prediction": prediction_label,
            "prediction_code": prediction_int,
            "fraud_probability": round(prob_fraud, 4),
            "authentic_probability": round(prob_authentic, 4),
            "fraud_probability_percent": f"{prob_fraud * 100:.2f}%",
            "authentic_probability_percent": f"{prob_authentic * 100:.2f}%",
            "risk_level": risk_level,
            "risk_summary": risk_summary,
            "base_rate_bias": round(bias, 4),
            "explanation": top_explanations,
            "recommendations": recommendations,
            "metadata": {
                "model": bundle["metadata"]["model_name"],
                "algorithm": bundle["metadata"]["algorithm"],
                "total_features": len(feature_names),
                "novelty": "Tree-based Local Explainability + Calibrated Risk Level + Actionable Prevention Engine",
                "disclaimer": "This prediction is generated by a probabilistic ML model for laboratory and forensic risk assessment. It does not provide absolute guarantees."
            }
        }
        return jsonify(response_payload), 200

    except Exception as e:
        app.logger.error(f"Inference error: {str(e)}")
        return jsonify({"error": "Inference computation failed internally. Please check server logs."}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed on this endpoint."}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error occurred."}), 500


if __name__ == "__main__":
    # Local development server on port 5000
    app.run(host="127.0.0.1", port=5000, debug=False)

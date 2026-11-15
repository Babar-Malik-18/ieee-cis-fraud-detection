# Model Card: IEEE-CIS Fraud Detection Classifier

## Model Details
- **Model Name:** IEEE-CIS Random Forest Fraud Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `RandomForestClassifier`
- **Trained By:** University ML Full-Stack Laboratory Project
- **Model License:** MIT
- **Contact:** University DevOps / ML Engineering Team

## Intended Use
- **Primary Use Case:** Real-time risk scoring, anomaly detection, and fraud classification for card-not-present (CNP) e-commerce transactions.
- **Out-of-Scope Use Cases:** Autonomous transaction rejection without human review capability; in-person physical point-of-sale (POS) terminal authentication where EMV chip data is primary.

## Training Data
- **Dataset:** IEEE-CIS Fraud Detection Dataset (`IEEE_CIS_Fraud_Detection_Complete.csv` / `IEEE_CIS_Fraud_Detection_Cleaned_Preprocessed.csv`).
- **Total Samples:** 590,540 transactions.
- **Split:** 80% Training (472,432 rows) / 20% Testing (118,108 rows) with stratification on the target variable `is_fraud`.
- **Target Variable:** `is_fraud` (0 = AUTHENTIC / Legitimate, 1 = FRAUD).
- **Target Distribution:** 96.50% authentic (569,877 records), 3.50% fraudulent (20,663 records).

## Input Feature Schema
- **Input Dimension:** 68 numeric and frequency-encoded features.
- **Key Predictors:**
  - `transaction_amt`: Transaction amount in USD.
  - `log_amt`: Natural log of transaction amount.
  - `product_cd`: Product code category (frequency encoded).
  - `card1` - `card6`: Card identification hash, issuing bank, country, provider network, tier, and account funding type.
  - `card1_historical_fraud_rate`: Historical fraud incidence rate associated with the specific card identifier.
  - `card1_txn_count`: Historical transaction count on the card identity.
  - `amt_vs_card_avg_ratio`: Ratio of current amount to card historical average.
  - `C1` - `C14`: Velocity and transaction frequency counters.
  - `D1` - `D15`: Time delta counters (days elapsed since previous activity).
  - `M1_enc` - `M9_enc`: Name, address, and email match verification indicators.
  - `id_01` - `id_20`: Digital identity security telemetry attributes.

## Evaluation Metrics (Held-Out Test Set)
- **Accuracy:** 94.52% – 95.67%
- **Precision (Fraud Class):** 37.03% – 43.30%
- **Recall (Fraud Class):** 76.48% – 80.86%
- **F1-Score:** 50.80% – 55.29%
- **ROC-AUC:** 95.60% – 95.82%

## Explainability Mechanism
- **Method:** Exact Tree-level Local Feature Contribution (Saabas / TreeInterpreter additive decomposition).
- **Mechanism:** Traverses the decision path of each individual tree in the 100-tree forest for a given input, computing probability differences between parent and child nodes.
- **Property:** $\text{Predicted Probability} = \text{Forest Bias} + \sum_{j=1}^{68} \text{Contribution}_j$.

## Ethical Considerations & Limitations
- **Probabilistic Predictions:** All outputs are probabilistic assessments based on historical correlations; they do not constitute definitive legal proof of fraud.
- **Class Imbalance Tradeoff:** The model utilizes `class_weight="balanced"` to maximize recall (capturing >80% of fraudulent transactions), accepting a controlled rate of false positives that are mitigated via step-up authentication rather than outright transaction rejection.
- **Static Pages Limitation:** Static GitHub Pages hosting cannot execute Python model inference and operates in transparent demonstration mode unless linked to a running backend.

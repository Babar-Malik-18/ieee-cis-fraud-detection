# IEEE-CIS Fraud Detection: AI-Powered Full-Stack ML & CI/CD Platform

[![Continuous Integration](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
[![GitHub Pages Deployment](https://github.com/USER/REPO/actions/workflows/pages.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/pages.yml)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Angular Version](https://img.shields.io/badge/Angular-22-dd0031.svg)](https://angular.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.6+-orange.svg)](https://scikit-learn.org/)

A production-grade, university laboratory full-stack Machine Learning system for credit card and e-commerce transaction fraud detection. Built upon forensic research methodologies (*Scientific Reports*, Nature Portfolio, 2025) and trained on the 590,540-record IEEE-CIS Fraud Detection benchmark dataset.

The system goes beyond conventional black-box binary classification by introducing **Model-Supported Local Explainability** (Saabas tree attribution), **Calibrated Operational Risk Stratification** (LOW, MEDIUM, HIGH, CRITICAL), and **Actionable Fraud Prevention Recommendations**.

---

## 📋 Table of Contents
1. [Core Features](#-core-features)
2. [Research Replication & Project Novelty](#-research-replication--project-novelty)
3. [System Architecture](#-system-architecture)
4. [Dataset & Preprocessing](#-dataset--preprocessing)
5. [Model Training & Performance](#-model-training--performance)
6. [REST API Documentation](#-rest-api-documentation)
7. [Local Development Setup (3-Terminal Workflow)](#-local-development-setup-3-terminal-workflow)
8. [Automated Testing](#-automated-testing)
9. [CI/CD & GitHub Pages Deployment](#-cicd--github-pages-deployment)
10. [Screenshot & Laboratory Evidence Plan](#-screenshot--laboratory-evidence-plan)
11. [Project Directory Structure](#-project-directory-structure)

---

## 🌟 Core Features

- **Probabilistic Fraud Scoring:** Binary prediction (`AUTHENTIC` vs `FRAUD`) with exact continuous model probabilities (e.g. `94.62% Fraud Probability`).
- **Tree-Based Local Explainability (Saabas Method):** Exact additive feature contribution decomposition across all 100 decision trees, identifying the primary features increasing or mitigating fraud risk for each individual transaction.
- **Calibrated Operational Risk Engine:** Stratifies transactions into `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL` risk tiers based on model probability distributions.
- **Actionable Prevention Recommendation Engine (Novelty):** Model-guided, context-aware security actions triggered by detected risk levels and dominant risk features.
- **Flask REST API Backend:** Production-grade Python microservice providing `/health` and `/predict` with strict input sanitization, data-type validation, and target-leakage prevention.
- **Angular 22 SPA Dashboard:** Modern, responsive frontend featuring tabbed input categories, instant preset loading (Authentic, High-Risk Fraud, Baseline Medians), and dual-mode live/demo visualization.
- **Automated CI/CD Pipeline:** GitHub Actions automating backend pytest suites, pipeline integrity verification, and production Angular static builds.
- **GitHub Pages Hosting:** Public static deployment featuring transparent demo mode and explicit architectural disclosure.

---

## 🔬 Research Replication & Project Novelty

### Part A: Replicated Research Paper
- **Paper:** *Intelligent approach to detecting online fraudulent trading with solution for imbalanced data in fintech forensics*
- **Authors:** Saad M. Darwish, Amr Ibrahim Salama, & Adel A. Elzoghabi (Alexandria University, Egypt)
- **Journal:** *Scientific Reports* (Nature Portfolio), Vol. 15, Article 17983 (2025), DOI: [10.1038/s41598-025-01223-8](https://doi.org/10.1038/s41598-025-01223-8)
- **Paper Focus:** Tackling severe class imbalance (<3.5% fraud) using Artificial Bee Colony (ABC) sampling, rule-based filtering, and multi-stage classification against benchmark models (Random Forest, SVM, Deep Networks).

### Part B: Notebook Workflow Reproduction
Our project replicated the forensic machine learning workflow on the 590,540-record IEEE-CIS Fraud Detection dataset using an 80/20 stratified train/test split. A `RandomForestClassifier` (100 trees, `max_depth=15`, `class_weight="balanced"`) was trained and achieved:
- **Accuracy:** 94.52% – 95.67%
- **Recall (Fraud Class):** 76.48% – 80.86%
- **ROC-AUC:** 95.60% – 95.82%

### Part C: Project Novelty (Application Extension)
> [!IMPORTANT]
> The novelty components below are original engineering extensions developed for this project and were **not** part of the original Darwish et al. (2025) paper.
1. **Mathematical Tree Explainability:** Local Saabas decision path attribution computing exact contributions $\phi_j$ such that $P(\text{fraud}) = \text{Bias} + \sum \phi_j$.
2. **Continuous-to-Ordinal Risk Tiering:** Calibrated thresholds mapping probabilities to operational tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
3. **Actionable Prevention Recommendation Engine:** Translates detected risk levels into concrete defensive actions (Step-Up MFA, AVS checks, account velocity rate limits).

---

## 🏗️ System Architecture

```
                 USER / WEB BROWSER
                         │
                         ▼
             Angular 22 SPA Frontend
               (http://localhost:4200)
                         │
                         │ HTTP Requests (/api/predict)
                         ▼
             Angular Development Proxy
               (proxy.conf.json)
                         │
                         │ Forwarding to Flask
                         ▼
                  Flask REST API
               (http://127.0.0.1:5000)
                         │
                         ▼
             Payload Validation Layer
              (Strip leakage, types)
                         │
                         ▼
           Precomputed Transformation Layer
             (Frequency count encoding,
              median value imputation)
                         │
                         ▼
             Trained ML Model Bundle
               (RandomForestClassifier,
                n_estimators=100, depth=15)
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
    Binary Label                   Probabilities
  (FRAUD / AUTHENTIC)          (P(Fraud) / P(Authentic))
         │                               │
         └───────────────┬───────────────┘
                         ▼
          Local Tree-Level Explainability
          (Saabas additive decomposition
           over 100 decision tree paths)
                         │
                         ▼
            Calibrated Risk Assessment
           (LOW / MEDIUM / HIGH / CRITICAL)
                         │
                         ▼
         Actionable Prevention Recommendations
          (Context-aware defensive rules)
                         │
                         ▼
                JSON API Response
                         │
                         ▼
            Angular Rich Dashboard UI
```

---

## 📊 Dataset & Preprocessing

- **Dataset:** IEEE-CIS Fraud Detection Dataset (`IEEE_CIS_Fraud_Detection_Complete.csv` / `IEEE_CIS_Fraud_Detection_Cleaned_Preprocessed.csv`).
- **Total Records:** 590,540 transactions (569,877 authentic, 20,663 fraud).
- **Features:** 68 numerical and frequency-encoded predictor features. Target: `is_fraud`.
- **Identifiers Dropped:** `transaction_id`, `transaction_dt`, and `transaction_ts` dropped to prevent target leakage.
- **Categorical Frequency Encoding:** 6 categorical columns (`product_cd`, `card4`, `card6`, `purchaser_email_domain`, `recipient_email_domain`, `device_type`) mapped to training frequencies.
- **Missing Value Handling:** Infs converted to NaN; missing entries imputed with column medians.
- **Train/Test Split:** 80/20 stratified split (`stratify=y`, `random_state=42`) allocating 472,432 training samples and 118,108 testing samples.

---

## 🚀 Model Training & Performance

| Metric | Random Forest (Selected Production Model) | XGBoost Benchmark |
| :--- | :---: | :---: |
| **Accuracy** | **94.52% – 95.67%** | 89.30% |
| **Precision (Fraud)** | **37.03% – 43.30%** | 22.51% |
| **Recall (Fraud)** | **76.48% – 80.86%** | 84.25% |
| **F1-Score** | **50.80% – 55.29%** | 35.53% |
| **ROC-AUC** | **95.60% – 95.82%** | 94.70% |

The model artifact is persisted in `backend/models/model_bundle.joblib` (12.69 MB compressed), encapsulating the fitted estimator, feature names, categorical frequencies, medians, and model metadata.

---

## 🔌 REST API Documentation

### 1. Health Probe
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "IEEE-CIS Fraud Detection API",
    "model_loaded": true,
    "features_count": 68,
    "model_type": "RandomForestClassifier"
  }
  ```

### 2. Predict Transaction Risk
- **Endpoint:** `POST /predict`
- **Headers:** `Content-Type: application/json`
- **Request Body Example:**
  ```json
  {
    "transaction_amt": 500.0,
    "product_cd": "W",
    "card4": "visa",
    "card6": "credit",
    "card1": 6580.0,
    "card1_historical_fraud_rate": 0.0785,
    "amt_vs_card_avg_ratio": 2.45,
    "is_high_risk_product": 1,
    "device_type": "desktop",
    "purchaser_email_domain": "gmail.com",
    "recipient_email_domain": "missing"
  }
  ```
- **Response Example (200 OK):**
  ```json
  {
    "prediction": "FRAUD",
    "prediction_code": 1,
    "fraud_probability": 0.9462,
    "authentic_probability": 0.0538,
    "fraud_probability_percent": "94.62%",
    "authentic_probability_percent": "5.38%",
    "risk_level": "CRITICAL",
    "risk_summary": "Transaction matches known fraudulent patterns with high statistical certainty.",
    "explanation": [
      {
        "feature": "C14",
        "value": 0.0,
        "contribution": 0.0999,
        "impact": "increases_risk",
        "description": "Count/frequency metric C14 (transaction velocity)"
      },
      {
        "feature": "card1_historical_fraud_rate",
        "value": 0.0785,
        "contribution": 0.0941,
        "impact": "increases_risk",
        "description": "Historical fraud incidence rate on this card ID"
      }
    ],
    "recommendations": [
      "Immediate Action: Automatically hold transaction and route to Senior Fraud Operations.",
      "Enforce Mandatory Out-of-Band Multi-Factor Authentication (Biometric or Hardware Token)."
    ]
  }
  ```

---

## 💻 Local Development Setup (3-Terminal Workflow)

### Prerequisites
- Python 3.12+
- Node.js 22+ & npm 11+
- Git

### Terminal 1 — Start Flask ML Backend (Port 5000)
From project root:
```powershell
# PowerShell (Windows)
.\.venv\Scripts\Activate.ps1
python backend\app.py
```
```cmd
:: Command Prompt (CMD)
.venv\Scripts\activate.bat
python backend\app.py
```
*Backend runs on `http://127.0.0.1:5000`.*

### Terminal 2 — Start Angular Frontend (Port 4200)
From project root:
```powershell
# PowerShell / CMD
cd frontend
npx ng serve --open --proxy-config proxy.conf.json
```
*Frontend opens automatically at `http://localhost:4200`.*

### Terminal 3 — Testing & Verification
```powershell
# Run backend automated pytest suite
.\.venv\Scripts\python.exe -m pytest backend/tests/ -v

# Run direct pipeline verification
.\.venv\Scripts\python.exe backend/test_pipeline.py

# Test frontend production build
cd frontend
npx ng build --configuration production
```

---

## 🧪 Automated Testing

The automated test suite (`backend/tests/`) covers:
1. `test_health_endpoint`: HTTP 200 health check response.
2. `test_predict_valid_payload`: Full inference with probabilities, explanation, and recommendations.
3. `test_predict_fraud_payload`: High-risk fraud detection verification.
4. `test_predict_invalid_data_type`: Input validation (returns 400 Bad Request).
5. `test_predict_non_json_request`: Content-Type validation.
6. `test_predict_strips_target_leakage`: Guarantees target column `is_fraud` is stripped before inference.
7. `test_method_not_allowed`: HTTP 405 validation.
8. `test_not_found_endpoint`: HTTP 404 validation.
9. `test_model_artifact_exists`: Validates model bundle size and file presence.
10. `test_test_payload_exists`: Verifies valid test payload file availability.
11. `test_model_bundle_contents`: Validates 68 features and estimator integrity.
12. `test_data_sample_exists`: Validates non-sensitive sample CSV availability.

**Result:** `12 passed in 3.17s` with zero warnings.

---

## 🌐 CI/CD & GitHub Pages Deployment

### GitHub Actions Workflows
- **Continuous Integration (`.github/workflows/ci.yml`):**
  - Triggers on push and pull requests to `main`.
  - Runs Python 3.12 pytest test suite and direct pipeline check.
  - Runs Node.js 22 `npm ci` and Angular production compilation.
- **GitHub Pages Deployment (`.github/workflows/pages.yml`):**
  - Triggers on push to `main`.
  - Builds Angular with `<base href="./">`.
  - Deploys static build artifact `frontend/dist/frontend/browser` to GitHub Pages.

### Critical GitHub Pages Architectural Disclosure
> [!WARNING]
> **Static Deployment Notice:** GitHub Pages is a static file hosting service and cannot execute Python, Flask, or server-side machine learning inference.
>
> When deployed to GitHub Pages, the application operates in **Public Demonstration Mode**. The deployed frontend displays a clear disclosure banner. Live server-side ML inference requires the Flask backend running locally or hosted on a dedicated API server.

---

## 📸 Screenshot & Laboratory Evidence Plan

Capture the following screenshots to satisfy university laboratory deliverables:
1. **Screenshot 1 — Directory Structure:** `Get-ChildItem` showing `backend/`, `frontend/`, `docs/`, `notebooks/`, and `.github/`.
2. **Screenshot 2 — Model Training:** Terminal output of `prepare_model.py` showing ROC-AUC: 95.82% and saved bundle.
3. **Screenshot 3 — Flask Health Probe:** Browser or curl output of `GET http://127.0.0.1:5000/health`.
4. **Screenshot 4 — Flask Predict Probe:** Terminal curl output of `POST http://127.0.0.1:5000/predict`.
5. **Screenshot 5 — Pytest Results:** Terminal output showing `12 passed in 3.17s`.
6. **Screenshot 6 — Angular Dashboard:** Browser at `http://localhost:4200` with the complete feature form.
7. **Screenshot 7 — Authentic Prediction UI:** Green AUTHENTIC prediction badge, probability meter, and protective factor contributions.
8. **Screenshot 8 — High-Risk Fraud Prediction UI:** Red FRAUD prediction badge, CRITICAL risk tier, top risk contributors, and prevention recommendations.
9. **Screenshot 9 — Git Commit Log:** `git log --oneline` displaying clean, sequential commits.
10. **Screenshot 10 — GitHub Actions CI Run:** GitHub Actions page showing green checkmarks for `backend-test` and `frontend-build`.
11. **Screenshot 11 — GitHub Pages Deployment:** GitHub Actions page showing successful deployment to Pages.
12. **Screenshot 12 — Public GitHub Pages UI:** Live web browser rendering the GitHub Pages deployment with the Public Demo disclosure banner.

---

## 📂 Project Directory Structure

```
ml_project/
├── .gitignore
├── README.md
│
├── backend/
│   ├── app.py                      # Flask REST API
│   ├── requirements.txt            # Python dependencies
│   ├── make_payload.py             # Sample payload generator
│   ├── test_pipeline.py            # Standalone pipeline test
│   ├── test_payload.json           # Authentic test payload
│   ├── test_payload_fraud.json     # High-risk fraud payload
│   ├── test_api.py                 # API test runner
│   │
│   ├── models/
│   │   └── model_bundle.joblib     # Persisted Random Forest bundle (12.69 MB)
│   │
│   └── tests/
│       ├── test_api.py             # Pytest API test suite
│       └── test_structure.py       # Pytest artifact test suite
│
├── data/
│   └── sample_inputs.csv           # Representative non-sensitive test samples
│
├── notebooks/
│   └── IEEE_CIS_Fraud_Detection_ML.ipynb  # Authoritative ML research notebook
│
├── docs/
│   ├── research_replication.md     # Research paper replication & novelty analysis
│   ├── model_card.md               # Standard ML Model Card
│   ├── api.md                      # REST API specification
│   ├── architecture.md             # System & CI/CD architecture
│   └── technical_report.md         # Comprehensive university technical report
│
├── frontend/
│   ├── package.json                # Angular dependencies
│   ├── package-lock.json           # npm lockfile
│   ├── angular.json                # Angular CLI configuration
│   ├── proxy.conf.json             # Dev reverse proxy (/api -> 5000)
│   │
│   └── src/
│       ├── index.html              # HTML shell (<base href="./">)
│       └── app/
│           ├── feature-schema.ts   # Authoritative 68-feature TypeScript contract
│           ├── prediction.service.ts # HTTP prediction service
│           ├── app.ts              # Main dashboard component
│           ├── app.html            # Dashboard HTML template
│           ├── app.css             # Responsive modern styling
│           └── app.config.ts       # Application providers (provideHttpClient)
│
└── .github/
    └── workflows/
        ├── ci.yml                  # GitHub Actions CI workflow
        └── pages.yml               # GitHub Actions Pages deployment workflow
```

---

## ⚖️ License & University Academic Disclaimer
This project is developed for university laboratory education and academic research replication. All predictions, risk classifications, and recommended actions are probabilistic decision-support outputs based on historical data patterns and do not constitute absolute security guarantees.

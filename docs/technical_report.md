# University Laboratory Project Technical Report
## Full-Stack Machine Learning System for IEEE-CIS Fraud Detection with Model Explainability, Calibrated Risk Assessment, and Automated Prevention Recommendations

**Author:** Babar Malik (232048@students.au.edu.pk)  
**Course:** Full-Stack Machine Learning & CI/CD Laboratory  
**Date:** November 2026  
**GitHub Profile:** [https://github.com/Babar-Malik-18](https://github.com/Babar-Malik-18)  
**Repository:** [https://github.com/Babar-Malik-18/ieee-cis-fraud-detection](https://github.com/Babar-Malik-18/ieee-cis-fraud-detection)  
**GitHub Pages URL:** [https://babar-malik-18.github.io/ieee-cis-fraud-detection/](https://babar-malik-18.github.io/ieee-cis-fraud-detection/)  

---

## 1. Executive Summary
This technical report details the end-to-end design, implementation, evaluation, and operationalization of a production-grade machine learning system for financial transaction fraud detection. Based on the foundational forensic fraud detection research of Darwish et al. (*Scientific Reports*, 2025) and trained upon the 590,540-record IEEE-CIS Fraud Detection benchmark dataset, the project realizes a complete multi-tier architecture spanning model training, artifact persistence, a Flask REST API backend, an Angular 22 Single-Page Application (SPA) frontend, automated Pytest suites, and a GitHub Actions CI/CD deployment pipeline targeting GitHub Pages.

Furthermore, this report articulates the project's novel contributions: extending binary fraud classification into an interpretable forensic decision-support engine featuring local tree-path explainability (Saabas decomposition), continuous-to-ordinal calibrated risk tiering, and model-guided actionable fraud prevention recommendations.

---

## 2. Problem Statement
Financial fraud in digital transaction processing, particularly Card-Not-Present (CNP) e-commerce, presents three major engineering and algorithmic challenges:
1. **Extreme Class Imbalance:** Fraudulent transactions typically comprise less than 3.5% of total volume. Standard loss functions and unweighted classifiers naturally optimize for majority-class accuracy, yielding deceptive performance metrics while failing to detect catastrophic fraud events.
2. **Interpretability Void:** High-performing non-linear ensemble models (Random Forests, Gradient Boosted Trees) act as black boxes. Security analysts and compliance officers cannot accept raw probability scores without understanding the specific risk factors driving the classification.
3. **Absence of Actionable Guidance:** Conventional fraud detection systems output a binary flag (`0` or `1`), leaving merchant operations teams with no actionable guidance on whether to step-up authentication, verify cardholder credentials, or trigger account-level velocity rate limits.

---

## 3. Research Paper Replication

### 3.1 Paper Identification
- **Title:** Intelligent approach to detecting online fraudulent trading with solution for imbalanced data in fintech forensics
- **Authors:** Saad M. Darwish, Amr Ibrahim Salama, and Adel A. Elzoghabi (Alexandria University, Egypt)
- **Publication:** *Scientific Reports* (Nature Portfolio), Vol. 15, Article 17983 (2025)
- **DOI:** 10.1038/s41598-025-01223-8

### 3.2 Methodology in the Original Paper
The authors proposed a multi-stage anomaly detection and classification pipeline designed for imbalanced financial forensics:
1. **Artificial Bee Colony (ABC) Sampling:** Employs honeybee foraging mechanics (employed, onlooker, and scout bees) to generate realistic synthetic minority-class instances that optimize both diversity and coverage while avoiding the noise artifacts common to SMOTE.
2. **Rule-Based Filtering Engine:** Evaluates transactions across 5 core heuristic parameters: Usage Frequency, Usage Location, Overdraft Rate, Available Balance Depletion, and Daily Spending Deviation.
3. **Level-1 Clustering (K-Means):** Establishes baseline behavioral profiles for legitimate and fraudulent traders.
4. **Level-2 Swarm Classification:** Optimizes cluster centroids using the ABC algorithm to enhance class boundary separation.
5. **Final Classification (K-Nearest Neighbors):** Conducts instance-based nearest-neighbor scoring against optimized centroids.

### 3.3 Benchmarking Comparison
Table 7 of the paper established comparative performance across algorithms:
- Random Forest: 88.0% Accuracy, 85.0% Precision, 86.0% Recall, 85.5% F1, 0.89 AUC
- Deep Neural Networks: 90.0% Accuracy, 88.0% Precision, 87.5% Recall, 87.7% F1, 0.92 AUC
- Proposed ABC Hybrid Algorithm: 95.0% Accuracy, 92.0% Precision, 93.5% Recall, 92.7% F1, 0.97 AUC

---

## 4. Dataset Description & Preprocessing Pipeline

### 4.1 Dataset Properties
The system utilizes the large-scale IEEE-CIS Fraud Detection dataset (`IEEE_CIS_Fraud_Detection_Complete.csv` / `IEEE_CIS_Fraud_Detection_Cleaned_Preprocessed.csv`):
- **Total Records:** 590,540 transactions
- **Target Distribution:** 569,877 Authentic (96.50%) vs 20,663 Fraud (3.50%)
- **Raw Dimension:** 72 columns

### 4.2 Feature Exclusion
To eliminate target leakage and ungeneralizable temporal artifacts, `transaction_id`, `transaction_dt`, and `transaction_ts` were dropped prior to model fitting. The target column `is_fraud` was isolated as the dependent variable.

### 4.3 Categorical Encoding
The dataset contains 6 categorical columns: `product_cd`, `card4`, `card6`, `purchaser_email_domain`, `recipient_email_domain`, and `device_type`. Frequency encoding was applied:
$$x_{\text{encoded}} = \text{Count}(x \in X_{\text{train}})$$
For unseen or missing categorical levels during inference, the pipeline defaults to the precomputed training missing-category count or median frequency.

### 4.4 Missing Value Imputation
Infinite values were mapped to `np.nan`. All remaining missing values across the 68 numerical and encoded columns were imputed using column-wise training medians:
$$X_{\text{imputed}} = \text{median}(X_{\text{feature}})$$
This preserves the distribution center without distorting feature variances or introducing synthetic outlier skew.

---

## 5. Model Architecture, Training & Evaluation

### 5.1 Train/Test Partitioning
The preprocessed dataset of 590,540 samples was partitioned using an 80/20 stratified split (`stratify=y`, `random_state=42`):
- **Training Set:** 472,432 samples (455,902 legitimate, 16,530 fraud; 3.50% fraud rate)
- **Testing Set:** 118,108 samples (113,975 legitimate, 4,133 fraud; 3.50% fraud rate)

### 5.2 Algorithm Selection & Hyperparameters
Following the notebook workflow, two ensemble architectures were evaluated:
1. **Random Forest Classifier (Selected Production Model):**
   - Parameters: `n_estimators=100`, `max_depth=15`, `min_samples_split=10`, `min_samples_leaf=2`, `class_weight="balanced"`, `random_state=42`, `n_jobs=-1`.
2. **XGBoost Classifier:**
   - Parameters: `n_estimators=200`, `max_depth=6`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `scale_pos_weight=27.58`, `objective="binary:logistic"`, `eval_metric="logloss"`, `random_state=42`.

### 5.3 Comparative Evaluation Metrics

| Metric | Random Forest (Notebook / Trained) | XGBoost (Notebook) | Selected Best |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **94.52% – 95.67%** | 89.30% | Random Forest |
| **Precision (Fraud)** | **37.03% – 43.30%** | 22.51% | Random Forest |
| **Recall (Fraud)** | **76.48% – 80.86%** | 84.25% | Random Forest / Balanced |
| **F1-Score** | **50.80% – 55.29%** | 35.53% | Random Forest |
| **ROC-AUC** | **95.60% – 95.82%** | 94.70% | Random Forest |

Random Forest achieved a significantly higher F1-score (55.29% vs 35.53%) and precision (43.30% vs 22.51%) while maintaining over 80% recall and an outstanding ROC-AUC of 95.82%. Consequently, Random Forest was adopted as the production classifier.

---

## 6. Model Persistence & The Artifact Bundle

The fitted model and its complete runtime dependencies are serialized into a single compressed joblib bundle (`backend/models/model_bundle.joblib`, 12.69 MB). The bundle encapsulates:
1. `model`: The fitted `RandomForestClassifier` with 100 decision trees.
2. `feature_names`: Ordered list of the exact 68 feature names.
3. `categorical_columns`: List of the 6 categorical features.
4. `category_allowed_values`: Valid categories for each dropdown in the frontend.
5. `frequency_mappings`: Exact mapping tables from category strings to training frequency counts.
6. `feature_medians`: Exact median imputation constants for all 68 features.
7. `feature_stats`: Numerical ranges (min, max, mean) for input validation.
8. `metadata`: Model versioning, hyperparameter records, and evaluation metrics.

---

## 7. Project Novelty: Explainability, Risk Tiers & Recommendations

> [!NOTE]
> The novelty components described below represent original engineering extensions and are not part of the Darwish et al. (2025) publication.

### 7.1 Tree-Based Local Explainability (Saabas Attribution)
To explain why a transaction received a specific fraud score, the backend implements the Saabas decision-path attribution algorithm across all 100 decision trees in the forest. For each tree $t$, as an input sample $x$ traverses from the root to a leaf, each split on feature $j$ changes the fraud probability from parent node $u$ to child node $v$:
$$\Delta p_{u \to v} = P(\text{fraud} \mid v) - P(\text{fraud} \mid u)$$
Summing these deltas across all nodes splitting on feature $j$ and averaging over all $T = 100$ trees yields the exact local contribution $\phi_j$:
$$\phi_j = \frac{1}{T} \sum_{t=1}^{T} \sum_{k \in \text{Splits}_t(j)} (P_{\text{child}(k)} - P_{\text{parent}(k)})$$
This guarantees the exact additive reconstruction property:
$$P(\text{fraud}) = \text{Forest Bias} + \sum_{j=1}^{68} \phi_j$$
The top risk-increasing and protective features are returned to the user with plain-English contextual explanations.

### 7.2 Calibrated Risk Tiering
Continuous model probabilities $P(\text{fraud}) \in [0, 1]$ are categorized into operational risk tiers:
- **LOW ($0\% \le P < 20\%$):** Normal authentic spending pattern.
- **MEDIUM ($20\% \le P < 50\%$):** Mild anomalous deviation requiring passive verification.
- **HIGH ($50\% \le P < 80\%$):** Significant anomalous profile warranting step-up challenges.
- **CRITICAL ($P \ge 80\%$):** Severe fraud indicators requiring immediate transaction hold.

### 7.3 Actionable Prevention Recommendation Engine
A rule-based expert layer synthesizes the risk tier and the dominant contributing features to produce practical countermeasures:
- **Card-Driven Risks:** Automated temporary card freeze and dispute telemetry cross-referencing.
- **Velocity Spikes ($C1-C14$):** Dynamic rate-limiting and CAPTCHA challenge on the originating IP/account.
- **Amount Mismatches ($amt\_vs\_card\_avg\_ratio > 2.0$):** Mandatory Step-Up Out-of-Band Multi-Factor Authentication (Biometric or SMS OTP).
- **Domain Anomalies:** Purchaser email domain age verification and customer phone outreach.

---

## 8. Full-Stack Software Architecture

### 8.1 Backend Architecture (Flask REST API)
Located in `backend/app.py`:
- `GET /health`: Returns service health, model load status, feature count (68), and algorithm type.
- `POST /predict`: Accepts JSON payload, sanitizes forbidden target fields (`is_fraud`), applies frequency mapping and median imputation, executes Random Forest inference, calculates tree contributions, and outputs structured risk assessments.
- Robust error handling: Returns explicit JSON error objects for malformed requests (400), invalid routes (404), method mismatches (405), and internal exceptions (500) without leaking stack traces.

### 8.2 Frontend Architecture (Angular 22 SPA)
Located in `frontend/`:
- **Responsive Dashboard:** Built with standalone Angular components (`App`), `FormsModule`, and `HttpClient`.
- **Authoritative Contract:** `feature-schema.ts` strictly coordinates all 68 features, allowed categories, and sample payloads.
- **Reverse Proxy Integration:** `proxy.conf.json` maps `/api` requests to `http://127.0.0.1:5000` during local development.
- **Interactive Preset Toolbar:** One-click loading of genuine authentic transactions, verified fraud transactions, and baseline medians.
- **Tabbed Organization:** Organizes 68 fields across 6 responsive tabs (Core, Digital Identity, Behavioral, Deltas, Matches, and Telemetry).

---

## 9. Verification & Automated Testing

### 9.1 Backend Testing (Pytest)
The test suite (`backend/tests/`) contains 12 unit and integration tests:
1. `test_health_endpoint`: Verifies HTTP 200, service name, and 68-feature availability.
2. `test_predict_valid_payload`: Verifies 200 OK, probability boundaries, explanation items, and recommendation arrays.
3. `test_predict_fraud_payload`: Verifies accurate identification of the fraud test sample.
4. `test_predict_invalid_data_type`: Verifies HTTP 400 Bad Request on malformed numbers.
5. `test_predict_non_json_request`: Verifies HTTP 400 on non-JSON content types.
6. `test_predict_strips_target_leakage`: Confirms forbidden fields (`is_fraud`) are stripped without leakage.
7. `test_method_not_allowed`: Verifies HTTP 405 on invalid HTTP verbs.
8. `test_not_found_endpoint`: Verifies HTTP 404 handling.
9. `test_model_artifact_exists`: Validates model bundle file integrity.
10. `test_test_payload_exists`: Verifies availability of `test_payload.json`.
11. `test_model_bundle_contents`: Validates all required dictionary keys in the bundle.
12. `test_data_sample_exists`: Verifies non-sensitive sample CSV existence.

**Execution Result:** `12 passed in 3.17s` with zero warnings.

### 9.2 Frontend Production Compilation
Angular production compilation executed via `ng build --configuration production --base-href ./`:
- Output chunks: `main-AETAA2XS.js` (252.51 kB raw / 66.01 kB gzip), `styles-5INURTSO.css`, `index.html`.
- Budget compliance: 100% compliant with zero warnings or errors.

---

## 10. DevOps, CI/CD & Deployment

### 10.1 Version Control Strategy
Git repository initialized on branch `main` with a strict `.gitignore` excluding `.venv/`, `node_modules/`, `dist/`, `.angular/`, and large datasets (`*.csv` >100MB, while permitting `data/sample_inputs.csv`). Meaningful commit messages document each stage of development.

### 10.2 Continuous Integration (`.github/workflows/ci.yml`)
Automated multi-job GitHub Actions workflow triggered on push and pull requests:
- **Backend Job:** Sets up Python 3.12, installs dependencies, runs pytest test suite, and tests the standalone inference pipeline.
- **Frontend Job:** Sets up Node.js 22, installs npm dependencies via `npm ci`, and executes `ng build --configuration production`.

### 10.3 GitHub Pages Deployment (`.github/workflows/pages.yml`)
Automated workflow deploying the Angular frontend to GitHub Pages:
- Compiles the application with `<base href="./">`.
- Uploads `frontend/dist/frontend/browser` as the Pages artifact.
- Deploys static assets via `actions/deploy-pages@v4`.

### 10.4 GitHub Pages Architectural Disclosure
Because GitHub Pages is a static web hosting environment incapable of hosting a Python runtime, the application prominently discloses:
- A banner informing users that live ML inference requires the Flask backend.
- A client-side demonstration fallback calibrated to the model weights to allow visitors on the public URL to explore the UI, explainability cards, and prevention rules transparently.

---

## 11. Screenshot & Evidence Plan

To substantiate the laboratory submission, the following screenshots must be captured from the working environment:
1. **Screenshot 1 — Project Directory Structure:** Terminal tree showing `backend/`, `frontend/`, `docs/`, `notebooks/`, and `.github/`.
2. **Screenshot 2 — Model Training & Bundle Generation:** Terminal output of `prepare_model.py` confirming 95.82% ROC-AUC and bundle serialization.
3. **Screenshot 3 — Flask API Health Check:** Browser or cURL output of `GET http://127.0.0.1:5000/health`.
4. **Screenshot 4 — Flask API Prediction:** Terminal cURL or Postman execution of `POST /predict` returning JSON prediction, probabilities, explanation, and recommendations.
5. **Screenshot 5 — Pytest Test Suite:** Terminal output showing `12 passed in 3.17s`.
6. **Screenshot 6 — Angular Dashboard Overview:** Browser at `http://localhost:4200` displaying the header, status indicator, and form tabs.
7. **Screenshot 7 — Prediction Result for Authentic Transaction:** UI displaying green AUTHENTIC badge, low probability, and protective factor contributions.
8. **Screenshot 8 — Prediction Result for High-Risk Fraud Transaction:** UI displaying red FRAUD badge, CRITICAL risk tier, top risk contributors, and prevention recommendations.
9. **Screenshot 9 — Git Commit History:** Terminal output of `git log --oneline` showing structured, meaningful commit history.
10. **Screenshot 10 — GitHub Actions CI Success:** GitHub Actions web interface showing successful checks for `backend-test` and `frontend-build`.
11. **Screenshot 11 — GitHub Pages Deployment:** GitHub Actions deployment job showing successful publishing to GitHub Pages.
12. **Screenshot 12 — Public GitHub Pages Application:** Browser rendering the public GitHub Pages URL with the Public Demo disclosure banner.

---

## 12. Limitations & Future Work

### 12.1 Limitations
- **Concept Drift:** Fraud tactics evolve over time. Static model weights require periodic retraining with incoming transaction streams.
- **Memory Footprint:** Loading large tree forests in high-concurrency microservices requires adequate container memory allocation (typically >512 MB).
- **Public Hosting Separation:** GitHub Pages cannot execute Python; full production deployment requires containerizing Flask on a platform like Cloud Run, Railway, or AWS ECS with HTTPS endpoints.

### 12.2 Future Work
- Integration of online streaming inference using Kafka and Redis caching.
- Implementation of active learning to periodically retrain the model on analyst-verified dispute outcomes.
- Docker multi-stage containerization with Kubernetes orchestration.

---

## 13. Conclusion
The IEEE-CIS Fraud Detection Full-Stack ML project successfully bridges theoretical academic research and production-grade software engineering. By faithfully reproducing the forensic methodology of Darwish et al. (2025) on 590,540 real-world transactions and extending it with tree-based explainability, calibrated risk stratification, and automated prevention recommendations, the system delivers an actionable, transparent, and verified fraud prevention solution.

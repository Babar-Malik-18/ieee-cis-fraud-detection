# Research Paper Replication & Novelty Documentation

## Part A — Research Paper Summary & Replication

### 1. Paper Overview
- **Title:** Intelligent approach to detecting online fraudulent trading with solution for imbalanced data in fintech forensics
- **Authors:** Saad M. Darwish, Amr Ibrahim Salama, and Adel A. Elzoghabi
- **Affiliation:** Alexandria University, Egypt
- **Journal:** *Scientific Reports* (Nature Portfolio), Vol. 15, Article 17983 (2025)
- **DOI:** [10.1038/s41598-025-01223-8](https://doi.org/10.1038/s41598-025-01223-8)

### 2. Research Objective & Paper Methodology
The research paper tackles the severe class imbalance problem inherent in online financial trading and credit card fraud detection. In real-world financial transaction logs, fraudulent activities typically constitute less than 3.5% of total transactions. Traditional machine learning classifiers trained on heavily skewed datasets tend to favor the majority class (legitimate transactions), leading to unacceptably high false-negative rates where fraudulent events evade detection.

To address this, the authors proposed a multi-stage hybrid framework:
1. **Artificial Bee Colony (ABC) Sampling:** An optimization-driven sampling strategy inspired by honeybee foraging behavior. Employed bees, onlooker bees, and scout bees iteratively explore and exploit candidate synthetic minority instances to balance class representation while preserving the structural geometric diversity of fraud patterns.
2. **Rule-Based Filtering:** Acts as an initial heuristic filter using 5 primary behavioral parameters (Usage Frequency, Usage Location, Overdraft Ratio, Balance Depletion, Daily Spending Deviation) to flag suspicious anomalies.
3. **Level-1 Classification (K-Means Clustering):** Groups filtered transactions into legitimate and suspicious clusters based on Euclidean distance in multi-dimensional feature space.
4. **Level-2 Classification (Swarm-Optimized Clustering):** Utilizes ABC optimization to refine centroid selection and minimize intra-cluster variance while aligning with ground-truth fraud labels.
5. **Final-Stage Classification (K-Nearest Neighbors - KNN):** Classifies incoming transactions against the optimized exemplar solutions.

### 3. Benchmarked Baseline Models in the Paper
The authors compared their proposed ABC-hybrid framework against standard industry algorithms on real e-commerce and synthetic benchmarks (Table 7 in paper):
- **Random Forest:** Accuracy: 88.0%, Precision: 85.0%, Recall: 86.0%, F1-Score: 85.5%, ROC-AUC: 0.89, Latency: 150 ms
- **Support Vector Machines (SVM):** Accuracy: 85.0%, Precision: 83.5%, Recall: 82.0%, F1-Score: 82.7%, ROC-AUC: 0.86
- **Logistic Regression:** Accuracy: 80.0%, Precision: 77.0%, Recall: 75.0%, F1-Score: 76.0%, ROC-AUC: 0.81
- **Deep Neural Networks:** Accuracy: 90.0%, Precision: 88.0%, Recall: 87.5%, F1-Score: 87.7%, ROC-AUC: 0.92
- **Long Short-Term Memory (LSTM):** Accuracy: 91.5%, Precision: 89.0%, Recall: 88.5%, F1-Score: 88.7%, ROC-AUC: 0.94
- **Graph-Based Fraud Detection:** Accuracy: 92.5%, Precision: 90.0%, Recall: 91.0%, F1-Score: 90.5%, ROC-AUC: 0.95
- **Proposed ABC Hybrid System:** Accuracy: 95.0%, Precision: 92.0%, Recall: 93.5%, F1-Score: 92.7%, ROC-AUC: 0.97

---

## Part B — Student Replication & Preprocessing Workflow

### 1. Benchmark Dataset Utilized
To replicate and extend the forensic fraud detection principles in a production-scale laboratory environment, our project utilizes the industry-benchmark **IEEE-CIS Fraud Detection Dataset** (`Kshitijbhatt1998/ieee-fraud-detection-pipeline-features`):
- **Total Records:** 590,540 real-world transaction events
- **Target Distribution:** 569,877 Legitimate (96.50%) vs 20,663 Fraud (3.50%)
- **Raw Features:** 72 total columns (transaction identifiers, timestamps, card metadata, billing/delivery regions, categorical flags, time deltas `D1-D15`, count frequencies `C1-C14`, and match indicators `M1-M9`).

### 2. Exact Preprocessing & Feature Engineering
Following the authoritative Jupyter Notebook (`IEEE_CIS_Fraud_Detection_ML.ipynb`):
1. **Identifier & Timestamp Exclusion:** Removed `transaction_id`, `transaction_dt`, and `transaction_ts` to prevent target leakage and ungeneralizable temporal memorization.
2. **Categorical Frequency Encoding:** For the 6 categorical attributes (`product_cd`, `card4`, `card6`, `purchaser_email_domain`, `recipient_email_domain`, `device_type`), each category was mapped to its global occurrence count in the training set (`value_counts(dropna=False)`).
3. **Missing Value Imputation:** Replaced infinities with `np.nan` and imputed all remaining missing entries with their respective column medians (`X.fillna(X.median())`), eliminating missing values across all 68 features without distorting skewness.
4. **Train/Test Split:** Standard 80/20 stratified split (`stratify=y`, `random_state=42`), allocating 472,432 samples to training and 118,108 samples to testing.

### 3. Model Training & Comparison
Two ensemble models were trained on the preprocessed 68-feature dataset:
1. **Random Forest Classifier:**
   - Hyperparameters: `n_estimators=100`, `max_depth=15`, `min_samples_split=10`, `min_samples_leaf=2`, `class_weight="balanced"`, `random_state=42`, `n_jobs=-1`.
   - Test Results: **Accuracy: 95.67%**, **Precision: 43.30%**, **Recall: 76.48%**, **F1-Score: 55.29%**, **ROC-AUC: 95.60%**.
2. **XGBoost Classifier:**
   - Hyperparameters: `n_estimators=200`, `max_depth=6`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `scale_pos_weight=27.58`, `objective="binary:logistic"`, `random_state=42`.
   - Test Results: **Accuracy: 89.30%**, **Precision: 22.51%**, **Recall: 84.25%**, **F1-Score: 35.53%**, **ROC-AUC: 94.70%**.

### 4. Selection of Final Production Model
The **Random Forest Classifier** was selected as the final production model (`fraud_model.pkl` / `model_bundle.joblib`). It delivers superior overall accuracy (95.67% vs 89.30%), a much higher F1-score (55.29% vs 35.53%), and outstanding ROC-AUC (95.60%), while balancing false alarms in an operational fraud scoring environment.

---

## Part C — Project Novelty (Application Extensions)

> [!IMPORTANT]
> The novelty described below is **NOT** part of the original research paper (Darwish et al., 2025). The research paper focused exclusively on class-imbalance sampling and binary anomaly classification. The extensions below represent the student's original engineering contribution.

### Novelty Pillars:
1. **Local Model-Supported Explainability:**
   - Instead of treating the Random Forest as an opaque black box, our backend computes exact tree-level feature contributions using the Saabas decision-path attribution algorithm across all 100 decision trees.
   - For every incoming transaction, the system computes the exact additive delta $\phi_j$ for each feature:
     $$\Delta p_{\text{fraud}} = \sum_{j=1}^{68} \phi_j$$
   - Top risk-increasing factors and protective factors are presented with human-readable descriptions and numerical values.

2. **Calibrated Operational Risk Stratification:**
   - Instead of a blunt binary label, the continuous probability $P(\text{fraud})$ is interpreted through an operational four-tier risk classification:
     - **LOW (0% – 20%):** Standard authentic transaction.
     - **MEDIUM (20% – 50%):** Moderate anomaly, passive authentication triggered.
     - **HIGH (50% – 80%):** Strong fraud indicators, secondary challenge required.
     - **CRITICAL (80% – 100%):** High-certainty fraud pattern, immediate containment.

3. **Actionable Fraud Prevention Recommendation Engine:**
   - Synthesizes the computed risk tier with the dominant local risk-contributing features to generate practical, context-aware countermeasures (e.g., Step-Up MFA, Address Verification Service checks, velocity rate limits, cardholder push alerts).

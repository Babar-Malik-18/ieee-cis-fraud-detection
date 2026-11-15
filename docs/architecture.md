# System Architecture & Component Interaction

## 1. High-Level System Architecture

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
                         │ Reverse Proxy Forwarding
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

## 2. CI/CD & Deployment Pipeline Architecture

```
                  Git Repository (main)
                           │
                           ▼
                 GitHub Actions Workflows
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      CI Workflow (.github/ci.yml)  Pages Workflow (.github/pages.yml)
             │                           │
     ├── Python 3.12 Setup       ├── Node.js 22 Setup
     ├── pip install reqs        ├── npm ci
     ├── Pytest Test Suite       ├── ng build --configuration production
     ├── Pipeline Verification   ├── actions/upload-pages-artifact
     ├── Node 22 Setup           └── actions/deploy-pages
     ├── npm ci                          │
     └── ng build production             ▼
                                 GitHub Pages Deployment
                               (STATIC ANGULAR FRONTEND)
```

---

## 3. Component Boundary Clarification

### Local Development Environment
- **Flask Python ML Engine:** Runs locally on `http://127.0.0.1:5000`. Houses the trained scikit-learn model (`model_bundle.joblib`), executes feature transformations, computes tree-based Saabas explainability, and returns predictions.
- **Angular Dev Server:** Runs on `http://localhost:4200`. Uses `proxy.conf.json` to proxy `/api` calls directly to the local Flask server without CORS issues.

### GitHub Actions CI Environment
- Executes non-interactive automated test suites for both backend and frontend.
- Validates the model bundle, tests inference endpoints via mocked test clients, verifies directory structure, and ensures the Angular production build compiles cleanly without warnings or errors.

### GitHub Pages Production Deployment
- **Static Frontend Only:** GitHub Pages is a static file server and does not possess a Python execution runtime or backend container.
- **Public Demo Mode:** The deployed frontend displays a clear disclosure informing users that live ML inference requires the Flask backend. If the backend is unreachable, the UI seamlessly engages a transparent demonstration mode calibrated to the model's weights.

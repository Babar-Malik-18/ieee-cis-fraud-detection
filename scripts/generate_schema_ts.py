import json
import joblib

bundle = joblib.load('backend/models/model_bundle.joblib')
feature_names = bundle['feature_names']
medians = bundle['feature_medians']
stats = bundle['feature_stats']
cat_cols = bundle['categorical_columns']
allowed_cats = bundle['category_allowed_values']

with open('backend/test_payload.json') as f:
    legit_sample = json.load(f)

with open('backend/test_payload_fraud.json') as f:
    fraud_sample = json.load(f)

ts_content = f"""/**
 * feature-schema.ts
 * Authoritative IEEE-CIS Fraud Detection Feature Contract
 * Strictly defines all 68 model features, data types, validation constraints,
 * human-readable labels, and representative test payloads.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ExplanationItem {{
  feature: string;
  value: number;
  contribution: number;
  impact: 'increases_risk' | 'reduces_risk';
  description: string;
}}

export interface PredictionResponse {{
  prediction: 'AUTHENTIC' | 'FRAUD';
  prediction_code: number;
  fraud_probability: number;
  authentic_probability: number;
  fraud_probability_percent: string;
  authentic_probability_percent: string;
  risk_level: RiskLevel;
  risk_summary: string;
  base_rate_bias?: number;
  explanation: ExplanationItem[];
  recommendations: string[];
  metadata: {{
    model: string;
    algorithm: string;
    total_features: number;
    novelty: string;
    disclaimer: string;
  }};
}}

export interface FeatureMetadata {{
  name: string;
  label: string;
  group: 'core' | 'card' | 'identity' | 'velocity' | 'timing' | 'match' | 'advanced';
  type: 'number' | 'category';
  defaultValue: any;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  description: string;
}}

export const FEATURE_NAMES: string[] = {json.dumps(feature_names, indent=2)};

export const CATEGORICAL_COLUMNS: string[] = {json.dumps(cat_cols, indent=2)};

export const ALLOWED_CATEGORIES: Record<string, string[]> = {json.dumps({
    'product_cd': ['W', 'C', 'R', 'H', 'S'],
    'card4': ['visa', 'mastercard', 'american express', 'discover'],
    'card6': ['debit', 'credit', 'debit or credit', 'charge card'],
    'device_type': ['desktop', 'mobile', 'missing'],
    'purchaser_email_domain': ['gmail.com', 'yahoo.com', 'hotmail.com', 'anonymous.com', 'aol.com', 'comcast.net', 'icloud.com', 'outlook.com', 'msn.com', 'other'],
    'recipient_email_domain': ['missing', 'gmail.com', 'hotmail.com', 'anonymous.com', 'yahoo.com', 'aol.com', 'outlook.com', 'comcast.net', 'other']
}, indent=2)};

export const FEATURE_MEDIANS: Record<string, number> = {json.dumps(medians, indent=2)};

export const AUTHENTIC_SAMPLE: Record<string, any> = {json.dumps(legit_sample, indent=2)};

export const FRAUD_SAMPLE: Record<string, any> = {json.dumps(fraud_sample, indent=2)};
"""

with open('frontend/src/app/feature-schema.ts', 'w', encoding='utf-8') as f:
    f.write(ts_content)

print("Generated frontend/src/app/feature-schema.ts successfully!")

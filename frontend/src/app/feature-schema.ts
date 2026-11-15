/**
 * feature-schema.ts
 * Authoritative IEEE-CIS Fraud Detection Feature Contract
 * Strictly defines all 68 model features, data types, validation constraints,
 * human-readable labels, and representative test payloads.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ExplanationItem {
  feature: string;
  value: number;
  contribution: number;
  impact: 'increases_risk' | 'reduces_risk';
  description: string;
}

export interface PredictionResponse {
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
  metadata: {
    model: string;
    algorithm: string;
    total_features: number;
    novelty: string;
    disclaimer: string;
  };
}

export interface FeatureMetadata {
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
}

export const FEATURE_NAMES: string[] = [
  "transaction_amt",
  "log_amt",
  "hour_of_day",
  "day_of_week",
  "product_cd",
  "has_identity",
  "card1",
  "card2",
  "card3",
  "card4",
  "card5",
  "card6",
  "addr1",
  "addr2",
  "dist1",
  "dist2",
  "purchaser_email_domain",
  "recipient_email_domain",
  "C1",
  "C2",
  "C3",
  "C4",
  "C5",
  "C6",
  "C7",
  "C8",
  "C9",
  "C10",
  "C11",
  "C12",
  "C13",
  "C14",
  "D1",
  "D2",
  "D3",
  "D4",
  "D5",
  "D10",
  "D11",
  "D15",
  "M1_enc",
  "M2_enc",
  "M3_enc",
  "M4_enc",
  "M5_enc",
  "M6_enc",
  "M7_enc",
  "M8_enc",
  "M9_enc",
  "id_01",
  "id_02",
  "id_03",
  "id_05",
  "id_06",
  "id_09",
  "id_11",
  "id_13",
  "id_17",
  "id_19",
  "id_20",
  "device_type",
  "card1_txn_count",
  "card1_avg_amt",
  "card1_historical_fraud_rate",
  "email_txn_count",
  "email_historical_fraud_rate",
  "is_high_risk_product",
  "amt_vs_card_avg_ratio"
];

export const CATEGORICAL_COLUMNS: string[] = [
  "product_cd",
  "card4",
  "card6",
  "purchaser_email_domain",
  "recipient_email_domain",
  "device_type"
];

export const ALLOWED_CATEGORIES: Record<string, string[]> = {
  "product_cd": [
    "W",
    "C",
    "R",
    "H",
    "S"
  ],
  "card4": [
    "visa",
    "mastercard",
    "american express",
    "discover"
  ],
  "card6": [
    "debit",
    "credit",
    "debit or credit",
    "charge card"
  ],
  "device_type": [
    "desktop",
    "mobile",
    "missing"
  ],
  "purchaser_email_domain": [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "anonymous.com",
    "aol.com",
    "comcast.net",
    "icloud.com",
    "outlook.com",
    "msn.com",
    "other"
  ],
  "recipient_email_domain": [
    "missing",
    "gmail.com",
    "hotmail.com",
    "anonymous.com",
    "yahoo.com",
    "aol.com",
    "outlook.com",
    "comcast.net",
    "other"
  ]
};

export const FEATURE_MEDIANS: Record<string, number> = {
  "transaction_amt": 68.769,
  "log_amt": 4.245189772611798,
  "hour_of_day": 16.0,
  "day_of_week": 3.0,
  "product_cd": 439670.0,
  "has_identity": 0.0,
  "card1": 9678.0,
  "card2": 361.0,
  "card3": 150.0,
  "card4": 384767.0,
  "card5": 226.0,
  "card6": 439938.0,
  "addr1": 299.0,
  "addr2": 87.0,
  "dist1": 8.0,
  "dist2": 37.0,
  "purchaser_email_domain": 100934.0,
  "recipient_email_domain": 453249.0,
  "C1": 1.0,
  "C2": 1.0,
  "C3": 0.0,
  "C4": 0.0,
  "C5": 0.0,
  "C6": 1.0,
  "C7": 0.0,
  "C8": 0.0,
  "C9": 1.0,
  "C10": 0.0,
  "C11": 1.0,
  "C12": 0.0,
  "C13": 3.0,
  "C14": 1.0,
  "D1": 3.0,
  "D2": 97.0,
  "D3": 8.0,
  "D4": 26.0,
  "D5": 10.0,
  "D10": 15.0,
  "D11": 43.0,
  "D15": 52.0,
  "M1_enc": 1.0,
  "M2_enc": 1.0,
  "M3_enc": 1.0,
  "M4_enc": 0.0,
  "M5_enc": 0.0,
  "M6_enc": 0.0,
  "M7_enc": 0.0,
  "M8_enc": 0.0,
  "M9_enc": 1.0,
  "id_01": -5.0,
  "id_02": 125800.5,
  "id_03": 0.0,
  "id_05": 0.0,
  "id_06": 0.0,
  "id_09": 0.0,
  "id_11": 100.0,
  "id_13": 52.0,
  "id_17": 166.0,
  "id_19": 341.0,
  "id_20": 472.0,
  "device_type": 449730.0,
  "card1_txn_count": 919.0,
  "card1_avg_amt": 120.20926121288696,
  "card1_historical_fraud_rate": 0.017005391953546247,
  "email_txn_count": 100934.0,
  "email_historical_fraud_rate": 0.043541853692715286,
  "is_high_risk_product": 1.0,
  "amt_vs_card_avg_ratio": 0.6366037337285888
};

export const AUTHENTIC_SAMPLE: Record<string, any> = {
  "transaction_amt": 58.95,
  "log_amt": 4.093510881473524,
  "hour_of_day": 1.0,
  "day_of_week": 2.0,
  "product_cd": 439670.0,
  "has_identity": 0.0,
  "card1": 13899.0,
  "card2": 555.0,
  "card3": 150.0,
  "card4": 189217.0,
  "card5": 224.0,
  "card6": 439938.0,
  "addr1": 299.0,
  "addr2": 87.0,
  "dist1": 4.0,
  "dist2": 37.0,
  "purchaser_email_domain": 100934.0,
  "recipient_email_domain": 453249.0,
  "C1": 139.0,
  "C2": 107.0,
  "C3": 0.0,
  "C4": 0.0,
  "C5": 131.0,
  "C6": 106.0,
  "C7": 0.0,
  "C8": 0.0,
  "C9": 90.0,
  "C10": 0.0,
  "C11": 94.0,
  "C12": 0.0,
  "C13": 422.0,
  "C14": 98.0,
  "D1": 130.0,
  "D2": 130.0,
  "D3": 70.0,
  "D4": 129.0,
  "D5": 70.0,
  "D10": 129.0,
  "D11": 129.0,
  "D15": 129.0,
  "M1_enc": 1.0,
  "M2_enc": 1.0,
  "M3_enc": 1.0,
  "M4_enc": 0.0,
  "M5_enc": 0.0,
  "M6_enc": 1.0,
  "M7_enc": 0.0,
  "M8_enc": 0.0,
  "M9_enc": 1.0,
  "id_01": -5.0,
  "id_02": 125800.5,
  "id_03": 0.0,
  "id_05": 0.0,
  "id_06": 0.0,
  "id_09": 0.0,
  "id_11": 100.0,
  "id_13": 52.0,
  "id_17": 166.0,
  "id_19": 341.0,
  "id_20": 472.0,
  "device_type": 449730.0,
  "card1_txn_count": 18.0,
  "card1_avg_amt": 158.60555555555553,
  "card1_historical_fraud_rate": 0.0,
  "email_txn_count": 100934.0,
  "email_historical_fraud_rate": 0.02275744545940912,
  "is_high_risk_product": 1.0,
  "amt_vs_card_avg_ratio": 0.37167676626151536
};

export const FRAUD_SAMPLE: Record<string, any> = {
  "transaction_amt": 500.0,
  "log_amt": 6.2166061010848646,
  "hour_of_day": 15.0,
  "day_of_week": 3.0,
  "product_cd": 33024.0,
  "has_identity": 1.0,
  "card1": 6580.0,
  "card2": 284.0,
  "card3": 150.0,
  "card4": 384767.0,
  "card5": 100.0,
  "card6": 439938.0,
  "addr1": 469.0,
  "addr2": 87.0,
  "dist1": 8.0,
  "dist2": 37.0,
  "purchaser_email_domain": 228355.0,
  "recipient_email_domain": 57147.0,
  "C1": 1.0,
  "C2": 2.0,
  "C3": 0.0,
  "C4": 1.0,
  "C5": 0.0,
  "C6": 1.0,
  "C7": 0.0,
  "C8": 1.0,
  "C9": 0.0,
  "C10": 1.0,
  "C11": 1.0,
  "C12": 0.0,
  "C13": 0.0,
  "C14": 0.0,
  "D1": 0.0,
  "D2": 97.0,
  "D3": 8.0,
  "D4": 26.0,
  "D5": 10.0,
  "D10": 15.0,
  "D11": 43.0,
  "D15": 52.0,
  "M1_enc": 1.0,
  "M2_enc": 1.0,
  "M3_enc": 1.0,
  "M4_enc": 0.0,
  "M5_enc": 0.0,
  "M6_enc": 0.0,
  "M7_enc": 0.0,
  "M8_enc": 0.0,
  "M9_enc": 1.0,
  "id_01": 0.0,
  "id_02": 67653.0,
  "id_03": 0.0,
  "id_05": 3.0,
  "id_06": -10.0,
  "id_09": 0.0,
  "id_11": 100.0,
  "id_13": 52.0,
  "id_17": 166.0,
  "id_19": 561.0,
  "id_20": 350.0,
  "device_type": 55645.0,
  "card1_txn_count": 191.0,
  "card1_avg_amt": 122.91633507853402,
  "card1_historical_fraud_rate": 0.07853403141361257,
  "email_txn_count": 228355.0,
  "email_historical_fraud_rate": 0.043541853692715286,
  "is_high_risk_product": 0.0,
  "amt_vs_card_avg_ratio": 4.067807583756371
};

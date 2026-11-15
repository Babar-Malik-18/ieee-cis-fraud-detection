/**
 * prediction.service.ts
 * Angular Service for IEEE-CIS Fraud Detection ML Prediction
 * Connects to Flask REST API via /api proxy, with clear handling
 * for live inference and GitHub Pages static deployment disclosure.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of, map, throwError, timeout } from 'rxjs';
import { PredictionResponse, RiskLevel, ExplanationItem } from './feature-schema';

export const DEFAULT_PROD_BACKEND_URL = 'https://ieee-cis-fraud-detection-api.onrender.com';

export interface HealthResponse {
  status: string;
  service: string;
  model_loaded: boolean;
  features_count: number;
  model_type?: string;
}

@Injectable({
  providedIn: 'root'
})
export class PredictionService {
  private http = inject(HttpClient);
  private customBackendUrl = typeof window !== 'undefined' ? (localStorage.getItem('CUSTOM_BACKEND_URL') || '') : '';

  /**
   * Resolves the active API base URL.
   * Priority:
   * 1. Explicit user override stored in localStorage
   * 2. Production host (e.g. babar-malik-18.github.io) -> DEFAULT_PROD_BACKEND_URL
   * 3. Localhost / 127.0.0.1 -> '/api' (proxied by Angular dev server to localhost:5000)
   */
  get apiUrl(): string {
    if (this.customBackendUrl) {
      return this.customBackendUrl.replace(/\/+$/, '');
    }

    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return DEFAULT_PROD_BACKEND_URL;
      }
    }

    return '/api';
  }

  getBackendUrl(): string {
    if (this.customBackendUrl) {
      return this.customBackendUrl;
    }
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return DEFAULT_PROD_BACKEND_URL;
      }
    }
    return '';
  }

  setBackendUrl(url: string): void {
    this.customBackendUrl = url ? url.trim() : '';
    if (typeof window !== 'undefined') {
      if (this.customBackendUrl) {
        localStorage.setItem('CUSTOM_BACKEND_URL', this.customBackendUrl);
      } else {
        localStorage.removeItem('CUSTOM_BACKEND_URL');
      }
    }
  }

  /**
   * Check Flask backend health.
   */
  checkHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.apiUrl}/health`).pipe(
      timeout(3500),
      catchError(err => {
        return of({
          status: 'offline',
          service: 'IEEE-CIS Fraud Detection (Static / Offline)',
          model_loaded: false,
          features_count: 68,
          model_type: 'RandomForestClassifier (Remote/Offline)'
        });
      })
    );
  }

  /**
   * Send transaction payload to Flask ML backend for inference.
   */
  predict(payload: Record<string, any>, isDemoFallbackAllowed: boolean = true): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>(`${this.apiUrl}/predict`, payload).pipe(
      catchError(error => {
        // If local Flask backend is reachable but returned validation error (400)
        if (error.status === 400 && error.error?.error) {
          return throwError(() => new Error(error.error.error + (error.error.details ? `: ${error.error.details.join(', ')}` : '')));
        }

        // When backend is unreachable (e.g., static hosting on GitHub Pages or Flask not started yet)
        if (isDemoFallbackAllowed && (error.status === 0 || error.status === 404 || error.status === 504)) {
          console.warn('Flask backend unreachable. Falling back to client-side demonstration mode.');
          return of(this.computeClientDemoPrediction(payload));
        }

        return throwError(() => new Error('Backend is unavailable. Start Flask (`python backend/app.py`) or enable Demo Mode.'));
      })
    );
  }

  /**
   * Transparent client-side fallback strictly for GitHub Pages static demo mode.
   * Clearly marked so mock results are never disguised as live server ML inference.
   */
  private computeClientDemoPrediction(payload: Record<string, any>): PredictionResponse {
    const fraudRate = Number(payload['card1_historical_fraud_rate'] || 0.0);
    const amount = Number(payload['transaction_amt'] || 50.0);
    const isHighRisk = Number(payload['is_high_risk_product'] || 0);
    const ratio = Number(payload['amt_vs_card_avg_ratio'] || 1.0);

    // Heuristic simulation calibrated to the Random Forest model's top weights
    let score = (fraudRate * 4.2) + (isHighRisk * 0.15) + (ratio > 2.0 ? 0.25 : 0.0) + (amount > 300 ? 0.2 : 0.0);
    score = Math.max(0.015, Math.min(0.975, score));

    const isFraud = score >= 0.50;
    const riskLevel: RiskLevel = score < 0.20 ? 'LOW' : score < 0.50 ? 'MEDIUM' : score < 0.80 ? 'HIGH' : 'CRITICAL';

    const explanations: ExplanationItem[] = [
      {
        feature: 'card1_historical_fraud_rate',
        value: Number(fraudRate.toFixed(4)),
        contribution: Number((fraudRate * 0.45).toFixed(4)),
        impact: fraudRate > 0.03 ? 'increases_risk' : 'reduces_risk',
        description: 'Historical fraud incidence rate for card identity association.'
      },
      {
        feature: 'amt_vs_card_avg_ratio',
        value: Number(ratio.toFixed(2)),
        contribution: Number((ratio > 1.5 ? 0.12 : -0.05).toFixed(4)),
        impact: ratio > 1.5 ? 'increases_risk' : 'reduces_risk',
        description: 'Deviation ratio of transaction amount from card historical average.'
      },
      {
        feature: 'transaction_amt',
        value: Number(amount.toFixed(2)),
        contribution: Number((amount > 250 ? 0.08 : -0.04).toFixed(4)),
        impact: amount > 250 ? 'increases_risk' : 'reduces_risk',
        description: 'Monetary value of the current transaction.'
      }
    ];

    const recommendations = riskLevel === 'CRITICAL' || riskLevel === 'HIGH' ? [
      'Immediate Action: Hold transaction and route to Senior Fraud Operations.',
      'Enforce Out-of-Band Multi-Factor Authentication (Biometric or OTP).',
      'Verify cardholder recent dispute telemetry and issuing bank records.'
    ] : riskLevel === 'MEDIUM' ? [
      'Apply standard passive 3-D Secure (3DS) authentication check.',
      'Send real-time transaction confirmation alert to cardholder phone.'
    ] : [
      'Approve transaction for automated straight-through processing (STP).',
      'Maintain standard continuous behavioral telemetry logging.'
    ];

    recommendations.push('Operational Advisory: Recommendations are model-guided precautionary actions and do not guarantee prevention.');

    return {
      prediction: isFraud ? 'FRAUD' : 'AUTHENTIC',
      prediction_code: isFraud ? 1 : 0,
      fraud_probability: Number(score.toFixed(4)),
      authentic_probability: Number((1.0 - score).toFixed(4)),
      fraud_probability_percent: `${(score * 100).toFixed(2)}%`,
      authentic_probability_percent: `${((1.0 - score) * 100).toFixed(2)}%`,
      risk_level: riskLevel,
      risk_summary: `[DEMO MODE] ${riskLevel} risk evaluated. (Public static preview: Flask backend is offline).`,
      explanation: explanations,
      recommendations: recommendations,
      metadata: {
        model: 'DEMO MODE (Static GitHub Pages Simulation)',
        algorithm: 'RandomForestClassifier (Simulated Fallback)',
        total_features: 68,
        novelty: 'Tree Explainability + Calibrated Risk Level + Actionable Prevention Engine',
        disclaimer: 'Notice: This prediction was computed in client-side demonstration mode because the Flask ML backend is offline. Live inference requires running `python backend/app.py`.'
      }
    };
  }
}

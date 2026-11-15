/**
 * app.ts
 * Main Angular Component for IEEE-CIS Fraud Detection UI Dashboard
 */

import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PredictionService } from './prediction.service';
import {
  PredictionResponse,
  RiskLevel,
  AUTHENTIC_SAMPLE,
  FRAUD_SAMPLE,
  FEATURE_MEDIANS,
  ALLOWED_CATEGORIES
} from './feature-schema';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App implements OnInit, OnDestroy {
  private predictionService = inject(PredictionService);
  private pollTimer: any = null;

  // Active form section tab
  activeTab: 'core' | 'card' | 'identity' | 'velocity' | 'timing' | 'match' | 'advanced' = 'core';

  // Form values map storing all 68 model features
  formData: Record<string, any> = {};

  // Dropdown options
  categories = ALLOWED_CATEGORIES;

  // System & inference status
  isLoading = false;
  backendOnline = false;
  backendChecking = true;
  backendMessage = 'Checking Flask connection...';
  errorMessage: string | null = null;
  predictionResult: PredictionResponse | null = null;
  isDemoMode = false;
  customBackendUrl = '';
  showBackendConfig = false;

  // Track which preset was selected
  activePreset: 'authentic' | 'fraud' | 'default' = 'authentic';

  ngOnInit(): void {
    this.customBackendUrl = this.predictionService.getBackendUrl();
    this.loadPreset('authentic');
    this.checkHealth();

    // Auto-poll every 3 seconds to immediately detect Flask once started
    this.pollTimer = setInterval(() => {
      if (!this.backendOnline) {
        this.checkHealth();
      }
    }, 3000);
  }

  ngOnDestroy(): void {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
    }
  }

  checkHealth(): void {
    this.backendChecking = true;
    this.predictionService.checkHealth().subscribe({
      next: res => {
        this.backendChecking = false;
        if (res.status === 'ok' && res.model_loaded) {
          this.backendOnline = true;
          this.backendMessage = `Flask ML Backend Active (${res.model_type})`;
          this.isDemoMode = false;
        } else {
          this.backendOnline = false;
          this.backendMessage = 'Flask Backend Offline (Public Demo Mode active)';
          this.isDemoMode = true;
        }
      },
      error: () => {
        this.backendChecking = false;
        this.backendOnline = false;
        this.backendMessage = 'Flask Backend Offline (Public Demo Mode active)';
        this.isDemoMode = true;
      }
    });
  }

  saveCustomBackendUrl(): void {
    this.predictionService.setBackendUrl(this.customBackendUrl);
    this.showBackendConfig = false;
    this.checkHealth();
  }

  clearCustomBackendUrl(): void {
    this.customBackendUrl = '';
    this.predictionService.setBackendUrl('');
    this.showBackendConfig = false;
    this.checkHealth();
  }

  loadPreset(type: 'authentic' | 'fraud' | 'default'): void {
    this.activePreset = type;
    this.errorMessage = null;

    if (type === 'authentic') {
      this.formData = { ...AUTHENTIC_SAMPLE };
    } else if (type === 'fraud') {
      this.formData = { ...FRAUD_SAMPLE };
    } else {
      this.formData = { ...FEATURE_MEDIANS };
      this.formData['product_cd'] = 'W';
      this.formData['card4'] = 'visa';
      this.formData['card6'] = 'debit';
      this.formData['device_type'] = 'desktop';
      this.formData['purchaser_email_domain'] = 'gmail.com';
      this.formData['recipient_email_domain'] = 'missing';
    }

    // Auto-update log_amt if transaction_amt changes
    this.syncLogAmount();
  }

  syncLogAmount(): void {
    const amt = Number(this.formData['transaction_amt'] || 0);
    if (amt >= 0) {
      this.formData['log_amt'] = Number(Math.log(1 + amt).toFixed(4));
    }
  }

  setTab(tab: 'core' | 'card' | 'identity' | 'velocity' | 'timing' | 'match' | 'advanced'): void {
    this.activeTab = tab;
  }

  analyzeTransaction(): void {
    this.errorMessage = null;
    this.isLoading = true;

    // Client-side quick check
    if (this.formData['transaction_amt'] === undefined || this.formData['transaction_amt'] === null || isNaN(Number(this.formData['transaction_amt']))) {
      this.errorMessage = 'Please provide a valid transaction amount.';
      this.isLoading = false;
      return;
    }

    this.predictionService.predict(this.formData, true).subscribe({
      next: (response: PredictionResponse) => {
        this.predictionResult = response;
        this.isLoading = false;
        if (response.metadata.model.includes('DEMO MODE')) {
          this.isDemoMode = true;
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = err.message || 'Prediction failed. Please ensure the backend is running.';
      }
    });
  }

  getRiskBadgeClass(level: RiskLevel): string {
    switch (level) {
      case 'CRITICAL': return 'badge-critical';
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      case 'LOW': return 'badge-low';
      default: return 'badge-neutral';
    }
  }

  getImpactClass(impact: string): string {
    return impact === 'increases_risk' ? 'impact-danger' : 'impact-safe';
  }
}

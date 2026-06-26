/**
 * api.ts
 * -------
 * Thin client for the ClaimSense AI FastAPI backend.
 * All requests go to /api/v1/... and are proxied by Vite dev server
 * (see vite.config.ts) to http://localhost:8000 during development.
 */

import type { ClaimFormData, ReportData, DamagedPart, DecisionType } from './types';

// ─────────────────────────────────────────────────────────────
//  Raw backend response types  (mirrors app/models/schemas.py)
// ─────────────────────────────────────────────────────────────

interface BackendDamagedPart {
  part_name: string;
  severity: string;          // MINOR | MODERATE | SEVERE | TOTAL_LOSS
  damage_description: string;
  confidence: number;
}

interface BackendPartAssessment {
  part_name: string;
  recommended_action: string;
  severity: string;
  justification: string;
}

interface BackendPartEstimate {
  part_name: string;
  action: string;
  parts_cost: number;
  labour_cost: number;
  total_cost: number;
}

interface BackendPolicyClause {
  clause_id: string;
  clause_text: string;
  relevance_score: number;
}

interface BackendResponse {
  claim_id: string;
  status: string;
  vision?: {
    damaged_parts: BackendDamagedPart[];
    overall_severity: string;
    accident_type: string;
    image_quality: string;
    raw_observations: string;
    modifications_detected: {
      modification_type: string;
      description: string;
      claim_impact: string;
      rejection_reason: string;
    }[];
  };
  damage_assessment?: {
    assessments: BackendPartAssessment[];
    overall_damage_category: string;
    total_parts_damaged: number;
    requires_towing: boolean;
    vehicle_drivable: boolean;
    notes: string;
  };
  policy?: {
    policy_number: string;
    policy_type: string;
    damage_covered: boolean;
    coverage_percentage: number;
    deductible_amount: number;
    max_payout: number;
    supporting_clauses: BackendPolicyClause[];
    exclusions_triggered: string[];
    coverage_notes: string;
  };
  repair_estimation?: {
    vehicle_model: string;
    estimates: BackendPartEstimate[];
    subtotal_parts: number;
    subtotal_labour: number;
    grand_total: number;
    currency: string;
    estimation_confidence: number;
    notes: string;
  };
  fraud_risk?: {
    fraud_score: number;           // 0–1 float
    fraud_risk_level: string;      // LOW | MEDIUM | HIGH
    indicators: { indicator: string; description: string; weight: number }[];
    inconsistencies_found: string[];
    reasoning: string;
    recommendation: string;
  };
  decision?: {
    decision: string;              // APPROVE | REJECT | HUMAN_REVIEW
    confidence: number;            // 0–1 float
    approved_amount: number;
    reasons: string[];
    conditions: string[];
    next_steps: string[];
    summary: string;
  };
  processing_errors: string[];
}

// ─────────────────────────────────────────────────────────────
//  Severity mapper
// ─────────────────────────────────────────────────────────────

function mapSeverity(s: string): 'minor' | 'moderate' | 'severe' {
  const upper = s.toUpperCase();
  if (upper === 'MINOR') return 'minor';
  if (upper === 'TOTAL_LOSS') return 'severe';
  if (upper === 'SEVERE') return 'severe';
  return 'moderate';
}

// ─────────────────────────────────────────────────────────────
//  Decision mapper
// ─────────────────────────────────────────────────────────────

function mapDecision(d: string): DecisionType {
  if (d === 'APPROVE') return 'APPROVED';
  if (d === 'REJECT') return 'REJECTED';
  return 'HUMAN REVIEW';
}

// ─────────────────────────────────────────────────────────────
//  Convert backend response → frontend ReportData
// ─────────────────────────────────────────────────────────────

function toReportData(
  raw: BackendResponse,
  claimData: ClaimFormData
): ReportData {
  // Damaged parts — prefer damage_assessment, fall back to vision
  let damagedParts: DamagedPart[] = [];

  if (raw.damage_assessment?.assessments?.length) {
    const repairMap: Record<string, number> = {};
    raw.repair_estimation?.estimates?.forEach((e) => {
      repairMap[e.part_name.toLowerCase()] = e.total_cost;
    });

    damagedParts = raw.damage_assessment.assessments.map((a) => ({
      part: a.part_name,
      severity: mapSeverity(a.severity),
      cost: repairMap[a.part_name.toLowerCase()] ?? 0,
    }));
  } else if (raw.vision?.damaged_parts?.length) {
    damagedParts = raw.vision.damaged_parts.map((p) => ({
      part: p.part_name,
      severity: mapSeverity(p.severity),
      cost: 0,
    }));
  }

  // Policy clauses
  const policyClauses =
    raw.policy?.supporting_clauses?.map(
      (c) => `${c.clause_id} — ${c.clause_text}`
    ) ?? [];
  if (policyClauses.length === 0 && raw.policy?.coverage_notes) {
    policyClauses.push(raw.policy.coverage_notes);
  }

  // Financial figures
  const estimatedRepairCost = raw.repair_estimation?.grand_total ?? 0;
  const deductible = raw.policy?.deductible_amount ?? 0;
  const maxPayout = raw.policy?.max_payout ?? 0;
  const approvedAmount = raw.decision?.approved_amount ?? 0;

  // Fraud score: backend sends 0–1 float, frontend expects 0–100 int
  const fraudScore = Math.round((raw.fraud_risk?.fraud_score ?? 0) * 100);

  // Confidence: backend sends 0–1 float, frontend expects 0–100 int
  const confidenceScore = Math.round((raw.decision?.confidence ?? 0) * 100);

  // Damage summary
  const damageSummary =
    raw.vision?.raw_observations ??
    raw.damage_assessment?.overall_damage_category ??
    'AI analysis complete.';

  return {
    claimNumber: raw.claim_id,
    decision: mapDecision(raw.decision?.decision ?? 'HUMAN_REVIEW'),
    fraudScore,
    confidenceScore,
    estimatedRepairCost,
    coverageAmount: maxPayout,
    deductible,
    damagedParts,
    policyClauses,
    damageSummary,
    vehicleMake: claimData.vehicleMake,
    vehicleModel: claimData.vehicleModel,
    policyNumber: claimData.policyNumber,
    modificationsDetected: raw.vision?.modifications_detected ?? [],
  };
}

// ─────────────────────────────────────────────────────────────
//  Public API function
// ─────────────────────────────────────────────────────────────

export async function submitClaim(claimData: ClaimFormData): Promise<ReportData> {
  const formData = new FormData();

  formData.append('description', claimData.accidentDescription);
  formData.append('policy_number', claimData.policyNumber);
  formData.append('vehicle_model', `${claimData.vehicleMake} ${claimData.vehicleModel}`.trim());

  if (claimData.video) {
    // Video path — backend extracts frames automatically
    formData.append('video', claimData.video);
  } else {
    // Image path
    if (claimData.images.length === 0) {
      throw new Error('At least one image is required.');
    }
    formData.append('image', claimData.images[0]);
  }

  const response = await fetch('/api/v1/claims/process', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Backend error ${response.status}: ${errorText}`);
  }

  const raw: BackendResponse = await response.json();
  return toReportData(raw, claimData);
}

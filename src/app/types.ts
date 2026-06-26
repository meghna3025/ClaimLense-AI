export type ViewType = 'dashboard' | 'new-claim' | 'processing' | 'report' | 'history';

export type DecisionType = 'APPROVED' | 'REJECTED' | 'HUMAN REVIEW';

export type ClaimStatus = 'approved' | 'rejected' | 'review' | 'processing';

export interface ClaimFormData {
  vehicleMake: string;
  vehicleModel: string;
  policyNumber: string;
  accidentDescription: string;
  images: File[];
}

export interface DamagedPart {
  part: string;
  severity: 'minor' | 'moderate' | 'severe';
  cost: number;
}

export interface ReportData {
  claimNumber: string;
  decision: DecisionType;
  fraudScore: number;
  confidenceScore: number;
  estimatedRepairCost: number;
  coverageAmount: number;
  deductible: number;
  damagedParts: DamagedPart[];
  policyClauses: string[];
  damageSummary: string;
  vehicleMake: string;
  vehicleModel: string;
  policyNumber: string;
}

export interface ClaimRecord {
  id: string;
  claimNumber: string;
  vehicleMake: string;
  vehicleModel: string;
  policyNumber: string;
  date: string;
  status: ClaimStatus;
  estimatedCost: number;
  decision: DecisionType;
  fraudScore: number;
  confidence: number;
}

export const MOCK_CLAIMS: ClaimRecord[] = [
  {
    id: '1',
    claimNumber: 'CLM-2025-0847',
    vehicleMake: 'Toyota',
    vehicleModel: 'Camry',
    policyNumber: 'POL-TY-88231',
    date: '2025-06-20',
    status: 'approved',
    estimatedCost: 3250,
    decision: 'APPROVED',
    fraudScore: 4,
    confidence: 94,
  },
  {
    id: '2',
    claimNumber: 'CLM-2025-0831',
    vehicleMake: 'Honda',
    vehicleModel: 'Civic',
    policyNumber: 'POL-HN-44512',
    date: '2025-06-17',
    status: 'rejected',
    estimatedCost: 12800,
    decision: 'REJECTED',
    fraudScore: 78,
    confidence: 88,
  },
  {
    id: '3',
    claimNumber: 'CLM-2025-0815',
    vehicleMake: 'Ford',
    vehicleModel: 'F-150',
    policyNumber: 'POL-FD-20188',
    date: '2025-06-14',
    status: 'review',
    estimatedCost: 6700,
    decision: 'HUMAN REVIEW',
    fraudScore: 42,
    confidence: 61,
  },
  {
    id: '4',
    claimNumber: 'CLM-2025-0798',
    vehicleMake: 'Tesla',
    vehicleModel: 'Model 3',
    policyNumber: 'POL-TS-93011',
    date: '2025-06-10',
    status: 'approved',
    estimatedCost: 8900,
    decision: 'APPROVED',
    fraudScore: 9,
    confidence: 97,
  },
  {
    id: '5',
    claimNumber: 'CLM-2025-0781',
    vehicleMake: 'BMW',
    vehicleModel: '3 Series',
    policyNumber: 'POL-BM-11422',
    date: '2025-06-07',
    status: 'approved',
    estimatedCost: 5100,
    decision: 'APPROVED',
    fraudScore: 6,
    confidence: 92,
  },
  {
    id: '6',
    claimNumber: 'CLM-2025-0762',
    vehicleMake: 'Chevrolet',
    vehicleModel: 'Silverado',
    policyNumber: 'POL-CH-67891',
    date: '2025-06-03',
    status: 'rejected',
    estimatedCost: 22500,
    decision: 'REJECTED',
    fraudScore: 85,
    confidence: 91,
  },
  {
    id: '7',
    claimNumber: 'CLM-2025-0744',
    vehicleMake: 'Audi',
    vehicleModel: 'A4',
    policyNumber: 'POL-AU-33287',
    date: '2025-05-28',
    status: 'approved',
    estimatedCost: 4350,
    decision: 'APPROVED',
    fraudScore: 11,
    confidence: 95,
  },
  {
    id: '8',
    claimNumber: 'CLM-2025-0729',
    vehicleMake: 'Hyundai',
    vehicleModel: 'Tucson',
    policyNumber: 'POL-HY-54001',
    date: '2025-05-22',
    status: 'review',
    estimatedCost: 3900,
    decision: 'HUMAN REVIEW',
    fraudScore: 38,
    confidence: 55,
  },
  {
    id: '9',
    claimNumber: 'CLM-2025-0711',
    vehicleMake: 'Mercedes',
    vehicleModel: 'C-Class',
    policyNumber: 'POL-MB-98234',
    date: '2025-05-16',
    status: 'approved',
    estimatedCost: 7200,
    decision: 'APPROVED',
    fraudScore: 5,
    confidence: 98,
  },
  {
    id: '10',
    claimNumber: 'CLM-2025-0688',
    vehicleMake: 'Nissan',
    vehicleModel: 'Altima',
    policyNumber: 'POL-NS-21456',
    date: '2025-05-09',
    status: 'approved',
    estimatedCost: 2750,
    decision: 'APPROVED',
    fraudScore: 3,
    confidence: 99,
  },
];

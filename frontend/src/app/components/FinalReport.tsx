import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Download,
  PlusCircle,
  Shield,
  Wrench,
  FileText,
  BarChart2,
  Home,
} from 'lucide-react';
import { motion } from 'motion/react';
import type { ViewType, ReportData } from '../types';

interface FinalReportProps {
  report: ReportData | null;
  onNavigate: (view: ViewType) => void;
}

const severityConfig = {
  severe: { color: '#DC2626', bg: '#FEE2E2', label: 'Severe' },
  moderate: { color: '#D97706', bg: '#FEF3C7', label: 'Moderate' },
  minor: { color: '#16A34A', bg: '#DCFCE7', label: 'Minor' },
};

export function FinalReport({ report, onNavigate }: FinalReportProps) {
  if (!report) return null;

  const decisionConfig = {
    APPROVED: {
      icon: CheckCircle,
      color: '#16A34A',
      bg: 'linear-gradient(135deg, #14532D, #16A34A)',
      badge: '#DCFCE7',
      badgeText: '#16A34A',
      glow: 'rgba(22, 163, 74, 0.25)',
      label: 'APPROVED',
      subtitle: 'Claim meets all policy criteria and coverage requirements',
    },
    REJECTED: {
      icon: XCircle,
      color: '#DC2626',
      bg: 'linear-gradient(135deg, #7F1D1D, #DC2626)',
      badge: '#FEE2E2',
      badgeText: '#DC2626',
      glow: 'rgba(220, 38, 38, 0.25)',
      label: 'REJECTED',
      subtitle: 'Claim does not meet policy terms or fraud indicators detected',
    },
    'HUMAN REVIEW': {
      icon: AlertTriangle,
      color: '#D97706',
      bg: 'linear-gradient(135deg, #78350F, #D97706)',
      badge: '#FEF3C7',
      badgeText: '#D97706',
      glow: 'rgba(217, 119, 6, 0.25)',
      label: 'HUMAN REVIEW',
      subtitle: 'Insufficient confidence — escalated to senior claims adjuster',
    },
  };

  const dc = decisionConfig[report.decision];
  const DecisionIcon = dc.icon;

  const fraudData = [{ value: report.fraudScore, fill: report.fraudScore < 30 ? '#22C55E' : report.fraudScore < 60 ? '#F59E0B' : '#EF4444' }];
  const confData = [{ value: report.confidenceScore, fill: '#1976D2' }];

  const netPayout = report.estimatedRepairCost - report.deductible;

  return (
    <div
      className="min-h-full p-6"
      style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('dashboard')}
            className="w-9 h-9 rounded-xl flex items-center justify-center transition-colors"
            style={{ background: '#fff', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}
          >
            <Home className="w-4 h-4 text-gray-600" />
          </button>
          <div>
            <h1 className="text-gray-900" style={{ fontSize: 24, fontWeight: 600 }}>
              Claim Report
            </h1>
            <p className="text-gray-400 text-sm">{report.claimNumber} · AI Decision Report</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('new-claim')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border"
            style={{ borderColor: '#DBEAFE', color: '#1976D2', background: '#EFF6FF' }}
          >
            <PlusCircle className="w-4 h-4" />
            New Claim
          </button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-white"
            style={{
              background: 'linear-gradient(135deg, #1565C0, #1976D2)',
              boxShadow: '0 4px 14px rgba(25, 118, 210, 0.35)',
            }}
          >
            <Download className="w-4 h-4" />
            Download PDF
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Left Column */}
        <div className="col-span-2 space-y-5">
          {/* Decision Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-2xl p-7 text-white relative overflow-hidden"
            style={{
              background: dc.bg,
              boxShadow: `0 8px 32px ${dc.glow}`,
            }}
          >
            {/* Background Decoration */}
            <div
              className="absolute -right-8 -top-8 w-40 h-40 rounded-full opacity-10"
              style={{ background: '#fff' }}
            />
            <div
              className="absolute right-12 bottom-4 w-20 h-20 rounded-full opacity-10"
              style={{ background: '#fff' }}
            />

            <div className="relative flex items-center gap-6">
              <div
                className="w-20 h-20 rounded-2xl flex items-center justify-center shrink-0"
                style={{ background: 'rgba(255,255,255,0.15)' }}
              >
                <DecisionIcon style={{ width: 40, height: 40, color: '#fff' }} />
              </div>
              <div>
                <div
                  className="text-xs font-semibold tracking-widest uppercase mb-1"
                  style={{ color: 'rgba(255,255,255,0.6)' }}
                >
                  AI Decision
                </div>
                <h2 className="text-5xl font-bold tracking-tight mb-2">{dc.label}</h2>
                <p style={{ color: 'rgba(255,255,255,0.75)', fontSize: 14 }}>{dc.subtitle}</p>
              </div>
            </div>

            <div className="relative flex items-center gap-8 mt-6 pt-5 border-t border-white/20">
              <div>
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>Claim Number</div>
                <div className="font-semibold text-sm mt-0.5">{report.claimNumber}</div>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>Vehicle</div>
                <div className="font-semibold text-sm mt-0.5">
                  {report.vehicleMake} {report.vehicleModel}
                </div>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>Policy</div>
                <div className="font-semibold text-sm mt-0.5">{report.policyNumber}</div>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>Est. Repair</div>
                <div className="font-semibold text-sm mt-0.5">
                  ${report.estimatedRepairCost.toLocaleString()}
                </div>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>Net Payout</div>
                <div className="font-semibold text-sm mt-0.5">${netPayout.toLocaleString()}</div>
              </div>
            </div>
          </motion.div>

          {/* Damage Summary */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl p-6"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#FEF3C7' }}>
                <Wrench style={{ width: 18, height: 18, color: '#D97706' }} />
              </div>
              <div>
                <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                  Damage Assessment
                </h3>
                <p className="text-xs text-gray-400">AI Vision-detected damaged components</p>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-5 p-3 rounded-xl" style={{ background: '#F8FAFF', border: '1px solid #DBEAFE' }}>
              {report.damageSummary}
            </p>

            <div className="space-y-3">
              {report.damagedParts.map((part, i) => {
                const sc = severityConfig[part.severity];
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.05 }}
                    className="flex items-center justify-between p-3 rounded-xl"
                    style={{ background: '#F9FAFB', border: '1px solid #F3F4F6' }}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-2 h-8 rounded-full"
                        style={{ background: sc.color }}
                      />
                      <div>
                        <div className="text-sm font-medium text-gray-800">{part.part}</div>
                        <span
                          className="text-xs px-2 py-0.5 rounded-full font-medium"
                          style={{ color: sc.color, background: sc.bg }}
                        >
                          {sc.label}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold text-gray-800">
                        ${part.cost.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-400">est. repair</div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Cost Summary */}
            <div
              className="mt-4 p-4 rounded-xl"
              style={{ background: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)' }}
            >
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500">Total Parts & Labor</span>
                <span className="font-semibold text-gray-800">
                  ${report.estimatedRepairCost.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500">Deductible</span>
                <span className="font-semibold text-red-600">
                  - ${report.deductible.toLocaleString()}
                </span>
              </div>
              <div
                className="flex justify-between text-sm pt-2 border-t"
                style={{ borderColor: '#BFDBFE' }}
              >
                <span className="font-semibold text-gray-700">Insurance Payout</span>
                <span className="font-bold" style={{ color: '#1976D2', fontSize: 16 }}>
                  ${netPayout.toLocaleString()}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Policy Coverage */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl p-6"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#EFF6FF' }}>
                <FileText style={{ width: 18, height: 18, color: '#1976D2' }} />
              </div>
              <div>
                <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                  Supporting Policy Clauses
                </h3>
                <p className="text-xs text-gray-400">Relevant coverage terms applied</p>
              </div>
            </div>
            <div className="space-y-3">
              {report.policyClauses.map((clause, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 + i * 0.05 }}
                  className="flex items-start gap-3 p-3.5 rounded-xl"
                  style={{ background: '#F8FBFF', border: '1px solid #DBEAFE' }}
                >
                  <div
                    className="w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                    style={{ background: '#DBEAFE' }}
                  >
                    <span style={{ fontSize: 10, color: '#1976D2', fontWeight: 700 }}>{i + 1}</span>
                  </div>
                  <p className="text-sm text-gray-600">{clause}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-5">
          {/* Confidence Score */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl p-5"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <h3 className="text-gray-900 text-sm mb-4" style={{ fontWeight: 600 }}>
              AI Confidence Score
            </h3>
            <div className="flex flex-col items-center py-2">
              <div className="relative w-28 h-28">
                <svg width="112" height="112" viewBox="0 0 112 112">
                  <circle
                    cx="56"
                    cy="56"
                    r="44"
                    fill="none"
                    stroke="#F3F4F6"
                    strokeWidth="10"
                  />
                  <motion.circle
                    cx="56"
                    cy="56"
                    r="44"
                    fill="none"
                    stroke="#1976D2"
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 44}`}
                    initial={{ strokeDashoffset: 2 * Math.PI * 44 }}
                    animate={{
                      strokeDashoffset:
                        2 * Math.PI * 44 * (1 - report.confidenceScore / 100),
                    }}
                    transition={{ delay: 0.3, duration: 1.2, ease: 'easeOut' }}
                    transform="rotate(-90 56 56)"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold text-gray-900">{report.confidenceScore}%</span>
                  <span className="text-xs text-gray-400">Confidence</span>
                </div>
              </div>
            </div>
            <div
              className="mt-3 text-center py-2 rounded-xl text-xs font-medium"
              style={{ background: '#EFF6FF', color: '#1976D2' }}
            >
              {report.confidenceScore >= 85 ? 'High Confidence Decision' : report.confidenceScore >= 65 ? 'Moderate Confidence' : 'Low Confidence — Review Recommended'}
            </div>
          </motion.div>

          {/* Fraud Score */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 }}
            className="bg-white rounded-2xl p-5"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <h3 className="text-gray-900 text-sm mb-4" style={{ fontWeight: 600 }}>
              Fraud Detection Score
            </h3>
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl font-bold text-gray-900">{report.fraudScore}</span>
              <span
                className="text-xs px-3 py-1.5 rounded-full font-medium"
                style={
                  report.fraudScore < 30
                    ? { background: '#DCFCE7', color: '#16A34A' }
                    : report.fraudScore < 60
                    ? { background: '#FEF3C7', color: '#D97706' }
                    : { background: '#FEE2E2', color: '#DC2626' }
                }
              >
                {report.fraudScore < 30 ? 'Low Risk' : report.fraudScore < 60 ? 'Moderate Risk' : 'High Risk'}
              </span>
            </div>
            <p className="text-xs text-gray-400 mb-3">out of 100 (lower is better)</p>
            <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{
                  background:
                    report.fraudScore < 30
                      ? 'linear-gradient(90deg, #22C55E, #4ADE80)'
                      : report.fraudScore < 60
                      ? 'linear-gradient(90deg, #F59E0B, #FCD34D)'
                      : 'linear-gradient(90deg, #EF4444, #F87171)',
                }}
                initial={{ width: 0 }}
                animate={{ width: `${report.fraudScore}%` }}
                transition={{ delay: 0.3, duration: 1 }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>No Risk</span>
              <span>High Risk</span>
            </div>
          </motion.div>

          {/* Coverage Summary */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl p-5"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-2 mb-4">
              <Shield style={{ width: 18, height: 18, color: '#1976D2' }} />
              <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                Coverage Analysis
              </h3>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Coverage Limit', value: `$${report.coverageAmount.toLocaleString()}`, color: '#16A34A' },
                { label: 'Repair Estimate', value: `$${report.estimatedRepairCost.toLocaleString()}`, color: '#1976D2' },
                { label: 'Deductible', value: `$${report.deductible.toLocaleString()}`, color: '#D97706' },
                { label: 'Net Insurance Payout', value: `$${netPayout.toLocaleString()}`, color: '#7C3AED' },
              ].map((item) => (
                <div
                  key={item.label}
                  className="flex justify-between items-center p-2.5 rounded-lg"
                  style={{ background: '#F9FAFB' }}
                >
                  <span className="text-xs text-gray-500">{item.label}</span>
                  <span className="text-sm font-semibold" style={{ color: item.color }}>
                    {item.value}
                  </span>
                </div>
              ))}
            </div>

            {/* Coverage bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Claim / Coverage utilization</span>
                <span>{Math.round((report.estimatedRepairCost / report.coverageAmount) * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ background: 'linear-gradient(90deg, #1976D2, #42A5F5)' }}
                  initial={{ width: 0 }}
                  animate={{ width: `${(report.estimatedRepairCost / report.coverageAmount) * 100}%` }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                />
              </div>
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            className="space-y-3"
          >
            <button
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-medium text-sm text-white"
              style={{
                background: 'linear-gradient(135deg, #1565C0, #1976D2)',
                boxShadow: '0 4px 14px rgba(25, 118, 210, 0.35)',
              }}
            >
              <Download className="w-4 h-4" />
              Download Full PDF Report
            </button>
            <button
              onClick={() => onNavigate('history')}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-medium text-sm border"
              style={{ borderColor: '#DBEAFE', color: '#1976D2', background: '#F0F7FF' }}
            >
              <BarChart2 className="w-4 h-4" />
              View Claim History
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

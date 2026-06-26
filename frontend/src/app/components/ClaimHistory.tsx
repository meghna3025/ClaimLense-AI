import React, { useState } from 'react';
import {
  Search,
  Filter,
  ChevronUp,
  ChevronDown,
  Eye,
  Download,
  Car,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  PlusCircle,
  SlidersHorizontal,
} from 'lucide-react';
import { motion } from 'motion/react';
import type { ViewType, ClaimRecord, ClaimStatus, DecisionType } from '../types';
import { MOCK_CLAIMS } from '../types';

interface ClaimHistoryProps {
  onNavigate: (view: ViewType) => void;
}

const statusConfig: Record<ClaimStatus, { label: string; color: string; bg: string; icon: React.ComponentType<{ style?: React.CSSProperties }> }> = {
  approved: { label: 'Approved', color: '#16A34A', bg: '#DCFCE7', icon: CheckCircle },
  rejected: { label: 'Rejected', color: '#DC2626', bg: '#FEE2E2', icon: XCircle },
  review: { label: 'Under Review', color: '#D97706', bg: '#FEF3C7', icon: AlertTriangle },
  processing: { label: 'Processing', color: '#1976D2', bg: '#DBEAFE', icon: Clock },
};

type SortField = 'claimNumber' | 'date' | 'estimatedCost' | 'confidence' | 'fraudScore';
type SortDir = 'asc' | 'desc';

const FILTERS: { label: string; value: string }[] = [
  { label: 'All Claims', value: 'all' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Under Review', value: 'review' },
];

export function ClaimHistory({ onNavigate }: ClaimHistoryProps) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const filtered = MOCK_CLAIMS.filter((c) => {
    const matchesSearch =
      search === '' ||
      c.claimNumber.toLowerCase().includes(search.toLowerCase()) ||
      c.vehicleMake.toLowerCase().includes(search.toLowerCase()) ||
      c.vehicleModel.toLowerCase().includes(search.toLowerCase()) ||
      c.policyNumber.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || c.status === filter;
    return matchesSearch && matchesFilter;
  });

  const sorted = [...filtered].sort((a, b) => {
    let va: number | string = a[sortField];
    let vb: number | string = b[sortField];
    if (sortField === 'date') {
      va = new Date(a.date).getTime();
      vb = new Date(b.date).getTime();
    }
    if (typeof va === 'string' && typeof vb === 'string') {
      return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    }
    return sortDir === 'asc' ? (va as number) - (vb as number) : (vb as number) - (va as number);
  });

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ChevronDown style={{ width: 12, height: 12, opacity: 0.3 }} />;
    return sortDir === 'asc' ? (
      <ChevronUp style={{ width: 12, height: 12, color: '#1976D2' }} />
    ) : (
      <ChevronDown style={{ width: 12, height: 12, color: '#1976D2' }} />
    );
  };

  const totalCost = MOCK_CLAIMS.reduce((s, c) => s + c.estimatedCost, 0);
  const approvedCount = MOCK_CLAIMS.filter((c) => c.status === 'approved').length;
  const rejectedCount = MOCK_CLAIMS.filter((c) => c.status === 'rejected').length;
  const reviewCount = MOCK_CLAIMS.filter((c) => c.status === 'review').length;

  return (
    <div
      className="min-h-full p-6"
      style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-gray-900" style={{ fontSize: 24, fontWeight: 600 }}>
            Claim History
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {MOCK_CLAIMS.length} total claims · AI-processed records
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border"
            style={{ borderColor: '#DBEAFE', color: '#1976D2', background: '#EFF6FF' }}
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onNavigate('new-claim')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-white"
            style={{
              background: 'linear-gradient(135deg, #1565C0, #1976D2)',
              boxShadow: '0 4px 14px rgba(25, 118, 210, 0.35)',
            }}
          >
            <PlusCircle className="w-4 h-4" />
            New Claim
          </motion.button>
        </div>
      </div>

      {/* Summary Stat Row */}
      <div className="grid grid-cols-4 gap-4 mb-5">
        {[
          { label: 'Total Claims', value: MOCK_CLAIMS.length, color: '#1976D2', bg: '#EFF6FF' },
          { label: 'Approved', value: approvedCount, color: '#16A34A', bg: '#DCFCE7' },
          { label: 'Rejected', value: rejectedCount, color: '#DC2626', bg: '#FEE2E2' },
          { label: 'Under Review', value: reviewCount, color: '#D97706', bg: '#FEF3C7' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="bg-white rounded-2xl px-5 py-4 flex items-center justify-between"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
          >
            <div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-xs text-gray-400 mt-0.5">{stat.label}</div>
            </div>
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: stat.bg }}
            >
              <span className="text-lg font-bold" style={{ color: stat.color }}>
                {Math.round((stat.value / MOCK_CLAIMS.length) * 100)}%
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Table Card */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="bg-white rounded-2xl overflow-hidden"
        style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
      >
        {/* Toolbar */}
        <div className="flex items-center justify-between gap-4 px-6 py-4 border-b border-gray-100">
          <div className="relative flex-1 max-w-xs">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              style={{ width: 15, height: 15 }}
            />
            <input
              className="w-full pl-9 pr-4 py-2 rounded-xl text-sm border border-gray-200 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
              placeholder="Search claims, vehicles, policies…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-gray-400" />
            {FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setFilter(f.value)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                style={
                  filter === f.value
                    ? { background: '#1976D2', color: '#fff' }
                    : { background: '#F3F4F6', color: '#6B7280' }
                }
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ background: '#FAFAFA' }}>
                {[
                  { label: 'Claim #', field: 'claimNumber' as SortField },
                  { label: 'Vehicle', field: null },
                  { label: 'Policy', field: null },
                  { label: 'Status', field: null },
                  { label: 'Decision', field: null },
                  { label: 'Est. Cost', field: 'estimatedCost' as SortField },
                  { label: 'Fraud Score', field: 'fraudScore' as SortField },
                  { label: 'Confidence', field: 'confidence' as SortField },
                  { label: 'Date', field: 'date' as SortField },
                  { label: 'Action', field: null },
                ].map((col) => (
                  <th
                    key={col.label}
                    onClick={() => col.field && handleSort(col.field)}
                    className={`text-left px-4 py-3 text-xs font-medium text-gray-400 ${
                      col.field ? 'cursor-pointer hover:text-gray-600' : ''
                    } first:pl-6 last:pr-6`}
                  >
                    <span className="flex items-center gap-1">
                      {col.label}
                      {col.field && <SortIcon field={col.field} />}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-gray-400 text-sm">
                    No claims match your search
                  </td>
                </tr>
              ) : (
                sorted.map((claim, i) => {
                  const s = statusConfig[claim.status];
                  const StatusIcon = s.icon;
                  return (
                    <motion.tr
                      key={claim.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: i * 0.04 }}
                      className="border-t border-gray-50 hover:bg-blue-50/30 transition-colors"
                    >
                      <td className="pl-6 pr-4 py-3.5">
                        <span className="text-sm font-medium text-gray-800">
                          {claim.claimNumber}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                            style={{ background: '#EFF6FF' }}
                          >
                            <Car style={{ width: 13, height: 13, color: '#1976D2' }} />
                          </div>
                          <span className="text-sm text-gray-700 whitespace-nowrap">
                            {claim.vehicleMake} {claim.vehicleModel}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="text-sm text-gray-500 font-mono text-xs">
                          {claim.policyNumber}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span
                          className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full whitespace-nowrap"
                          style={{ color: s.color, background: s.bg }}
                        >
                          <StatusIcon style={{ width: 11, height: 11 }} />
                          {s.label}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span
                          className="text-xs font-semibold px-2.5 py-1 rounded-full"
                          style={
                            claim.decision === 'APPROVED'
                              ? { background: '#DCFCE7', color: '#16A34A' }
                              : claim.decision === 'REJECTED'
                              ? { background: '#FEE2E2', color: '#DC2626' }
                              : { background: '#FEF3C7', color: '#D97706' }
                          }
                        >
                          {claim.decision}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <span className="text-sm font-semibold text-gray-800">
                          ${claim.estimatedCost.toLocaleString()}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-12 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${claim.fraudScore}%`,
                                background:
                                  claim.fraudScore < 30
                                    ? '#22C55E'
                                    : claim.fraudScore < 60
                                    ? '#F59E0B'
                                    : '#EF4444',
                              }}
                            />
                          </div>
                          <span
                            className="text-xs font-medium"
                            style={{
                              color:
                                claim.fraudScore < 30
                                  ? '#16A34A'
                                  : claim.fraudScore < 60
                                  ? '#D97706'
                                  : '#DC2626',
                            }}
                          >
                            {claim.fraudScore}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-12 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${claim.confidence}%`,
                                background:
                                  claim.confidence >= 85
                                    ? '#1976D2'
                                    : claim.confidence >= 65
                                    ? '#F59E0B'
                                    : '#EF4444',
                              }}
                            />
                          </div>
                          <span className="text-xs text-gray-600">{claim.confidence}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="text-xs text-gray-500">
                          {new Date(claim.date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </span>
                      </td>
                      <td className="px-4 pr-6 py-3.5">
                        <div className="flex items-center gap-2">
                          <button
                            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
                            style={{ background: '#EFF6FF', color: '#1976D2' }}
                            title="View"
                          >
                            <Eye style={{ width: 13, height: 13 }} />
                          </button>
                          <button
                            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
                            style={{ background: '#F3F4F6', color: '#6B7280' }}
                            title="Download"
                          >
                            <Download style={{ width: 13, height: 13 }} />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-gray-100">
          <span className="text-xs text-gray-400">
            Showing {sorted.length} of {MOCK_CLAIMS.length} claims
          </span>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>Total portfolio value:</span>
            <span className="font-semibold text-gray-700">
              ${totalCost.toLocaleString()}
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

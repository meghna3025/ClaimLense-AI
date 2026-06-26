import {
  FileText,
  CheckCircle,
  Clock,
  DollarSign,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  PlusCircle,
  Eye,
  Car,
  AlertTriangle,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { motion } from 'motion/react';
import type { ViewType } from '../types';
import { MOCK_CLAIMS } from '../types';

interface DashboardProps {
  onNavigate: (view: ViewType) => void;
}

const monthlyData = [
  { month: 'Jan', claims: 18, approved: 14 },
  { month: 'Feb', claims: 22, approved: 17 },
  { month: 'Mar', claims: 19, approved: 15 },
  { month: 'Apr', claims: 28, approved: 22 },
  { month: 'May', claims: 24, approved: 19 },
  { month: 'Jun', claims: 31, approved: 25 },
  { month: 'Jul', claims: 26, approved: 21 },
  { month: 'Aug', claims: 35, approved: 29 },
  { month: 'Sep', claims: 29, approved: 23 },
  { month: 'Oct', claims: 38, approved: 31 },
  { month: 'Nov', claims: 32, approved: 26 },
  { month: 'Dec', claims: 41, approved: 34 },
];

const pieData = [
  { name: 'Approved', value: 189, color: '#22C55E' },
  { name: 'Rejected', value: 32, color: '#EF4444' },
  { name: 'Under Review', value: 14, color: '#F59E0B' },
  { name: 'Processing', value: 12, color: '#1976D2' },
];

const stats = [
  {
    label: 'Total Claims',
    value: '247',
    change: '+12.4%',
    trend: 'up',
    icon: FileText,
    color: '#1976D2',
    bg: '#E3F2FD',
    sub: 'vs last quarter',
  },
  {
    label: 'Approved Claims',
    value: '189',
    change: '76.5%',
    trend: 'up',
    icon: CheckCircle,
    color: '#16A34A',
    bg: '#DCFCE7',
    sub: 'approval rate',
  },
  {
    label: 'Pending Review',
    value: '14',
    change: '-3',
    trend: 'down',
    icon: Clock,
    color: '#D97706',
    bg: '#FEF3C7',
    sub: 'needs attention',
  },
  {
    label: 'Avg. Repair Cost',
    value: '$4,820',
    change: '+8.2%',
    trend: 'up',
    icon: DollarSign,
    color: '#7C3AED',
    bg: '#EDE9FE',
    sub: 'this quarter',
  },
];

const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  approved: { label: 'Approved', color: '#16A34A', bg: '#DCFCE7' },
  rejected: { label: 'Rejected', color: '#DC2626', bg: '#FEE2E2' },
  review: { label: 'Under Review', color: '#D97706', bg: '#FEF3C7' },
  processing: { label: 'Processing', color: '#1976D2', bg: '#DBEAFE' },
};

export function Dashboard({ onNavigate }: DashboardProps) {
  const recentClaims = MOCK_CLAIMS.slice(0, 5);

  return (
    <div
      className="min-h-full p-6 space-y-6"
      style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-gray-900" style={{ fontSize: 24, fontWeight: 600 }}>
            Claims Dashboard
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Friday, June 26, 2026 · AI-powered claims overview
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onNavigate('new-claim')}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white"
          style={{
            background: 'linear-gradient(135deg, #1565C0, #1976D2)',
            boxShadow: '0 4px 14px rgba(25, 118, 210, 0.35)',
          }}
        >
          <PlusCircle className="w-4 h-4" />
          New Claim
        </motion.button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className="bg-white rounded-2xl p-5"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center"
                style={{ background: stat.bg }}
              >
                <stat.icon style={{ width: 20, height: 20, color: stat.color }} />
              </div>
              <span
                className="flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full"
                style={
                  stat.trend === 'up'
                    ? { color: '#16A34A', background: '#DCFCE7' }
                    : { color: '#DC2626', background: '#FEE2E2' }
                }
              >
                {stat.trend === 'up' ? (
                  <ArrowUpRight style={{ width: 12, height: 12 }} />
                ) : (
                  <ArrowDownRight style={{ width: 12, height: 12 }} />
                )}
                {stat.change}
              </span>
            </div>
            <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
            <div className="text-sm text-gray-500 mt-0.5">{stat.label}</div>
            <div className="text-xs mt-1" style={{ color: stat.color }}>
              {stat.sub}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Area Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="col-span-2 bg-white rounded-2xl p-5"
          style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-gray-900" style={{ fontWeight: 600, fontSize: 16 }}>
                Claims Volume Trend
              </h3>
              <p className="text-gray-400 text-xs mt-0.5">Monthly claims vs. approvals — 2025</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full inline-block" style={{ background: '#BFDBFE' }} />
                Total Claims
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full inline-block" style={{ background: '#1976D2' }} />
                Approved
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={monthlyData} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
              <defs>
                <linearGradient id="colorClaims" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#BFDBFE" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#BFDBFE" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorApproved" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1976D2" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#1976D2" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.12)', fontSize: 12 }}
              />
              <Area type="monotone" dataKey="claims" stroke="#BFDBFE" strokeWidth={2} fill="url(#colorClaims)" />
              <Area type="monotone" dataKey="approved" stroke="#1976D2" strokeWidth={2} fill="url(#colorApproved)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Pie Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-white rounded-2xl p-5"
          style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
        >
          <h3 className="text-gray-900 mb-1" style={{ fontWeight: 600, fontSize: 16 }}>
            Decision Breakdown
          </h3>
          <p className="text-gray-400 text-xs mb-3">Current portfolio distribution</p>
          <ResponsiveContainer width="100%" height={140}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={42}
                outerRadius={62}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.12)', fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ background: item.color }}
                  />
                  <span className="text-gray-500">{item.name}</span>
                </span>
                <span className="font-medium text-gray-700">{item.value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Recent Claims Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-2xl"
        style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h3 className="text-gray-900" style={{ fontWeight: 600, fontSize: 16 }}>
              Recent Claims
            </h3>
            <p className="text-gray-400 text-xs mt-0.5">Latest claim submissions</p>
          </div>
          <button
            onClick={() => onNavigate('history')}
            className="text-sm flex items-center gap-1 font-medium"
            style={{ color: '#1976D2' }}
          >
            View all <ArrowUpRight style={{ width: 14, height: 14 }} />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-gray-400" style={{ background: '#FAFAFA' }}>
                <th className="text-left px-6 py-3 font-medium">Claim #</th>
                <th className="text-left px-4 py-3 font-medium">Vehicle</th>
                <th className="text-left px-4 py-3 font-medium">Policy</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-right px-4 py-3 font-medium">Est. Cost</th>
                <th className="text-center px-4 py-3 font-medium">Confidence</th>
                <th className="text-right px-6 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {recentClaims.map((claim, i) => {
                const s = statusConfig[claim.status];
                return (
                  <tr
                    key={claim.id}
                    className="border-t border-gray-50 hover:bg-blue-50/30 transition-colors"
                  >
                    <td className="px-6 py-3.5">
                      <span className="text-sm font-medium text-gray-800">{claim.claimNumber}</span>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                          style={{ background: '#EFF6FF' }}
                        >
                          <Car style={{ width: 14, height: 14, color: '#1976D2' }} />
                        </div>
                        <span className="text-sm text-gray-700">
                          {claim.vehicleMake} {claim.vehicleModel}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="text-sm text-gray-500">{claim.policyNumber}</span>
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className="text-xs font-medium px-2.5 py-1 rounded-full"
                        style={{ color: s.color, background: s.bg }}
                      >
                        {s.label}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <span className="text-sm font-medium text-gray-800">
                        ₹{claim.estimatedCost.toLocaleString('en-IN')}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${claim.confidence}%`,
                              background: claim.confidence > 85 ? '#22C55E' : claim.confidence > 60 ? '#F59E0B' : '#EF4444',
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{claim.confidence}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() => onNavigate('history')}
                        className="text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
                        style={{ color: '#1976D2', background: '#EFF6FF' }}
                      >
                        <Eye style={{ width: 12, height: 12, display: 'inline', marginRight: 4 }} />
                        View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Quick AI Insights Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45 }}
        className="rounded-2xl p-5 flex items-center justify-between"
        style={{
          background: 'linear-gradient(135deg, #0D1B3E 0%, #1565C0 100%)',
          boxShadow: '0 4px 20px rgba(13,27,62,0.25)',
        }}
      >
        <div className="flex items-center gap-4">
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0"
            style={{ background: 'rgba(255,255,255,0.12)' }}
          >
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">AI Insight · Fraud Alert</div>
            <div className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.65)' }}>
              2 claims flagged for anomalous damage patterns this week. Review recommended before approval.
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium"
            style={{ background: 'rgba(255,255,255,0.15)', color: '#fff' }}
          >
            <AlertTriangle style={{ width: 14, height: 14 }} />
            Review Flagged
          </button>
          <button
            onClick={() => onNavigate('history')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-white"
            style={{ background: 'linear-gradient(135deg, #1976D2, #42A5F5)' }}
          >
            View All <ArrowUpRight style={{ width: 14, height: 14 }} />
          </button>
        </div>
      </motion.div>
    </div>
  );
}

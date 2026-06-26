import React, { useState, useEffect, useRef } from 'react';
import {
  Eye,
  Wrench,
  FileSearch,
  Calculator,
  ShieldAlert,
  Gavel,
  CheckCircle,
  Loader,
  AlertCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import type { ViewType, ClaimFormData, ReportData } from '../types';
import { submitClaim } from '../api';

interface ProcessingScreenProps {
  claimData: ClaimFormData | null;
  onComplete: (report: ReportData) => void;
}

type AgentStatus = 'pending' | 'running' | 'completed' | 'error';

interface AgentDef {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ style?: React.CSSProperties }>;
  /** Simulated duration in ms — used only for the animated progress bar */
  duration: number;
  resultLabel: string;
  color: string;
}

const AGENTS: AgentDef[] = [
  {
    id: 'vision',
    name: 'Vision Agent',
    description: 'Analyzing vehicle damage photographs using Gemini Vision',
    icon: Eye,
    duration: 6000,
    resultLabel: 'Damaged parts detected and classified.',
    color: '#7C3AED',
  },
  {
    id: 'damage',
    name: 'Damage Assessment',
    description: 'Classifying damaged components and severity levels',
    icon: Wrench,
    duration: 5000,
    resultLabel: 'Insurance-standard damage categories assigned.',
    color: '#DC2626',
  },
  {
    id: 'policy',
    name: 'Policy Analysis',
    description: 'RAG search over policy documents for coverage terms',
    icon: FileSearch,
    duration: 5000,
    resultLabel: 'Coverage clauses identified and deductibles applied.',
    color: '#0369A1',
  },
  {
    id: 'estimation',
    name: 'Repair Estimation',
    description: 'Computing repair costs from the repair catalog',
    icon: Calculator,
    duration: 4000,
    resultLabel: 'Parts and labour costs estimated.',
    color: '#059669',
  },
  {
    id: 'fraud',
    name: 'Fraud Detection',
    description: 'Screening for anomalous patterns and inconsistencies',
    icon: ShieldAlert,
    duration: 5000,
    resultLabel: 'Fraud risk score calculated.',
    color: '#D97706',
  },
  {
    id: 'decision',
    name: 'Decision Engine',
    description: 'Synthesising all agent outputs for a final verdict',
    icon: Gavel,
    duration: 3000,
    resultLabel: 'Final claim decision rendered.',
    color: '#1976D2',
  },
];

// Total simulated time including overlaps
const TOTAL_SIM_MS = AGENTS.reduce((s, a) => s + a.duration, 0) + 1200;

export function ProcessingScreen({ claimData, onComplete }: ProcessingScreenProps) {
  const [statuses, setStatuses] = useState<Record<string, AgentStatus>>(() =>
    Object.fromEntries(AGENTS.map((a) => [a.id, 'pending']))
  );
  const [progress, setProgress] = useState<Record<string, number>>(() =>
    Object.fromEntries(AGENTS.map((a) => [a.id, 0]))
  );
  const [allDone, setAllDone] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const apiCalledRef = useRef(false);

  // ── 1. Call the real backend (fire once) ───────────────────
  useEffect(() => {
    if (apiCalledRef.current || !claimData) return;
    apiCalledRef.current = true;

    submitClaim(claimData)
      .then((report) => {
        // Mark all remaining agents complete then navigate
        setStatuses(Object.fromEntries(AGENTS.map((a) => [a.id, 'completed'])));
        setProgress(Object.fromEntries(AGENTS.map((a) => [a.id, 100])));
        setAllDone(true);
        setTimeout(() => onComplete(report), 1600);
      })
      .catch((err: Error) => {
        setApiError(err.message);
      });
  }, [claimData]);

  // ── 2. Animated progress (purely visual, runs in parallel) ─
  useEffect(() => {
    if (apiError) return;
    let cancelled = false;
    let agentIdx = 0;

    const runNext = () => {
      if (cancelled || agentIdx >= AGENTS.length) return;
      const agent = AGENTS[agentIdx];

      setStatuses((prev) => ({ ...prev, [agent.id]: 'running' }));

      const interval = 60;
      const steps = agent.duration / interval;
      let step = 0;

      const timer = setInterval(() => {
        if (cancelled) { clearInterval(timer); return; }
        step++;
        const pct = Math.min(Math.round((step / steps) * 100), 99);
        setProgress((prev) => ({ ...prev, [agent.id]: pct }));

        if (step >= steps) {
          clearInterval(timer);
          // Only mark completed if the agent hasn't been force-completed by API response
          setStatuses((prev) => {
            if (prev[agent.id] === 'running') {
              return { ...prev, [agent.id]: 'completed' };
            }
            return prev;
          });
          setProgress((prev) => ({ ...prev, [agent.id]: 100 }));
          agentIdx++;
          if (agentIdx < AGENTS.length) setTimeout(runNext, 300);
        }
      }, interval);
    };

    const t = setTimeout(runNext, 500);
    return () => { cancelled = true; clearTimeout(t); };
  }, [apiError]);

  const completedCount = Object.values(statuses).filter((s) => s === 'completed').length;
  const overallPct = Math.round((completedCount / AGENTS.length) * 100);

  // ── Error state ─────────────────────────────────────────────
  if (apiError) {
    return (
      <div
        className="min-h-full flex flex-col items-center justify-center p-6"
        style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
      >
        <div className="w-full max-w-md text-center">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
            style={{ background: '#FEE2E2' }}
          >
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-gray-900 text-xl font-semibold mb-2">Processing Failed</h2>
          <p className="text-sm text-gray-500 mb-6 px-4">{apiError}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => window.location.reload()}
              className="px-5 py-2.5 rounded-xl text-sm font-medium text-white"
              style={{ background: 'linear-gradient(135deg, #1565C0, #1976D2)' }}
            >
              Try Again
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-4">
            Make sure the backend server is running on port 8000 and your GEMINI_API_KEY is set.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-full flex flex-col items-center justify-center p-6"
      style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
    >
      <div className="w-full max-w-2xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
            style={{
              background: 'linear-gradient(135deg, #0D1B3E, #1976D2)',
              boxShadow: '0 8px 24px rgba(25, 118, 210, 0.35)',
            }}
          >
            <motion.div
              animate={{ rotate: allDone ? 0 : 360 }}
              transition={
                allDone
                  ? { duration: 0.3 }
                  : { repeat: Infinity, duration: 3, ease: 'linear' }
              }
            >
              {allDone ? (
                <CheckCircle className="w-7 h-7 text-white" />
              ) : (
                <Loader className="w-7 h-7 text-white" />
              )}
            </motion.div>
          </div>
          <h1 className="text-gray-900 mb-2" style={{ fontSize: 24, fontWeight: 600 }}>
            {allDone ? 'Analysis Complete' : 'AI Agents Processing Claim'}
          </h1>
          <p className="text-gray-500 text-sm">
            {allDone
              ? 'All agents completed. Loading final report…'
              : `Analyzing ${claimData?.vehicleMake ?? ''} ${claimData?.vehicleModel ?? ''} · Policy ${claimData?.policyNumber ?? ''}`}
          </p>
        </motion.div>

        {/* Overall Progress */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl px-6 py-4 mb-5"
          style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className="text-sm font-semibold" style={{ color: '#1976D2' }}>
              {completedCount} / {AGENTS.length} agents complete
            </span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: 'linear-gradient(90deg, #1565C0, #42A5F5)' }}
              animate={{ width: `${overallPct}%` }}
              transition={{ duration: 0.4 }}
            />
          </div>
          <div className="flex justify-between mt-1.5">
            <span className="text-xs text-gray-400">
              {allDone ? 'All agents done — generating report…' : 'Processing via Gemini AI…'}
            </span>
            <span className="text-xs font-medium text-gray-600">{overallPct}%</span>
          </div>
        </motion.div>

        {/* Agent Cards */}
        <div className="space-y-3">
          {AGENTS.map((agent, idx) => {
            const status = statuses[agent.id];
            const pct = progress[agent.id];
            const isRunning = status === 'running';
            const isCompleted = status === 'completed';
            const isPending = status === 'pending';

            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.06 }}
                className="bg-white rounded-2xl p-5 transition-all"
                style={{
                  boxShadow: isRunning
                    ? '0 4px 20px rgba(25, 118, 210, 0.15), 0 1px 3px rgba(0,0,0,0.08)'
                    : '0 1px 3px rgba(0,0,0,0.06)',
                  border: isRunning
                    ? '1px solid rgba(25, 118, 210, 0.2)'
                    : '1px solid transparent',
                }}
              >
                <div className="flex items-center gap-4">
                  {/* Icon */}
                  <div
                    className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                    style={{
                      background: isCompleted
                        ? '#DCFCE7'
                        : isRunning
                        ? `${agent.color}18`
                        : '#F3F4F6',
                    }}
                  >
                    {isCompleted ? (
                      <CheckCircle style={{ width: 20, height: 20, color: '#16A34A' }} />
                    ) : isRunning ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
                      >
                        <agent.icon style={{ width: 20, height: 20, color: agent.color }} />
                      </motion.div>
                    ) : (
                      <agent.icon style={{ width: 20, height: 20, color: '#9CA3AF' }} />
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span
                        className="text-sm"
                        style={{ fontWeight: 600, color: isPending ? '#9CA3AF' : '#111827' }}
                      >
                        {agent.name}
                      </span>
                      <span
                        className="text-xs px-2.5 py-1 rounded-full font-medium"
                        style={
                          isCompleted
                            ? { background: '#DCFCE7', color: '#16A34A' }
                            : isRunning
                            ? { background: '#DBEAFE', color: '#1976D2' }
                            : { background: '#F3F4F6', color: '#9CA3AF' }
                        }
                      >
                        {isCompleted ? '✓ Completed' : isRunning ? '⚡ Running' : '· Pending'}
                      </span>
                    </div>

                    <p className="text-xs text-gray-400 mt-0.5 truncate">
                      {isCompleted ? agent.resultLabel : agent.description}
                    </p>

                    {(isRunning || isCompleted) && (
                      <div className="mt-2">
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <motion.div
                            className="h-full rounded-full"
                            style={{
                              background: isCompleted
                                ? 'linear-gradient(90deg, #16A34A, #4ADE80)'
                                : `linear-gradient(90deg, ${agent.color}, ${agent.color}88)`,
                            }}
                            animate={{ width: `${pct}%` }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                        <div className="flex justify-end mt-0.5">
                          <span className="text-xs text-gray-400">{pct}%</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Step number */}
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-xs font-bold"
                    style={
                      isCompleted
                        ? { background: '#DCFCE7', color: '#16A34A' }
                        : isRunning
                        ? { background: '#1976D2', color: '#fff' }
                        : { background: '#F3F4F6', color: '#9CA3AF' }
                    }
                  >
                    {idx + 1}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Completion banner */}
        <AnimatePresence>
          {allDone && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-5 rounded-2xl p-4 flex items-center gap-3"
              style={{
                background: 'linear-gradient(135deg, #0D1B3E, #1565C0)',
                boxShadow: '0 4px 20px rgba(25, 118, 210, 0.3)',
              }}
            >
              <CheckCircle className="w-5 h-5 text-white shrink-0" />
              <p className="text-sm text-white">
                All 6 agents completed successfully. Loading final report…
              </p>
              <motion.div
                className="ml-auto w-4 h-4 border-2 border-white/30 border-t-white rounded-full shrink-0"
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

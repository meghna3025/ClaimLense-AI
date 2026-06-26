import React, { useState, useEffect } from 'react';
import {
  Eye,
  Wrench,
  FileSearch,
  Calculator,
  ShieldAlert,
  Gavel,
  CheckCircle,
  Loader,
  Clock,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import type { ViewType, ClaimFormData, ReportData, DamagedPart } from '../types';

interface ProcessingScreenProps {
  claimData: ClaimFormData | null;
  onComplete: (report: ReportData) => void;
}

type AgentStatus = 'pending' | 'running' | 'completed';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ style?: React.CSSProperties }>;
  duration: number;
  result?: string;
  color: string;
}

const AGENTS: Agent[] = [
  {
    id: 'vision',
    name: 'Vision Agent',
    description: 'Analyzing vehicle damage photographs using computer vision',
    icon: Eye,
    duration: 3200,
    result: 'Detected 4 damage zones across front and side panels. Crumple deformation noted.',
    color: '#7C3AED',
  },
  {
    id: 'damage',
    name: 'Damage Assessment',
    description: 'Classifying damaged components and severity levels',
    icon: Wrench,
    duration: 2800,
    result: 'Front bumper: Severe · Hood: Moderate · Driver fender: Moderate · Headlight: Severe',
    color: '#DC2626',
  },
  {
    id: 'policy',
    name: 'Policy Analysis',
    description: 'Cross-referencing coverage terms against claim details',
    icon: FileSearch,
    duration: 2500,
    result: 'Comprehensive coverage active. Collision clause §4.2 applicable. Deductible: $500.',
    color: '#0369A1',
  },
  {
    id: 'estimation',
    name: 'Repair Estimation',
    description: 'Computing repair costs using market pricing data',
    icon: Calculator,
    duration: 2200,
    result: 'Total estimate: $6,840. OEM parts: $4,120. Labor: $2,720. Within coverage limit.',
    color: '#059669',
  },
  {
    id: 'fraud',
    name: 'Fraud Detection',
    description: 'Screening for anomalous patterns and prior claim history',
    icon: ShieldAlert,
    duration: 2600,
    result: 'No suspicious patterns detected. Fraud score: 8/100. Policy history: Clean.',
    color: '#D97706',
  },
  {
    id: 'decision',
    name: 'Decision Engine',
    description: 'Rendering final recommendation based on all agent outputs',
    icon: Gavel,
    duration: 1800,
    result: 'Recommendation: APPROVED — All criteria met with 94% confidence.',
    color: '#1976D2',
  },
];

function generateReport(claimData: ClaimFormData | null): ReportData {
  const damagedParts: DamagedPart[] = [
    { part: 'Front Bumper', severity: 'severe', cost: 1200 },
    { part: 'Hood', severity: 'moderate', cost: 800 },
    { part: 'Driver-side Fender', severity: 'moderate', cost: 650 },
    { part: 'Left Headlight Assembly', severity: 'severe', cost: 420 },
    { part: 'Radiator Support', severity: 'minor', cost: 380 },
    { part: 'Airbag Sensor Replacement', severity: 'minor', cost: 290 },
  ];
  return {
    claimNumber: `CLM-2026-${String(Math.floor(Math.random() * 900) + 100).padStart(4, '0')}`,
    decision: 'APPROVED',
    fraudScore: 8,
    confidenceScore: 94,
    estimatedRepairCost: 6840,
    coverageAmount: 50000,
    deductible: 500,
    damagedParts,
    policyClauses: [
      'Section 4.2 — Collision Coverage: Covers damage resulting from collision with another vehicle or object.',
      'Section 7.1 — OEM Parts: Policyholder entitled to manufacturer-certified replacement parts.',
      'Section 9.3 — Rental Reimbursement: Up to $50/day for 30 days during repair.',
    ],
    damageSummary:
      'Significant front-end collision damage consistent with frontal impact at moderate speed. Structural components show controlled crumple zone deformation. No evidence of pre-existing damage or staged incident.',
    vehicleMake: claimData?.vehicleMake ?? 'Toyota',
    vehicleModel: claimData?.vehicleModel ?? 'Camry',
    policyNumber: claimData?.policyNumber ?? 'POL-DEMO-001',
  };
}

export function ProcessingScreen({ claimData, onComplete }: ProcessingScreenProps) {
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>(() =>
    Object.fromEntries(AGENTS.map((a) => [a.id, 'pending']))
  );
  const [agentProgress, setAgentProgress] = useState<Record<string, number>>(() =>
    Object.fromEntries(AGENTS.map((a) => [a.id, 0]))
  );
  const [currentAgentIndex, setCurrentAgentIndex] = useState(-1);
  const [allDone, setAllDone] = useState(false);

  useEffect(() => {
    let agentIdx = 0;
    let cancelled = false;

    const runNextAgent = () => {
      if (cancelled || agentIdx >= AGENTS.length) return;

      const agent = AGENTS[agentIdx];
      setCurrentAgentIndex(agentIdx);
      setAgentStatuses((prev) => ({ ...prev, [agent.id]: 'running' }));

      const progressInterval = 50;
      const steps = agent.duration / progressInterval;
      let step = 0;

      const progressTimer = setInterval(() => {
        if (cancelled) {
          clearInterval(progressTimer);
          return;
        }
        step++;
        const progress = Math.min(Math.round((step / steps) * 100), 99);
        setAgentProgress((prev) => ({ ...prev, [agent.id]: progress }));
        if (step >= steps) {
          clearInterval(progressTimer);
          setAgentProgress((prev) => ({ ...prev, [agent.id]: 100 }));
          setAgentStatuses((prev) => ({ ...prev, [agent.id]: 'completed' }));
          agentIdx++;
          if (agentIdx < AGENTS.length) {
            setTimeout(runNextAgent, 300);
          } else {
            if (!cancelled) {
              setAllDone(true);
              setTimeout(() => {
                if (!cancelled) onComplete(generateReport(claimData));
              }, 1800);
            }
          }
        }
      }, progressInterval);
    };

    const startTimeout = setTimeout(runNextAgent, 600);

    return () => {
      cancelled = true;
      clearTimeout(startTimeout);
    };
  }, []);

  const totalCompleted = Object.values(agentStatuses).filter((s) => s === 'completed').length;
  const overallProgress = Math.round((totalCompleted / AGENTS.length) * 100);

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
                allDone ? { duration: 0.3 } : { repeat: Infinity, duration: 3, ease: 'linear' }
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
              ? 'All agents have completed analysis. Generating final report…'
              : `Analyzing ${claimData?.vehicleMake} ${claimData?.vehicleModel} · Policy ${claimData?.policyNumber}`}
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
              {totalCompleted} / {AGENTS.length} agents complete
            </span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: 'linear-gradient(90deg, #1565C0, #42A5F5)' }}
              initial={{ width: 0 }}
              animate={{ width: `${overallProgress}%` }}
              transition={{ duration: 0.4 }}
            />
          </div>
          <div className="flex justify-between mt-1.5">
            <span className="text-xs text-gray-400">Processing…</span>
            <span className="text-xs font-medium text-gray-600">{overallProgress}%</span>
          </div>
        </motion.div>

        {/* Agent Cards */}
        <div className="space-y-3">
          {AGENTS.map((agent, idx) => {
            const status = agentStatuses[agent.id];
            const progress = agentProgress[agent.id];
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
                    ? `0 4px 20px rgba(25, 118, 210, 0.15), 0 1px 3px rgba(0,0,0,0.08)`
                    : '0 1px 3px rgba(0,0,0,0.06)',
                  border: isRunning ? '1px solid rgba(25, 118, 210, 0.2)' : '1px solid transparent',
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
                        style={{
                          fontWeight: 600,
                          color: isPending ? '#9CA3AF' : '#111827',
                        }}
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
                      {isCompleted ? agent.result : agent.description}
                    </p>

                    {/* Progress Bar */}
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
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                        <div className="flex justify-end mt-0.5">
                          <span className="text-xs text-gray-400">{progress}%</span>
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

        {/* Completion Message */}
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

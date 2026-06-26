import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { NewClaimForm } from './components/NewClaimForm';
import { ProcessingScreen } from './components/ProcessingScreen';
import { FinalReport } from './components/FinalReport';
import { ClaimHistory } from './components/ClaimHistory';
import type { ViewType, ClaimFormData, ReportData } from './types';

export default function App() {
  const [view, setView] = useState<ViewType>('dashboard');
  const [claimData, setClaimData] = useState<ClaimFormData | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);

  const navigateTo = (newView: ViewType, data?: ClaimFormData) => {
    if (data) setClaimData(data);
    setView(newView);
  };

  const handleProcessingComplete = (report: ReportData) => {
    setReportData(report);
    setView('report');
  };

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ fontFamily: "'Roboto', 'Google Sans', sans-serif" }}
    >
      <Sidebar currentView={view} onNavigate={navigateTo} />

      <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={view}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="min-h-full"
          >
            {view === 'dashboard' && <Dashboard onNavigate={navigateTo} />}
            {view === 'new-claim' && <NewClaimForm onNavigate={navigateTo} />}
            {view === 'processing' && (
              <ProcessingScreen
                claimData={claimData}
                onComplete={handleProcessingComplete}
              />
            )}
            {view === 'report' && (
              <FinalReport report={reportData} onNavigate={navigateTo} />
            )}
            {view === 'history' && <ClaimHistory onNavigate={navigateTo} />}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

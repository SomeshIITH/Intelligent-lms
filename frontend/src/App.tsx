import React, { useState } from 'react';
import { LayoutDashboard, BookOpen, Brain, Map, BarChart3, GraduationCap } from 'lucide-react';
import { UploadSection } from './components/UploadSection';
import { ChatSection } from './components/ChatSection';
import { QuizSection } from './components/QuizSection';
import { RoadmapSection } from './components/RoadmapSection';
import { AnalyticsSection } from './components/AnalyticsSection';
import { logger } from './utils/logger';

const CONTEXT = 'APP_ROOT';
type ActiveTab = 'chat' | 'quiz' | 'roadmap' | 'analytics';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);

  const handleUploadSuccess = (filename: string) => {
    logger.info(CONTEXT, `Root tracking state synchronized with new active context: ${filename}`);
    setUploadedFilename(filename);
  };

  const navItems = [
    { id: 'chat', label: 'RAG AI Tutor', icon: BookOpen },
    { id: 'quiz', label: 'Assessment Center', icon: Brain },
    { id: 'roadmap', label: 'Curriculum Path', icon: Map },
    { id: 'analytics', label: 'Telemetry Analytics', icon: BarChart3 },
  ] as const;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Central Application Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-slate-900 text-white p-2 rounded-xl shadow-md">
              <GraduationCap className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-slate-900 tracking-tight leading-none">
                Intelligent LMS Workspace
              </h1>
              <p className="text-[11px] text-slate-400 font-medium mt-1">
                Multi-Agent Academic Co-Pilot Framework
              </p>
            </div>
          </div>

          {uploadedFilename && (
            <div className="hidden sm:flex items-center gap-2 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-lg">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-slate-600 font-mono font-medium max-w-[200px] truncate" title={uploadedFilename}>
                Context: {uploadedFilename}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main Workspace Frame */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Hand Column: Control Panels & Navigation Elements */}
        <section className="lg:col-span-4 space-y-6">
          {/* Document Context Ingestion Subsystem */}
          <UploadSection onUploadSuccess={handleUploadSuccess} />

          {/* Navigation Control Deck */}
          <nav className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-1">
            <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase px-3 mb-2 font-mono">
              Agent Control Deck
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    logger.debug(CONTEXT, `Switching active workspace layout target to: ${item.id}`);
                    setActiveTab(item.id);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer group ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`h-4 w-4 shrink-0 transition-colors ${
                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'
                  }`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </section>

        {/* Right Hand Column: Active Agent Workflow Viewport */}
        <section className="lg:col-span-8">
          <div className="h-full">
            {activeTab === 'chat' && <ChatSection />}
            {activeTab === 'quiz' && <QuizSection />}
            {activeTab === 'roadmap' && <RoadmapSection />}
            {activeTab === 'analytics' && <AnalyticsSection />}
          </div>
        </section>

      </main>
    </div>
  );
}
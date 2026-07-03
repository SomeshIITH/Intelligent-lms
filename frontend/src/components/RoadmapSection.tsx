import React, { useState } from 'react';
import { Map, Milestone, Clock, BookOpen, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import type { RoadmapMilestone } from '../types';

const CONTEXT = 'ROADMAP_COMPONENT';

export const RoadmapSection: React.FC = () => {
  const [milestones, setMilestones] = useState<RoadmapMilestone[]>([]);
  const [summary, setSummary] = useState<string>('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const generateCurriculumRoadmap = async () => {
    setStatus('loading');
    setErrorMessage('');
    logger.info(CONTEXT, 'Requesting optimized learning sequence from CurriculumAgent.');

    try {
      const response = await apiService.fetchRoadmap() as any; // Cast to bypass rigid field schema locks during parsing
      
      // Look for the array values inside any potential nested schema envelopes
      const rawMilestones = response.sequenced_milestones || response.milestones || (response.data && response.data.milestones);
      const rawSummary = response.document_outline_summary || response.summary || (response.data && response.data.summary);

      if (response.success && rawMilestones && rawMilestones.length > 0) {
        // Safe mapping translation layer to protect interface schema integrity
        const normalizedMilestones: RoadmapMilestone[] = rawMilestones.map((ms: any, idx: number) => ({
          milestone_number: ms.milestone_number || ms.id || (idx + 1),
          core_concept_title: ms.core_concept_title || ms.title || ms.concept || 'Key Milestone Topic',
          depth_explanation: ms.depth_explanation || ms.description || ms.explanation || 'No depth overview supplied.',
          estimated_study_minutes: ms.estimated_study_minutes || ms.duration || ms.minutes || 15,
          source_page_references: ms.source_page_references || ms.pages || ms.references || []
        }));

        logger.info(CONTEXT, `Curriculum path synthesized successfully with ${normalizedMilestones.length} milestones.`);
        setMilestones(normalizedMilestones);
        setSummary(rawSummary || 'Document executive outline parsed successfully.');
        setStatus('success');
      } else {
        throw new Error(response.message || 'CurriculumAgent returned an empty or unparsable structural architecture.');
      }
    } catch (err: any) {
      const msg = err.message || 'Failed to draw chronological curriculum paths from vector index stores.';
      logger.error(CONTEXT, 'Curriculum processing sequence encountered an execution error.', err);
      setErrorMessage(msg);
      setStatus('error');
    }
  };

  if (status === 'idle') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm text-center flex flex-col items-center justify-center max-w-xl mx-auto my-6">
        <div className="bg-emerald-50 p-4 rounded-full border border-emerald-100 text-emerald-600 mb-4">
          <Map className="h-10 w-10" />
        </div>
        <h3 className="text-xl font-bold text-slate-800 tracking-tight">Structured Knowledge Roadmap</h3>
        <p className="text-sm text-slate-500 mt-2 mb-6 max-w-sm">
          Let the CurriculumAgent run a topological sort across your material contexts to trace an optimized chronological study path.
        </p>
        <button
          onClick={generateCurriculumRoadmap}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors cursor-pointer flex items-center gap-2 text-sm"
        >
          Generate Curriculum Roadmap
        </button>
      </div>
    );
  }

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 shadow-sm text-center flex flex-col items-center justify-center min-h-[300px]">
        <Loader2 className="h-10 w-10 text-emerald-600 animate-spin mb-4" />
        <h4 className="font-bold text-slate-800">Synthesizing Sequential Milestones...</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-xs">
          CurriculumAgent is structuring concepts linearly based on core dependencies. This could take up to 20 seconds.
        </p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm max-w-xl mx-auto my-6">
        <div className="flex items-start gap-3 bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block text-base mb-1">Curriculum Engine Error</span>
            <p className="leading-relaxed">{errorMessage}</p>
          </div>
        </div>
        <button
          onClick={generateCurriculumRoadmap}
          className="mt-4 w-full bg-slate-900 text-white font-medium py-2 px-4 rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 text-sm cursor-pointer"
        >
          <RefreshCw className="h-4 w-4" />
          Retry Sequence Processing
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto my-2">
      {summary && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider font-mono mb-2">Document Context Executive Summary</h4>
          <p className="text-sm text-slate-600 leading-relaxed">{summary}</p>
        </div>
      )}

      <div className="relative border-l border-slate-200 ml-4 space-y-6">
        {milestones.map((milestone, idx) => (
          <div key={idx} className="relative pl-8 group">
            {/* Chronological Milestone Bullet Anchor Marker */}
            <div className="absolute -left-[13px] top-1.5 bg-white border-2 border-emerald-500 rounded-full h-6 w-6 flex items-center justify-center shadow-sm group-hover:bg-emerald-50 transition-colors">
              <Milestone className="h-3 w-3 text-emerald-600" />
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                <span className="text-xs font-bold font-mono text-emerald-600 uppercase bg-emerald-50 px-2.5 py-1 rounded-md">
                  Milestone #{milestone.milestone_number}
                </span>
                <div className="flex items-center gap-4 text-xs font-semibold text-slate-400">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5 text-slate-400" />
                    <span>Est: {milestone.estimated_study_minutes} mins</span>
                  </div>
                  {milestone.source_page_references && milestone.source_page_references.length > 0 && (
                    <div className="flex items-center gap-1">
                      <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                      <span>Pages: {milestone.source_page_references.join(', ')}</span>
                    </div>
                  )}
                </div>
              </div>

              <h3 className="text-base font-bold text-slate-800 leading-tight mb-2">
                {milestone.core_concept_title}
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {milestone.depth_explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
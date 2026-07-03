import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, Target, Loader2, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import type { AnalyticsDataPayload } from '../types/index';

const CONTEXT = 'ANALYTICS_COMPONENT';

export const AnalyticsSection: React.FC = () => {
  const [data, setData] = useState<AnalyticsDataPayload | null>(null);
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const fetchAnalytics = async () => {
    setStatus('loading');
    logger.info(CONTEXT, 'Initiating telemetry aggregation from AnalyticsAgent.');

    try {
      const response = await apiService.fetchAnalytics();
      if (response.success && response.data) {
        logger.info(CONTEXT, 'Telemetry analytics matrix retrieved successfully.');
        setData(response.data);
        setStatus('success');
      } else {
        throw new Error(response.message || 'AnalyticsAgent returned invalid telemetry state.');
      }
    } catch (err: any) {
      const msg = err.message || 'Network crash encountered while streaming metric data.';
      logger.error(CONTEXT, 'Analytics streaming sequence encountered execution error.', err);
      setErrorMessage(msg);
      setStatus('error');
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (status === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center h-[400px]">
        <Loader2 className="h-10 w-10 text-indigo-600 animate-spin mb-4" />
        <p className="text-slate-500 font-medium">Aggregating historical learning telemetry...</p>
      </div>
    );
  }

  if (status === 'error' || !data) {
    return (
      <div className="bg-red-50 border border-red-200 p-6 rounded-xl text-center">
        <AlertTriangle className="h-10 w-10 text-red-500 mx-auto mb-3" />
        <h4 className="font-bold text-red-800">Telemetry Stream Error</h4>
        <p className="text-sm text-red-600 mt-1 mb-4">{errorMessage}</p>
        <button 
          onClick={fetchAnalytics}
          className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors flex items-center gap-2 mx-auto"
        >
          <RefreshCw className="h-4 w-4" /> Retry Aggregation
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Score Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2 opacity-90">
            <Target className="h-5 w-5" />
            <span className="font-semibold text-sm">Overall Mastery Score</span>
          </div>
          <div className="text-4xl font-extrabold tracking-tighter">{data.overall_score}%</div>
          <p className="text-indigo-100 text-xs mt-1">Based on {data.quizzes_taken} total evaluation attempts.</p>
        </div>
        
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-600" /> Topic Mastery Matrix
          </h3>
          <div className="space-y-3">
            {data.topic_breakdown.map((topic, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-600">{topic.topic_context}</span>
                  <span className="font-bold text-slate-900">{topic.calculated_mastery_percentage}%</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-500 rounded-full" 
                    style={{ width: `${topic.calculated_mastery_percentage}%` }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-6">
          <h4 className="font-bold text-emerald-900 mb-3 text-sm">Core Proficiencies</h4>
          <ul className="space-y-2">
            {data.strengths.map((s, i) => (
              <li key={i} className="text-sm text-emerald-800 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-6">
          <h4 className="font-bold text-amber-900 mb-3 text-sm">Concept Gaps</h4>
          <ul className="space-y-2">
            {data.weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-amber-800 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Remediation */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h4 className="font-bold text-slate-800 mb-2">Agent-Recommended Remediation Plan</h4>
        <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
          {data.remediation_plan}
        </p>
      </div>
    </div>
  );
};
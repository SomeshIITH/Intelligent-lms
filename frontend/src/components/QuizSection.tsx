import React, { useState } from 'react';
import { HelpCircle, Brain, Check, X, ArrowRight, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import type { QuizItem } from '../types';

const CONTEXT = 'QUIZ_COMPONENT';

export const QuizSection: React.FC = () => {
  const [quizItems, setQuizItems] = useState<QuizItem[]>([]);
  const [topicContext, setTopicContext] = useState<string>('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'active' | 'completed' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  
  // Evaluation state matrices
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, 'A' | 'B' | 'C' | 'D'>>({});
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [score, setScore] = useState<number>(0);

  const startQuizGeneration = async () => {
    setStatus('loading');
    setErrorMessage('');
    logger.info(CONTEXT, 'Requesting dynamic evaluation package synthesis from AssessorAgent');

    try {
      const response = await apiService.fetchQuiz() as any; // Cast temporarily to safely map flexible keys
      
      // Adapt dynamically to whether the backend named the array 'quiz_items' or 'questions'
      const extractedItems = response.quiz_items || response.questions || (response.data && response.data.questions);

      if (response.success && extractedItems && extractedItems.length > 0) {
        // Map backend properties safely to match what our UI renders
        const normalizedItems = extractedItems.map((item: any, idx: number) => ({
          question_number: item.question_number || item.id || (idx + 1),
          conceptual_question: item.conceptual_question || item.question,
          options: item.options,
          correct_option: item.correct_option || item.correct_answer || item.answer,
          detailed_justification: item.detailed_justification || item.explanation || item.justification || 'Contextually verified.'
        }));

        logger.info(CONTEXT, `Quiz generation complete. Normalized ${normalizedItems.length} items.`);
        setQuizItems(normalizedItems);
        setTopicContext(response.topic_context || 'DeepSeek-MoE Architecture Analysis');
        setCurrentIndex(0);
        setSelectedAnswers({});
        setIsSubmitted(false);
        setScore(0);
        setStatus('active');
      } else {
        throw new Error(response.message || 'AssessorAgent generated an unparsable layout frame.');
      }
    } catch (err: any) {
      const msg = err.message || 'Failed to draw structural evaluations from system memory stores.';
      logger.error(CONTEXT, 'Evaluation generation sequence crashed.', err);
      setErrorMessage(msg);
      setStatus('error');
    }
  };

  const selectOption = (option: 'A' | 'B' | 'C' | 'D') => {
    if (isSubmitted) return;
    setSelectedAnswers({ ...selectedAnswers, [currentIndex]: option });
  };

  const handleNextStep = () => {
    if (currentIndex < quizItems.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      // Finalize evaluation tracking logic loop
      let calculatedScore = 0;
      quizItems.forEach((item, idx) => {
        if (selectedAnswers[idx] === item.correct_option) {
          calculatedScore++;
        }
      });
      
      setScore(calculatedScore);
      setIsSubmitted(true);
      setStatus('completed');
      
      logger.info(CONTEXT, `Evaluation completed. Score logged: ${calculatedScore}/${quizItems.length}`);
      
      // Fire-and-forget telemetry push to background services
      apiService.submitQuizScore(calculatedScore, quizItems.length, topicContext)
        .then(() => logger.info(CONTEXT, 'Telemetry analytics matrix dispatched safely.'))
        .catch(err => logger.error(CONTEXT, 'Failed to stream evaluation score packet upstream.', err));
    }
  };

  if (status === 'idle') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm text-center flex flex-col items-center justify-center max-w-xl mx-auto my-6">
        <div className="bg-blue-50 p-4 rounded-full border border-blue-100 text-blue-600 mb-4">
          <Brain className="h-10 w-10" />
        </div>
        <h3 className="text-xl font-bold text-slate-800 tracking-tight">AI Assessment Center</h3>
        <p className="text-sm text-slate-500 mt-2 mb-6 max-w-sm">
          Let the AssessorAgent parse your current vector space to build a custom multi-choice verification exam mapping directly to your materials.
        </p>
        <button
          onClick={startQuizGeneration}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors cursor-pointer flex items-center gap-2 text-sm"
        >
          Generate Assessment Panel
        </button>
      </div>
    );
  }

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 shadow-sm text-center flex flex-col items-center justify-center min-h-[300px]">
        <Loader2 className="h-10 w-10 text-blue-600 animate-spin mb-4" />
        <h4 className="font-bold text-slate-800">Synthesizing Examination Matrix...</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-xs">
          AssessorAgent is mapping complex conceptual boundaries into structured problem layouts. This could take up to 30 seconds.
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
            <span className="font-bold block text-base mb-1">Assessment Pipeline Error</span>
            <p className="leading-relaxed">{errorMessage}</p>
          </div>
        </div>
        <button
          onClick={startQuizGeneration}
          className="mt-4 w-full bg-slate-900 text-white font-medium py-2 px-4 rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 text-sm cursor-pointer"
        >
          <RefreshCw className="h-4 w-4" />
          Retry Generation
        </button>
      </div>
    );
  }

  const currentItem = quizItems[currentIndex];
  const selectedOption = selectedAnswers[currentIndex];

  if (status === 'completed') {
    const successRatio = score / quizItems.length;
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm text-center max-w-xl mx-auto my-4">
        <h3 className="text-2xl font-bold text-slate-800">Performance Evaluation Card</h3>
        <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold font-mono">{topicContext}</p>
        
        <div className="my-8">
          <div className="inline-block relative p-6 bg-slate-50 border border-slate-200 rounded-2xl">
            <span className={`text-4xl font-extrabold ${successRatio >= 0.75 ? 'text-emerald-600' : successRatio >= 0.5 ? 'text-blue-600' : 'text-red-500'}`}>
              {score} / {quizItems.length}
            </span>
            <p className="text-xs font-medium text-slate-500 mt-1">Total Validated Concepts Correct</p>
          </div>
        </div>

        <div className="space-y-4 text-left max-h-[250px] overflow-y-auto mb-6 p-2 border border-slate-100 rounded-lg bg-slate-50/50">
          {quizItems.map((item, idx) => (
            <div key={idx} className="text-xs p-3 border border-slate-200 rounded-lg bg-white">
              <div className="flex items-center gap-2 font-semibold mb-1">
                {selectedAnswers[idx] === item.correct_option ? (
                  <Check className="h-4 w-4 text-emerald-600" />
                ) : (
                  <X className="h-4 w-4 text-red-500" />
                )}
                <span className="text-slate-800">Question {item.question_number}</span>
              </div>
              <p className="text-slate-600 mb-1">{item.conceptual_question}</p>
              <p className="text-slate-400 font-mono text-[10px] bg-slate-50 p-1.5 rounded mt-1 leading-normal">
                <span className="font-bold text-slate-600">Justification:</span> {item.detailed_justification}
              </p>
            </div>
          ))}
        </div>

        <button
          onClick={startQuizGeneration}
          className="w-full bg-slate-900 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 text-sm cursor-pointer"
        >
          <RefreshCw className="h-4 w-4" />
          Generate New Assessment Suite
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 max-w-2xl mx-auto my-2">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
        <div className="flex items-center gap-2">
          <HelpCircle className="h-5 w-5 text-blue-600" />
          <span className="font-bold text-slate-800 text-sm">Question {currentIndex + 1} of {quizItems.length}</span>
        </div>
        <span className="text-[11px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-1 rounded border border-slate-200/40">
          Target: Verified Core Context
        </span>
      </div>

      <h4 className="text-base font-bold text-slate-800 leading-snug mb-5">{currentItem.conceptual_question}</h4>

      <div className="space-y-2.5">
        {(Object.keys(currentItem.options) as Array<'A' | 'B' | 'C' | 'D'>).map((key) => {
          const isCurrentSelected = selectedOption === key;
          return (
            <button
              key={key}
              onClick={() => selectOption(key)}
              className={`w-full text-left p-3.5 text-sm rounded-xl border transition-all flex items-center justify-between cursor-pointer group ${
                isCurrentSelected
                  ? 'border-blue-600 bg-blue-50/60 font-semibold text-blue-900'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/40 text-slate-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`h-6 w-6 rounded-md flex items-center justify-center text-xs font-bold border transition-colors ${
                  isCurrentSelected ? 'bg-blue-600 border-blue-600 text-white' : 'bg-slate-50 border-slate-200 group-hover:bg-white text-slate-500'
                }`}>
                  {key}
                </span>
                <span className="leading-tight">{currentItem.options[key]}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100 flex justify-end">
        <button
          onClick={handleNextStep}
          disabled={!selectedOption}
          className="bg-slate-900 text-white text-sm font-medium py-2 px-5 rounded-lg hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-400 transition-colors cursor-pointer flex items-center gap-1.5"
        >
          <span>{currentIndex === quizItems.length - 1 ? 'Complete Assessment' : 'Next Item'}</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
import React, { useState } from 'react';
import { Bot, HelpCircle, CheckCircle, XCircle, BookOpen, Loader2, AlertCircle, RefreshCw, Send } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';

const CONTEXT = 'QUIZ_COMPONENT';

interface QuizItem {
  question_number: number;
  conceptual_question: string;
  options: string[];
  correct_option: number;
  detailed_justification: string;
}

export const QuizSection: React.FC = () => {
  const [quizItems, setQuizItems] = useState<QuizItem[]>([]);
  const [status, setStatus] = useState<'idle' | 'loading' | 'active' | 'submitted' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [score, setScore] = useState<number>(0);
  const [topicContext, setTopicContext] = useState<string>('');

  const startQuizGeneration = async () => {
    setStatus('loading');
    setErrorMessage('');
    setSelectedAnswers({});
    logger.info(CONTEXT, 'Requesting dynamic evaluation package synthesis from AssessorAgent');

    try {
      const response = await apiService.fetchQuiz() as any;
      const extractedItems = response.quiz_items || response.questions || (response.data && response.data.questions);

      if (response.success && extractedItems && extractedItems.length > 0) {
        const normalizedItems = extractedItems.map((item: any, idx: number) => ({
          question_number: item.question_number || item.id || (idx + 1),
          conceptual_question: item.conceptual_question || item.question,
          options: item.options,
          correct_option: typeof item.correct_option === 'number' ? item.correct_option : (item.correct_answer || 0),
          detailed_justification: item.detailed_justification || item.explanation || item.justification || 'Contextually verified in source text.'
        }));

        logger.info(CONTEXT, `Quiz generation complete. Loaded ${normalizedItems.length} items.`);
        setQuizItems(normalizedItems);
        setTopicContext(response.topic_context || 'DeepSeek-MoE Architecture Analysis');
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

  const handleSelectOption = (qNum: number, oIdx: number) => {
    if (status === 'submitted') return;
    setSelectedAnswers(prev => ({ ...prev, [qNum]: oIdx }));
  };

  const handleSubmitQuiz = async () => {
    // Calculate final score metrics
    let correctCount = 0;
    quizItems.forEach(item => {
      if (selectedAnswers[item.question_number] === item.correct_option) {
        correctCount++;
      }
    });

    setScore(correctCount);
    setStatus('submitted');
    logger.info(CONTEXT, `Submitting telemetry metrics data card: ${correctCount}/${quizItems.length}`);

    try {
      await apiService.submitQuizScore(correctCount, quizItems.length, topicContext);
    } catch (err) {
      logger.error(CONTEXT, 'Failed to log background evaluation scores telemetry.', err);
    }
  };

  if (status === 'idle') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm text-center flex flex-col items-center justify-center max-w-xl mx-auto my-6">
        <div className="bg-blue-50 p-4 rounded-full border border-blue-100 text-blue-600 mb-4">
          <HelpCircle className="h-10 w-10" />
        </div>
        <h3 className="text-xl font-bold text-slate-800 tracking-tight">Conceptual Assessment Hub</h3>
        <p className="text-sm text-slate-500 mt-2 mb-6 max-w-sm">
          Trigger the AssessorAgent to isolate key knowledge claims within the document text and evaluate your understanding.
        </p>
        <button
          onClick={startQuizGeneration}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors cursor-pointer flex items-center gap-2 text-sm"
        >
          Generate Concept Evaluation
        </button>
      </div>
    );
  }

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 shadow-sm text-center flex flex-col items-center justify-center min-h-[300px]">
        <Loader2 className="h-10 w-10 text-blue-600 animate-spin mb-4" />
        <h4 className="font-bold text-slate-800">Synthesizing Comprehensive Evaluation Check...</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-xs">
          AssessorAgent is assembling grounding facts, distractors, and justifications. This might take up to 15 seconds.
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

  return (
    <div className="space-y-6 max-w-3xl mx-auto my-2 pb-12">
      {/* Quiz Progress & Metadata Sticky Banner */}
      <div className="bg-slate-900 text-white rounded-xl p-5 shadow-md flex flex-wrap items-center justify-between gap-4 sticky top-2 z-10">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-blue-400 font-mono">Evaluation Stream</span>
          <h3 className="text-base font-bold text-white leading-tight">{topicContext}</h3>
        </div>
        {status === 'submitted' ? (
          <div className="bg-blue-600 text-white px-5 py-2 rounded-lg font-bold text-sm tracking-wide">
            Final Score: {score} / {quizItems.length} ({Math.round((score / quizItems.length) * 100)}%)
          </div>
        ) : (
          <div className="text-xs font-semibold text-slate-300 bg-slate-800 px-3 py-1.5 rounded-md border border-slate-700">
            Answered: {Object.keys(selectedAnswers).length} / {quizItems.length}
          </div>
        )}
      </div>

      {/* Vertical Stacking of Questions */}
      <div className="space-y-6">
        {quizItems.map((item, qIdx) => {
          const selectedOption = selectedAnswers[item.question_number];
          const hasAnswered = selectedOption !== undefined;

          return (
            <div key={qIdx} className={`bg-white rounded-xl border p-6 shadow-sm transition-all ${
              status === 'submitted' 
                ? selectedOption === item.correct_option 
                  ? 'border-emerald-200 bg-emerald-50/10' 
                  : 'border-red-200 bg-red-50/10'
                : 'border-slate-200'
            }`}>
              {/* Question Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                <span className="text-xs font-bold font-mono uppercase bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md">
                  Question {qIdx + 1} of {quizItems.length}
                </span>
                {status === 'submitted' && (
                  selectedOption === item.correct_option ? (
                    <span className="flex items-center gap-1 text-emerald-600 text-xs font-bold uppercase bg-emerald-50 px-2.5 py-1 rounded-md">
                      <CheckCircle className="h-3.5 w-3.5" /> Correct
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-red-600 text-xs font-bold uppercase bg-red-50 px-2.5 py-1 rounded-md">
                      <XCircle className="h-3.5 w-3.5" /> Incorrect
                    </span>
                  )
                )}
              </div>

              {/* Question Text */}
              <h3 className="text-base font-bold text-slate-800 leading-snug mb-4">
                {item.conceptual_question}
              </h3>

              {/* Options Grid */}
              <div className="space-y-2.5">
                {item.options.map((option, oIdx) => {
                  const isSelected = selectedOption === oIdx;
                  const isCorrectAnswer = item.correct_option === oIdx;

                  let optionStyle = 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700';
                  if (isSelected) optionStyle = 'border-blue-600 bg-blue-50/40 text-blue-900 font-medium';

                  // Apply color styles post-submission
                  if (status === 'submitted') {
                    if (isCorrectAnswer) {
                      optionStyle = 'border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold shadow-sm';
                    } else if (isSelected && !isCorrectAnswer) {
                      optionStyle = 'border-red-400 bg-red-50 text-red-950 line-through';
                    } else {
                      optionStyle = 'border-slate-200 bg-white opacity-60 text-slate-400';
                    }
                  }

                  return (
                    <button
                      key={oIdx}
                      type="button"
                      disabled={status === 'submitted'}
                      onClick={() => handleSelectOption(item.question_number, oIdx)}
                      className={`w-full text-left p-3.5 rounded-xl border text-sm flex items-center gap-3 transition-all ${
                        status !== 'submitted' ? 'cursor-pointer' : 'cursor-default'
                      } ${optionStyle}`}
                    >
                      <div className={`h-6 w-6 rounded-full border flex items-center justify-center text-xs shrink-0 font-mono ${
                        isSelected 
                          ? 'bg-blue-600 border-blue-600 text-white font-bold' 
                          : status === 'submitted' && isCorrectAnswer
                            ? 'bg-emerald-600 border-emerald-600 text-white font-bold'
                            : 'bg-slate-50 border-slate-200 text-slate-500'
                      }`}>
                        {oIdx}
                      </div>
                      <span className="flex-1">{option}</span>
                    </button>
                  );
                })}
              </div>

              {/* Rich Justification & References Block (Revealed post-submission) */}
              {status === 'submitted' && (
                <div className="mt-5 pt-4 border-t border-slate-100 bg-slate-50/60 rounded-xl p-4 border border-slate-200/50">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wider font-mono">
                    <BookOpen className="h-4 w-4 text-blue-600" />
                    <span>Grounding Analysis & Solution Reference:</span>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    {item.detailed_justification}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Global Submission Bar Trigger */}
      {status === 'active' && (
        <div className="pt-4">
          <button
            type="button"
            onClick={handleSubmitQuiz}
            disabled={Object.keys(selectedAnswers).length < quizItems.length}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-bold py-3 px-6 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-sm cursor-pointer"
          >
            <Send className="h-4 w-4" />
            Submit Answers & Reveal Reference Explanations
          </button>
          {Object.keys(selectedAnswers).length < quizItems.length && (
            <p className="text-center text-xs text-slate-400 mt-2 font-medium">
              Please choose answers for all {quizItems.length} items to complete evaluation.
            </p>
          )}
        </div>
      )}

      {/* Retake Challenge Node */}
      {status === 'submitted' && (
        <button
          type="button"
          onClick={startQuizGeneration}
          className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-6 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-sm cursor-pointer"
        >
          <RefreshCw className="h-4 w-4" />
          Retake Assessment (Regenerate Concepts)
        </button>
      )}
    </div>
  );
};
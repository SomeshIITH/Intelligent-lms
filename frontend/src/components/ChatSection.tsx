import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertCircle, BookOpen } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';
import type { ChatMessage } from '../types';

const CONTEXT = 'CHAT_COMPONENT';

export const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'tutor', content: 'Hello! Upload a document to build our custom knowledge base, then ask me anything about the concepts.' }
  ]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Adjusted to hold custom structured citation schemas from your Pydantic ChatCitation models
  const [activeSources, setActiveSources] = useState<Array<{ page: number; content: string }>>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuery = input.trim();
    setInput('');
    setErrorMsg(null);
    
    // Optimistically update chat window track
    const updatedHistory: ChatMessage[] = [...messages, { role: 'student', content: userQuery }];
    setMessages(updatedHistory);
    setIsLoading(true);

    logger.info(CONTEXT, `Dispatching query transaction packet down to RAG: "${userQuery.substring(0, 30)}..."`);

    try {
      // Send message along with existing trailing logs history tracking array
      const response = await apiService.sendChatMessage({
        message: userQuery,
        history: messages
      }) as any; // Temporary cast to cleanly extract custom enveloped data parameters

      if (response.success) {
        logger.info(CONTEXT, `Received balanced multi-agent reply.`);
        
        // Extract the nested answer matching your Pydantic ChatDataPayload container setup
        const botAnswer = response.data?.answer || response.response || 'No contextual evaluation compiled.';
        const citations = response.data?.citations || [];

        setMessages((prev) => [...prev, { role: 'tutor', content: botAnswer }]);
        setActiveSources(citations);
      } else {
        throw new Error(response.message || 'The RAG orchestrator rejected our conversation turn state.');
      }
    } catch (err: any) {
      const fallbackMsg = err.message || 'Failed to exchange messages with the agent runtime server.';
      logger.error(CONTEXT, `Turn execution crash encountered.`, err);
      setErrorMsg(fallbackMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[600px]">
      {/* Header element */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50 rounded-t-xl">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-blue-600" />
          <h2 className="font-bold text-slate-800">RAG AI Tutor Space</h2>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">
          Multi-Agent Contextual Router
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-3 max-w-[85%] ${msg.role === 'student' ? 'ml-auto flex-row-reverse' : ''}`}>
            <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 border ${
              msg.role === 'student' ? 'bg-slate-900 border-slate-800 text-white' : 'bg-blue-50 border-blue-200 text-blue-600'
            }`}>
              {msg.role === 'student' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>
            <div className={`p-3.5 rounded-xl text-sm leading-relaxed ${
              msg.role === 'student' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200/60'
            }`}>
              <p className="whitespace-pre-line">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="h-8 w-8 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Bot className="h-4 w-4" />
            </div>
            <div className="p-3.5 rounded-xl bg-slate-100 text-slate-500 text-sm rounded-tl-none border border-slate-200/60 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Agents extracting matching document contexts...</span>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200 p-3 rounded-lg text-red-700 text-sm">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span><span className="font-semibold">Chat Broker Error:</span> {errorMsg}</span>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Context citations drawer */}
      {activeSources.length > 0 && (
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 max-h-[100px] overflow-y-auto">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-1">
            <BookOpen className="h-3.5 w-3.5 text-emerald-600" />
            <span>Grounded Source Citations:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {activeSources.map((src, idx) => (
              <div key={idx} title={src.content} className="text-[11px] bg-white border border-slate-300 text-slate-600 px-2 py-0.5 rounded cursor-help font-medium">
                Document Page {src.page}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Form submit input controller bar */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-200 bg-white rounded-b-xl flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your course materials..."
          disabled={isLoading}
          className="flex-1 border border-slate-300 rounded-lg px-3.5 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-400"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-slate-300 cursor-pointer flex items-center justify-center shrink-0 w-10 h-10"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};
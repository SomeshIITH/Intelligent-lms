import axios from 'axios';
import { logger } from '../utils/logger';
import type { 
  UploadResponse, 
  ChatMessageRequest, 
  ChatResponse, 
  QuizResponse, 
  RoadmapResponse, 
  AnalyticsResponse 
} from '../types';

const CONTEXT = 'API_SERVICE';

// Initialize a base instance pointing to your FastAPI backend gateway port
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 60000, // 60s timeout for complex agent generation steps
});

/**
 * Centrally traps outbound configuration and intercepts errors for clear tracking.
 */
apiClient.interceptors.response.use(
  (response) => {
    logger.debug(CONTEXT, `HTTP Outbound Success [${response.status}] -> ${response.config.url}`);
    return response;
  },
  (error) => {
    const errorDetails = {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
      metadata: error.response?.data?.metadata,
    };
    logger.error(CONTEXT, `Network Transaction Crash on endpoint ${errorDetails.url}`, errorDetails);
    return Promise.reject(errorDetails);
  }
);

export const apiService = {
  /**
   * Dispatches binary streams to backend upload structures.
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    logger.info(CONTEXT, `Initiating multi-part payload payload upload for: ${file.name}`);
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post<UploadResponse>('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  /**
   * Transmits streaming conversation histories down into the RAG Tutor pipeline.
   */
  async sendChatMessage(payload: ChatMessageRequest): Promise<ChatResponse> {
    logger.info(CONTEXT, `Sending query payload packet to RAG routing layer`);

    // Map your structured chat messages into a flat list of alternating text strings
    const flatStringHistory = payload.history.map(msg => msg.content);

    const strictPayload = {
      message: payload.message,
      history: flatStringHistory
    };

    const { data } = await apiClient.post<ChatResponse>('/chat', strictPayload);
    return data;
  },

  /**
   * Pulls synthesized multi-choice questions from the evaluation engines.
   */
  async fetchQuiz(): Promise<QuizResponse> {
    logger.info(CONTEXT, `Triggering explicit call to assessment generation framework`);
    const { data } = await apiClient.get<QuizResponse>('/quiz');
    return data;
  },

  /**
   * Posts evaluation parameters back to system memory trackers.
   */
  async submitQuizScore(score: number, total: number, topicContext: string): Promise<void> {
    logger.info(CONTEXT, `Logging transaction score tracking event metrics: ${score}/${total}`);
    await apiClient.post('/quiz/score', {
      score,
      total,
      topic_context: topicContext,
    });
  },

  /**
   * Gathers structural roadmap items mapped out by your Curriculum Agent.
   */
  async fetchRoadmap(): Promise<RoadmapResponse> {
    logger.info(CONTEXT, `Requesting structured milestone progression sequence framework`);
    const { data } = await apiClient.get<RoadmapResponse>('/roadmap');
    return data;
  },

  /**
   * Compiles diagnostic performance metrics across your dashboard workspace.
   */
  async fetchAnalytics(): Promise<AnalyticsResponse> {
    logger.info(CONTEXT, `Pulling historical metric calculations from profile analyzers`);
    const { data } = await apiClient.get<AnalyticsResponse>('/analytics');
    return data;
  },
};
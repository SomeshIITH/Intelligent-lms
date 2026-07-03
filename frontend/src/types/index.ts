export interface BaseResponse {
    success: boolean;
    message: string;
    metadata?: Record<string, any>;
  }
  
  export interface UploadResponse extends BaseResponse {
    filename: string;
    chunk_count: number;
  }
  
  export interface ChatMessage {
    role: 'student' | 'tutor';
    content: string;
  }
  
  export interface ChatMessageRequest {
    message: string;
    history: ChatMessage[];
  }
  
  export interface ChatResponse extends BaseResponse {
    response: string;
    source_nodes: {
      page_content: string;
      page_number: number;
    }[];
  }
  
  export interface QuizItem {
    question_number: number;
    conceptual_question: string;
    options: { A: string; B: string; C: string; D: string };
    correct_option: 'A' | 'B' | 'C' | 'D';
    detailed_justification: string;
  }
  
  export interface QuizResponse extends BaseResponse {
    topic_context: string;
    quiz_items: QuizItem[];
  }
  
  export interface RoadmapMilestone {
    milestone_number: number;
    core_concept_title: string;
    depth_explanation: string;
    estimated_study_minutes: number;
    source_page_references: number[];
  }
  
  export interface RoadmapResponse extends BaseResponse {
    document_outline_summary: string;
    sequenced_milestones: RoadmapMilestone[];
  }
  
  export interface TopicPerformance {
    topic_context: string;
    calculated_mastery_percentage: number;
    tracked_attempts: number;
  }
  
  export interface AnalyticsDataPayload {
    overall_score: number;
    quizzes_taken: number;
    topic_breakdown: TopicPerformance[];
    strengths: string[];
    weaknesses: string[];
    remediation_plan: string;
  }
  
  export interface AnalyticsResponse extends BaseResponse {
    data: AnalyticsDataPayload;
  }
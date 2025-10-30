export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'trainer' | 'admin';
  profile?: UserProfile;
}

export interface UserProfile {
  id: string;
  college?: string;
  graduation_year?: number;
  target_companies: string[];
  preferred_roles: string[];
  skill_levels: Record<string, number>;
}

export enum InterviewType {
  BEHAVIORAL = 'behavioral',
  TECHNICAL = 'technical',
  HR = 'hr',
  CASE_STUDY = 'case_study',
  MIXED = 'mixed'
}

export enum InterviewStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  PAUSED = 'paused'
}

export enum QuestionCategory {
  BEHAVIORAL = 'behavioral',
  TECHNICAL_CODING = 'technical_coding',
  TECHNICAL_SYSTEM_DESIGN = 'technical_system_design',
  HR_GENERAL = 'hr_general',
  COMPANY_SPECIFIC = 'company_specific',
  SITUATIONAL = 'situational'
}

export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard'
}

export interface InterviewSessionCreate {
  interview_type: InterviewType;
  title: string;
  description?: string;
  company_name?: string;
  position_title?: string;
  total_duration: number;
  question_count: number;
  difficulty_level: DifficultyLevel;
  adaptive_mode: boolean;
  performance_threshold: number;
  question_categories: QuestionCategory[];
  company_tags?: string[];
  topic_tags?: string[];
  enable_video_recording: boolean;
  enable_audio_recording: boolean;
  scheduled_time?: string;
}

export interface InterviewSession {
  id: string;
  user_id: string;
  interview_type: InterviewType;
  title: string;
  description?: string;
  company_name?: string;
  position_title?: string;
  total_duration: number;
  question_count: number;
  difficulty_level: DifficultyLevel;
  adaptive_mode: boolean;
  performance_threshold: number;
  question_categories: QuestionCategory[];
  company_tags?: string[];
  topic_tags?: string[];
  status: InterviewStatus;
  current_question_index: number;
  questions_asked: string[];
  scheduled_time?: string;
  start_time?: string;
  end_time?: string;
  total_pause_duration: number;
  enable_video_recording: boolean;
  enable_audio_recording: boolean;
  video_file_url?: string;
  audio_file_url?: string;
  overall_score?: number;
  communication_score?: number;
  technical_score?: number;
  behavioral_score?: number;
  ai_feedback: Record<string, any>;
  performance_analysis: Record<string, any>;
  improvement_suggestions: string[];
  created_at: string;
  updated_at: string;
}

export interface InterviewQuestion {
  id: string;
  session_id: string;
  question_text: string;
  category: QuestionCategory;
  difficulty_level: DifficultyLevel;
  expected_duration: number;
  question_order: number;
  is_followup: boolean;
  parent_question_id?: string;
  generated_by_ai: boolean;
  generation_prompt?: string;
  generation_context: Record<string, any>;
  context_information?: string;
  evaluation_criteria: string[];
  sample_answers: string[];
  difficulty_adjustment?: number;
  created_at: string;
  asked_at?: string;
}

export interface InterviewResponseCreate {
  response_text?: string;
  response_duration: number;
  thinking_time: number;
  audio_file_url?: string;
  video_file_url?: string;
}

export interface InterviewResponse {
  id: string;
  session_id: string;
  question_id: string;
  response_text?: string;
  audio_file_url?: string;
  video_file_url?: string;
  response_duration: number;
  thinking_time: number;
  transcript_confidence?: number;
  sentiment_score?: number;
  confidence_level?: number;
  speech_pace?: number;
  filler_word_count: number;
  pause_count: number;
  volume_consistency?: number;
  content_relevance?: number;
  technical_accuracy?: number;
  structure_score?: number;
  overall_score?: number;
  communication_score?: number;
  content_score?: number;
  ai_feedback?: string;
  improvement_suggestions: string[];
  strengths: string[];
  weaknesses: string[];
  analysis_version?: string;
  processing_time?: number;
  created_at: string;
  analyzed_at?: string;
}

export interface InterviewSessionSummary {
  id: string;
  title: string;
  interview_type: InterviewType;
  company_name?: string;
  position_title?: string;
  status: InterviewStatus;
  total_duration: number;
  actual_duration?: number;
  question_count: number;
  questions_answered: number;
  overall_score?: number;
  communication_score?: number;
  technical_score?: number;
  behavioral_score?: number;
  created_at: string;
  start_time?: string;
  end_time?: string;
}

export interface InterviewAnalytics {
  total_interviews: number;
  completed_interviews: number;
  average_score?: number;
  average_duration?: number;
  score_distribution: Record<string, number>;
  category_performance: Record<QuestionCategory, number>;
  improvement_trends: Array<Record<string, any>>;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
}

export interface AIInterviewerMessage {
  type: string;
  text: string;
  metadata: Record<string, any>;
}

export interface WebSocketMessage {
  type: string;
  data: Record<string, any>;
  timestamp?: string;
}

export interface RealTimeProgress {
  session_id: string;
  progress_percentage: number;
  questions_answered: number;
  total_questions: number;
  current_scores: Record<string, number>;
  time_elapsed_minutes: number;
  estimated_remaining_minutes: number;
}

export interface InterviewSessionWithDetails extends InterviewSession {
  questions: InterviewQuestion[];
  responses: InterviewResponse[];
  current_question?: InterviewQuestion;
}

export interface VideoRecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  mediaStream?: MediaStream;
  mediaRecorder?: MediaRecorder;
  recordedChunks: Blob[];
}

export interface InterviewTimer {
  totalTime: number;
  elapsedTime: number;
  questionTime: number;
  isRunning: boolean;
  isPaused: boolean;
}

export interface InterviewFeedback {
  overall_feedback: string;
  communication_feedback: string;
  technical_feedback: string;
  behavioral_feedback: string;
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
  next_steps: string[];
}
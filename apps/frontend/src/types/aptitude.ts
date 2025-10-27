/**
 * TypeScript types for Aptitude Testing System
 */

export interface TestSession {
  id: string;
  user_id: string;
  test_type: string;
  title?: string;
  description?: string;
  configuration: Record<string, any>;
  question_ids: string[];
  current_question_index: number;
  total_questions: number;
  time_limit?: number;
  time_per_question?: number;
  start_time?: string;
  end_time?: string;
  pause_time?: string;
  total_pause_duration: number;
  status: SessionStatus;
  score?: number;
  max_score?: number;
  percentage?: number;
  correct_answers: number;
  incorrect_answers: number;
  skipped_answers: number;
  total_time_taken?: number;
  allow_review: boolean;
  show_results: boolean;
  randomize_questions: boolean;
  randomize_options: boolean;
  categories?: string[];
  difficulty_levels?: number[];
  company_tags?: string[];
  topic_tags?: string[];
  extra_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: string;
  type: QuestionType;
  category: string;
  subcategory?: string;
  difficulty: DifficultyLevel;
  title: string;
  content: string;
  options?: string[];
  correct_answer: string;
  explanation?: string;
  hints?: string[];
  company_tags: string[];
  topic_tags: string[];
  skill_tags: string[];
  extra_data: Record<string, any>;
  status: QuestionStatus;
  version: number;
  parent_question_id?: string;
  usage_count: number;
  success_rate?: number;
  average_time?: number;
  created_by?: string;
  reviewed_by?: string;
  is_active: boolean;
  is_premium: boolean;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Submission {
  id: string;
  user_id: string;
  session_id: string;
  question_id: string;
  submission_type: SubmissionType;
  user_answer: string;
  is_correct?: boolean;
  score?: number;
  max_score?: number;
  status: SubmissionStatus;
  time_taken: number;
  time_limit?: number;
  evaluation_attempts: number;
  feedback?: string;
  detailed_analysis: Record<string, any>;
  evaluated_by?: string;
  evaluation_time?: number;
  extra_data: Record<string, any>;
  submitted_at: string;
  evaluated_at?: string;
  created_at: string;
  updated_at: string;
}

// Enums
export enum SessionStatus {
  CREATED = 'created',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  ABANDONED = 'abandoned',
  EXPIRED = 'expired'
}

export enum QuestionType {
  APTITUDE = 'aptitude',
  CODING = 'coding',
  COMMUNICATION = 'communication',
  BEHAVIORAL = 'behavioral',
  TECHNICAL = 'technical'
}

export enum DifficultyLevel {
  BEGINNER = 1,
  EASY = 2,
  MEDIUM = 3,
  HARD = 4,
  EXPERT = 5
}

export enum QuestionStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived'
}

export enum SubmissionType {
  APTITUDE = 'aptitude',
  CODING = 'coding',
  COMMUNICATION = 'communication',
  BEHAVIORAL = 'behavioral'
}

export enum SubmissionStatus {
  SUBMITTED = 'submitted',
  EVALUATING = 'evaluating',
  EVALUATED = 'evaluated',
  FAILED = 'failed'
}

export enum AdaptiveAlgorithm {
  RANDOM = 'random',
  DIFFICULTY_BASED = 'difficulty_based',
  PERFORMANCE_BASED = 'performance_based',
  IRT_BASED = 'irt_based',
  BALANCED = 'balanced'
}

// Request/Response types
export interface AptitudeTestConfigRequest {
  total_questions?: number;
  time_limit?: number;
  time_per_question?: number;
  categories?: string[];
  difficulty_levels?: number[];
  company_tags?: string[];
  topic_tags?: string[];
  adaptive_algorithm?: AdaptiveAlgorithm;
  randomize_questions?: boolean;
  randomize_options?: boolean;
  allow_review?: boolean;
  show_results?: boolean;
  passing_score?: number;
  negative_marking?: boolean;
  negative_marking_ratio?: number;
  difficulty_distribution?: Record<number, number>;
  title?: string;
  description?: string;
}

export interface TestSessionCreate {
  test_type: string;
  title?: string;
  description?: string;
  configuration: Record<string, any>;
  question_ids: string[];
}

export interface AnswerSubmissionRequest {
  question_id: string;
  user_answer: string;
  time_taken: number;
}

export interface SessionProgressResponse {
  session_id: string;
  status: string;
  current_question: number;
  total_questions: number;
  progress_percentage: number;
  correct_answers: number;
  incorrect_answers: number;
  skipped_answers: number;
  current_score: number;
  accuracy_percentage: number;
  time_remaining?: number;
  time_limit?: number;
  start_time?: string;
  submissions_count: number;
  can_pause: boolean;
  can_resume: boolean;
  allow_review: boolean;
}

export interface SessionResultsResponse {
  session_id: string;
  title: string;
  test_type: string;
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  skipped_answers: number;
  final_score: number;
  max_score: number;
  percentage?: number;
  accuracy_percentage: number;
  total_time_taken?: number;
  average_time_per_question?: number;
  start_time?: string;
  end_time?: string;
  passed: boolean;
  category_performance: Record<string, CategoryPerformance>;
  difficulty_performance: Record<string, DifficultyPerformance>;
  time_analysis: TimeAnalysis;
  detailed_submissions: DetailedSubmission[];
}

export interface CategoryPerformance {
  total: number;
  correct: number;
  accuracy: number;
  average_time: number;
  average_score: number;
  total_time: number;
  total_score: number;
}

export interface DifficultyPerformance {
  total: number;
  correct: number;
  accuracy: number;
  average_time: number;
  average_score: number;
  total_time: number;
  total_score: number;
}

export interface TimeAnalysis {
  total_time: number;
  average_time: number;
  min_time: number;
  max_time: number;
  time_efficiency?: number;
}

export interface DetailedSubmission {
  question_id: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  score: number;
  time_taken: number;
  category: string;
  difficulty: number;
}

export interface UserPerformanceAnalytics {
  total_sessions: number;
  average_score: number;
  improvement_trend: 'improving' | 'declining' | 'stable' | 'no_data' | 'insufficient_data';
  category_performance: Record<string, {
    sessions: number;
    total_score: number;
    average_score: number;
  }>;
  sessions_over_time: Array<{
    date: string;
    score?: number;
    duration?: number;
  }>;
}

export interface AvailableFilters {
  categories: string[];
  company_tags: string[];
  topic_tags: string[];
  difficulty_levels: number[];
  adaptive_algorithms: string[];
}

// UI State types
export interface TestSessionState {
  session?: TestSession;
  currentQuestion?: Question;
  progress?: SessionProgressResponse;
  results?: SessionResultsResponse;
  isLoading: boolean;
  error?: string;
  timeRemaining?: number;
  isPaused: boolean;
}

export interface TestConfigurationState {
  config: AptitudeTestConfigRequest;
  availableFilters?: AvailableFilters;
  isLoading: boolean;
  error?: string;
}

export interface TestHistoryState {
  sessions: TestSession[];
  analytics?: UserPerformanceAnalytics;
  isLoading: boolean;
  error?: string;
  pagination: {
    skip: number;
    limit: number;
    total?: number;
  };
}
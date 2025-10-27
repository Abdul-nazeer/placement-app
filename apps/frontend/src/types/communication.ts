/**
 * Communication assessment types
 */

export interface CommunicationPrompt {
  id: string;
  title: string;
  description: string;
  prompt_text: string;
  category: 'hr_interview' | 'behavioral' | 'presentation';
  difficulty_level: number;
  time_limit?: number;
  evaluation_criteria?: string[];
  tags?: string[];
  is_active: string;
  created_at: string;
  updated_at: string;
}

export interface CommunicationSession {
  id: string;
  user_id: string;
  session_type: 'hr_interview' | 'behavioral' | 'presentation';
  prompt_id?: string;
  start_time: string;
  end_time?: string;
  status: 'active' | 'completed' | 'abandoned';
  overall_score?: number;
  feedback?: string;
  created_at: string;
  updated_at: string;
}

export interface CommunicationSessionWithPrompt extends CommunicationSession {
  prompt?: CommunicationPrompt;
}

export interface CommunicationRecording {
  id: string;
  session_id: string;
  audio_file_path: string;
  duration?: number;
  file_size?: number;
  transcript?: string;
  confidence_score?: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_results?: Record<string, any>;
  created_at: string;
  processed_at?: string;
}

export interface SpeechMetrics {
  words_per_minute?: number;
  pause_frequency?: number;
  average_pause_duration?: number;
  filler_word_count?: number;
  filler_word_percentage?: number;
}

export interface LanguageMetrics {
  grammar_score?: number;
  vocabulary_complexity?: number;
  sentence_structure_score?: number;
  clarity_score?: number;
}

export interface ContentMetrics {
  relevance_score?: number;
  completeness_score?: number;
  coherence_score?: number;
}

export interface CommunicationAnalysis {
  id: string;
  recording_id: string;
  
  // Speech metrics
  words_per_minute?: number;
  pause_frequency?: number;
  average_pause_duration?: number;
  filler_word_count?: number;
  filler_word_percentage?: number;
  
  // Language metrics
  grammar_score?: number;
  vocabulary_complexity?: number;
  sentence_structure_score?: number;
  clarity_score?: number;
  
  // Content metrics
  relevance_score?: number;
  completeness_score?: number;
  coherence_score?: number;
  
  // Overall metrics
  fluency_score?: number;
  confidence_score?: number;
  overall_score?: number;
  
  // Detailed analysis
  strengths?: string[];
  weaknesses?: string[];
  suggestions?: string[];
  filler_words_detected?: Array<Record<string, any>>;
  
  created_at: string;
}

export interface CommunicationProgress {
  id: string;
  user_id: string;
  skill_category: string;
  current_level: number;
  sessions_completed: number;
  total_practice_time: number;
  last_session_date?: string;
  improvement_rate?: number;
  created_at: string;
  updated_at: string;
}

export interface CommunicationDashboard {
  user_id: string;
  total_sessions: number;
  total_practice_time: number;
  average_score?: number;
  skill_progress: CommunicationProgress[];
  recent_sessions: CommunicationSession[];
  strengths: string[];
  areas_for_improvement: string[];
  recommended_exercises: string[];
}

export interface CommunicationFeedback {
  session_id: string;
  overall_score: number;
  analysis: CommunicationAnalysis;
  recording: CommunicationRecording;
  recommendations: string[];
  next_steps: string[];
  progress_comparison?: Record<string, any>;
}

// Request types
export interface CreateCommunicationSessionRequest {
  session_type: 'hr_interview' | 'behavioral' | 'presentation';
  prompt_id?: string;
}

export interface UpdateCommunicationSessionRequest {
  status?: 'active' | 'completed' | 'abandoned';
  overall_score?: number;
  feedback?: string;
}

export interface AudioUploadRequest {
  session_id: string;
  duration?: number;
}

// UI State types
export interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioBlob?: Blob;
  audioUrl?: string;
}

export interface CommunicationFilters {
  category?: 'hr_interview' | 'behavioral' | 'presentation';
  difficulty_level?: number;
  status?: 'active' | 'completed' | 'abandoned';
}

export interface PracticeScenario {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: number;
  estimatedTime: number;
  skills: string[];
}
/**
 * Aptitude Test Service
 * 
 * This service handles all API calls related to aptitude testing including:
 * - Test session creation and management
 * - Answer submission and progress tracking
 * - Results retrieval and analytics
 */

import api from '../lib/api';
import type {
  TestSession,
  Question,
  Submission,
  TestSessionCreate,
  AnswerSubmissionRequest,
  SessionProgressResponse,
  SessionResultsResponse,
  AptitudeTestConfigRequest,
  UserPerformanceAnalytics,
  AvailableFilters
} from '../types/aptitude';

export class AptitudeService {
  /**
   * Create a new aptitude test session
   */
  static async createTestSession(config: AptitudeTestConfigRequest): Promise<TestSession> {
    const response = await api.post('/aptitude/sessions', config);
    return response.data;
  }

  /**
   * Start a test session
   */
  static async startSession(sessionId: string): Promise<TestSession> {
    const response = await api.post(`/aptitude/sessions/${sessionId}/start`);
    return response.data;
  }

  /**
   * Get the current question for a session
   */
  static async getCurrentQuestion(sessionId: string): Promise<Question | null> {
    const response = await api.get(`/aptitude/sessions/${sessionId}/current-question`);
    return response.data;
  }

  /**
   * Submit an answer for the current question
   */
  static async submitAnswer(
    sessionId: string,
    submission: AnswerSubmissionRequest
  ): Promise<{
    submission_id: string;
    is_correct: boolean;
    score: number;
    max_score: number;
    is_session_complete: boolean;
    feedback?: string;
    time_taken: number;
  }> {
    const response = await api.post(`/aptitude/sessions/${sessionId}/submit`, submission);
    return response.data;
  }

  /**
   * Pause a test session
   */
  static async pauseSession(sessionId: string): Promise<TestSession> {
    const response = await api.post(`/aptitude/sessions/${sessionId}/pause`);
    return response.data;
  }

  /**
   * Resume a test session
   */
  static async resumeSession(sessionId: string): Promise<TestSession> {
    const response = await api.post(`/aptitude/sessions/${sessionId}/resume`);
    return response.data;
  }

  /**
   * Get session progress information
   */
  static async getSessionProgress(sessionId: string): Promise<SessionProgressResponse> {
    const response = await api.get(`/aptitude/sessions/${sessionId}/progress`);
    return response.data;
  }

  /**
   * Get session results and analysis
   */
  static async getSessionResults(sessionId: string): Promise<SessionResultsResponse> {
    const response = await api.get(`/aptitude/sessions/${sessionId}/results`);
    return response.data;
  }

  /**
   * Get user's test session history
   */
  static async getUserSessions(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    test_type?: string;
  }): Promise<TestSession[]> {
    const response = await api.get('/aptitude/sessions', { params });
    return response.data;
  }

  /**
   * Get user performance analytics
   */
  static async getUserPerformanceAnalytics(days: number = 30): Promise<UserPerformanceAnalytics> {
    const response = await api.get('/aptitude/analytics/performance', {
      params: { days }
    });
    return response.data;
  }

  /**
   * Get available filter options for creating tests
   */
  static async getAvailableFilters(): Promise<AvailableFilters> {
    const response = await api.get('/aptitude/available-filters');
    return response.data;
  }
}

export default AptitudeService;
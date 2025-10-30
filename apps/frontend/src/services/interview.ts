import api from '../lib/api';
import {
  InterviewSession,
  InterviewSessionCreate,
  InterviewSessionSummary,
  InterviewQuestion,
  InterviewResponse,
  InterviewResponseCreate,
  InterviewAnalytics,
  InterviewSessionWithDetails,
  AIInterviewerMessage,
  RealTimeProgress
} from '../types/interview';

export class InterviewService {
  /**
   * Create a new interview session
   */
  static async createSession(data: InterviewSessionCreate): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>('/interviews/sessions', data);
    return response.data;
  }

  /**
   * Get interview session by ID
   */
  static async getSession(sessionId: string): Promise<InterviewSessionWithDetails> {
    const response = await api.get<InterviewSessionWithDetails>(`/interviews/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * Get user's interview sessions
   */
  static async getUserSessions(
    limit: number = 20,
    offset: number = 0,
    status?: string
  ): Promise<{ sessions: InterviewSessionSummary[]; total: number }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    
    if (status) {
      params.append('status', status);
    }

    const response = await api.get<{ sessions: InterviewSessionSummary[]; total: number }>(
      `/interviews/sessions?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Start an interview session
   */
  static async startSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interviews/sessions/${sessionId}/start`);
    return response.data;
  }

  /**
   * Pause an interview session
   */
  static async pauseSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interviews/sessions/${sessionId}/pause`);
    return response.data;
  }

  /**
   * Resume an interview session
   */
  static async resumeSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interviews/sessions/${sessionId}/resume`);
    return response.data;
  }

  /**
   * Complete an interview session
   */
  static async completeSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interviews/sessions/${sessionId}/complete`);
    return response.data;
  }

  /**
   * Get next question for interview session
   */
  static async getNextQuestion(sessionId: string): Promise<InterviewQuestion> {
    const response = await api.get<InterviewQuestion>(`/interviews/sessions/${sessionId}/next-question`);
    return response.data;
  }

  /**
   * Submit response to interview question
   */
  static async submitResponse(
    sessionId: string,
    questionId: string,
    responseData: InterviewResponseCreate
  ): Promise<InterviewResponse> {
    const response = await api.post<InterviewResponse>(
      `/interviews/sessions/${sessionId}/questions/${questionId}/responses`,
      responseData
    );
    return response.data;
  }

  /**
   * Upload audio recording for response
   */
  static async uploadAudioRecording(
    sessionId: string,
    questionId: string,
    audioFile: File,
    duration: number,
    thinkingTime: number = 0
  ): Promise<InterviewResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('response_duration', duration.toString());
    formData.append('thinking_time', thinkingTime.toString());

    const response = await api.post<InterviewResponse>(
      `/interviews/sessions/${sessionId}/questions/${questionId}/audio`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Upload video recording for response
   */
  static async uploadVideoRecording(
    sessionId: string,
    questionId: string,
    videoFile: File,
    duration: number,
    thinkingTime: number = 0
  ): Promise<InterviewResponse> {
    const formData = new FormData();
    formData.append('video_file', videoFile);
    formData.append('response_duration', duration.toString());
    formData.append('thinking_time', thinkingTime.toString());

    const response = await api.post<InterviewResponse>(
      `/interviews/sessions/${sessionId}/questions/${questionId}/video`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Get response analysis
   */
  static async getResponseAnalysis(responseId: string): Promise<InterviewResponse> {
    const response = await api.get<InterviewResponse>(`/interviews/responses/${responseId}/analysis`);
    return response.data;
  }

  /**
   * Get session analytics
   */
  static async getSessionAnalytics(sessionId: string): Promise<InterviewAnalytics> {
    const response = await api.get<InterviewAnalytics>(`/interviews/sessions/${sessionId}/analytics`);
    return response.data;
  }

  /**
   * Get user interview analytics
   */
  static async getUserAnalytics(): Promise<InterviewAnalytics> {
    const response = await api.get<InterviewAnalytics>('/interviews/analytics');
    return response.data;
  }

  /**
   * Get AI interviewer message
   */
  static async getAIMessage(
    sessionId: string,
    messageType: string,
    context?: Record<string, any>
  ): Promise<AIInterviewerMessage> {
    const response = await api.post<AIInterviewerMessage>(
      `/interviews/sessions/${sessionId}/ai-message`,
      {
        message_type: messageType,
        context: context || {}
      }
    );
    return response.data;
  }

  /**
   * Get real-time progress
   */
  static async getRealTimeProgress(sessionId: string): Promise<RealTimeProgress> {
    const response = await api.get<RealTimeProgress>(`/interviews/sessions/${sessionId}/progress`);
    return response.data;
  }

  /**
   * Delete interview session
   */
  static async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/interviews/sessions/${sessionId}`);
  }

  /**
   * Generate AI questions for session
   */
  static async generateQuestions(
    sessionId: string,
    count: number = 1,
    context?: Record<string, any>
  ): Promise<InterviewQuestion[]> {
    const response = await api.post<InterviewQuestion[]>(
      `/interviews/sessions/${sessionId}/generate-questions`,
      {
        count,
        context: context || {}
      }
    );
    return response.data;
  }

  /**
   * Get session feedback report
   */
  static async getSessionFeedback(sessionId: string): Promise<any> {
    const response = await api.get(`/interviews/sessions/${sessionId}/feedback`);
    return response.data;
  }

  /**
   * Export session data
   */
  static async exportSession(sessionId: string, format: 'pdf' | 'json' = 'pdf'): Promise<Blob> {
    const response = await api.get(`/interviews/sessions/${sessionId}/export`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  /**
   * Get interview templates
   */
  static async getTemplates(): Promise<any[]> {
    const response = await api.get('/interviews/templates');
    return response.data;
  }

  /**
   * Create session from template
   */
  static async createFromTemplate(templateId: string, customizations?: any): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interviews/templates/${templateId}/create`, {
      customizations: customizations || {}
    });
    return response.data;
  }
}
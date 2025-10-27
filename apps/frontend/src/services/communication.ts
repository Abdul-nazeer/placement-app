/**
 * Communication assessment service
 */

import api from '../lib/api';
import {
  CommunicationPrompt,
  CommunicationSession,
  CommunicationSessionWithPrompt,
  CommunicationRecording,
  CommunicationAnalysis,
  CommunicationProgress,
  CommunicationDashboard,
  CreateCommunicationSessionRequest,
  UpdateCommunicationSessionRequest,
  CommunicationFilters,
} from '../types/communication';

export class CommunicationService {
  // Prompt Management
  async getPrompts(filters?: CommunicationFilters): Promise<CommunicationPrompt[]> {
    const params = new URLSearchParams();
    
    if (filters?.category) {
      params.append('category', filters.category);
    }
    if (filters?.difficulty_level) {
      params.append('difficulty_level', filters.difficulty_level.toString());
    }
    
    const response = await api.get(`/communication/prompts?${params.toString()}`);
    return response.data;
  }

  async getPromptById(promptId: string): Promise<CommunicationPrompt> {
    const response = await api.get(`/communication/prompts/${promptId}`);
    return response.data;
  }

  // Session Management
  async createSession(sessionData: CreateCommunicationSessionRequest): Promise<CommunicationSession> {
    const response = await api.post('/communication/sessions', sessionData);
    return response.data;
  }

  async getUserSessions(filters?: CommunicationFilters): Promise<CommunicationSessionWithPrompt[]> {
    const params = new URLSearchParams();
    
    if (filters?.category) {
      params.append('session_type', filters.category);
    }
    if (filters?.status) {
      params.append('status', filters.status);
    }
    
    const response = await api.get(`/communication/sessions?${params.toString()}`);
    return response.data;
  }

  async getSessionById(sessionId: string): Promise<CommunicationSessionWithPrompt> {
    const response = await api.get(`/communication/sessions/${sessionId}`);
    return response.data;
  }

  async updateSession(
    sessionId: string, 
    sessionData: UpdateCommunicationSessionRequest
  ): Promise<CommunicationSession> {
    const response = await api.put(`/communication/sessions/${sessionId}`, sessionData);
    return response.data;
  }

  // Audio Recording and Processing
  async uploadAudioRecording(
    sessionId: string,
    audioFile: File,
    duration?: number
  ): Promise<CommunicationRecording> {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    if (duration) {
      formData.append('duration', duration.toString());
    }

    const response = await api.post(
      `/communication/sessions/${sessionId}/upload-audio`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getRecordingAnalysis(recordingId: string): Promise<CommunicationAnalysis> {
    const response = await api.get(`/communication/recordings/${recordingId}/analysis`);
    return response.data;
  }

  // Progress and Analytics
  async getProgress(): Promise<CommunicationProgress[]> {
    const response = await api.get('/communication/progress');
    return response.data;
  }

  async getDashboard(): Promise<CommunicationDashboard> {
    const response = await api.get('/communication/dashboard');
    return response.data;
  }
}

export const communicationService = new CommunicationService();
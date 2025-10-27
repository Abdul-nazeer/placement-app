import api from '../lib/api';
import {
  CodingChallenge,
  CodingChallengeSearchResult,
  CodingChallengeFilters,
  CodeSubmission,
  CodeSubmissionCreate,
  UserCodingStats,
  CodeQualityMetrics,
  CodingChallengeAnalytics,
  DifficultyLevel,
  LanguageType
} from '../types/coding';

export class CodingService {
  // Challenge Management
  static async getChallenges(filters: CodingChallengeFilters): Promise<CodingChallengeSearchResult> {
    const params = new URLSearchParams();
    
    if (filters.difficulty?.length) {
      filters.difficulty.forEach(d => params.append('difficulty', d));
    }
    if (filters.category?.length) {
      filters.category.forEach(c => params.append('category', c));
    }
    if (filters.topic_tags?.length) {
      filters.topic_tags.forEach(t => params.append('topic_tags', t));
    }
    if (filters.company_tags?.length) {
      filters.company_tags.forEach(c => params.append('company_tags', c));
    }
    if (filters.search) {
      params.append('search', filters.search);
    }
    if (filters.is_active !== undefined) {
      params.append('is_active', filters.is_active.toString());
    }
    if (filters.limit) {
      params.append('limit', filters.limit.toString());
    }
    if (filters.offset) {
      params.append('offset', filters.offset.toString());
    }

    const response = await api.get(`/coding/challenges?${params.toString()}`);
    return response.data;
  }

  static async getChallenge(challengeId: string): Promise<CodingChallenge> {
    const response = await api.get(`/coding/challenges/${challengeId}`);
    return response.data;
  }

  static async getCategories(): Promise<string[]> {
    const response = await api.get('/coding/categories');
    return response.data;
  }

  static async getSupportedLanguages(): Promise<string[]> {
    const response = await api.get('/coding/languages');
    return response.data;
  }

  static async getDifficultyLevels(): Promise<string[]> {
    const response = await api.get('/coding/difficulties');
    return response.data;
  }

  // Code Submission
  static async submitCode(submission: CodeSubmissionCreate): Promise<CodeSubmission> {
    const response = await api.post('/coding/submissions', submission);
    return response.data;
  }

  static async getSubmission(submissionId: string): Promise<CodeSubmission> {
    const response = await api.get(`/coding/submissions/${submissionId}`);
    return response.data;
  }

  static async getUserSubmissions(
    challengeId?: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<CodeSubmission[]> {
    const params = new URLSearchParams();
    if (challengeId) params.append('challenge_id', challengeId);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await api.get(`/coding/submissions?${params.toString()}`);
    return response.data;
  }

  // Analytics and Stats
  static async getUserStats(): Promise<UserCodingStats> {
    const response = await api.get('/coding/users/me/stats');
    return response.data;
  }

  static async getChallengeAnalytics(challengeId: string): Promise<CodingChallengeAnalytics> {
    const response = await api.get(`/coding/challenges/${challengeId}/analytics`);
    return response.data;
  }

  static async getCodeQuality(submissionId: string): Promise<CodeQualityMetrics> {
    const response = await api.get(`/coding/submissions/${submissionId}/quality`);
    return response.data;
  }

  // Utility functions
  static getDifficultyColor(difficulty: DifficultyLevel): string {
    switch (difficulty) {
      case 'easy':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'hard':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  static getLanguageDisplayName(language: LanguageType): string {
    switch (language) {
      case 'python':
        return 'Python';
      case 'java':
        return 'Java';
      case 'cpp':
        return 'C++';
      case 'javascript':
        return 'JavaScript';
      default:
        return language;
    }
  }

  static getLanguageExtension(language: LanguageType): string {
    switch (language) {
      case 'python':
        return 'py';
      case 'java':
        return 'java';
      case 'cpp':
        return 'cpp';
      case 'javascript':
        return 'js';
      default:
        return 'txt';
    }
  }

  static getMonacoLanguage(language: LanguageType): string {
    switch (language) {
      case 'python':
        return 'python';
      case 'java':
        return 'java';
      case 'cpp':
        return 'cpp';
      case 'javascript':
        return 'javascript';
      default:
        return 'plaintext';
    }
  }

  static formatExecutionTime(timeMs?: number): string {
    if (!timeMs) return 'N/A';
    if (timeMs < 1000) return `${timeMs.toFixed(0)}ms`;
    return `${(timeMs / 1000).toFixed(2)}s`;
  }

  static formatMemoryUsage(memoryMB?: number): string {
    if (!memoryMB) return 'N/A';
    if (memoryMB < 1) return `${(memoryMB * 1024).toFixed(0)}KB`;
    return `${memoryMB.toFixed(2)}MB`;
  }

  static getStatusColor(status: string): string {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
      case 'timeout':
      case 'memory_exceeded':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }
}
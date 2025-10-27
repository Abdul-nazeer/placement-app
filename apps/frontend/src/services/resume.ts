/**
 * Resume analysis and optimization service
 */

import api from '../lib/api';
import {
  Resume,
  ResumeAnalysisResponse,
  ResumeVersion,
  ResumeTemplate,
  ResumeOptimizationRequest,
  ResumeComparisonRequest,
  ResumeComparisonResponse,
  ResumeUploadRequest,
  ResumeFilters,
  ResumeTemplateFilters,
} from '../types/resume';

export class ResumeService {
  // Resume Upload and Management
  async uploadResume(
    file: File,
    uploadData?: ResumeUploadRequest
  ): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (uploadData?.target_role) {
      formData.append('target_role', uploadData.target_role);
    }
    if (uploadData?.target_industry) {
      formData.append('target_industry', uploadData.target_industry);
    }

    const response = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getUserResumes(filters?: ResumeFilters): Promise<Resume[]> {
    const params = new URLSearchParams();
    
    if (filters?.processing_status) {
      params.append('processing_status', filters.processing_status);
    }
    if (filters?.file_type) {
      params.append('file_type', filters.file_type);
    }
    if (filters?.date_range) {
      params.append('start_date', filters.date_range.start);
      params.append('end_date', filters.date_range.end);
    }
    
    const response = await api.get(`/resume/?${params.toString()}`);
    return response.data;
  }

  async getResumeById(resumeId: string): Promise<Resume> {
    const response = await api.get(`/resume/${resumeId}`);
    return response.data;
  }

  async deleteResume(resumeId: string): Promise<void> {
    await api.delete(`/resume/${resumeId}`);
  }

  // Resume Analysis
  async getResumeAnalysis(resumeId: string): Promise<ResumeAnalysisResponse> {
    const response = await api.get(`/resume/${resumeId}/analysis`);
    return response.data;
  }

  async reanalyzeResume(
    resumeId: string,
    targetRole?: string,
    targetIndustry?: string
  ): Promise<{ message: string; resume_id: string }> {
    const formData = new FormData();
    
    if (targetRole) {
      formData.append('target_role', targetRole);
    }
    if (targetIndustry) {
      formData.append('target_industry', targetIndustry);
    }

    const response = await api.post(`/resume/${resumeId}/reanalyze`, formData);
    return response.data;
  }

  // Resume Optimization
  async optimizeResume(
    request: ResumeOptimizationRequest
  ): Promise<ResumeAnalysisResponse> {
    const response = await api.post('/resume/optimize', request);
    return response.data;
  }

  // Resume Comparison
  async compareResumes(
    request: ResumeComparisonRequest
  ): Promise<ResumeComparisonResponse> {
    const response = await api.post('/resume/compare', request);
    return response.data;
  }

  // Resume Templates
  async getResumeTemplates(
    filters?: ResumeTemplateFilters
  ): Promise<ResumeTemplate[]> {
    const params = new URLSearchParams();
    
    if (filters?.category) {
      params.append('category', filters.category);
    }
    if (filters?.industry) {
      params.append('industry', filters.industry);
    }
    if (filters?.ats_friendly !== undefined) {
      params.append('ats_friendly', filters.ats_friendly.toString());
    }
    
    const response = await api.get(`/resume/templates/?${params.toString()}`);
    return response.data;
  }

  // Resume Versions
  async getResumeVersions(resumeId: string): Promise<ResumeVersion[]> {
    const response = await api.get(`/resume/${resumeId}/versions`);
    return response.data;
  }

  // File Download
  async downloadResume(resumeId: string): Promise<Blob> {
    const response = await api.get(`/resume/${resumeId}/download`);
    return response.data;
  }

  // Utility methods
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getScoreColor(score: number): string {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  }

  getScoreBadgeColor(score: number): string {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  }

  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }

  validateFileType(file: File): boolean {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    return allowedTypes.includes(file.type);
  }

  validateFileSize(file: File, maxSizeMB: number = 10): boolean {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
  }
}

export const resumeService = new ResumeService();
import api from '../lib/api';
import {
  Question,
  QuestionCreate,
  QuestionUpdate,
  QuestionFilters,
  QuestionSearchResult,
  Category,
  Tag,
  Company,
  BulkOperationResult,
  QuestionAnalytics,
  ContentAnalytics
} from '../types/content';

export const contentService = {
  // Question management
  async createQuestion(data: QuestionCreate): Promise<Question> {
    const response = await api.post('/content/questions', data);
    return response.data;
  },

  async searchQuestions(
    filters: QuestionFilters = {},
    page: number = 1,
    size: number = 20,
    sortBy: string = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<QuestionSearchResult> {
    const params = new URLSearchParams();
    
    // Add filters to params
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
    
    // Add pagination and sorting
    params.append('page', page.toString());
    params.append('size', size.toString());
    params.append('sort_by', sortBy);
    params.append('sort_order', sortOrder);

    const response = await api.get(`/content/questions/search?${params.toString()}`);
    return response.data;
  },

  async getQuestion(id: string): Promise<Question> {
    const response = await api.get(`/content/questions/${id}`);
    return response.data;
  },

  async updateQuestion(id: string, data: QuestionUpdate): Promise<Question> {
    const response = await api.put(`/content/questions/${id}`, data);
    return response.data;
  },

  async deleteQuestion(id: string): Promise<void> {
    await api.delete(`/content/questions/${id}`);
  },

  async approveQuestion(id: string): Promise<Question> {
    const response = await api.post(`/content/questions/${id}/approve`);
    return response.data;
  },

  async rejectQuestion(id: string, reason?: string): Promise<Question> {
    const params = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    const response = await api.post(`/content/questions/${id}/reject${params}`);
    return response.data;
  },

  // Bulk operations
  async bulkCreateQuestions(questions: QuestionCreate[]): Promise<BulkOperationResult> {
    const response = await api.post('/content/questions/bulk', { questions });
    return response.data;
  },

  async bulkUpdateQuestions(questionIds: string[], updates: QuestionUpdate): Promise<BulkOperationResult> {
    const response = await api.put('/content/questions/bulk', {
      question_ids: questionIds,
      updates
    });
    return response.data;
  },

  // Import/Export
  async exportQuestionsCSV(filters?: QuestionFilters): Promise<Blob> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v.toString()));
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }

    const response = await api.get(`/content/questions/export/csv?${params.toString()}`);
    return response.data;
  },

  async importQuestionsCSV(file: File): Promise<BulkOperationResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/content/questions/import/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Analytics
  async getQuestionAnalytics(id: string): Promise<QuestionAnalytics> {
    const response = await api.get(`/content/questions/${id}/analytics`);
    return response.data;
  },

  async getContentAnalytics(): Promise<ContentAnalytics> {
    const response = await api.get('/content/analytics');
    return response.data;
  },

  // Categories
  async getCategories(typeFilter?: string, parentId?: string, isActive: boolean = true): Promise<Category[]> {
    const params = new URLSearchParams();
    if (typeFilter) params.append('type_filter', typeFilter);
    if (parentId) params.append('parent_id', parentId);
    params.append('is_active', isActive.toString());

    const response = await api.get(`/content/categories?${params.toString()}`);
    return response.data;
  },

  // Tags
  async getTags(typeFilter?: string, isActive: boolean = true): Promise<Tag[]> {
    const params = new URLSearchParams();
    if (typeFilter) params.append('type_filter', typeFilter);
    params.append('is_active', isActive.toString());

    const response = await api.get(`/content/tags?${params.toString()}`);
    return response.data;
  },

  // Companies
  async getCompanies(isActive: boolean = true, isFeatured?: boolean): Promise<Company[]> {
    const params = new URLSearchParams();
    params.append('is_active', isActive.toString());
    if (isFeatured !== undefined) params.append('is_featured', isFeatured.toString());

    const response = await api.get(`/content/companies?${params.toString()}`);
    return response.data;
  }
};
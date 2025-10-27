/**
 * Resume analysis and optimization types
 */

export interface ContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
  linkedin?: string;
  github?: string;
  website?: string;
}

export interface WorkExperience {
  company: string;
  position: string;
  start_date?: string;
  end_date?: string;
  location?: string;
  description: string[];
  skills_used: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  achievements: string[];
}

export interface Skill {
  name: string;
  category: string;
  proficiency?: string;
  years_experience?: number;
}

export interface ResumeSection {
  type: string;
  title: string;
  content: string;
  items?: Record<string, any>[];
}

export interface StructuredResumeData {
  contact_info: ContactInfo;
  summary?: string;
  work_experience: WorkExperience[];
  education: Education[];
  skills: Skill[];
  certifications: string[];
  projects: Record<string, any>[];
  sections: ResumeSection[];
}

export interface ATSAnalysis {
  overall_score: number;
  keyword_score: number;
  format_score: number;
  structure_score: number;
  missing_keywords: string[];
  keyword_density: Record<string, number>;
  format_issues: string[];
  structure_issues: string[];
  keyword_suggestions: string[];
  format_recommendations: string[];
  structure_recommendations: string[];
}

export interface ContentAnalysis {
  readability_score: number;
  grammar_score: number;
  impact_score: number;
  grammar_issues: Array<{ type: string; message: string }>;
  weak_phrases: string[];
  missing_metrics: string[];
  content_suggestions: Array<{ type: string; suggestion: string }>;
  rewrite_suggestions: Array<{ original: string; suggested: string }>;
}

export interface ResumeAnalysisResult {
  ats_analysis: ATSAnalysis;
  content_analysis: ContentAnalysis;
  overall_score: number;
  industry_match_score?: number;
  strengths: string[];
  weaknesses: string[];
  priority_improvements: string[];
}

export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  ats_score?: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface ResumeAnalysisResponse {
  id: string;
  filename: string;
  ats_score: number;
  analysis_results: ResumeAnalysisResult;
  suggestions: Array<{
    type: string;
    priority: string;
    suggestion: string;
    impact: string;
  }>;
  processing_status: string;
  created_at: string;
}

export interface ResumeVersion {
  id: string;
  resume_id: string;
  version_number: number;
  filename: string;
  ats_score?: number;
  changes_made?: Record<string, any>;
  created_at: string;
}

export interface ResumeTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  industry?: string;
  preview_image?: string;
  is_premium: boolean;
  popularity_score: number;
  ats_friendly_score: number;
}

export interface ResumeOptimizationRequest {
  resume_id: string;
  target_role?: string;
  target_company?: string;
  industry?: string;
  optimization_focus: string[];
}

export interface ResumeComparisonRequest {
  resume_ids: string[];
  comparison_criteria: string[];
}

export interface ResumeComparisonResponse {
  resumes: Resume[];
  comparison_matrix: Record<string, Record<string, number>>;
  recommendations: string[];
  best_practices: string[];
}

export interface ResumeUploadRequest {
  target_role?: string;
  target_industry?: string;
}

export interface ResumeFilters {
  processing_status?: 'pending' | 'processing' | 'completed' | 'failed';
  file_type?: 'pdf' | 'doc' | 'docx';
  date_range?: {
    start: string;
    end: string;
  };
}

export interface ResumeTemplateFilters {
  category?: string;
  industry?: string;
  ats_friendly?: boolean;
}

export interface OptimizationSuggestion {
  type: 'ats_improvement' | 'content_improvement' | 'skill_improvement' | 'format_improvement';
  priority: 'high' | 'medium' | 'low';
  suggestion: string;
  impact: string;
  category?: string;
}

export interface ResumeMetrics {
  total_resumes: number;
  average_ats_score: number;
  improvement_over_time: number;
  top_skills: string[];
  recent_uploads: number;
}

export interface ResumeEditorState {
  content: StructuredResumeData;
  isDirty: boolean;
  isLoading: boolean;
  activeSection?: string;
  suggestions: OptimizationSuggestion[];
}

export interface DragDropFile {
  file: File;
  preview?: string;
  progress?: number;
  error?: string;
}
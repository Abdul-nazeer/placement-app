export enum QuestionType {
  APTITUDE = 'aptitude',
  CODING = 'coding',
  COMMUNICATION = 'communication'
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
  is_premium: boolean;
  status: QuestionStatus;
  version: number;
  parent_question_id?: string;
  usage_count: number;
  success_rate?: number;
  average_time?: number;
  created_by?: string;
  reviewed_by?: string;
  is_active: boolean;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreate {
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
  is_premium: boolean;
  status?: QuestionStatus;
}

export interface QuestionUpdate {
  type?: QuestionType;
  category?: string;
  subcategory?: string;
  difficulty?: DifficultyLevel;
  title?: string;
  content?: string;
  options?: string[];
  correct_answer?: string;
  explanation?: string;
  hints?: string[];
  company_tags?: string[];
  topic_tags?: string[];
  skill_tags?: string[];
  extra_data?: Record<string, any>;
  status?: QuestionStatus;
  is_premium?: boolean;
}

export interface QuestionFilters {
  type?: QuestionType;
  category?: string;
  subcategory?: string;
  difficulty?: DifficultyLevel[];
  company_tags?: string[];
  topic_tags?: string[];
  skill_tags?: string[];
  status?: QuestionStatus[];
  is_active?: boolean;
  is_premium?: boolean;
  search?: string;
  min_success_rate?: number;
  max_success_rate?: number;
  min_usage_count?: number;
}

export interface QuestionSearchResult {
  questions: Question[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  type: string;
  parent_id?: string;
  level: number;
  sort_order: number;
  icon?: string;
  color?: string;
  is_active: boolean;
  question_count: number;
  children: Category[];
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  description?: string;
  type: string;
  color?: string;
  is_active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  description?: string;
  industry?: string;
  size?: string;
  headquarters?: string;
  website?: string;
  logo_url?: string;
  is_active: boolean;
  is_featured: boolean;
  question_count: number;
  popularity_score: number;
  created_at: string;
  updated_at: string;
}

export interface BulkOperationResult {
  success_count: number;
  error_count: number;
  errors: Array<Record<string, any>>;
}

export interface QuestionAnalytics {
  question_id: string;
  usage_count: number;
  success_rate?: number;
  average_time?: number;
  difficulty_rating?: number;
  user_feedback_score?: number;
}

export interface ContentAnalytics {
  total_questions: number;
  questions_by_type: Record<string, number>;
  questions_by_difficulty: Record<string, number>;
  questions_by_status: Record<string, number>;
  top_companies: Array<{ name: string; count: number }>;
  top_topics: Array<{ name: string; count: number }>;
  average_success_rate?: number;
  total_submissions: number;
}
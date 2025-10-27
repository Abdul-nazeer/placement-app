export type DifficultyLevel = 'easy' | 'medium' | 'hard';
export type LanguageType = 'python' | 'java' | 'cpp' | 'javascript';
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'timeout' | 'memory_exceeded';

export interface TestCase {
  id: string;
  challenge_id: string;
  input_data: string;
  expected_output: string;
  is_sample: boolean;
  is_hidden: boolean;
  weight: number;
  explanation?: string;
  created_at: string;
}

export interface CodingChallenge {
  id: string;
  title: string;
  description: string;
  difficulty: DifficultyLevel;
  category: string;
  topic_tags: string[];
  company_tags: string[];
  time_limit: number;
  memory_limit: number;
  template_code: Record<string, string>;
  solution_approach?: string;
  hints: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  created_by: string;
  test_cases: TestCase[];
}

export interface CodingChallengeList {
  id: string;
  title: string;
  difficulty: DifficultyLevel;
  category: string;
  topic_tags: string[];
  company_tags: string[];
  created_at: string;
  is_active: boolean;
}

export interface TestCaseResult {
  test_case_id: string;
  passed: boolean;
  execution_time: number;
  memory_usage: number;
  actual_output?: string;
  error_message?: string;
}

export interface CodeSubmission {
  id: string;
  user_id: string;
  challenge_id: string;
  session_id?: string;
  language: LanguageType;
  code: string;
  status: ExecutionStatus;
  score: number;
  total_test_cases: number;
  passed_test_cases: number;
  execution_time?: number;
  memory_usage?: number;
  test_results: TestCaseResult[];
  compilation_error?: string;
  runtime_error?: string;
  submitted_at: string;
  executed_at?: string;
}

export interface CodeSubmissionCreate {
  challenge_id: string;
  language: LanguageType;
  code: string;
  session_id?: string;
}

export interface CodingChallengeFilters {
  difficulty?: DifficultyLevel[];
  category?: string[];
  topic_tags?: string[];
  company_tags?: string[];
  is_active?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface CodingChallengeSearchResult {
  challenges: CodingChallengeList[];
  total: number;
  limit: number;
  offset: number;
}

export interface UserCodingStats {
  user_id: string;
  total_submissions: number;
  successful_submissions: number;
  average_score: number;
  challenges_solved: number;
  favorite_language?: string;
  difficulty_breakdown: Record<string, number>;
  recent_submissions: CodeSubmission[];
}

export interface CodeQualityMetrics {
  submission_id: string;
  complexity_score: number;
  readability_score: number;
  efficiency_score: number;
  best_practices_score: number;
  suggestions: string[];
  code_smells: string[];
  analyzed_at: string;
  model_version: string;
}

export interface CodingChallengeAnalytics {
  challenge_id: string;
  title: string;
  total_submissions: number;
  successful_submissions: number;
  average_score: number;
  average_execution_time?: number;
  difficulty_rating: number;
  popular_languages: Record<string, number>;
}

// UI-specific types
export interface ChallengeFilters {
  difficulty: DifficultyLevel[];
  category: string[];
  topicTags: string[];
  companyTags: string[];
  search: string;
}

export interface CodeEditorProps {
  language: LanguageType;
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  height?: string;
}

export interface TestResult {
  testCase: TestCase;
  result: TestCaseResult;
}

export interface SubmissionHistory {
  submissions: CodeSubmission[];
  totalPages: number;
  currentPage: number;
}
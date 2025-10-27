// Shared TypeScript types for PlacementPrep

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  createdAt: string
  lastLogin?: string
  isActive: boolean
}

export interface UserProfile {
  userId: string
  college?: string
  graduationYear?: number
  targetCompanies: string[]
  preferredRoles: string[]
  skillLevels: Record<string, number>
}

export type UserRole = 'student' | 'trainer' | 'admin'

export interface Question {
  id: string
  type: QuestionType
  category: string
  difficulty: DifficultyLevel
  content: string
  options?: string[]
  correctAnswer: string
  explanation?: string
  companyTags: string[]
  topicTags: string[]
}

export type QuestionType = 'aptitude' | 'coding' | 'communication'
export type DifficultyLevel = 1 | 2 | 3 | 4 | 5

export interface TestSession {
  id: string
  userId: string
  testType: TestType
  configuration: TestConfig
  startTime: string
  endTime?: string
  status: SessionStatus
  score?: number
}

export type TestType = 'aptitude' | 'coding' | 'communication' | 'mock_interview'
export type SessionStatus = 'active' | 'completed' | 'abandoned'

export interface TestConfig {
  category: string
  difficulty?: DifficultyLevel
  timeLimit: number
  questionCount: number
  companyFilter?: string[]
}

export interface Submission {
  id: string
  sessionId: string
  questionId: string
  userAnswer: string
  isCorrect: boolean
  timeTaken: number
  submittedAt: string
}

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
  context?: SessionContext
}

export interface SessionContext {
  type: 'coding' | 'aptitude' | 'general'
  sessionId?: string
  questionId?: string
}

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
  hasPrev: boolean
}
// Shared constants for PlacementPrep

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
  },
  USERS: {
    PROFILE: '/users/profile',
    PROGRESS: '/users/progress',
  },
  QUESTIONS: {
    LIST: '/questions',
    CATEGORIES: '/questions/categories',
    COMPANIES: '/questions/companies',
  },
  SESSIONS: {
    CREATE: '/sessions',
    SUBMIT: '/sessions/{id}/submit',
    COMPLETE: '/sessions/{id}/complete',
  },
  CHAT: {
    MESSAGE: '/chat',
    HISTORY: '/chat/history',
  },
} as const

export const QUESTION_CATEGORIES = {
  APTITUDE: {
    LOGICAL_REASONING: 'logical_reasoning',
    QUANTITATIVE: 'quantitative',
    VERBAL: 'verbal',
    DATA_INTERPRETATION: 'data_interpretation',
  },
  CODING: {
    ARRAYS: 'arrays',
    STRINGS: 'strings',
    LINKED_LISTS: 'linked_lists',
    TREES: 'trees',
    GRAPHS: 'graphs',
    DYNAMIC_PROGRAMMING: 'dynamic_programming',
    ALGORITHMS: 'algorithms',
  },
  COMMUNICATION: {
    HR_QUESTIONS: 'hr_questions',
    BEHAVIORAL: 'behavioral',
    SITUATIONAL: 'situational',
    PRESENTATION: 'presentation',
  },
} as const

export const DIFFICULTY_LEVELS = {
  BEGINNER: 1,
  EASY: 2,
  MEDIUM: 3,
  HARD: 4,
  EXPERT: 5,
} as const

export const USER_ROLES = {
  STUDENT: 'student',
  TRAINER: 'trainer',
  ADMIN: 'admin',
} as const

export const SESSION_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  ABANDONED: 'abandoned',
} as const

export const SUPPORTED_LANGUAGES = {
  PYTHON: 'python',
  JAVASCRIPT: 'javascript',
  JAVA: 'java',
  CPP: 'cpp',
  C: 'c',
} as const
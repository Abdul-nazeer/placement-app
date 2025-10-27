export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'trainer' | 'admin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: string;
  college?: string;
  graduation_year?: number;
  target_companies: string[];
  preferred_roles: string[];
  skill_levels: Record<string, number>;
  bio?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  resume_url?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  name: string;
  password: string;
  role?: 'student' | 'trainer' | 'admin';
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp?: string;
}
import api, { tokenUtils } from '../lib/api';
import {
  User,
  LoginCredentials,
  RegisterData,
  TokenResponse,
  UserProfile,
  PasswordChangeData,
} from '../types/auth';

export class AuthService {
  /**
   * Register a new user
   */
  static async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  }

  /**
   * Login user and store tokens
   */
  static async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    const tokenData = response.data;

    // Store tokens in cookies
    tokenUtils.setTokens(tokenData.access_token, tokenData.refresh_token);

    return tokenData;
  }

  /**
   * Logout user and clear tokens
   */
  static async logout(): Promise<void> {
    const refreshToken = tokenUtils.getRefreshToken();
    
    try {
      await api.post('/auth/logout', {
        refresh_token: refreshToken,
      });
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear tokens
      tokenUtils.clearTokens();
    }
  }

  /**
   * Refresh access token
   */
  static async refreshToken(): Promise<TokenResponse> {
    const refreshToken = tokenUtils.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    const tokenData = response.data;
    tokenUtils.setTokens(tokenData.access_token, tokenData.refresh_token);

    return tokenData;
  }

  /**
   * Get current user information
   */
  static async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  }

  /**
   * Verify if current token is valid
   */
  static async verifyToken(): Promise<{ valid: boolean; user?: User }> {
    try {
      const response = await api.post('/auth/verify-token');
      return {
        valid: true,
        user: response.data.user,
      };
    } catch {
      return { valid: false };
    }
  }

  /**
   * Change user password
   */
  static async changePassword(data: PasswordChangeData): Promise<void> {
    await api.post('/auth/change-password', data);
  }

  /**
   * Get user profile
   */
  static async getUserProfile(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/users/profile');
    return response.data;
  }

  /**
   * Update user profile
   */
  static async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.put<UserProfile>('/users/profile', data);
    return response.data;
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const token = tokenUtils.getAccessToken();
    return token !== null && !tokenUtils.isTokenExpired(token);
  }

  /**
   * Get user role from token
   */
  static getUserRole(): string | null {
    const token = tokenUtils.getAccessToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.role || null;
    } catch {
      return null;
    }
  }

  /**
   * Check if user has specific role
   */
  static hasRole(role: string): boolean {
    const userRole = this.getUserRole();
    return userRole === role;
  }

  /**
   * Check if user has any of the specified roles
   */
  static hasAnyRole(roles: string[]): boolean {
    const userRole = this.getUserRole();
    return userRole ? roles.includes(userRole) : false;
  }
}
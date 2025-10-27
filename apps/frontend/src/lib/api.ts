import axios, { AxiosInstance, AxiosError } from 'axios';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Token storage keys
export const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const;

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management utilities
export const tokenUtils = {
  getAccessToken: (): string | null => {
    return Cookies.get(TOKEN_KEYS.ACCESS_TOKEN) || null;
  },

  getRefreshToken: (): string | null => {
    return Cookies.get(TOKEN_KEYS.REFRESH_TOKEN) || null;
  },

  setTokens: (accessToken: string, refreshToken: string): void => {
    // Set secure cookies with appropriate expiration
    const accessTokenExpiry = new Date(Date.now() + 30 * 60 * 1000); // 30 minutes
    const refreshTokenExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

    Cookies.set(TOKEN_KEYS.ACCESS_TOKEN, accessToken, {
      expires: accessTokenExpiry,
      secure: import.meta.env.PROD || false,
      sameSite: 'strict',
    });

    Cookies.set(TOKEN_KEYS.REFRESH_TOKEN, refreshToken, {
      expires: refreshTokenExpiry,
      secure: import.meta.env.PROD || false,
      sameSite: 'strict',
    });
  },

  clearTokens: (): void => {
    Cookies.remove(TOKEN_KEYS.ACCESS_TOKEN);
    Cookies.remove(TOKEN_KEYS.REFRESH_TOKEN);
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: any) => {
    const token = tokenUtils.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh and error handling
api.interceptors.response.use(
  (response: any) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Handle 401 errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = tokenUtils.getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          tokenUtils.setTokens(access_token, newRefreshToken);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api.request(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          tokenUtils.clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        tokenUtils.clearTokens();
        window.location.href = '/login';
      }
    }

    // Handle other errors
    if (error.response?.data) {
      const errorData = error.response.data as any;
      if (errorData.message) {
        toast.error(errorData.message);
      }
    } else if (error.message) {
      toast.error(error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
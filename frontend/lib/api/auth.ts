import { apiClient } from './client';
import {
  RegisterRequest,
  LoginRequest,
  TokenResponse,
  UserResponse,
  EmailVerificationRequest,
  ResendVerificationRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  MessageResponse,
} from './types';

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterRequest): Promise<UserResponse> => {
    return apiClient.post<UserResponse>('/auth/register', data);
  },

  /**
   * Login with email and password
   */
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    // Store tokens
    apiClient.setTokens(response.access_token, response.refresh_token);
    return response;
  },

  /**
   * Logout - clear tokens
   */
  logout: (): void => {
    apiClient.clearTokens();
  },

  /**
   * Verify email with token
   */
  verifyEmail: async (data: EmailVerificationRequest): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>('/auth/verify-email', data);
  },

  /**
   * Resend verification email
   */
  resendVerification: async (data: ResendVerificationRequest): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>('/auth/resend-verification', data);
  },

  /**
   * Request password reset
   */
  requestPasswordReset: async (data: PasswordResetRequest): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>('/auth/request-password-reset', data);
  },

  /**
   * Reset password with token
   */
  resetPassword: async (data: PasswordResetConfirm): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>('/auth/reset-password', data);
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<UserResponse> => {
    return apiClient.get<UserResponse>('/auth/me');
  },

  /**
   * Refresh access token
   */
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh-token', {
      refresh_token: refreshToken,
    });
    // Store new tokens
    apiClient.setTokens(response.access_token, response.refresh_token);
    return response;
  },
};

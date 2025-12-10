import { apiClient } from './client';
import {
  TelegramAccountStartAuth,
  StartAuthResponse,
  TelegramAccountVerifyCode,
  TelegramAccountResponse,
  TelegramAccountDetail,
  DialogInfo,
  SubscriptionCreate,
  SubscriptionUpdate,
  SubscriptionResponse,
} from './telegram-types';

export const telegramApi = {
  // Telegram Accounts
  startAuth: async (data: TelegramAccountStartAuth): Promise<StartAuthResponse> => {
    return apiClient.post<StartAuthResponse>('/telegram/accounts/start-auth', data);
  },

  verifyCode: async (data: TelegramAccountVerifyCode): Promise<TelegramAccountResponse> => {
    return apiClient.post<TelegramAccountResponse>('/telegram/accounts/verify-code', data);
  },

  listAccounts: async (): Promise<TelegramAccountResponse[]> => {
    return apiClient.get<TelegramAccountResponse[]>('/telegram/accounts');
  },

  getAccount: async (accountId: string): Promise<TelegramAccountDetail> => {
    return apiClient.get<TelegramAccountDetail>(`/telegram/accounts/${accountId}`);
  },

  deleteAccount: async (accountId: string): Promise<void> => {
    return apiClient.delete<void>(`/telegram/accounts/${accountId}`);
  },

  getDialogs: async (accountId: string, limit: number = 100): Promise<DialogInfo[]> => {
    return apiClient.get<DialogInfo[]>(`/telegram/accounts/${accountId}/dialogs`, {
      params: { limit },
    });
  },

  // Subscriptions
  createSubscription: async (data: SubscriptionCreate): Promise<SubscriptionResponse> => {
    return apiClient.post<SubscriptionResponse>('/subscriptions', data);
  },

  listSubscriptions: async (): Promise<SubscriptionResponse[]> => {
    return apiClient.get<SubscriptionResponse[]>('/subscriptions');
  },

  getSubscription: async (subscriptionId: string): Promise<SubscriptionResponse> => {
    return apiClient.get<SubscriptionResponse>(`/subscriptions/${subscriptionId}`);
  },

  updateSubscription: async (subscriptionId: string, data: SubscriptionUpdate): Promise<SubscriptionResponse> => {
    return apiClient.patch<SubscriptionResponse>(`/subscriptions/${subscriptionId}`, data);
  },

  deleteSubscription: async (subscriptionId: string): Promise<void> => {
    return apiClient.delete<void>(`/subscriptions/${subscriptionId}`);
  },
};

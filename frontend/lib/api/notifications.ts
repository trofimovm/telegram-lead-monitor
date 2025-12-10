import { apiClient } from './client';
import {
  NotificationResponse,
  NotificationListResponse,
  NotificationStats,
  NotificationMarkAsRead,
  NotificationMarkAllAsRead,
  NotificationListParams,
  NotificationPreferences,
  TelegramBotInfo,
  TelegramVerificationCodeResponse,
  TelegramVerifyRequest,
  TelegramVerifyResponse,
  TelegramDisconnectResponse,
} from './notification-types';

/**
 * API клиент для работы с уведомлениями
 */
export const notificationsApi = {
  /**
   * Получить список уведомлений с фильтрацией и пагинацией
   */
  listNotifications: async (params?: NotificationListParams): Promise<NotificationListResponse> => {
    const queryParams: Record<string, any> = {};

    if (params?.is_read !== undefined) {
      queryParams.is_read = params.is_read;
    }
    if (params?.notification_type) {
      queryParams.notification_type = params.notification_type;
    }
    if (params?.skip !== undefined) {
      queryParams.skip = params.skip;
    }
    if (params?.limit !== undefined) {
      queryParams.limit = params.limit;
    }

    return apiClient.get<NotificationListResponse>('/notifications', { params: queryParams });
  },

  /**
   * Получить статистику по уведомлениям
   */
  getNotificationStats: async (): Promise<NotificationStats> => {
    return apiClient.get<NotificationStats>('/notifications/stats');
  },

  /**
   * Получить одно уведомление по ID
   */
  getNotification: async (notificationId: string): Promise<NotificationResponse> => {
    return apiClient.get<NotificationResponse>(`/notifications/${notificationId}`);
  },

  /**
   * Пометить уведомление как прочитанное/непрочитанное
   */
  markAsRead: async (notificationId: string, isRead: boolean = true): Promise<NotificationResponse> => {
    const data: NotificationMarkAsRead = { is_read: isRead };
    return apiClient.patch<NotificationResponse>(`/notifications/${notificationId}`, data);
  },

  /**
   * Пометить все уведомления как прочитанные
   */
  markAllAsRead: async (): Promise<NotificationMarkAllAsRead> => {
    return apiClient.post<NotificationMarkAllAsRead>('/notifications/mark-all-read', {});
  },

  /**
   * Удалить уведомление
   */
  deleteNotification: async (notificationId: string): Promise<void> => {
    return apiClient.delete<void>(`/notifications/${notificationId}`);
  },

  /**
   * Получить настройки уведомлений текущего пользователя
   */
  getPreferences: async (): Promise<NotificationPreferences> => {
    return apiClient.get<NotificationPreferences>('/users/me/notification-preferences');
  },

  /**
   * Обновить настройки уведомлений
   */
  updatePreferences: async (preferences: NotificationPreferences): Promise<NotificationPreferences> => {
    return apiClient.patch<NotificationPreferences>('/users/me/notification-preferences', preferences);
  },

  /**
   * Получить информацию о подключении Telegram бота
   */
  getTelegramBotInfo: async (): Promise<TelegramBotInfo> => {
    return apiClient.get<TelegramBotInfo>('/users/me/telegram-bot');
  },

  /**
   * Сгенерировать код верификации для Telegram
   */
  generateTelegramCode: async (): Promise<TelegramVerificationCodeResponse> => {
    return apiClient.post<TelegramVerificationCodeResponse>('/users/me/telegram-bot/generate-code', {});
  },

  /**
   * Верифицировать код и подключить Telegram
   */
  verifyTelegramCode: async (data: TelegramVerifyRequest): Promise<TelegramVerifyResponse> => {
    return apiClient.post<TelegramVerifyResponse>('/users/me/telegram-bot/verify', data);
  },

  /**
   * Отключить Telegram бота
   */
  disconnectTelegramBot: async (): Promise<TelegramDisconnectResponse> => {
    return apiClient.post<TelegramDisconnectResponse>('/users/me/telegram-bot/disconnect', {});
  },
};

/**
 * TypeScript типы для Notifications (системные уведомления).
 * Соответствуют Pydantic schemas из backend/app/schemas/notification.py
 */

/**
 * Типы уведомлений
 */
export enum NotificationType {
  LEAD_CREATED = 'lead_created',
  LEAD_STATUS_CHANGED = 'lead_status_changed',
  LEAD_ASSIGNED = 'lead_assigned',
  RULE_TRIGGERED = 'rule_triggered',
  SYSTEM = 'system',
}

/**
 * Цвета для иконок уведомлений
 */
export const NotificationTypeColors: Record<NotificationType, string> = {
  [NotificationType.LEAD_CREATED]: 'bg-blue-100 text-blue-600',
  [NotificationType.LEAD_STATUS_CHANGED]: 'bg-yellow-100 text-yellow-600',
  [NotificationType.LEAD_ASSIGNED]: 'bg-green-100 text-green-600',
  [NotificationType.RULE_TRIGGERED]: 'bg-purple-100 text-purple-600',
  [NotificationType.SYSTEM]: 'bg-gray-100 text-gray-600',
};

/**
 * Базовый тип уведомления
 */
export interface NotificationResponse {
  id: string;
  tenant_id: string;
  type: NotificationType;
  title: string;
  message: string;
  related_lead_id?: string | null;
  metadata?: Record<string, any> | null;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Список уведомлений с пагинацией
 */
export interface NotificationListResponse {
  notifications: NotificationResponse[];
  total: number;
  unread_count: number;
}

/**
 * Статистика по уведомлениям
 */
export interface NotificationStats {
  total: number;
  unread: number;
  by_type: Record<NotificationType, number>;
  recent_count: number; // За последние 24 часа
}

/**
 * Данные для обновления уведомления
 */
export interface NotificationMarkAsRead {
  is_read: boolean;
}

/**
 * Ответ при пометке всех как прочитанных
 */
export interface NotificationMarkAllAsRead {
  marked_count: number;
}

/**
 * Настройки уведомлений пользователя
 */
export interface NotificationPreferences {
  email_notifications_enabled: boolean;
  in_app_notifications_enabled: boolean;
  telegram_bot_enabled: boolean;
  notify_on_new_lead: boolean;
  notify_on_lead_status_change: boolean;
  notify_on_lead_assignment: boolean;
}

/**
 * Параметры для запроса списка уведомлений
 */
export interface NotificationListParams {
  is_read?: boolean;
  notification_type?: NotificationType;
  skip?: number;
  limit?: number;
}

/**
 * Информация о подключении Telegram бота
 */
export interface TelegramBotInfo {
  bot_username: string;
  is_connected: boolean;
  chat_id?: string | null;
}

/**
 * Ответ с кодом верификации для Telegram
 */
export interface TelegramVerificationCodeResponse {
  verification_code: string;
  expires_at: string;
  bot_username: string;
  instructions: string;
}

/**
 * Запрос на верификацию Telegram
 */
export interface TelegramVerifyRequest {
  verification_code: string;
  chat_id: string;
}

/**
 * Ответ после верификации Telegram
 */
export interface TelegramVerifyResponse {
  success: boolean;
  message: string;
}

/**
 * Ответ после отключения Telegram бота
 */
export interface TelegramDisconnectResponse {
  success: boolean;
  message: string;
}

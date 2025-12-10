/**
 * TypeScript типы для Leads (найденные лиды).
 * Соответствуют Pydantic schemas из backend/app/schemas/lead.py
 */

/**
 * Статусы лида
 */
export enum LeadStatus {
  NEW = 'new',
  IN_PROGRESS = 'in_progress',
  PROCESSED = 'processed',
  ARCHIVED = 'archived',
}

/**
 * Цвета для статусов (для badge компонента)
 */
export const LeadStatusColors: Record<LeadStatus, string> = {
  [LeadStatus.NEW]: 'bg-blue-100 text-blue-800',
  [LeadStatus.IN_PROGRESS]: 'bg-yellow-100 text-yellow-800',
  [LeadStatus.PROCESSED]: 'bg-green-100 text-green-800',
  [LeadStatus.ARCHIVED]: 'bg-gray-100 text-gray-800',
};

/**
 * Извлеченные сущности из сообщения (LLM analysis)
 */
export interface ExtractedEntities {
  contacts?: string[];
  keywords?: string[];
  budget?: string | null;
  deadline?: string | null;
  summary?: string;
}

/**
 * Базовый тип лида
 */
export interface LeadResponse {
  id: string;
  tenant_id: string;
  message_id: string;
  rule_id: string;
  score: number; // 0.00-1.00
  reasoning?: string | null;
  extracted_entities?: ExtractedEntities | null;
  status: LeadStatus;
  assignee_id?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Лид с полными деталями (сообщение, источник, правило, assignee)
 */
export interface LeadWithDetails extends LeadResponse {
  // Message data
  message_text?: string | null;
  message_date?: string | null;
  message_sender_id?: number | null;
  message_views_count?: number | null;
  message_links?: string[];

  // Channel data
  channel_id?: string | null;
  channel_title?: string | null;
  channel_username?: string | null;
  channel_type?: string | null;
  telegram_message_link?: string | null;

  // Rule data
  rule_name?: string | null;
  rule_prompt?: string | null;

  // Assignee data
  assignee_email?: string | null;
  assignee_name?: string | null;
}

/**
 * Данные для обновления лида
 */
export interface LeadUpdate {
  status?: LeadStatus;
  assignee_id?: string | null;
}

/**
 * Фильтры для списка лидов
 */
export interface LeadListFilters {
  status?: LeadStatus;
  rule_id?: string;
  channel_id?: string;
  assignee_id?: string;
  date_from?: string; // ISO date string
  date_to?: string; // ISO date string
  min_score?: number; // 0.00-1.00
  search?: string;
}

/**
 * Параметры для API запроса списка лидов (с пагинацией)
 */
export interface LeadListParams extends LeadListFilters {
  skip?: number;
  limit?: number;
}

/**
 * Статистика по лидам
 */
export interface LeadStats {
  total: number;
  by_status: Record<LeadStatus, number>;
  by_rule: Record<string, number>; // rule_id: count
  by_channel: Record<string, number>; // channel_id: count
  avg_score?: number | null;
  recent_count: number; // За последние 24 часа
}

/**
 * UI state для фильтров лидов
 */
export interface LeadFiltersState {
  status: LeadStatus | 'all';
  rule_id: string | 'all';
  channel_id: string | 'all';
  date_range: 'all' | '24h' | '7d' | '30d' | 'custom';
  date_from?: Date | null;
  date_to?: Date | null;
  min_score: number;
  search: string;
}

/**
 * UI state для detail modal
 */
export interface LeadDetailModalState {
  isOpen: boolean;
  lead: LeadWithDetails | null;
  isLoading: boolean;
  error: string | null;
}
